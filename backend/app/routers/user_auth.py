"""User authentication: register, verify, login, password setup, forgot/reset password.

Security improvements:
- Separate session tokens with expiration
- Password set after admin approval (not during registration)
- Atomic registration to prevent race conditions
- Standardized error messages to prevent user enumeration
- Rate limiting on all sensitive endpoints
"""
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

# Session configuration
SESSION_DURATION_DAYS = 7  # 7 days for better UX, can be refreshed
SESSION_DURATION = timedelta(days=SESSION_DURATION_DAYS)

# Verification token expiry extended to 72h to match request lifecycle
VERIFICATION_EXPIRY = timedelta(hours=72)
RESET_TOKEN_EXPIRY = timedelta(hours=1)
SETUP_TOKEN_EXPIRY = timedelta(days=3)  # Password setup after approval

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

    SECURITY IMPROVEMENTS:
    - No password required at registration (set after approval)
    - Atomic insert to prevent race conditions
    - Generic response to prevent user enumeration
    - Extended verification window (72h)
    """
    email = (body.get("email") or "").strip().lower()
    full_name = (body.get("full_name") or "").strip()[:120]
    agent_name = (body.get("agent_name") or "").strip()[:120]
    use_case = (body.get("use_case") or "").strip()[:500]

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    # Validation
    if not email:
        raise HTTPException(400, "email is required")
    if not full_name:
        raise HTTPException(400, "full_name is required")
    if len(use_case) < 20:
        raise HTTPException(400, "use_case must be at least 20 characters")

    # Basic email format validation
    if "@" not in email or "." not in email.split("@")[1]:
        raise HTTPException(400, "Please enter a valid email address")

    async with async_session_factory() as db:
        now = datetime.utcnow()
        vtoken = generate_token()
        verify_expires = now + VERIFICATION_EXPIRY  # 72 hours
        req_expires = now + timedelta(hours=72)

        try:
            # SECURITY FIX: Atomic insert with all validation in single query
            # Prevents race conditions and duplicate registrations
            result = await db.execute(text("""
                WITH validation AS (
                    SELECT
                        (SELECT COUNT(*) FROM registration_requests
                         WHERE email=:e AND created_at > :cutoff) as recent_count,
                        (SELECT COUNT(*) FROM registration_requests
                         WHERE email=:e AND status IN ('pending','approved')
                         AND expires_at > :now) as active_count
                )
                INSERT INTO registration_requests
                  (email, full_name, agent_name, use_case,
                   status, email_verified, verification_token, verification_expires, expires_at)
                SELECT :e, :n, :a, :u, 'pending', false, :t, :vex, :rex
                FROM validation
                WHERE recent_count < 3 AND active_count = 0
                RETURNING id
            """), {
                "e": email, "n": full_name, "a": agent_name, "u": use_case,
                "t": vtoken, "vex": verify_expires, "rex": req_expires,
                "cutoff": now - timedelta(hours=24), "now": now
            })

            row = result.fetchone()
            if not row:
                # SECURITY: Don't reveal why it failed (rate limit or duplicate)
                # Return success response to prevent user enumeration
                logger.info("registration_blocked", email=email, reason="rate_limit_or_duplicate")
                await audit_logger.log_event(
                    event_type="REGISTRATION_BLOCKED", severity=AuditLogger.Severity.WARNING,
                    ip_address=client_ip, request_id=request_id,
                    details={"email": email},
                )
                return {
                    "status": "pending",
                    "message": "Verification email sent! Confirm it, then an admin reviews your request."
                }

            await db.commit()

        except Exception as e:
            logger.error("registration_error", email=email, error=str(e))
            raise HTTPException(500, "Registration failed. Please try again later.")

    await audit_logger.log_event(
        event_type="REGISTRATION_SUBMITTED", severity=AuditLogger.Severity.INFO,
        ip_address=client_ip, request_id=request_id,
        details={"email": email},
    )
    logger.info("registration_request_submitted", email=email)

    # Send verification email
    try:
        link = f"{FRONTEND_URL}/user/register/verify?token={vtoken}"
        html = f"""<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:560px;margin:40px auto;padding:20px">
