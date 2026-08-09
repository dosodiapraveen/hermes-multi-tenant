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


async def verify_jwt(token: str) -> dict:
    """Validate JWT against Supabase Auth API (supports new ES256 signing keys)."""
    if not SUPABASE_AUTH_URL or not SUPABASE_ANON_KEY:
        # Fallback to dev mode - accept our own JWTs
        from jose import jwt, JWTError
        try:
            return jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
        except JWTError:
            raise HTTPException(401, "Invalid token")

    # Validate against Supabase Auth API
    async with httpx.AsyncClient() as client:
        r = await client.get(
            SUPABASE_AUTH_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_ANON_KEY,
            },
        )
        if r.status_code != 200:
            raise HTTPException(401, "Invalid or expired token")
        return r.json()


async def require_admin(request: Request) -> dict:
    user = await verify_jwt(get_token(request))
    email = user.get("email", "")
    role = user.get("role", "")
    # Check if user is admin (by email or role)
    if role == "admin" or email == "admin@hermes.io":
        return user
    raise HTTPException(403, "Admin access required")
