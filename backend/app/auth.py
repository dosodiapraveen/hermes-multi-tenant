from fastapi import Request, HTTPException
from jose import jwt, JWTError
from app.config import settings

def get_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing auth")
    return auth[7:]

def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
    except JWTError:
        raise HTTPException(401, "Invalid token")

async def require_admin(request: Request) -> dict:
    p = verify_jwt(get_token(request))
    if p.get("role") != "admin":
        raise HTTPException(403, "Admin only")
    return p
