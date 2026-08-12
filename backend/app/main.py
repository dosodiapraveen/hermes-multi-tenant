from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from jose import jwt
import httpx
import bcrypt
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import init_db, close_db
from app.routers import admin, invite, user_auth, user_portal, webhook
from app.auth import verify_jwt
from app.logging_config import setup_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware
from app.services.audit_logger import audit_logger, AuditLogger
from app.cookie_auth import set_admin_auth_cookies, clear_admin_cookies

# Initialize structured logging
setup_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
    service_name="hermes-api"
)

logger = get_logger(__name__)

# Initialize Sentry for error tracking and performance monitoring
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(
                level=None,  # Capture breadcrumbs for all levels
                event_level=None  # Don't send logs as events (we handle this separately)
            ),
        ],
        # Set release version for tracking
        release="hermes-api@0.1.0",
        # Send user context with errors
        send_default_pii=False,  # Don't send PII automatically (we'll add context manually)
    )
    logger.info("sentry_initialized", environment=settings.sentry_environment)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Hermes API", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add logging middleware for request correlation and audit trails
app.add_middleware(LoggingMiddleware)

# Configure CORS with specific allowed origins
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Request-ID"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'"
    return response

@app.get("/api/health")
async def health():
    return {"status":"ok","version":"0.1.0"}

# Admin login
@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def dev_login(request: Request, response: Response, body: dict):
    email = body.get("email", "")
    password = body.get("password", "")

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email or not password:
        logger.warning("admin_login_missing_credentials", email=email)
        raise HTTPException(400, "Email and password required")

    # Verify admin credentials
    if email == settings.admin_email:
        if not settings.admin_password_hash:
            logger.error("admin_password_not_configured")
            raise HTTPException(500, "Admin password not configured. Set ADMIN_PASSWORD_HASH environment variable.")

        try:
            if bcrypt.checkpw(password.encode(), settings.admin_password_hash.encode()):
                # Successful login
                exp = datetime.utcnow() + timedelta(hours=8)
                token = jwt.encode({"sub":"admin","role":"admin","email":email,"exp":exp,"aud":"authenticated"}, settings.supabase_jwt_secret, algorithm="HS256")

                # Set authentication cookies (Phase 2: Cookie-based auth)
                set_admin_auth_cookies(response, token, email)

                # Log successful admin login
                await audit_logger.log_event(
                    event_type=AuditLogger.EventType.ADMIN_LOGIN,
                    severity=AuditLogger.Severity.INFO,
                    ip_address=client_ip,
                    request_id=request_id,
                    admin_email=email,
                )
                logger.info("admin_login_success", email=email, auth_method="cookie")

                # Return token in response body for backward compatibility
                # Frontend can transition from localStorage to cookies
                return {"access_token":token,"token_type":"bearer"}
        except Exception as e:
            logger.error("admin_login_error", email=email, error=str(e))
            pass  # Invalid hash format or other error

    # Failed login attempt
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.ADMIN_LOGIN_FAILED,
        severity=AuditLogger.Severity.WARNING,
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.warning("admin_login_failed", email=email)

    raise HTTPException(401, "Invalid credentials")

# Supabase login (accepts Google SSO token from Supabase)
@app.post("/api/auth/supabase")
@limiter.limit("10/minute")
async def supabase_login(request: Request, response: Response, body: dict):
    """Exchange a Supabase JWT for an internal admin token."""
    supabase_token = body.get("access_token", "")

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not supabase_token:
        logger.warning("supabase_login_missing_token")
        raise HTTPException(400, "Missing access_token")

    try:
        user = await verify_jwt(supabase_token)
        email = user.get("email", "")

        if email == "admin@hermes.io":
            exp = datetime.utcnow() + timedelta(hours=8)
            token = jwt.encode({"sub":email,"role":"admin","email":email,"exp":exp,"aud":"authenticated"}, settings.supabase_jwt_secret, algorithm="HS256")

            # Set authentication cookies (Phase 2: Cookie-based auth)
            set_admin_auth_cookies(response, token, email)

            # Log successful Supabase admin login
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.ADMIN_LOGIN,
                severity=AuditLogger.Severity.INFO,
                ip_address=client_ip,
                request_id=request_id,
                admin_email=email,
                details={"auth_method": "supabase_sso"},
            )
            logger.info("supabase_admin_login_success", email=email, auth_method="cookie")

            return {"access_token":token,"token_type":"bearer","email":email}

        # Not an admin user
        await audit_logger.log_event(
            event_type=AuditLogger.EventType.ADMIN_LOGIN_FAILED,
            severity=AuditLogger.Severity.WARNING,
            ip_address=client_ip,
            request_id=request_id,
            details={"email": email, "reason": "not_admin", "auth_method": "supabase_sso"},
        )
        logger.warning("supabase_login_not_admin", email=email)
        raise HTTPException(403, "Not authorized as admin")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("supabase_login_error", error=str(e), exc_info=True)
        raise HTTPException(401, f"Auth failed: {e}")

# Admin logout
@app.post("/api/auth/logout")
async def admin_logout(request: Request, response: Response):
    """Clear admin authentication cookies."""
    clear_admin_cookies(response)

    # Get admin info for logging if available
    request_id = getattr(request.state, "request_id", None)
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")

    # Log logout event
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.LOGOUT,
        severity=AuditLogger.Severity.INFO,
        ip_address=client_ip,
        request_id=request_id,
    )
    logger.info("admin_logout", ip_address=client_ip)

    return {"status": "logged_out"}

app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(invite.router, prefix="/api/invite", tags=["invite"])
app.include_router(user_auth.router, tags=["user_auth"])
app.include_router(user_portal.router, tags=["portal"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
