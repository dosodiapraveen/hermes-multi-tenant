"""Admin notification service --- alerts the admin to events needing review."""
import os
import httpx
from app.config import settings

# Admin Telegram chat (numeric chat id). Configurable via env ADMIN_TELEGRAM_CHAT_ID.
ADMIN_CHAT_ID = os.environ.get("ADMIN_TELEGRAM_CHAT_ID", "1832518861")
PUBLIC_URL = getattr(settings, "public_url", None) or "https://beprepared.dev"


async def _send_tg(text: str):
    token = getattr(settings, "telegram_bot_token", None)
    if not token:
        print("ADMIN_NOTIFY: no bot token configured")
        return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post("https://api.telegram.org/bot" + token + "/sendMessage",
                     data={"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"})


async def notify_admin_new_registration(email: str, full_name: str = "", agent_name: str = ""):
    """Alert admin that a verified registration request awaits approval."""
    NL = chr(10)
    name_fragment = (" \u2022 " + full_name) if full_name else ""
    agent_fragment = (" \u2022 Agent: " + agent_name) if agent_name else ""
    review_url = f"{PUBLIC_URL}/registration-requests"
    text = NL.join([
        "\U0001f514 <b>New registration request (verified)</b>",
        f"\U0001f4e7 <b>{email}</b>{name_fragment}{agent_fragment}",
        "Status: awaiting your approval",
        f"Review: {review_url}",
    ])
    await _send_tg(text)


async def notify_admin_rejected(resp_email: str):
    """Alert admin when a rejection is processed (informational)."""
    text = f"\u26d4 Rejected registration for <b>{resp_email}</b>. The user was notified."
    await _send_tg(text)
