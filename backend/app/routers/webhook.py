from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import httpx, logging
from app.database import get_db
from app.config import settings

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
        r = await db.execute(text("SELECT id,is_vip,trial_ends_at,is_active,primary_model,backup_model FROM user_profiles WHERE phone_number=:p"),{"p":phone})
        u = r.fetchone()
        if not u: return {"status":"unknown"}
        if not u[3]: return {"status":"inactive"}
        if not u[1] and u[2] and u[2] < datetime.utcnow():
            await _send_wa(phone,"Trial expired. Subscribe at "+settings.public_url+"/subscribe")
            return {"status":"expired"}
        resp = await _call_ai(u[4],u[5],text_msg)
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
    logger.info(f"Telegram msg from chat_id={chat_id}: {text_msg[:50]}")
    if not chat_id or not text_msg: return {"status":"ok"}
    # Look up user by chat_id stored in phone_number field
    r = await db.execute(text("SELECT id,is_active,primary_model,backup_model FROM user_profiles WHERE phone_number=:c"),{"c":chat_id})
    u = r.fetchone()
    if not u or not u[1]: return {"status":"ignored"}
    resp = await _call_ai(u[2],u[3],text_msg)
    async with httpx.AsyncClient() as c:
        await c.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json={"chat_id":int(chat_id),"text":resp})
    await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'message',:det)"),{"uid":str(u[0]),"det":'{"platform":"telegram","tokens":'+str(len(text_msg)//4)+'}'})
    return {"status":"ok"}

# ── AI ──

async def _call_ai(primary:str,backup:str,msg:str)->str:
    try: return await _api(primary,msg)
    except:
        try: return await _api(backup,msg)
        except: return "Service unavailable."

async def _api(model:str,msg:str)->str:
    if model.startswith("claude"):
        if not settings.anthropic_api_key: return "Agent ready! (API pending)"
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key":settings.anthropic_api_key,"anthropic-version":"2023-06-01","content-type":"application/json"},
                json={"model":model,"max_tokens":1024,"messages":[{"role":"user","content":msg}]})
            return r.json()["content"][0]["text"]
    if model.startswith("gpt"):
        if not settings.openai_api_key: return "Agent ready! (API pending)"
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post("https://api.openai.com/v1/chat/completions",
                headers={"Authorization":f"Bearer {settings.openai_api_key}","content-type":"application/json"},
                json={"model":model,"max_tokens":1024,"messages":[{"role":"user","content":msg}]})
            return r.json()["choices"][0]["message"]["content"]
    if "fireworks" in model or model.startswith("accounts/"):
        if not settings.fireworks_api_key: return "Agent ready! (API pending)"
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post("https://api.fireworks.ai/inference/v1/chat/completions",
                headers={"Authorization":f"Bearer {settings.fireworks_api_key}","content-type":"application/json"},
                json={"model":model,"max_tokens":1024,"messages":[{"role":"user","content":msg}]})
            return r.json()["choices"][0]["message"]["content"]
    return "Agent ready!"

async def _send_wa(to:str,text:str):
    if not settings.whatsapp_api_token: return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages",
            headers={"Authorization":f"Bearer {settings.whatsapp_api_token}","Content-Type":"application/json"},
            json={"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text}})
