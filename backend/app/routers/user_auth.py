"""User authentication: register, verify, login, forgot/reset password."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import text
from app.database import async_session_factory
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
import bcrypt, secrets, httpx
from datetime import datetime, timedelta
from app.logging_config import get_logger
from app.services.audit_logger import audit_logger, AuditLogger
from app.cookie_auth import set_portal_auth_cookies, clear_portal_cookies

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth/user", tags=["user_auth"])
limiter = Limiter(key_func=get_remote_address)

FRONTEND_URL = "https://beprepared.dev"

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, pw_hash: str) -> bool:
    return bcrypt.checkpw(pw.encode(), pw_hash.encode())

def generate_token() -> str:
    return secrets.token_urlsafe(32)

async def send_email(to: str, subject: str, html: str):
    key = settings.resend_api_key
    if not key:
        logger.warning("email_not_configured", subject=subject, recipient=to)
        raise Exception("No API key")
    async with httpx.AsyncClient() as c:
        r = await c.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"from": "Hermes <noreply@beprepared.dev>", "to": to, "subject": subject, "html": html},
        )
        if r.status_code != 200:
            logger.error("email_send_failed", status_code=r.status_code, error=r.text[:100], subject=subject)
            raise Exception(f"Resend: {r.status_code} {r.text[:100]}")
        else:
            logger.info("email_sent_successfully", subject=subject, recipient=to)

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, body: dict):
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    profile_id = body.get("profile_id") or ""

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email or not password:
        logger.warning("registration_missing_fields", has_email=bool(email), has_password=bool(password))
        raise HTTPException(400, "email and password required")

    if len(password) < 12:
        logger.warning("registration_weak_password", email=email, reason="too_short")
        raise HTTPException(400, "Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        logger.warning("registration_weak_password", email=email, reason="no_uppercase")
        raise HTTPException(400, "Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        logger.warning("registration_weak_password", email=email, reason="no_lowercase")
        raise HTTPException(400, "Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        logger.warning("registration_weak_password", email=email, reason="no_digit")
        raise HTTPException(400, "Password must contain at least one number")

    async with async_session_factory() as db:
        # Verify the profile_id exists in user_profiles (only claimed agents)
        if profile_id:
            r = await db.execute(text("SELECT id, agent_name FROM user_profiles WHERE id::text=:p"), {"p": profile_id})
            profile = r.fetchone()
            if not profile:
                logger.warning("registration_invalid_profile", email=email, profile_id=profile_id)
                raise HTTPException(404, "Agent profile not found. You need an invitation link to register.")
        else:
            logger.warning("registration_no_profile", email=email)
            raise HTTPException(400, "Registration requires an agent profile link. Contact your admin.")

        # Check email not already used
        existing = await db.execute(text("SELECT id FROM user_accounts WHERE email=:e"), {"e": email})
        if existing.fetchone():
            logger.warning("registration_email_exists", email=email)
            raise HTTPException(409, "Email already registered")

        pw_hash = hash_password(password)
        vtoken = generate_token()
        expires = datetime.utcnow() + timedelta(hours=24)
        await db.execute(
            text("INSERT INTO user_accounts (user_profile_id, email, password_hash, verification_token, verification_expires) VALUES (:p, :e, :h, :t, :ex)"),
            {"p": profile_id, "e": email, "h": pw_hash, "t": vtoken, "ex": expires},
        )
        await db.commit()

    # Log successful registration
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.REGISTRATION,
        severity=AuditLogger.Severity.INFO,
        user_id=profile_id,
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.info("user_registered", email=email, profile_id=profile_id)

    # Try email, but always show the verification link so user isn't stuck
    try:
        link = f"{FRONTEND_URL}/user/verify?token={vtoken}"
        html = f"""<h2>Welcome, {profile[1]}!</h2><p>Click below to verify your email:</p><a href="{link}">Verify Email</a><p>Link expires in 24 hours.</p>"""
        await send_email(email, "Verify your email", html)
        sent = True
    except Exception as e:
        logger.warning("registration_email_failed", email=email, error=str(e))
        sent = False

    return {"status": "registered", "message": "Verification email sent" if sent else "Verification pending", "verify_link": f"{FRONTEND_URL}/user/verify?token={vtoken}"}

@router.get("/verify")
async def verify(token: str = ""):
    if not token:
        logger.warning("email_verification_missing_token")
        raise HTTPException(400, "Token required")

    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, user_profile_id, email FROM user_accounts WHERE verification_token=:t AND verification_expires > NOW() AND email_verified=false"),
            {"t": token},
        )
        u = r.fetchone()
        if not u:
            logger.warning("email_verification_invalid_token", token_prefix=token[:8])
            raise HTTPException(400, "Invalid or expired token")

        await db.execute(text("UPDATE user_accounts SET email_verified=true, verification_token=NULL WHERE id=:id"), {"id": u[0]})
        await db.commit()

    # Log successful email verification
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.EMAIL_VERIFICATION,
        severity=AuditLogger.Severity.INFO,
        user_id=str(u[1]),
        details={"email": u[2]},
    )
    logger.info("email_verified", user_id=str(u[1]), email=u[2])

    return {"status": "verified"}

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, body: dict):
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email or not password:
        logger.warning("login_missing_credentials", has_email=bool(email), has_password=bool(password))
        raise HTTPException(400, "Email and password required")

    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, user_profile_id, password_hash, email_verified FROM user_accounts WHERE email=:e"),
            {"e": email},
        )
        u = r.fetchone()

        if not u or not verify_password(password, u[2]):
            # Log failed login attempt
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "invalid_credentials"},
            )
            logger.warning("user_login_failed", email=email, reason="invalid_credentials")
            raise HTTPException(401, "Invalid email or password")

        if not u[3]:
            # Log failed login due to unverified email
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                user_id=str(u[1]),
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "email_not_verified"},
            )
            logger.warning("user_login_failed", email=email, reason="email_not_verified")
            raise HTTPException(403, "Email not verified. Check your inbox.")

        token = generate_token()
        await db.execute(text("UPDATE user_accounts SET verification_token=:t WHERE id=:id"), {"t": token, "id": u[0]})
        await db.commit()

        user_id = str(u[1])

    # Set authentication cookies (Phase 2: Cookie-based auth)
    set_portal_auth_cookies(response, token, user_id)

    # Log successful login
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.LOGIN_SUCCESS,
        severity=AuditLogger.Severity.INFO,
        user_id=user_id,
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.info("user_login_success", email=email, user_id=user_id, auth_method="cookie")

    # Return token in response body for backward compatibility
    return {"token": token, "profile_id": user_id}

@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, body: dict):
    email = (body.get("email") or "").strip().lower()

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email:
        logger.warning("forgot_password_missing_email")
        raise HTTPException(400, "Email required")

    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id, user_profile_id FROM user_accounts WHERE email=:e"), {"e": email})
        u = r.fetchone()
        if not u:
            logger.info("forgot_password_unknown_email", email=email)
            return {"status": "sent"}  # Don't reveal if email exists

        rtoken = generate_token()
        expires = datetime.utcnow() + timedelta(hours=1)
        await db.execute(text("UPDATE user_accounts SET reset_token=:t, reset_expires=:ex WHERE id=:id"), {"t": rtoken, "ex": expires, "id": u[0]})
        await db.commit()

    # Log password reset request
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.PASSWORD_RESET_REQUEST,
        severity=AuditLogger.Severity.INFO,
        user_id=str(u[1]),
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.info("password_reset_requested", email=email, user_id=str(u[1]))

    link = f"{FRONTEND_URL}/user/reset?token={rtoken}"
    html = f"""<h2>Reset your password</h2><p>Click the link to set a new password:</p><a href="{link}">Reset Password</a><p>Link expires in 1 hour.</p><p>If you didn't request this, ignore this email.</p>"""

    try:
        await send_email(email, "Reset your password", html)
    except Exception as e:
        logger.error("password_reset_email_failed", email=email, error=str(e))

    return {"status": "sent"}

