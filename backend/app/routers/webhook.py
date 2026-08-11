"""Webhook handlers for Telegram and WhatsApp."""
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.config import settings
from app.database import async_session_factory
from app.services.agent_manager import hermes_profile_chat_with_fallback
from app.services.profile_init import init_user_profile
import httpx, json, asyncio
from datetime import datetime, timedelta

router = APIRouter()

WELCOME = (
    "🎉 **Welcome! Your AI agent is ready.**\n\n"
    "Here's what I can do:\n"
    "📝 *\"Save a note about...\"* — I'll store it in your vault\n"
    "📖 *\"What notes do I have?\"* — I'll read your vault\n"
    "🌐 *\"Search for...\"* — I'll find and summarize\n"
    "💾 I remember our conversations\n\n"
    "👉 **Try saying:** *\"Save a note about my meeting today\"* or *\"Search for the latest AI news\"*"
)

async def typing_indicator(chat_id: str, stop_event: asyncio.Event):
    """Keep typing indicator alive every 4 seconds until stop_event is set."""
    while not stop_event.is_set():
        try:
            async with httpx.AsyncClient() as c:
                await c.post(
                    f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendChatAction",
                    json={"chat_id": int(chat_id), "action": "typing"},
                    timeout=5,
                )
        except: pass
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=4)
        except asyncio.TimeoutError:
            continue

async def send_tg(chat_id: str, text: str):
    async with httpx.AsyncClient() as c:
        await c.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": int(chat_id), "text": text, "parse_mode": "Markdown"},
        )

@router.post("/telegram")
async def telegram(request: Request):
    body = await request.json()
    chat_id = str(body.get("message", {}).get("chat", {}).get("id", ""))
    text_msg = body.get("message", {}).get("text", "")
    if not chat_id or not text_msg:
        return {"status": "ok"}

    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id,is_active,profile_path FROM user_profiles WHERE phone_number=:c"),
            {"c": chat_id},
        )
        u = r.fetchone()

        # ── Handle /start commands for ALL users (existing or not) ──
        if text_msg.startswith("/start "):
            code = text_msg.split(" ", 1)[1].strip()

            # Handle telegram-link codes (link existing user to Telegram)
            if code.startswith("link_"):
                r = await db.execute(
                    text("SELECT claimed_by, agent_name FROM invite_links WHERE code=:c AND claimed_by IS NOT NULL"),
                    {"c": code},
                )
                link = r.fetchone()
                if not link:
                    r2 = await db.execute(text("SELECT claimed_by FROM invite_links WHERE code=:c"), {"c": code})
                    if r2.fetchone():
                        await send_tg(chat_id, "✅ You're already connected! Send me any message.")
                    else:
                        await send_tg(chat_id, "❌ This link is invalid or expired.")
                    return {"status": "ok"}
                uid = str(link[0])
                name = link[1] or "Agent"
                await db.execute(text("UPDATE user_profiles SET phone_number=:c WHERE id::text=:uid"), {"c": chat_id, "uid": uid})
                await db.execute(text("DELETE FROM invite_links WHERE code=:c"), {"c": code})
                await db.commit()
                try:
                    from pathlib import Path
                    if not (Path("/opt/hermes/profiles") / uid / "config.yaml").exists():
                        profile = init_user_profile(user_id=uid, agent_name=name, plan="pro")
                        await db.execute(text("UPDATE user_profiles SET profile_path=:pp WHERE id::text=:uid"), {"pp": profile["profile_dir"], "uid": uid})
                except:
                    pass
                await send_tg(chat_id,
                    f"✅ *Connected!* Your Telegram is now linked to **{name}**.\n\n"
                    f"Try saying:\n"
                    f"📝 *\"Save a note about...\"*\n"
                    f"🌐 *\"Search for...\"*\n"
                    f"📖 *\"What's in my vault?\"*")
                return {"status": "linked"}

            # Handle invite codes (new users only)
            if not u:
                r = await db.execute(
                    text("SELECT id,label,agent_name,plan,trial_days,is_vip FROM invite_links WHERE code=:c AND claimed_by IS NULL"),
                    {"c": code},
                )
                inv = r.fetchone()
                if not inv:
                    await send_tg(chat_id, "❌ This invite link is invalid or has already been used.")
                    return {"status": "invalid"}
                agent_name = inv[2] or "My Assistant"
                plan = inv[3] or "pro"
                is_vip = inv[5]
                trial_ends = datetime.utcnow() + timedelta(days=inv[4]) if inv[4] else None
                r2 = await db.execute(
                    text("""INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip, trial_ends_at, primary_model, backup_model)
                           VALUES (:p,:a,:pl,:v,:te,:m1,:m2) RETURNING id"""),
                    {"p": chat_id, "a": agent_name, "pl": plan, "v": is_vip, "te": trial_ends,
                     "m1": settings.default_primary_model, "m2": settings.default_backup_model},
                )
                uid = str(r2.fetchone()[0])
                try:
                    profile = init_user_profile(user_id=uid, agent_name=agent_name, plan=plan, is_vip=is_vip)
                    await db.execute(
                        text("UPDATE user_profiles SET profile_path=:pp WHERE id::text=:uid"),
                        {"pp": profile["profile_dir"], "uid": uid},
                    )
                except Exception as e:
                    pass
                await db.execute(
                    text("UPDATE invite_links SET claimed_by=:u, claimed_at=NOW() WHERE code=:c"),
                    {"u": uid, "c": code},
                )
                await db.commit()
                await send_tg(chat_id, WELCOME)
                return {"status": "activated"}
            else:
                await send_tg(chat_id, "👋 I don't know you yet! You need an invite link to use this bot.")
                return {"status": "ignored"}

        if not u or not u[1]:
            await send_tg(chat_id, "⏳ Your account is inactive. Contact your admin.")
            return {"status": "inactive"}

        # ── Process message with typing indicator ──
        stop_typing = asyncio.Event()
        typing_task = asyncio.create_task(typing_indicator(chat_id, stop_typing))

        try:
            resp = await hermes_profile_chat_with_fallback(
                user_id=str(u[0]),
                message=text_msg,
                profile_dir=str(u[2]) if u[2] else None,
            )
            await send_tg(chat_id, resp)
        except Exception as e:
            await send_tg(chat_id, "⚠️ Something went wrong. Please try again in a moment.")
        finally:
            stop_typing.set()
            typing_task.cancel()

        await db.execute(
            text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'message',:det)"),
            {"uid": str(u[0]), "det": '{"platform":"telegram","tokens":' + str(len(text_msg) // 4) + "}"},
        )
        await db.commit()
        return {"status": "ok"}
