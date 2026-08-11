#!/usr/bin/env python3
"""Daily morning tips for all active users on the Hermes platform."""
import os, sys, json, random, httpx
from datetime import datetime

sys.path.insert(0, "/opt/hermes-multi-tenant/backend")
os.environ.setdefault("DATABASE_URL", os.environ.get("DATABASE_URL", ""))
os.environ.setdefault("TELEGRAM_BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""))

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DB_URL = os.environ.get("DATABASE_URL", "")

TIPS = [
    ("📝 Save ideas", '"Save this idea to my vault" — I\'ll store it in your personal knowledge base.'),
    ("🌐 Search the web", '"Search for latest AI news" — I\'ll find current information.'),
    ("📖 Review notes", '"What notes do I have?" — I\'ll show everything in your vault.'),
    ("💾 Remember things", '"Remember that my project deadline is Friday" — I won\'t forget.'),
    ("📚 Journal", '"Help me journal about today" — I\'ll prompt you through it.'),
    ("🔍 Research", '"Research quantum computing basics" — I\'ll search and summarize.'),
    ("📋 Create lists", '"Make a to-do list for this week" — I\'ll track it for you.'),
    ("🧠 Brain dump", '"I have an idea about..." — Tell me and I\'ll save it organized.'),
    ("📊 Summarize", '"Summarize my notes from this week" — I\'ll pull it all together.'),
    ("🎯 Set goals", '"Help me set 3 goals for today" — I\'ll keep you accountable.'),
]

async def send_tg(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        )

async def main():
    if not BOT_TOKEN:
        print("No TELEGRAM_BOT_TOKEN set")
        return

    # Connect to DB and get active users
    import asyncpg
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("SELECT phone_number, agent_name FROM user_profiles WHERE is_active=true AND phone_number ~ '^\\d+$'")
    await conn.close()

    if not rows:
        print("No active users found")
        return

    # Pick 2 random tips for today
    todays_tips = random.sample(TIPS, min(2, len(TIPS)))
    tips_text = "\n".join([f"• *{t[0]}*: {t[1]}" for t in todays_tips])

    for row in rows:
        chat_id = int(row["phone_number"])
        name = row["agent_name"] or "there"
        msg = f"☀️ *Good morning, {name}!*\n\nHere's what you can try with your agent today:\n\n{tips_text}\n\nJust send me a message anytime!"
        try:
            await send_tg(chat_id, msg)
            print(f"Sent to {chat_id}")
        except Exception as e:
            print(f"Failed for {chat_id}: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
