"""Webhook handlers for Telegram and WhatsApp."""
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text
from app.config import settings
from app.database import async_session_factory
from app.services.agent_manager import hermes_profile_chat_with_fallback
import os
from app.services.profile_init import init_user_profile
import httpx, json, asyncio
from datetime import datetime, timedelta
from pathlib import Path
from app.logging_config import get_logger
from app.services.audit_logger import audit_logger, AuditLogger

logger = get_logger(__name__)

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
    # Get client info for audit logging
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                (request.client.host if request.client else "unknown")
    request_id = getattr(request.state, "request_id", None)

    # Verify webhook secret if configured
    if settings.telegram_webhook_secret:
        secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret_header != settings.telegram_webhook_secret:
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.WEBHOOK_SIGNATURE_FAILED,
                severity=AuditLogger.Severity.WARNING,
                ip_address=client_ip,
                request_id=request_id,
                details={"platform": "telegram", "reason": "invalid_webhook_secret"},
            )
            logger.warning("telegram_webhook_invalid_secret", ip_address=client_ip)
            raise HTTPException(403, "Invalid webhook secret")

    body = await request.json()
    chat_id = str(body.get("message", {}).get("chat", {}).get("id", ""))
    text_msg = body.get("message", {}).get("text", "")
    if not chat_id or not text_msg:
        return {"status": "ok"}

    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id,is_active,profile_path,runtime FROM user_profiles WHERE phone_number=:c"),
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
                await db.execute(text("UPDATE user_profiles SET phone_number=:c, platform='telegram' WHERE id::text=:uid"), {"c": chat_id, "uid": uid})
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
                    text("""INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip, trial_ends_at, primary_model, backup_model, platform)
                           VALUES (:p,:a,:pl,:v,:te,:m1,:m2,'telegram') RETURNING id"""),
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

        # Handle document uploads (PDFs, docs, etc.) to knowledge base
        doc = body.get("message", {}).get("document", None)
        if doc:
            try:
                file_id = doc.get("file_id", "")
                file_name = doc.get("file_name", "document")
                async with httpx.AsyncClient() as c:
                    fr = await c.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/getFile?file_id={file_id}")
                    fp = fr.json().get("result", {}).get("file_path", "")
                    if fp:
                        dl = await c.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/{fp}")
                        uid = str(u[0])
                        kb_dir = Path("/opt/hermes/obsidian") / uid / "Knowledge"
                        kb_dir.mkdir(parents=True, exist_ok=True)
                        save_path = kb_dir / file_name
                        save_path.write_bytes(dl.content)

                        # Log document upload
                        await audit_logger.log_event(
                            event_type=AuditLogger.EventType.WEBHOOK_DOCUMENT_UPLOAD,
                            severity=AuditLogger.Severity.INFO,
                            user_id=uid,
                            ip_address=client_ip,
                            request_id=request_id,
                            details={"platform": "telegram", "file_name": file_name, "file_size": len(dl.content)},
                        )
                        logger.info("telegram_document_uploaded", user_id=uid, file_name=file_name, file_size=len(dl.content))

                        await send_tg(chat_id, f"📎 Saved **{file_name}** to your knowledge base.")
                        stop_typing.set()
                        typing_task.cancel()
                        return {"status": "document_saved"}
            except Exception as e:
                logger.error("telegram_document_upload_failed", user_id=str(u[0]), error=str(e), exc_info=True)
                await send_tg(chat_id, "⚠️ Couldn't save the document. Please try again.")
                stop_typing.set()
                typing_task.cancel()
                return {"status": "doc_error"}

        # Handle voice messages — transcribe and process as text
        voice = body.get("message", {}).get("voice", None)
        if voice:
            try:
                file_id = voice.get("file_id", "")
                async with httpx.AsyncClient() as c:
                    fr = await c.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/getFile?file_id={file_id}")
                    fp = fr.json().get("result", {}).get("file_path", "")
                    if fp:
                        dl = await c.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/{fp}")
                        # Save OGG, convert to WAV, transcribe
                        ogg_path = Path(f"/tmp/voice_{chat_id}.ogg")
                        wav_path = Path(f"/tmp/voice_{chat_id}.wav")
                        ogg_path.write_bytes(dl.content)
                        # Convert to WAV using pydub
                        from pydub import AudioSegment
                        audio = AudioSegment.from_ogg(str(ogg_path))
                        audio.export(str(wav_path), format="wav")
                        # Transcribe using SpeechRecognition
                        import speech_recognition as sr
                        recognizer = sr.Recognizer()
                        with sr.AudioFile(str(wav_path)) as source:
                            audio_data = recognizer.record(source)
                            text_msg = recognizer.recognize_google(audio_data)
                        # Cleanup temp files
                        ogg_path.unlink(missing_ok=True)
                        wav_path.unlink(missing_ok=True)
                        await send_tg(chat_id, f"🎤 *You said:* {text_msg}")
                # Fall through to regular agent processing with transcribed text_msg
            except Exception as e:
                await send_tg(chat_id, "⚠️ Couldn't transcribe your voice message. Please try again or type instead.")
                stop_typing.set()
                typing_task.cancel()
                return {"status": "voice_error"}

        # ── Agent personality (SOUL) commands ──
        _low = (text_msg or "").strip()
        if _low.startswith("/personality") or _low.startswith("/soul"):
            _rest = _low.split(None, 1)[1] if " " in _low else ""
            if _rest:
                async with async_session_factory() as db:
                    await db.execute(text("UPDATE user_profiles SET personality=:p WHERE id::text=:u"), {"p": _rest, "u": str(u[0])})
                    await db.commit()
                await send_tg(chat_id, "✅ **Personality updated!** I'll follow these instructions from now on.\n\n" + _rest[:400])
            else:
                async with async_session_factory() as db:
                    _r = await db.execute(text("SELECT personality FROM user_profiles WHERE id::text=:u"), {"u": str(u[0])})
                    _row = _r.fetchone()
                if _row and _row[0]:
                    await send_tg(chat_id, "🧠 **Your agent personality:**\n\n" + _row[0][:1000])
                else:
                    await send_tg(chat_id, "🧠 Your agent uses the **default personality**. Send `/personality` followed by your instructions to customize me — e.g. `/personality Always keep replies under 100 words and greet me by name.`")
            stop_typing.set()
            typing_task.cancel()
            return {"status": "personality"}

        try:
            resp = None
            if len(u) > 3 and u[3] == "hermes":
                resp = await run_hermes_runtime(str(u[0]), text_msg)
            if resp is None:  # default agent runtime, or hermes unavailable -> fallback
                resp = await hermes_profile_chat_with_fallback(
                    user_id=str(u[0]),
                    message=text_msg,
                    profile_dir=str(u[2]) if u[2] else None,
                )
            await send_tg(chat_id, resp)

            # Log successful message processing
            await audit_logger.log_event(
                event_type=AuditLogger.EventType.WEBHOOK_MESSAGE_RECEIVED,
                severity=AuditLogger.Severity.INFO,
                user_id=str(u[0]),
                ip_address=client_ip,
                request_id=request_id,
                details={"platform": "telegram", "message_length": len(text_msg)},
            )
            logger.info("telegram_message_processed", user_id=str(u[0]), message_length=len(text_msg))

        except Exception as e:
            logger.error("telegram_message_processing_failed", user_id=str(u[0]), error=str(e), exc_info=True)
            await send_tg(chat_id, "⚠️ Something went wrong. Please try again in a moment.")
        finally:
            stop_typing.set()
            typing_task.cancel()

        await db.execute(
            text("INSERT INTO activity_logs (user_id,action,details,request_id,ip_address) VALUES (:uid,'message',:det,:rid,:ip)"),
            {"uid": str(u[0]), "det": '{"platform":"telegram","tokens":' + str(len(text_msg) // 4) + "}", "rid": request_id, "ip": client_ip},
        )
        await db.commit()
        return {"status": "ok"}


async def run_hermes_runtime(user_id: str, message: str, timeout: int = 240) -> str | None:
    """Invoke the container's Hermes runtime headlessly for a profile.

    Returns the assistant reply, or None if Hermes is unavailable/fails so the
    caller can gracefully fall back to the platform's agent_manager. Safe by default.
    """
    import asyncio, shutil
    herm = shutil.which("hermes")
    if not herm:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            herm, "-p", user_id, "chat", "-q", message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HERMES_HOME": "/opt/hermes"},
            cwd="/opt/hermes",
        )
        out, _err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        text = (out or b"").decode("utf-8", "replace").strip()
        return text or None
    except Exception:
        return None
