from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from app.database import get_db
from app.models.schemas import InviteLinkRedeem
from app.services.profile_init import init_user_profile

router = APIRouter()

@router.post("/redeem")
async def redeem(body: InviteLinkRedeem, db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,label,agent_name,plan,trial_days,is_vip FROM invite_links WHERE code=:c AND claimed_by IS NULL"), {"c": body.code})
    link = r.fetchone()
    if not link:
        raise HTTPException(404, "Invalid or claimed link")

    trial_end = None
    if not link[5] and link[4]:
        trial_end = datetime.utcnow() + timedelta(days=link[4])

    plan = link[3] if not link[5] else "vip"
    agent_name = link[2]

    # Create user in database
    r2 = await db.execute(text("""
        INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip, trial_ends_at,
            primary_model, backup_model)
        VALUES (:p, :a, :pl, :v, :te,
            'accounts/fireworks/models/deepseek-v4-flash-0731',
            'accounts/fireworks/models/deepseek-v4-flash-0731')
        RETURNING id
    """), {
        "p": body.phone_number, "a": agent_name, "pl": plan,
        "v": link[5], "te": trial_end
    })
    uid = str(r2.fetchone()[0])

    # Mark invite as claimed
    await db.execute(text("UPDATE invite_links SET claimed_by=:uid, claimed_at=NOW() WHERE id=:lid"),
        {"uid": uid, "lid": link[0]})

    # Initialize Hermes profile + Obsidian vault (isolated per user)
    try:
        profile = init_user_profile(
            user_id=uid,
            agent_name=agent_name,
            plan=plan,
            is_vip=link[5],
        )
        # Save profile & vault paths to DB
        await db.execute(text("UPDATE user_profiles SET profile_path=:pp WHERE id=:uid"),
            {"pp": profile["profile_dir"], "uid": uid})
        profile_status = "created"
        vault_path = profile["vault_dir"]
    except Exception as e:
        profile_status = f"failed: {e}"
        vault_path = None

    # Log - SECURITY FIX: Use json.dumps to prevent JSON injection
    import json
    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES (:uid, 'onboarding', :det)"),
        {"uid": uid, "det": json.dumps({"plan": plan, "profile": profile_status})})

    return {
        "status": "ok",
        "user_id": uid,
        "agent_name": agent_name,
        "trial_ends_at": trial_end.isoformat() if trial_end else None,
        "is_vip": link[5],
        "profile_path": profile.get("profile_dir") if profile_status == "created" else None,
        "vault_path": vault_path,
        "profile_status": profile_status,
    }
