from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import secrets
import shutil, os
from app.database import get_db
from app.auth import require_admin
from app.models.schemas import InviteLinkCreate
from app.config import settings
from app.services.profile_init import init_user_profile

router = APIRouter(dependencies=[Depends(require_admin)])

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT (SELECT COUNT(*) FROM user_profiles WHERE is_active=true) as au, (SELECT COUNT(*) FROM user_profiles) as tu, (SELECT COALESCE(SUM((details->>'tokens')::int),0) FROM activity_logs WHERE action='message' AND created_at>NOW()-INTERVAL'1 day') as tt"))
    row = r.fetchone()
    return {"active_users":row[0] or 0,"total_users":row[1] or 0,"total_agents":row[1] or 0,"tokens_today":row[2] or 0}

@router.post("/users")
async def create_user(body: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Create a user directly with Hermes profile + Obsidian vault. All data stays isolated."""
    phone = body.get("phone_number", "")
    agent_name = body.get("agent_name", "My Assistant")
    plan = body.get("plan", "pro")
    is_vip = body.get("is_vip", False)
    if not phone:
        raise HTTPException(400, "phone_number is required")
    # Create DB record
    r = await db.execute(text("""
        INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip,
            primary_model, backup_model)
        VALUES (:p, :a, :pl, :v,
            'accounts/fireworks/models/deepseek-v4-flash-0731',
            'accounts/fireworks/models/deepseek-v4-flash-0731')
        RETURNING id
    """), {"p": phone, "a": agent_name, "pl": plan if not is_vip else "vip", "v": is_vip})
    uid = str(r.fetchone()[0])

    # Initialize Hermes profile + Obsidian vault (completely isolated)
    try:
        profile = init_user_profile(
            user_id=uid,
            agent_name=agent_name,
            plan=plan if not is_vip else "vip",
            is_vip=is_vip,
        )
        await db.execute(text("UPDATE user_profiles SET profile_path=:pp WHERE id=:uid"),
            {"pp": profile["profile_dir"], "uid": uid})
        profile_status = "created"
        vault_path = profile["vault_dir"]
        profile_path = profile["profile_dir"]
    except Exception as e:
        profile_status = f"failed: {e}"
        vault_path = None
        profile_path = None

    await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'admin_create',:det)"),
        {"uid": uid, "det": f'{{"plan":"{plan}","profile":"{profile_status}"}}'})

    return {
        "status": "ok",
        "user_id": uid,
        "agent_name": agent_name,
        "plan": plan if not is_vip else "vip",
        "is_vip": is_vip,
        "profile_path": profile_path,
        "vault_path": vault_path,
        "profile_status": profile_status,
    }

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a user, their Hermes profile, Obsidian vault, and logs."""
    r = await db.execute(text("SELECT id, profile_path FROM user_profiles WHERE id=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    # Delete profile and vault from disk
    profile_path = user[1]
    if profile_path:
        vault_path = profile_path.replace("/profiles/", "/obsidian/")
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)
        if os.path.exists(vault_path):
            shutil.rmtree(vault_path)

    # Delete from DB (cascade to activity_logs, invite_links)
    await db.execute(text("DELETE FROM activity_logs WHERE user_id=:uid"), {"uid": user_id})
    await db.execute(text("UPDATE invite_links SET claimed_by=NULL, claimed_at=NULL WHERE claimed_by=:uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM user_profiles WHERE id=:uid"), {"uid": user_id})

    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES ('system', 'user_deleted', :det)"),
        {"det": f'{{"deleted_user":"{user_id}"}}'})

    return {"status": "deleted", "user_id": user_id}

@router.post("/invite-links")
async def create_invite(body: InviteLinkCreate, db: AsyncSession = Depends(get_db)):
    code = secrets.token_urlsafe(8)[:12]
    r = await db.execute(text("INSERT INTO invite_links (code,label,agent_name,plan,trial_days,is_vip) VALUES (:c,:l,:a,:p,:td,:v) RETURNING id,code,label,agent_name,plan,trial_days,is_vip,claimed_by,created_at"),
        {"c":code,"l":body.label,"a":body.agent_name,"p":body.plan,"td":body.trial_days if not body.is_vip else None,"v":body.is_vip})
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
    r = await db.execute(text("SELECT id,phone_number,agent_name,plan,is_vip,trial_ends_at,primary_model,backup_model,is_active,profile_path,created_at FROM user_profiles ORDER BY created_at DESC LIMIT 100"))
    return [{"id":str(row[0]),"phone_number":row[1],"agent_name":row[2],"plan":row[3],"is_vip":row[4],
        "trial_ends_at":row[5].isoformat() if row[5] else None,
        "primary_model":row[6],"backup_model":row[7],"is_active":row[8],
        "profile_path":row[9],"created_at":row[10].isoformat()} for row in r.fetchall()]
