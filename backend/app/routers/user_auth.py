"""User authentication: register, verify, login, forgot/reset password."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from app.database import async_session_factory
from app.config import settings
import bcrypt, secrets, httpx
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth/user", tags=["user_auth"])

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
        print(f"EMAIL NOT SENT (no key): {subject} to {to}")
        return
    async with httpx.AsyncClient() as c:
        await c.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"from": "Hermes <noreply@beprepared.dev>", "to": to, "subject": subject, "html": html},
        )

@router.post("/register")
async def register(body: dict):
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    profile_id = body.get("profile_id") or ""
    if not email or not password or not profile_id:
        raise HTTPException(400, "email, password, and profile_id required")
    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    async with async_session_factory() as db:
        existing = await db.execute(text("SELECT id FROM user_accounts WHERE email=:e"), {"e": email})
        if existing.fetchone():
            raise HTTPException(409, "Email already registered")
        pw_hash = hash_password(password)
        vtoken = generate_token()
        expires = datetime.utcnow() + timedelta(hours=24)
        await db.execute(
            text("INSERT INTO user_accounts (user_profile_id, email, password_hash, verification_token, verification_expires) VALUES (:p, :e, :h, :t, :ex)"),
            {"p": profile_id, "e": email, "h": pw_hash, "t": vtoken, "ex": expires},
        )
        await db.commit()
    link = f"{FRONTEND_URL}/user/verify?token={vtoken}"
    html = f"""<h2>Welcome!</h2><p>Verify your email by clicking the link below:</p><a href="{link}">Verify Email</a><p>Link expires in 24 hours.</p>"""
    await send_email(email, "Verify your email", html)
    return {"status": "registered", "message": "Verification email sent"}

@router.get("/verify")
async def verify(token: str = ""):
    if not token:
        raise HTTPException(400, "Token required")
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id FROM user_accounts WHERE verification_token=:t AND verification_expires > NOW() AND email_verified=false"),
            {"t": token},
        )
        u = r.fetchone()
        if not u:
            raise HTTPException(400, "Invalid or expired token")
        await db.execute(text("UPDATE user_accounts SET email_verified=true, verification_token=NULL WHERE id=:id"), {"id": u[0]})
        await db.commit()
    return {"status": "verified"}

@router.post("/login")
async def login(body: dict):
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        raise HTTPException(400, "Email and password required")
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, user_profile_id, password_hash, email_verified FROM user_accounts WHERE email=:e"),
            {"e": email},
        )
        u = r.fetchone()
        if not u or not verify_password(password, u[2]):
            raise HTTPException(401, "Invalid email or password")
        if not u[3]:
            raise HTTPException(403, "Email not verified. Check your inbox.")
        token = generate_token()
        await db.execute(text("UPDATE user_accounts SET verification_token=:t WHERE id=:id"), {"t": token, "id": u[0]})
        await db.commit()
    return {"token": token, "profile_id": str(u[1])}

@router.post("/forgot-password")
async def forgot_password(body: dict):
    email = (body.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(400, "Email required")
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM user_accounts WHERE email=:e"), {"e": email})
        u = r.fetchone()
        if not u:
            return {"status": "sent"}  # Don't reveal if email exists
        rtoken = generate_token()
        expires = datetime.utcnow() + timedelta(hours=1)
        await db.execute(text("UPDATE user_accounts SET reset_token=:t, reset_expires=:ex WHERE id=:id"), {"t": rtoken, "ex": expires, "id": u[0]})
        await db.commit()
    link = f"{FRONTEND_URL}/user/reset?token={rtoken}"
    html = f"""<h2>Reset your password</h2><p>Click the link to set a new password:</p><a href="{link}">Reset Password</a><p>Link expires in 1 hour.</p><p>If you didn't request this, ignore this email.</p>"""
    await send_email(email, "Reset your password", html)
    return {"status": "sent"}

@router.post("/reset-password")
async def reset_password(body: dict):
    token = body.get("token") or ""
    password = body.get("password") or ""
    if not token or not password:
        raise HTTPException(400, "Token and password required")
    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id FROM user_accounts WHERE reset_token=:t AND reset_expires > NOW()"),
            {"t": token},
        )
        u = r.fetchone()
        if not u:
            raise HTTPException(400, "Invalid or expired reset token")
        pw_hash = hash_password(password)
        await db.execute(text("UPDATE user_accounts SET password_hash=:h, reset_token=NULL, reset_expires=NULL WHERE id=:id"), {"h": pw_hash, "id": u[0]})
        await db.commit()
    return {"status": "reset"}
