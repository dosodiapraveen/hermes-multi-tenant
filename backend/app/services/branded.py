"""Branded transactional email template for be prepared."""
from __future__ import annotations


def render_branded_email(
    title: str,
    body_html: str,
    button_text: str | None = None,
    button_link: str | None = None,
) -> str:
    """Render a clean, branded email wrapper with a single CTA button."""
    btn = ""
    if button_text and button_link:
        btn = (
            f'<div style="text-align:center;margin:30px 0 6px">'
            f'<a href="{button_link}" '
            f'style="background:#5A4FCF;color:#ffffff;text-decoration:none;'
            f'padding:14px 36px;border-radius:999px;font-weight:600;'
            f'font-size:15px;display:inline-block">{button_text}</a></div>'
        )

    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f5f7;padding:32px 16px">
<tr><td align="center">
<table role="presentation" width="560" cellspacing="0" cellpadding="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(20,20,40,0.08)">
<tr><td style="background:linear-gradient(135deg,#5A4FCF,#7C6FF0);padding:26px 32px">
<div style="color:#ffffff;font-size:21px;font-weight:800">✨ be&nbsp;prepared</div>
<div style="color:rgba(255,255,255,0.85);font-size:13px;margin-top:3px">Your personal AI assistant</div>
</td></tr>
<tr><td style="padding:34px 32px 28px">
<h1 style="margin:0 0 14px;font-size:20px;color:#1A1A2E;font-weight:700">{title}</h1>
{body_html}
{btn}
</td></tr>
<tr><td style="padding:16px 32px;background:#FAFAFC;border-top:1px solid #ECEDF1">
<div style="color:#8A8FA6;font-size:11px;line-height:1.6">
<div style="font-weight:600;color:#6A6F85;font-size:12px">be prepared</div>
<div>If you didn't request this, you can safely ignore this email.</div>
<div>&copy; 2026 be prepared &middot; <a href="https://beprepared.dev" style="color:#5A4FCF;text-decoration:none">beprepared.dev</a></div>
</div>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""
