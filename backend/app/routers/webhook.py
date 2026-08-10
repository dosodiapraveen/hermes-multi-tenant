"""Webhook handlers for Telegram and WhatsApp."""
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.config import settings
from app.database import async_session_factory
from app.services.agent_manager import hermes_profile_chat_with_fallback
from app.services.profile_init import init_user_profile
import httpx
import json
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/telegram")
async def telegram(request: Request):
    body = await request.json()
    chat_id = str(body.get("message",{}).get("chat",{}).get("id",""))
    text_msg = body.get("message",{}).get("text","")
    if not chat_id or not text_msg: return {"status":"ok"}

    async with async_session_factory() as db:
        # Check if user exists
        r = await db.execute(text("SELECT id,is_active,profile_path FROM user_profiles WHERE phone_number=:c"),{"c":chat_id})
        u = r.fetchone()

        if not u:
            # Handle /start INVITE_CODE
            if text_msg.startswith("/start "):
                code = text_msg.split(" ", 1)[1].strip()
                r = await db.execute(text("SELECT id,label,agent_name,plan,trial_days,is_vip FROM invite_links WHERE code=:c AND claimed_by IS NULL"), {"c": code})
                inv = r.fetchone()
                if not inv:
                    async with httpx.AsyncClient() as c:
                        await c.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json={"chat_id":int(chat_id),"text":"Invalid or expired invite link."})
                    return {"status":"invalid"}
                # Redeem invite - create user
                agent_name = inv[2] or "My Assistant"
                plan = inv[3] or "pro"
                is_vip = inv[5]
                trial_ends = datetime.utcnow() + timedelta(days=inv[4]) if inv[4] else None
                r2 = await db.execute(text("""INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip, trial_ends_at, primary_model, backup_model) VALUES (:p,:a,:pl,:v,:te,:m1,:m2) RETURNING id"""),{
                    "p": chat_id, "a": agent_name, "pl": plan, "v": is_vip, "te": trial_ends,
                    "m1": settings.default_primary_model, "m2": settings.default_backup_model
                })
                uid = str(r2.fetchone()[0])
                # Create profile + vault
                try:
                    profile = init_user_profile(user_id=uid, agent_name=agent_name, plan=plan, is_vip=is_vip)
                    await db.execute(text("UPDATE user_profiles SET profile_path=:pp WHERE id::text=:uid"), {"pp": profile["profile_dir"], "uid": uid})
                except Exception as e:
                    pass
                # Mark invite as claimed
                await db.execute(text("UPDATE invite_links SET claimed_by=:u, claimed_at=NOW() WHERE code=:c"), {"u": uid, "c": code})
                await db.commit()
                async with httpx.AsyncClient() as c:
                    await c.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json={"chat_id":int(chat_id),"text":f"Welcome, {agent_name}! Your agent is ready. Send me any message to start!"})
                return {"status":"activated"}
            else:
                # Unknown user - ignore
                return {"status":"ignored"}

        if not u[1]: return {"status":"ignored"}

        # Route through Hermes agent
        resp = await hermes_profile_chat_with_fallback(
            user_id=str(u[0]),
            message=text_msg,
            profile_dir=str(u[2]) if u[2] else None,
        )
        async with httpx.AsyncClient() as c:
            await c.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json={"chat_id":int(chat_id),"text":resp})
        await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'message',:det)"),{"uid":str(u[0]),"det":'{"platform":"telegram","tokens":'+str(len(text_msg)//4)+'}'})
        await db.commit()
        return {"status":"ok"}
