"""Reminder worker - fires due reminders via Telegram.

Run inside the API container (has DB + bot token access), e.g. from cron:
    docker exec hermes-multi-tenant-api-1 python3 /app/app/services/reminder_worker.py

Sends each due (remind_at <= now, undone) reminder to the owning user's
Telegram chat, then marks it done so it fires exactly once.
"""
import asyncio
import httpx
import sys
from datetime import datetime

from sqlalchemy import text
from app.database import async_session_factory
from app.config import settings


async def fire_due_reminders() -> int:
    bot_token = getattr(settings, "telegram_bot_token", None)
    if not bot_token:
        print("REMINDER_WORKER: no bot token configured", flush=True)
        return 0

    async with async_session_factory() as db:
        r = await db.execute(text(
            """SELECT r.id,
                      r.title,
                      up.phone_number AS chat_id,
                      up.platform,
                      up.agent_name
               FROM reminders r
               JOIN user_profiles up ON up.id = r.user_id
               WHERE r.done = false
                 AND r.remind_at <= NOW()
            """
        ))
        rows = r.fetchall()

        sent = 0
        async with httpx.AsyncClient(timeout=10) as client:
            for row in rows:
                rid, title, chat_id, platform, agent_name = row
                # Only deliver to Telegram-active users (chat id in phone_number).
                if platform != "telegram" or not chat_id or not str(chat_id).lstrip("-").isdigit():
                    continue

                msg = (
                    f"⏰ <b>Reminder</b>\n{title}\n"
                    f"(from {agent_name or 'your agent'})"
                )
                try:
                    resp = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        data={"chat_id": str(chat_id), "text": msg, "parse_mode": "HTML"},
                    )
                    if resp.status_code == 200:
                        sent += 1
                        # Mark done once sent
                        await db.execute(text("UPDATE reminders SET done=true WHERE id=:id"), {"id": rid})
                    else:
                        print(f"REMINDER_WORKER: send failed {resp.status_code} for reminder {rid}", flush=True)
                except Exception as e:
                    print(f"REMINDER_WORKER: error sending reminder {rid}: {e}", flush=True)

        await db.commit()
        return sent


async def main():
    n = await fire_due_reminders()
    print(f"REMINDER_WORKER: {datetime.utcnow().isoformat()} fired {n} reminder(s)", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
