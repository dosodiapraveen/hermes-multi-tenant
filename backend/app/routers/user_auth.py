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
@limiter.limit("5/hour")
async def register(request: Request, body: dict):
    """Public registration -> creates a PENDING request an admin must approve.
    Email verification is required before approval (enforced in the approve endpoint)."""
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    full_name = (body.get("full_name") or "").strip()[:120]
    agent_name = (body.get("agent_name") or "").strip()[:120]
    use_case = (body.get("use_case") or "").strip()[:500]

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email or not password:
        raise HTTPException(400, "email and password required")
    if len(password) < 12:
        raise HTTPException(400, "Password must be at least 12 characters")
    if not (any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password)):
        raise HTTPException(400, "Password must include uppercase, lowercase, and a number")

    async with async_session_factory() as db:
        r = await db.execute(text(
            "SELECT id FROM registration_requests WHERE email=:e AND status IN ('pending','approved')"
        ), {"e": email})
        if r.fetchone():
            raise HTTPException(409, "A request for this email is already pending or approved.")

        pw_hash = hash_password(password)
        vtoken = generate_token()
        expires = datetime.utcnow() + timedelta(hours=24)
        await db.execute(text("""
            INSERT INTO registration_requests
              (email, password_hash, full_name, agent_name, use_case,
               status, email_verified, verification_token, verification_expires)
            VALUES
              (:e, :h, :n, :a, :u, 'pending', false, :t, :ex)
        """), {"e": email, "h": pw_hash, "n": full_name, "a": agent_name,
               "u": use_case, "t": vtoken, "ex": expires})
        await db.commit()

    await audit_logger.log_event(
        event_type="REGISTRATION_SUBMITTED", severity=AuditLogger.Severity.INFO,
        ip_address=client_ip, request_id=request_id,
        details={"email": email},
    )
    logger.info("registration_request_submitted", email=email)

    try:
        link = f"{FRONTEND_URL}/user/register/verify?token={vtoken}"
        html = f"""<h2>Verify your email</h2>
<p>Hi{f' {full_name}' if full_name else ''},</p>
<p>Please verify your email address to submit your registration for admin review.</p>
<a href="{link}" style="background:#6C5CE7;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none">Verify Email</a>
<p style="color:#888;font-size:13px">Link expires in 24 hours. This only proves you control this email; an admin must still approve your request.</p>"""
        await send_email(email, "Verify your email", html)
        sent = True
    except Exception as e:
        logger.warning("registration_verify_email_failed", email=email, error=str(e))
        sent = False

    return {"status": "pending",
            "message": ("Verification email sent! Confirm it, then an admin reviews your request." if sent else "Verification pending"),
            "verify_link": f"{FRONTEND_URL}/user/register/verify?token={vtoken}"}


@router.get("/register/verify")
async def register_verify(token: str = ""):
    """Verify the email on a pending registration request. Only verified
    requests are eligible for admin approval."""
    if not token:
        raise HTTPException(400, "Token required")

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT id, email, full_name, agent_name FROM registration_requests
            WHERE verification_token=:t AND verification_expires > NOW() AND email_verified=false
        """), {"t": token})
        u = r.fetchone()
        if not u:
            raise HTTPException(400, "Invalid or expired verification token")

        await db.execute(text("""
            UPDATE registration_requests SET email_verified=true, verification_token=NULL WHERE id=:id
        """), {"id": u[0]})
        await db.commit()
        req_id, email, full_name, agent_name = str(u[0]), u[1], u[2] or "", u[3] or ""

    await audit_logger.log_event(
        event_type="REGISTRATION_EMAIL_VERIFIED", severity=AuditLogger.Severity.INFO,
        user_id=req_id, details={"email": email},
    )
    logger.info("registration_email_verified", email=email)

    # Notify admin so they can review + approve.
    try:
        from app.services.admin_notify import notify_admin_new_registration
        await notify_admin_new_registration(email=email, full_name=full_name, agent_name=agent_name)
    except Exception as e:
        logger.warning("admin_notify_failed", error=str(e))

    return {"status": "verified",
            "message": f"Email verified{f', {full_name}' if full_name else ''}! Your request is now with an admin for review. We'll email you once approved."}


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