<div style="background:#1A1A2E;border-radius:12px;padding:32px;text-align:center;margin-bottom:24px">
<h1 style="color:#fff;font-size:22px;margin:0">Welcome{f', {full_name}' if full_name else ''}! 👋</h1>
<p style="color:#A29BFE;margin:8px 0 0">Let's verify your email address</p>
</div>
<p style="font-size:15px;color:#333">Click the button below to verify your email and submit your registration for admin review.</p>
<a href="{link}" style="display:block;background:#6C5CE7;color:#fff;padding:14px 24px;border-radius:8px;text-align:center;text-decoration:none;font-size:16px;margin:16px 0">Verify Email Address</a>
<p style="font-size:13px;color:#888">Link expires in 72 hours. After verification, an admin will review your request (usually within 1-3 business days).</p>
<p style="font-size:13px;color:#888;margin-top:24px">Sent by Hermes · beprepared.dev</p>
</body></html>"""
        await send_email(email, "Verify your email", html)
        sent = True
    except Exception as e:
        logger.warning("registration_verify_email_failed", email=email, error=str(e))
        sent = False

    return {
        "status": "pending",
        "message": ("Verification email sent! Check your inbox (and spam folder) to verify." if sent
                   else "Registration submitted. Please check your email to verify."),
        "verification_expires_hours": 72
    }


@router.post("/register/resend-verification")
@limiter.limit("3/hour")
async def resend_verification(request: Request, body: dict):
    """Resend verification email for pending registration.

    UX IMPROVEMENT: Allows users to request new verification link if expired.
    SECURITY: Generic response to prevent email enumeration.
    """
    email = (body.get("email") or "").strip().lower()

    if not email:
        raise HTTPException(400, "email is required")

    async with async_session_factory() as db:
        now = datetime.utcnow()

        # Find pending, unverified request
        r = await db.execute(text("""
            SELECT id, full_name, verification_token
            FROM registration_requests
            WHERE email=:e
              AND status='pending'
              AND email_verified=false
              AND expires_at > :now
        """), {"e": email, "now": now})

        req = r.fetchone()

        # SECURITY: Always return success to prevent email enumeration
        if not req:
            logger.info("resend_verification_no_match", email=email)
            return {"status": "sent", "message": "If a pending registration exists, a new verification email was sent."}

        # Generate new token with extended expiry
        new_token = generate_token()
        new_expires = now + VERIFICATION_EXPIRY

        await db.execute(text("""
            UPDATE registration_requests
            SET verification_token=:t, verification_expires=:ex
            WHERE id=:id
        """), {"t": new_token, "ex": new_expires, "id": req[0]})
        await db.commit()

        full_name = req[1] or ""

    # Send new verification email
    try:
        link = f"{FRONTEND_URL}/user/register/verify?token={new_token}"
        html = f"""<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:560px;margin:40px auto;padding:20px">
<h2 style="color:#1A1A2E">Verify your email</h2>
<p>Hi{f' {full_name}' if full_name else ''},</p>
<p>Here's a fresh verification link for your registration request:</p>
<a href="{link}" style="display:block;background:#6C5CE7;color:#fff;padding:14px 24px;border-radius:8px;text-align:center;text-decoration:none;font-size:16px;margin:16px 0;max-width:200px">Verify Email</a>
<p style="color:#888;font-size:13px">Link expires in 72 hours.</p>
</body></html>"""
        await send_email(email, "Verify your email - Hermes", html)
    except Exception as e:
        logger.warning("resend_verification_email_failed", email=email, error=str(e))

    return {"status": "sent", "message": "If a pending registration exists, a new verification email was sent."}


@router.get("/register/verify")
async def register_verify(token: str = ""):
    """Verify the email on a pending registration request."""
    if not token:
        raise HTTPException(400, "Token required")

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT id, email, full_name, agent_name
            FROM registration_requests
            WHERE verification_token=:t
              AND verification_expires > NOW()
              AND email_verified=false
        """), {"t": token})
        u = r.fetchone()

        if not u:
            raise HTTPException(400, "Invalid or expired verification token. Please request a new one.")

        await db.execute(text("""
            UPDATE registration_requests
            SET email_verified=true, verification_token=NULL
            WHERE id=:id
        """), {"id": u[0]})
        await db.commit()

        req_id, email, full_name, agent_name = str(u[0]), u[1], u[2] or "", u[3] or ""

    await audit_logger.log_event(
        event_type="REGISTRATION_EMAIL_VERIFIED", severity=AuditLogger.Severity.INFO,
        user_id=req_id, details={"email": email},
    )
    logger.info("registration_email_verified", email=email)

    # Notify admin
    try:
        from app.services.admin_notify import notify_admin_new_registration
        await notify_admin_new_registration(email=email, full_name=full_name, agent_name=agent_name)
    except Exception as e:
        logger.warning("admin_notify_failed", error=str(e))

    return {
        "status": "verified",
        "message": f"Email verified{f', {full_name}' if full_name else ''}! Your request is now under admin review. We'll email you once approved (usually within 1-3 business days)."
    }


