from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import secrets
from app.database import get_db
from app.auth import require_admin
from app.models.schemas import InviteLinkCreate
from app.config import settings

router = APIRouter(dependencies=[Depends(require_admin)])

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT (SELECT COUNT(*) FROM user_profiles WHERE is_active=true) as au, (SELECT COUNT(*) FROM user_profiles) as tu, (SELECT COALESCE(SUM((details->>'tokens')::int),0) FROM activity_logs WHERE action='message' AND created_at>NOW()-INTERVAL'1 day') as tt"))
    row = r.fetchone()
    return {"active_users":row[0] or 0,"total_users":row[1] or 0,"total_agents":row[1] or 0,"tokens_today":row[2] or 0}

@router.post("/invite-links")
async def create_invite(body: InviteLinkCreate, db: AsyncSession = Depends(get_db)):
    code = secrets.token_urlsafe(8)[:12]
    r = await db.execute(text("INSERT INTO invite_links (code,label,agent_name,plan,trial_days,is_vip) VALUES (:c,:l,:a,:p,:td,:v) RETURNING id,code,label,agent_name,plan,trial_days,is_vip,claimed_by,created_at"),{"c":code,"l":body.label,"a":body.agent_name,"p":body.plan,"td":body.trial_days if not body.is_vip else None,"v":body.is_vip})
    row = r.fetchone()
    return {"id":str(row[0]),"code":row[1],"label":row[2],"agent_name":row[3],"plan":row[4],"trial_days":row[5],"is_vip":row[6],"claimed":row[7] is not None,"link_url":f"{settings.public_url}/join/{row[1]}","created_at":row[8].isoformat()}

@router.get("/invite-links")
async def list_invites(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,code,label,agent_name,plan,trial_days,is_vip,claimed_by,claimed_at,created_at FROM invite_links ORDER BY created_at DESC LIMIT 50"))
    return [{"id":str(row[0]),"code":row[1],"label":row[2],"agent_name":row[3],"plan":row[4],"trial_days":row[5],"is_vip":row[6],"claimed":row[7] is not None,"link_url":f"{settings.public_url}/join/{row[1]}","created_at":row[9].isoformat()} for row in r.fetchall()]

@router.get("/models")
async def get_models():
    return {"primary_model":settings.default_primary_model,"backup_model":settings.default_backup_model}

@router.post("/models")
async def update_models(body: dict, db: AsyncSession = Depends(get_db)):
    if body.get("primary_model"):
        await db.execute(text("UPDATE user_profiles SET primary_model=:m,updated_at=NOW() WHERE model_overridden_at IS NULL"),{"m":body["primary_model"]})
    if body.get("backup_model"):
        await db.execute(text("UPDATE user_profiles SET backup_model=:m,updated_at=NOW() WHERE model_overridden_at IS NULL"),{"m":body["backup_model"]})
    return {"status":"updated"}

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,phone_number,agent_name,plan,is_vip,trial_ends_at,primary_model,backup_model,is_active,created_at FROM user_profiles ORDER BY created_at DESC LIMIT 100"))
    return [{"id":str(row[0]),"phone_number":row[1],"agent_name":row[2],"plan":row[3],"is_vip":row[4],"trial_ends_at":row[5].isoformat() if row[5] else None,"primary_model":row[6],"backup_model":row[7],"is_active":row[8],"created_at":row[9].isoformat()} for row in r.fetchall()]
