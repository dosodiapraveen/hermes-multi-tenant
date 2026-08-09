from fastapi import Request, HTTPException
from app.config import settings
import httpx

SUPABASE_AUTH_URL = f"{settings.supabase_url}/auth/v1/user" if settings.supabase_url else None
SUPABASE_ANON_KEY = settings.supabase_anon_key


def get_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing auth")
    return auth[7:]


def validate_dev_jwt(token: str) -> dict:
    """Validate locally-signed JWT (dev mode)."""
    from jose import jwt, JWTError
    try:
        return jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
    except JWTError:
        raise HTTPException(401, "Invalid token")


async def validate_supabase_jwt(token: str) -> dict:
    """Validate JWT against Supabase Auth API."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            SUPABASE_AUTH_URL,
            headers={"Authorization": f"Bearer {token}", "apikey": SUPABASE_ANON_KEY},
        )
        if r.status_code == 200:
            return r.json()
    raise HTTPException(401, "Invalid or expired token")


async def verify_jwt(token: str) -> dict:
    """Validate JWT — try Supabase first, fall back to dev JWT."""
    if SUPABASE_AUTH_URL and SUPABASE_ANON_KEY:
        try:
            return await validate_supabase_jwt(token)
        except HTTPException:
            pass  # Fall through to dev JWT
    return validate_dev_jwt(token)


async def require_admin(request: Request) -> dict:
    user = await verify_jwt(get_token(request))
    email = user.get("email", "")
    role = user.get("role", "")
    if role == "admin" or email == "admin@hermes.io":
        return user
    raise HTTPException(403, "Admin access required")