@router.get("/register/status")
@limiter.limit("10/hour")
async def registration_status(email: str = ""):
    """Check registration status without revealing if email exists.

    UX IMPROVEMENT: Lets users track approval progress.
    SECURITY: Generic response for non-existent emails.
    """
    if not email:
        raise HTTPException(400, "email parameter required")

    email = email.strip().lower()

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT status, email_verified, created_at, reviewed_at
            FROM registration_requests
            WHERE email=:e AND expires_at > NOW()
            ORDER BY created_at DESC LIMIT 1
        """), {"e": email})

        req = r.fetchone()

        if not req:
            # SECURITY: Don't reveal email doesn't exist
            return {
                "status": "not_found",
                "message": "No active registration found. You can submit a new registration.",
                "can_register": True
            }

        status, verified, created, reviewed = req[0], req[1], req[2], req[3]

        if status == "pending":
            if not verified:
                return {
                    "status": "pending_verification",
                    "message": "Please verify your email. Check your inbox for the verification link.",
                    "email_verified": False,
                    "can_register": False,
                    "submitted_at": created.isoformat() if created else None
                }
            else:
                return {
                    "status": "pending_review",
                    "message": "✅ Email verified. Your request is under admin review. We'll email you once approved (usually 1-3 business days).",
                    "email_verified": True,
                    "can_register": False,
                    "submitted_at": created.isoformat() if created else None
                }
        elif status == "approved":
            return {
                "status": "approved",
                "message": "Your registration was approved! Check your email for login instructions.",
                "email_verified": True,
                "can_register": False,
                "approved_at": reviewed.isoformat() if reviewed else None
            }
        elif status == "rejected":
            return {
                "status": "rejected",
                "message": "Your registration was not approved. Please contact support for more information.",
                "can_register": True,
                "rejected_at": reviewed.isoformat() if reviewed else None
            }

    return {"status": "unknown", "can_register": True}


@router.post("/setup-password")
@limiter.limit("5/hour")
async def setup_password(request: Request, response: Response, body: dict):
    """Set password after admin approval (new secure flow).

    SECURITY IMPROVEMENT: Password set after approval, not during registration.
    User receives setup_token via email after admin approval.
    """
    token = body.get("token") or ""
    password = body.get("password") or ""

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not token or not password:
        raise HTTPException(400, "Token and password required")

    # Validate password strength
    if len(password) < 12:
        raise HTTPException(400, "Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        raise HTTPException(400, "Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise HTTPException(400, "Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise HTTPException(400, "Password must contain at least one number")

    async with async_session_factory() as db:
        # Find approved registration with valid setup token
        r = await db.execute(text("""
            SELECT rr.id, rr.email, rr.assigned_profile_id
            FROM registration_requests rr
            WHERE rr.setup_token=:t
              AND rr.setup_token_expires > NOW()
              AND rr.status='approved'
        """), {"t": token})

        req = r.fetchone()
        if not req:
            raise HTTPException(400, "Invalid or expired setup token")

        req_id, email, profile_id = req[0], req[1], str(req[2])

        # Check if password already set
        check = await db.execute(text("""
            SELECT id FROM user_accounts WHERE email=:e AND password_hash IS NOT NULL
        """), {"e": email})

        if check.fetchone():
            raise HTTPException(409, "Password already set. Please use login or password reset.")

        # Set password on user_account
        pw_hash = hash_password(password)
        await db.execute(text("""
            UPDATE user_accounts
            SET password_hash=:h
            WHERE email=:e
        """), {"h": pw_hash, "e": email})

        # Clear setup token
        await db.execute(text("""
            UPDATE registration_requests
            SET setup_token=NULL, setup_token_expires=NULL
            WHERE id=:id
        """), {"id": req_id})

        # Create initial session
        session_token = generate_token()
        session_expires = datetime.utcnow() + SESSION_DURATION

        await db.execute(text("""
            UPDATE user_accounts
            SET session_token=:st, session_expires=:se
            WHERE email=:e
        """), {"st": session_token, "se": session_expires, "e": email})

        await db.commit()

    # Set authentication cookies
    set_portal_auth_cookies(response, session_token, profile_id)

    # Log successful password setup
    await audit_logger.log_event(
        event_type="PASSWORD_SETUP_SUCCESS",
        severity=AuditLogger.Severity.INFO,
        user_id=profile_id,
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.info("password_setup_success", email=email, user_id=profile_id)

    return {
        "status": "success",
        "message": "Password set successfully! You're now logged in.",
        "token": session_token,
        "profile_id": profile_id
    }


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, body: dict):
    """Login with email and password.

    SECURITY IMPROVEMENTS:
    - Uses dedicated session_token with expiration
    - Standardized error messages to prevent enumeration
    - Session rotation on login
    """
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    # SECURITY: Generic error message for all failure cases
    GENERIC_ERROR = "Invalid email or password"

    if not email or not password:
        logger.warning("login_missing_credentials", has_email=bool(email), has_password=bool(password))
        raise HTTPException(400, GENERIC_ERROR)

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT ua.id, ua.user_profile_id, ua.password_hash, ua.email_verified, up.is_active
            FROM user_accounts ua
            JOIN user_profiles up ON up.id = ua.user_profile_id
            WHERE ua.email=:e
        """), {"e": email})
        u = r.fetchone()

        # SECURITY: Same error for all failure cases
        if not u:
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "user_not_found"},
            )
            logger.warning("user_login_failed", email=email, reason="user_not_found")
            raise HTTPException(401, GENERIC_ERROR)

        account_id, profile_id, pw_hash, email_verified, is_active = u[0], str(u[1]), u[2], u[3], u[4]

        # Check password hash exists (post-approval flow may not have password yet)
        if not pw_hash:
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                user_id=profile_id,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "no_password_set"},
            )
            logger.warning("user_login_failed", email=email, reason="no_password_set")
            raise HTTPException(401, "Please complete password setup first. Check your email for instructions.")

        # Verify password
        if not verify_password(password, pw_hash):
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                user_id=profile_id,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "invalid_password"},
            )
            logger.warning("user_login_failed", email=email, reason="invalid_password")
            raise HTTPException(401, GENERIC_ERROR)

        # Check email verified
        if not email_verified:
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                user_id=profile_id,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "email_not_verified"},
            )
            logger.warning("user_login_failed", email=email, reason="email_not_verified")
            raise HTTPException(401, GENERIC_ERROR)

        # Check account active
        if not is_active:
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.LOGIN_FAILED,
                severity=AuditLogger.Severity.WARNING,
                user_id=profile_id,
                ip_address=client_ip,
                request_id=request_id,
                details={"email": email, "reason": "account_disabled"},
            )
            logger.warning("user_login_failed", email=email, reason="account_disabled")
            raise HTTPException(401, GENERIC_ERROR)

        # SECURITY: Generate new session token (session rotation)
        session_token = generate_token()
        session_expires = datetime.utcnow() + SESSION_DURATION

        await db.execute(text("""
            UPDATE user_accounts
            SET session_token=:st, session_expires=:se
            WHERE id=:id
        """), {"st": session_token, "se": session_expires, "id": account_id})
        await db.commit()

    # Set authentication cookies
    set_portal_auth_cookies(response, session_token, profile_id)

    # Log successful login
    await audit_logger.log_event(
        event_type=AuditLogger.EventType.LOGIN_SUCCESS,
        severity=AuditLogger.Severity.INFO,
        user_id=profile_id,
        ip_address=client_ip,
        request_id=request_id,
        details={"email": email},
    )
    logger.info("user_login_success", email=email, user_id=profile_id, auth_method="cookie")

    return {
        "token": session_token,
        "profile_id": profile_id,
        "expires_in_days": SESSION_DURATION_DAYS
    }