@router.post("/reset-password")
@limiter.limit("5/hour")
async def reset_password(request: Request, body: dict):
    token = body.get("token") or ""
    password = body.get("password") or ""

    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not token or not password:
        logger.warning("reset_password_missing_fields", has_token=bool(token), has_password=bool(password))
        raise HTTPException(400, "Token and password required")

    if len(password) < 12:
        logger.warning("reset_password_weak_password", reason="too_short")
        raise HTTPException(400, "Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        logger.warning("reset_password_weak_password", reason="no_uppercase")
        raise HTTPException(400, "Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        logger.warning("reset_password_weak_password", reason="no_lowercase")
        raise HTTPException(400, "Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        logger.warning("reset_password_weak_password", reason="no_digit")
        raise HTTPException(400, "Password must contain at least one number")

    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, user_profile_id, email FROM user_accounts WHERE reset_token=:t AND reset_expires > NOW()"),
            {"t": token},
        )
        u = r.fetchone()
        if not u:
            logger.warning("reset_password_invalid_token", token_prefix=token[:8])
            raise HTTPException(400, "Invalid or expired reset token")

        pw_hash = hash_password(password)
        await db.execute(text("UPDATE user_accounts SET password_hash=:h, reset_token=NULL, reset_expires=NULL WHERE id=:id"), {"h": pw_hash, "id": u[0]})
        await db.commit()

    # Log successful password reset
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.PASSWORD_RESET_SUCCESS,
        severity=AuditLogger.Severity.INFO,
        user_id=str(u[1]),
        ip_address=client_ip,
        request_id=request_id,
        details={"email": u[2]},
    )
    logger.info("password_reset_success", user_id=str(u[1]), email=u[2])

    return {"status": "reset"}

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Clear user authentication cookies."""
    clear_portal_cookies(response)

    # Get user info for logging if available
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
    logger.info("user_logout", ip_address=client_ip)

    return {"status": "logged_out"}
