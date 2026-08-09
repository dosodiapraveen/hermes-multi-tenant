from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings
from app.database import init_db, close_db
from app.routers import admin, invite, webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(title="Hermes API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
async def health():
    return {"status":"ok","version":"0.1.0"}

@app.post("/api/auth/login")
async def dev_login(body: dict):
    if body.get("email") == "admin@hermes.io" and body.get("password") == "admin":
        exp = datetime.utcnow() + timedelta(hours=8)
        token = jwt.encode({"sub":"dev-admin","role":"admin","email":body["email"],"exp":exp,"aud":"authenticated"}, settings.supabase_jwt_secret, algorithm="HS256")
        return {"access_token":token,"token_type":"bearer"}
    raise HTTPException(401,"Invalid credentials")

app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(invite.router, prefix="/api/invite", tags=["invite"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
