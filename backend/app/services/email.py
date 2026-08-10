"""Email service for onboarding and notifications via Resend."""
import httpx
from app.config import settings

RESEND_API = "https://api.resend.com/emails"
FROM_ADDR = "Hermes <hermes@beprepared.dev>"


async def send_email(to: str, subject: str, html: str) -> bool:
    """Send an email via Resend API."""
    if not settings.resend_api_key:
        print("Resend API key not configured")
        return False
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(
            RESEND_API,
            headers={"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"},
            json={"from": FROM_ADDR, "to": [to], "subject": subject, "html": html},
        )
        if r.status_code != 200:
            print(f"Email send failed: {r.text}")
            return False
        return True


async def send_welcome_email(to: str, agent_name: str, plan: str, telegram_bot: str = "BotBePreparedBot") -> bool:
    """Send a welcome email when a user signs up."""
    plan_label = {"trial": "Free Trial", "basic": "Basic", "pro": "Pro", "business": "Business", "vip": "VIP"}.get(plan, plan)
    html = f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:560px;margin:40px auto;padding:20px">
<div style="background:#1A1A2E;border-radius:12px;padding:32px;text-align:center;margin-bottom:24px">
<div style="width:40px;height:40px;background:linear-gradient(135deg,#6C5CE7,#A29BFE);border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#fff;margin-bottom:12px">H</div>
<h1 style="color:#fff;font-size:22px;margin:0">Welcome, {agent_name}!</h1>
</div>
<p style="font-size:15px;line-height:1.6;color:#333">Your AI agent is ready. Here's what you can do:</p>
<table style="width:100%;margin:16px 0">
<tr><td style="padding:10px 0;font-size:14px">🤖 <strong>Chat on Telegram</strong><br><span style="color:#666">Message <a href="https://t.me/{telegram_bot}" style="color:#6C5CE7">@{telegram_bot}</a> to start</span></td></tr>
<tr><td style="padding:10px 0;font-size:14px">📁 <strong>Private Knowledge Vault</strong><br><span style="color:#666">Your agent saves notes and remembers everything</span></td></tr>
<tr><td style="padding:10px 0;font-size:14px">📊 <strong>Plan: {plan_label}</strong><br><span style="color:#666">{'Unlimited usage' if plan == 'vip' else 'Check your plan details in the admin panel'}</span></td></tr>
</table>
<div style="background:#F8F9FA;border-radius:8px;padding:16px;font-size:13px;color:#636E70;margin:16px 0">
<strong>Quick Start:</strong> Send "hello" to @{telegram_bot} on Telegram to test your agent.
</div>
<p style="font-size:13px;color:#999;margin-top:24px">Sent by Hermes · beprepared.dev</p>
</body></html>"""
    return await send_email(to, f"Welcome to Hermes, {agent_name}! 🎉", html)
