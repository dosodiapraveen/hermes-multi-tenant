from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import httpx, logging
from app.database import get_db
from app.config import settings
from app.services.agent_manager import hermes_profile_chat_with_fallback

logger = logging.getLogger(__name__)
router = APIRouter()

# ── WhatsApp ──

@router.post("/whatsapp")
async def whatsapp(request: Request, db: AsyncSession = Depends(get_db)):
    if "hub.challenge" in request.query_params:
        if request.query_params["hub.verify_token"] == settings.whatsapp_verify_token:
            return int(request.query_params["hub.challenge"])
    body = await request.json()
    try:
        msg = body.get("entry",[{}])[0].get("changes",[{}])[0].get("value",{}).get("messages",[None])[0]
        if not msg: return {"status":"ok"}
        phone = msg.get("from","")
        text_msg = msg.get("text",{}).get("body","")
        r = await db.execute(text("SELECT id,is_vip,trial_ends_at,is_active,profile_path FROM user_profiles WHERE phone_number=:p"),{"p":phone})
        u = r.fetchone()
        if not u: return {"status":"unknown"}
        if not u[3]: return {"status":"inactive"}
        if not u[1] and u[2] and u[2] < datetime.utcnow():
            await _send_wa(phone,"Trial expired. Subscribe at "+settings.public_url+"/subscribe")
            return {"status":"expired"}
        # Route through Hermes agent instead of direct AI API
        resp = await hermes_profile_chat_with_fallback(
            user_id=str(u[0]),
            message=text_msg,
            profile_dir=str(u[4]) if u[4] else None,
        )
        await _send_wa(phone,resp)
        await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'message',:det)"),{"uid":str(u[0]),"det":'{"tokens":'+str(len(text_msg)//4)+'}'})
        return {"status":"ok"}
    except Exception as e:
        logger.error(f"WA error: {e}")
        return {"status":"error"}

@router.get("/whatsapp")
async def wa_verify(request: Request):
    if request.query_params.get("hub.verify_token") == settings.whatsapp_verify_token:
        return int(request.query_params.get("hub.challenge",0))

# ── Telegram ──

@router.post("/telegram")
async def telegram(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    chat_id = str(body.get("message",{}).get("chat",{}).get("id",""))
    text_msg = body.get("message",{}).get("text","")
    if not chat_id or not text_msg: return {"status":"ok"}
    # Look up user by chat_id stored in phone_number field
    r = await db.execute(text("SELECT id,is_active,profile_path FROM user_profiles WHERE phone_number=:c"),{"c":chat_id})
    u = r.fetchone()
    if not u or not u[1]: return {"status":"ignored"}
    # Route through Hermes agent instead of direct AI API
    resp = await hermes_profile_chat_with_fallback(
        user_id=str(u[0]),
        message=text_msg,
        profile_dir=str(u[2]) if u[2] else None,
    )
    async with httpx.AsyncClient() as c:
        await c.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json={"chat_id":int(chat_id),"text":resp})
    await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'message',:det)"),{"uid":str(u[0]),"det":'{"platform":"telegram","tokens":'+str(len(text_msg)//4)+'}'})
    return {"status":"ok"}

# ── WhatsApp sender helper ──

async def _send_wa(to:str,text:str):
    if not settings.whatsapp_api_token: return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages",
            headers={"Authorization":f"Bearer {settings.whatsapp_api_token}","Content-Type":"application/json"},
            json={"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text}})