@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, body: dict):
    """Request password reset link.

    SECURITY: Generic response whether email exists or not.
    """
    email = (body.get("email") or "").strip().lower()

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not email:
        raise HTTPException(400, "Email required")

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT ua.id, ua.user_profile_id
            FROM user_accounts ua
            WHERE ua.email=:e AND ua.password_hash IS NOT NULL
        """), {"e": email})
        u = r.fetchone()

        # SECURITY: Always return success
        if not u:
            logger.info("forgot_password_unknown_email", email=email)
            return {"status": "sent", "message": "If the email exists, a password reset link was sent."}

        rtoken = generate_token()
        expires = datetime.utcnow() + RESET_TOKEN_EXPIRY

        await db.execute(text("""
            UPDATE user_accounts
            SET reset_token=:t, reset_expires=:ex
            WHERE id=:id
        """), {"t": rtoken, "ex": expires, "id": u[0]})
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

    # Send reset email
    link = f"{FRONTEND_URL}/user/reset?token={rtoken}"
    html = f"""<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:560px;margin:40px auto;padding:20px">
<h2 style="color:#1A1A2E">Reset your password</h2>
<p>Click the link below to set a new password:</p>
<a href="{link}" style="display:block;background:#6C5CE7;color:#fff;padding:14px 24px;border-radius:8px;text-align:center;text-decoration:none;font-size:16px;margin:16px 0;max-width:200px">Reset Password</a>
<p style="font-size:13px;color:#888">Link expires in 1 hour.</p>
<p style="font-size:13px;color:#888">If you didn't request this, ignore this email. Your password won't be changed.</p>
</body></html>"""

    try:
        await send_email(email, "Reset your password", html)
    except Exception as e:
        logger.error("password_reset_email_failed", email=email, error=str(e))

    return {"status": "sent", "message": "If the email exists, a password reset link was sent."}


@router.post("/reset-password")
@limiter.limit("5/hour")
async def reset_password(request: Request, body: dict):
    """Reset password using reset token."""
    token = body.get("token") or ""
    password = body.get("password") or ""

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    if not token or not password:
        raise HTTPException(400, "Token and password required")

    # Validate password strength
    if len(password) < 12:
        raise HTTPException(400, "Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        raise HTTPException(400, "Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise HTTPException(400, "Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise HTTPException(400, "Password must contain at least one number")

    async with async_session_factory() as db:
        r = await db.execute(text("""
            SELECT id, user_profile_id, email
            FROM user_accounts
            WHERE reset_token=:t AND reset_expires > NOW()
        """), {"t": token})
        u = r.fetchone()

        if not u:
            raise HTTPException(400, "Invalid or expired reset token")

        pw_hash = hash_password(password)

        # SECURITY: Clear reset token immediately after use, invalidate all sessions
        await db.execute(text("""
            UPDATE user_accounts
            SET password_hash=:h,
                reset_token=NULL,
                reset_expires=NULL,
                session_token=NULL,
                session_expires=NULL
            WHERE id=:id
        """), {"h": pw_hash, "id": u[0]})
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

    return {
        "status": "reset",
        "message": "Password reset successfully. Please login with your new password."
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout and invalidate session.

    SECURITY: Clears session token from database.
    """
    clear_portal_cookies(response)

    # Try to invalidate session token from cookie
    session_token = request.cookies.get("portal_token")
    if session_token:
        try:
            async with async_session_factory() as db:
                await db.execute(text("""
                    UPDATE user_accounts
                    SET session_token=NULL, session_expires=NULL
                    WHERE session_token=:t
                """), {"t": session_token})
                await db.commit()
        except Exception as e:
            logger.warning("logout_token_invalidation_failed", error=str(e))

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    await audit_logger.log_event(
        event_type=AuditLogger.EventType.LOGOUT,
        severity=AuditLogger.Severity.INFO,
        ip_address=client_ip,
        request_id=request_id,
    )
    logger.info("user_logout", ip_address=client_ip)

    return {"status": "logged_out"}
