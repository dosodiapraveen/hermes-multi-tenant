from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import secrets
import shutil, os
from datetime import datetime, timedelta
from app.database import get_db
from app.auth import require_admin
from app.models.schemas import (
    InviteLinkCreate,
    UserModelOverride,
    UserSkillCreate,
    GlobalSkillTemplate,
)
from app.config import settings
from app.services.profile_init import init_user_profile
from app.services.agent_manager import (
    profile_exists,
    write_user_skill,
    update_user_model_config,
    write_global_skill_template,
    hermes_profile_chat,
    PROFILES_ROOT,
)

import logging
logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_admin)])

# ═══════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT (SELECT COUNT(*) FROM user_profiles WHERE is_active=true) as au, (SELECT COUNT(*) FROM user_profiles) as tu, (SELECT COALESCE(SUM((details->>'tokens')::int),0) FROM activity_logs WHERE action='message' AND created_at>NOW()-INTERVAL'1 day') as tt"))
    row = r.fetchone()
    return {"active_users":row[0] or 0,"total_users":row[1] or 0,"total_agents":row[1] or 0,"tokens_today":row[2] or 0}

# ═══════════════════════════════════════════
# User CRUD
# ═══════════════════════════════════════════

@router.post("/users")
async def create_user(body: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Create a user directly with Hermes profile + Obsidian vault. All data stays isolated."""
    phone = body.get("phone_number", "")
    email = body.get("email", "")
    agent_name = body.get("agent_name", "My Assistant")
    plan = body.get("plan", "pro")
    is_vip = body.get("is_vip", False)
    if not phone and not email:
        raise HTTPException(400, "phone_number or email is required")
    # Create DB record
    r = await db.execute(text("""
        INSERT INTO user_profiles (phone_number, agent_name, plan, is_vip,
            primary_model, backup_model)
        VALUES (:p, :a, :pl, :v,
            'accounts/fireworks/models/deepseek-v4-flash-0731',
            'accounts/fireworks/models/deepseek-v4-flash-0731')
        RETURNING id
    """), {"p": phone, "a": agent_name, "pl": plan if not is_vip else "vip", "v": is_vip})
    uid = str(r.fetchone()[0])

    # Initialize Hermes profile + Obsidian vault (completely isolated)
    try:
        profile = init_user_profile(
            user_id=uid,
            agent_name=agent_name,
            plan=plan if not is_vip else "vip",
            is_vip=is_vip,
        )
        await db.execute(text("UPDATE user_profiles SET profile_path=:pp WHERE id::text=:uid OR phone_number=:uid"),
            {"pp": profile["profile_dir"], "uid": uid})
        profile_status = "created"
        vault_path = profile["vault_dir"]
        profile_path = profile["profile_dir"]
    except Exception as e:
        profile_status = f"failed: {e}"
        vault_path = None
        profile_path = None

    # SECURITY FIX: Use json.dumps to prevent JSON injection
    await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'admin_create',:det)"),
        {"uid": uid, "det": json.dumps({"plan": plan, "profile": profile_status, "email": email})})

    # Send welcome email if email was provided
    if email:
        try:
            from app.services.email import send_welcome_email
            await send_welcome_email(email, agent_name, plan if not is_vip else "vip")
            email_status = "sent"
        except Exception as e:
            email_status = f"failed: {e}"
    else:
        email_status = "no_email"

    return {
        "status": "ok",
        "user_id": uid,
        "agent_name": agent_name,
        "plan": plan if not is_vip else "vip",
        "is_vip": is_vip,
        "profile_path": profile_path,
        "vault_path": vault_path,
        "profile_status": profile_status,
        "email_status": email_status,
    }

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a user, their Hermes profile, Obsidian vault, and logs."""
    r = await db.execute(text("SELECT id, profile_path FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    # Delete profile and vault from disk
    profile_path = user[1]
    if profile_path:
        vault_path = profile_path.replace("/profiles/", "/obsidian/")
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)
        if os.path.exists(vault_path):
            shutil.rmtree(vault_path)

    # Delete from DB (cascade to activity_logs, invite_links)
    await db.execute(text("DELETE FROM activity_logs WHERE user_id=:uid"), {"uid": user_id})
    await db.execute(text("UPDATE invite_links SET claimed_by=NULL, claimed_at=NULL WHERE claimed_by=:uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})

    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES ('system', 'user_deleted', :det)"),
        {"det": f'{{"deleted_user":"{user_id}"}}'})

    return {"status": "deleted", "user_id": user_id}

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,phone_number,agent_name,plan,is_vip,trial_ends_at,primary_model,backup_model,is_active,profile_path,created_at FROM user_profiles ORDER BY created_at DESC LIMIT 100"))
    return [{"id":str(row[0]),"phone_number":row[1],"agent_name":row[2],"plan":row[3],"is_vip":row[4],
        "trial_ends_at":row[5].isoformat() if row[5] else None,
        "primary_model":row[6],"backup_model":row[7],"is_active":row[8],
        "profile_path":row[9],"created_at":row[10].isoformat()} for row in r.fetchall()]

# ═══════════════════════════════════════════
# Usage Analytics
# ═══════════════════════════════════════════

@router.get("/usage")
async def get_usage(db: AsyncSession = Depends(get_db)):
    """Get usage stats: messages per day, per user, total tokens."""
    # Messages per day (last 7 days)
    r = await db.execute(text("""
        SELECT DATE(created_at) as day, COUNT(*) as msgs,
               COALESCE(SUM((details->>'tokens')::int), 0) as tokens
        FROM activity_logs WHERE action='message'
          AND created_at > NOW() - INTERVAL '7 days'
        GROUP BY day ORDER BY day
    """))
    daily = [{"date": str(row[0]), "messages": row[1], "tokens": row[2]} for row in r.fetchall()]

    # Per user stats
    r = await db.execute(text("""
        SELECT u.agent_name, u.phone_number,
               COUNT(l.id) as msgs,
               COALESCE(SUM((l.details->>'tokens')::int), 0) as tokens,
               MAX(l.created_at) as last_active
        FROM activity_logs l
        JOIN user_profiles u ON u.id::text = l.user_id
        WHERE l.action='message' AND l.created_at > NOW() - INTERVAL '30 days'
        GROUP BY u.id, u.agent_name, u.phone_number
        ORDER BY msgs DESC
    """))
    per_user = [{
        "agent_name": row[0], "phone": row[1],
        "messages": row[2], "tokens": row[3],
        "last_active": row[4].isoformat() if row[4] else None
    } for row in r.fetchall()]

    # Totals
    r = await db.execute(text("""
        SELECT COUNT(*) as total, COALESCE(SUM((details->>'tokens')::int), 0) as total_tokens
        FROM activity_logs WHERE action='message'
    """))
    totals = r.fetchone()

    return {
        "daily": daily,
        "per_user": per_user,
        "totals": {"messages": totals[0], "tokens": totals[1]},
    }

@router.post("/test-email")
async def test_email(body: dict = Body(...)):
    email = body.get("email", "")
    if not email: raise HTTPException(400, "email required")
    from app.services.email import send_welcome_email
    await send_welcome_email(email, "Test User", "pro")
    return {"status": "sent", "email": email}

@router.post("/users/{user_id}/access-link")
async def generate_access_link(user_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a fresh, ONE-TIME, expiring dashboard access link for an EXISTING
    agent. Each click produces a new random token (not the profile UUID). The token
    is consumed on successful registration and expires after 72h.
    """
    r = await db.execute(text(
        "SELECT agent_name, is_active FROM user_profiles WHERE id::text=:id"), {"id": user_id})
    p = r.fetchone()
    if not p:
        raise HTTPException(404, "Agent not found")
    if not p[1]:
        raise HTTPException(400, "Agent is inactive")

    signup_token = secrets.token_urlsafe(32)
    await db.execute(text(
        "UPDATE user_profiles SET signup_token=:tok, signup_expires=NOW() + INTERVAL '72 hours' WHERE id::text=:id"),
        {"tok": signup_token, "id": user_id})
    await db.commit()

    url = f"https://beprepared.dev/user/agent-access?token={signup_token}"
    return {"agent_name": p[0] or "Agent", "access_link": url, "expires_in": "72h"}


@router.post("/users/{user_id}/timezone")
async def set_user_timezone(user_id: str, body: dict = Body(...), db: AsyncSession = Depends(get_db)):
    tz = body.get("timezone", "")
    if not tz: raise HTTPException(400, "timezone required")
    r = await db.execute(text("UPDATE user_profiles SET timezone=:tz WHERE id::text=:uid"), {"tz": tz, "uid": user_id})
    await db.commit()
    return {"status": "ok"}

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id, agent_name, phone_number, timezone, plan, is_active FROM user_profiles WHERE id::text=:uid"), {"uid": user_id})
    u = r.fetchone()
    if not u: raise HTTPException(404, "User not found")
    return {"id": str(u[0]), "agent_name": u[1], "phone_number": u[2], "timezone": u[3], "plan": u[4], "is_active": u[5]}

@router.get("/users/{user_id}/register-link")
async def user_register_link(user_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a one-click registration link for the user dashboard."""
    r = await db.execute(text("SELECT id, agent_name FROM user_profiles WHERE id::text=:uid"), {"uid": user_id})
    u = r.fetchone()
    if not u: raise HTTPException(404, "User not found")
    return {"register_url": f"https://beprepared.dev/user/register?token={user_id}", "agent_name": u[1]}

@router.post("/users/{user_id}/telegram-link")
async def create_telegram_link(user_id: str, db: AsyncSession = Depends(get_db)):
    import secrets
    r = await db.execute(text("SELECT id, agent_name FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    u = r.fetchone()
    if not u: raise HTTPException(404, "User not found")
    uid, name = str(u[0]), u[1] or "Agent"
    code = "link_" + secrets.token_urlsafe(16)
    # Store user_id as reserved in claimed_by so webhook can look it up
    await db.execute(text("INSERT INTO invite_links (code, label, agent_name, plan, trial_days, claimed_by) VALUES (:c, :l, :a, 'pro', 0, :uid)"),
        {"c": code, "l": f"TG link {name}", "a": name, "uid": uid})
    await db.commit()
    return {"code": code, "link_url": f"https://t.me/BotBePreparedBot?start={code}"}

# ═══════════════════════════════════════════
# Invite Links
# ═══════════════════════════════════════════

@router.post("/invite-links")
async def create_invite(body: InviteLinkCreate, db: AsyncSession = Depends(get_db)):
    code = secrets.token_urlsafe(8)[:12]
    r = await db.execute(text("INSERT INTO invite_links (code,label,agent_name,plan,trial_days,is_vip) VALUES (:c,:l,:a,:p,:td,:v) RETURNING id,code,label,agent_name,plan,trial_days,is_vip,claimed_by,created_at"),
        {"c":code,"l":body.label,"a":body.agent_name,"p":body.plan,"td":body.trial_days if not body.is_vip else None,"v":body.is_vip})
    row = r.fetchone()
    return {"id":str(row[0]),"code":row[1],"label":row[2],"agent_name":row[3],"plan":row[4],"trial_days":row[5],"is_vip":row[6],"claimed":row[7] is not None,"link_url":f"{settings.public_url}/join/{row[1]}","created_at":row[8].isoformat()}

@router.get("/invite-links")
async def list_invites(db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,code,label,agent_name,plan,trial_days,is_vip,claimed_by,claimed_at,created_at FROM invite_links ORDER BY created_at DESC LIMIT 50"))
    return [{"id":str(row[0]),"code":row[1],"label":row[2],"agent_name":row[3],"plan":row[4],"trial_days":row[5],"is_vip":row[6],"claimed":row[7] is not None,"link_url":f"{settings.public_url}/join/{row[1]}","created_at":row[9].isoformat()} for row in r.fetchall()]

@router.delete("/invite-links/{invite_id}")
async def delete_invite(invite_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an invite link. Only unclaimed invites can be deleted (claimed ones have no extra resources, but we allow cleanup)."""
    r = await db.execute(text("SELECT id, claimed_by FROM invite_links WHERE id::text=:id"), {"id": invite_id})
    inv = r.fetchone()
    if not inv:
        raise HTTPException(404, "Invite not found")
    await db.execute(text("DELETE FROM invite_links WHERE id::text=:id"), {"id": invite_id})
    await db.commit()
    return {"status": "deleted", "id": invite_id}

# ═══════════════════════════════════════════
# Registration Requests (admin approval flow)
# ═══════════════════════════════════════════

@router.get("/registration-requests")
async def list_registration_requests(status: str = "pending", db: AsyncSession = Depends(get_db)):
    """List registration requests. By default shows pending. Only requests with a
    verified email are approvable (enforced again in the approve endpoint)."""
    allowed = {"pending", "approved", "rejected", "all"}
    flt = status if status in allowed and status != "all" else None
    if flt:
        r = await db.execute(text("""
            SELECT id, email, full_name, agent_name, use_case, plan_requested,
                   status, email_verified, created_at, reviewed_at, review_note,
                   assigned_profile_id
            FROM registration_requests WHERE status=:s ORDER BY created_at DESC
        """), {"s": flt})
    else:
        r = await db.execute(text("""
            SELECT id, email, full_name, agent_name, use_case, plan_requested,
                   status, email_verified, created_at, reviewed_at, review_note,
                   assigned_profile_id
            FROM registration_requests ORDER BY created_at DESC
        """))
    return [{
        "id": str(row[0]), "email": row[1], "full_name": row[2], "agent_name": row[3],
        "use_case": row[4], "plan_requested": row[5], "status": row[6],
        "email_verified": row[7], "created_at": row[8].isoformat() if row[8] else None,
        "reviewed_at": row[9].isoformat() if row[9] else None, "review_note": row[10],
        "assigned_profile_id": str(row[11]) if row[11] else None,
    } for row in r.fetchall()]


@router.post("/registration-requests/{req_id}/approve")
async def approve_registration(req_id: str, body: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Approve a registration request: create the agent + login account, send password setup link.

    SECURITY IMPROVEMENTS:
    - Password set AFTER approval (not during registration)
    - User receives setup_token to create password
    - Email verified requirement enforced
    - No password hash stored until user completes setup
    """
    r = await db.execute(text("""
        SELECT id, email, full_name, agent_name, use_case,
               plan_requested, status, email_verified
        FROM registration_requests WHERE id::text=:id
    """), {"id": req_id})
    req = r.fetchone()
    if not req:
        raise HTTPException(404, "Registration request not found")
    if req[6] != "pending":
        raise HTTPException(409, f"Request is already {req[6]}. Only pending requests can be approved.")
    if not req[7]:
        raise HTTPException(400, "Email not verified. Approval requires a verified email (security requirement).")

    email, full_name = req[1], req[2] or ""
    submitted_agent_name = req[3] or ""
    plan = req[5] or "pro"

    # Admin-chosen overrides (default to submitted details)
    agent_name = (body.get("agent_name") or submitted_agent_name or "My Assistant").strip()
    final_plan = (body.get("plan") or plan or "pro").strip()
    is_vip = final_plan == "vip"
    if final_plan not in ("trial", "basic", "pro", "business", "vip"):
        raise HTTPException(400, "Invalid plan. Must be one of trial/basic/pro/business/vip.")

    # ── 1. Create agent (user_profiles + isolated Hermes profile + vault) ──
    rr = await db.execute(text("""
        INSERT INTO user_profiles (agent_name, plan, is_vip,
            primary_model, backup_model)
        VALUES (:a, :p, :v,
            'accounts/fireworks/models/deepseek-v4-flash-0731',
            'accounts/fireworks/models/deepseek-v4-flash-0731')
        RETURNING id
    """), {"a": agent_name, "p": final_plan, "v": is_vip})
    uid = str(rr.fetchone()[0])

    try:
        profile = init_user_profile(user_id=uid, agent_name=agent_name, plan=final_plan, is_vip=is_vip)
        await db.execute(text("UPDATE user_profiles SET profile_path=:pp, updated_at=NOW() WHERE id::text=:uid"),
                         {"pp": profile["profile_dir"], "uid": uid})
        profile_status = "created"
    except Exception as e:
        profile_status = f"failed: {e}"

    # ── 2. Create login account WITHOUT password (password set later by user) ──
    # SECURITY FIX: No password_hash here - user sets it after approval
    await db.execute(text("""
        INSERT INTO user_accounts (user_profile_id, email, email_verified)
        VALUES (:p, :e, true)
        ON CONFLICT (email) DO NOTHING
    """), {"p": uid, "e": email})

    # ── 3. Generate password setup token (3-day expiry) ──
    setup_token = secrets.token_urlsafe(32)
    setup_expires = datetime.utcnow() + timedelta(days=3)

    # ── 4. Generate Telegram activation link (optional) ──
    tg_code = "link_" + secrets.token_urlsafe(16)
    await db.execute(text("""
        INSERT INTO invite_links (code, label, agent_name, plan, trial_days, claimed_by)
        VALUES (:c, :l, :a, 'pro', 0, :uid)
    """), {"c": tg_code, "l": f"Activation {email}", "a": agent_name, "uid": uid})

    # ── 5. Mark request approved + store setup token ──
    await db.execute(text("""
        UPDATE registration_requests
        SET status='approved', assigned_profile_id=:pid,
            setup_token=:st, setup_token_expires=:sx,
            review_note=:rn, reviewed_at=NOW()
        WHERE id=:id
    """), {"pid": uid, "st": setup_token, "sx": setup_expires,
           "rn": (body.get("review_note") or "")[:500], "id": req_id})
    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES (:u, 'registration_approved', :d)"),
                     {"u": uid, "d": f'{{"email":"{email}","plan":"{final_plan}"}}'})
    await db.commit()

    # ── 6. Email the user with password setup link ──
    setup_link = f"https://beprepared.dev/user/setup-password?token={setup_token}"
    tg_link = f"https://t.me/BotBePreparedBot?start={tg_code}"
    subject = f"You're approved{f', {full_name}' if full_name else ''}! Set up your account"

    email_html = f"""<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:560px;margin:40px auto;padding:20px">
<div style="background:#1A1A2E;border-radius:12px;padding:32px;text-align:center;margin-bottom:24px">
<h1 style="color:#fff;font-size:22px;margin:0">🎉 You're approved{f', {full_name}' if full_name else ''}!</h1>
<p style="color:#A29BFE;margin:8px 0 0">Your AI agent <strong>{agent_name}</strong> is ready</p>
</div>

<h2 style="color:#1A1A2E;font-size:18px">Get started in 2 steps:</h2>

<div style="background:#F3F4F6;border-radius:10px;padding:20px;margin:16px 0">
<h3 style="color:#1A1A2E;font-size:16px;margin:0 0 8px">1️⃣ Set your password</h3>
<p style="color:#4B5563;font-size:14px;margin:0 0 12px">Create a secure password to access your dashboard</p>
<a href="{setup_link}" style="display:block;background:#6C5CE7;color:#fff;padding:14px 24px;border-radius:8px;text-align:center;text-decoration:none;font-size:16px">Set Password & Login</a>
<p style="color:#9CA3AF;font-size:12px;margin:12px 0 0">Link expires in 3 days</p>
</div>

<div style="background:#F3F4F6;border-radius:10px;padding:20px;margin:16px 0">
<h3 style="color:#1A1A2E;font-size:16px;margin:0 0 8px">2️⃣ Connect Telegram (Optional)</h3>
<p style="color:#4B5563;font-size:14px;margin:0 0 12px">Chat with your agent on Telegram</p>
<a href="{tg_link}" style="display:block;background:#0088CC;color:#fff;padding:14px 24px;border-radius:8px;text-align:center;text-decoration:none;font-size:16px">Connect Telegram</a>
</div>

<p style="font-size:13px;color:#6B7280;margin-top:24px">
<strong>Plan:</strong> {final_plan.title()}<br>
<strong>Agent Name:</strong> {agent_name}
</p>

<p style="font-size:13px;color:#888;margin-top:24px">Sent by Hermes · beprepared.dev</p>
</body></html>"""

    try:
        from app.services.email import send_email
        await send_email(email, subject, email_html)
        email_status = "sent"
    except Exception as e:
        email_status = f"failed: {e}"

    return {
        "status": "approved",
        "user_id": uid,
        "agent_name": agent_name,
        "plan": final_plan,
        "profile_status": profile_status,
        "telegram_link": tg_link,
        "setup_link": setup_link,
        "email_status": email_status,
        "message": "User will receive email with password setup link"
    }


@router.post("/registration-requests/{req_id}/reject")
async def reject_registration(req_id: str, body: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Reject a pending registration request. Ends the user flow and notifies them."""
    r = await db.execute(text("SELECT id, email, full_name, status FROM registration_requests WHERE id::text=:id"), {"id": req_id})
    req = r.fetchone()
    if not req:
        raise HTTPException(404, "Registration request not found")
    if req[3] != "pending":
        raise HTTPException(409, f"Request is already {req[3]}")

    email, full_name = req[1], req[2] or ""
    note = (body.get("review_note") or "").strip()[:500]

    await db.execute(text("""
        UPDATE registration_requests SET status='rejected', review_note=:n, reviewed_at=NOW() WHERE id=:id
    """), {"n": note, "id": req_id})
    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES ('system', 'registration_rejected', :d)"),
                     {"d": f'{{"email":"{email}"}}'})
    await db.commit()

    # Notify the user their request was declined.
    try:
        from app.services.email import send_email
        note_html = f"<p>Reason: {note}</p>" if note else ""
        await send_email(email, "Update on your registration", f"""<h2>Registration update</h2>
<p>We're sorry — your request{f' {full_name}' if full_name else ''} was not approved at this time.</p>
{note_html}
<p>If you believe this is a mistake, please contact the administrator.</p>""")
    except Exception:
        pass

    try:
        from app.services.admin_notify import notify_admin_rejected
        await notify_admin_rejected(email)
    except Exception:
        pass

    return {"status": "rejected", "email": email}


# ═══════════════════════════════════════════
# Global Model Config
# ═══════════════════════════════════════════

@router.get("/models")
async def get_models():
    return {"primary_model":settings.default_primary_model,"backup_model":settings.default_backup_model}

@router.post("/models")
async def update_models(body: dict, db: AsyncSession = Depends(get_db)):
    if body.get("primary_model"):
        await db.execute(text("UPDATE user_profiles SET primary_model=:m,updated_at=NOW() WHERE model_overridden_at IS NULL"),{"m":body["primary_model"]})
    if body.get("backup_model"):
        await db.execute(text("UPDATE user_profiles SET backup_model=:m,updated_at=NOW() WHERE model_overridden_at IS NULL"),{"m":body["backup_model"]})
    return {"status":"updated"}

# ═══════════════════════════════════════════
# Per-User Model Override
# ═══════════════════════════════════════════
# POST /api/admin/users/{user_id}/model

@router.post("/users/{user_id}/model")
async def override_user_model(user_id: str, body: UserModelOverride, db: AsyncSession = Depends(get_db)):
    """Override the AI model for a specific user. This sets model_overridden_at
    so that global model updates won't overwrite this user's choice."""
    r = await db.execute(text("SELECT id, profile_path FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    updates = []
    params = {"uid": user_id, "now": datetime.utcnow()}

    if body.primary_model:
        updates.append("primary_model = :pm")
        params["pm"] = body.primary_model
    if body.backup_model:
        updates.append("backup_model = :bm")
        params["bm"] = body.backup_model

    if not updates:
        raise HTTPException(400, "At least one of primary_model or backup_model is required")

    updates.append("model_overridden_at = :now")
    updates.append("updated_at = :now")

    await db.execute(
        text(f"UPDATE user_profiles SET {', '.join(updates)} WHERE id::text=:uid OR phone_number=:uid"),
        params,
    )

    # Also update the on-disk Hermes profile config.yaml
    profile_path = user[1]
    if profile_path:
        try:
            await update_user_model_config(
                user_id=user_id,
                primary_model=body.primary_model,
                backup_model=body.backup_model,
                profile_dir=profile_path,
            )
        except Exception as e:
            logger.error("Failed to update config.yaml for user %s: %s", user_id, e)

    # Log the override
    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES (:uid, 'model_override', :det)"),
        {"uid": user_id, "det": f'{{"primary":"{body.primary_model or ""}","backup":"{body.backup_model or ""}"}}'})

    return {
        "status": "updated",
        "user_id": user_id,
        "primary_model": body.primary_model,
        "backup_model": body.backup_model,
    }

# ═══════════════════════════════════════════
# Per-User Skills
# ═══════════════════════════════════════════
# POST /api/admin/users/{user_id}/skills

@router.post("/users/{user_id}/skills")
async def add_user_skill(user_id: str, body: UserSkillCreate, db: AsyncSession = Depends(get_db)):
    """Add or update a skill file for a specific user's Hermes profile."""
    r = await db.execute(text("SELECT id, profile_path FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    if not body.skill_name.endswith(".md"):
        raise HTTPException(400, "Skill name must end with .md")

    profile_path = user[1]
    if not profile_path:
        raise HTTPException(400, "User has no profile path set up")

    try:
        skill_path = await write_user_skill(
            user_id=user_id,
            skill_name=body.skill_name,
            content=body.content,
            profile_dir=profile_path,
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to write skill: {e}")

    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES (:uid, 'skill_added', :det)"),
        {"uid": user_id, "det": f'{{"skill":"{body.skill_name}","path":"{skill_path}"}}'})

    return {
        "status": "ok",
        "user_id": user_id,
        "skill_name": body.skill_name,
        "path": skill_path,
    }

# ═══════════════════════════════════════════
# Global Skills Template (push to all users)
# ═══════════════════════════════════════════
# POST /api/admin/skills

@router.post("/skills")
async def add_global_skill(body: GlobalSkillTemplate, db: AsyncSession = Depends(get_db)):
    """Add or update a skill template and push it to all users (or a subset)."""
    if not body.skill_name.endswith(".md"):
        raise HTTPException(400, "Skill name must end with .md")

    results = await write_global_skill_template(
        skill_name=body.skill_name,
        content=body.content,
        user_ids=body.user_ids,
    )

    success_count = sum(1 for r in results if r["status"] == "ok")
    failed_count = sum(1 for r in results if r["status"] == "failed")

    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES ('system', 'global_skill', :det)"),
        {"det": f'{{"skill":"{body.skill_name}","success":{success_count},"failed":{failed_count}}}'})

    return {
        "status": "ok",
        "skill_name": body.skill_name,
        "users_targeted": len(results),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results,
    }

# ═══════════════════════════════════════════
# Agent Status & Restart
# ═══════════════════════════════════════════

@router.get("/users/{user_id}/status")
async def agent_status(user_id: str, db: AsyncSession = Depends(get_db)):
    """Check if a user's Hermes agent profile is healthy."""
    r = await db.execute(text("SELECT id, is_active, profile_path, primary_model, backup_model FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    profile_path = user[2]
    config_exists = False
    skills_count = 0
    memories_count = 0

    if profile_path and os.path.exists(profile_path):
        config_exists = os.path.exists(os.path.join(profile_path, "config.yaml"))
        skills_dir = os.path.join(profile_path, "skills")
        memories_dir = os.path.join(profile_path, "memories")
        if os.path.exists(skills_dir):
            skills_count = len([f for f in os.listdir(skills_dir) if f.endswith(".md")])
        if os.path.exists(memories_dir):
            memories_count = len(os.listdir(memories_dir))

    return {
        "user_id": user_id,
        "is_active": bool(user[1]),
        "profile_exists": bool(profile_path) and os.path.exists(profile_path) if profile_path else False,
        "config_exists": config_exists,
        "skills_count": skills_count,
        "memories_count": memories_count,
        "primary_model": user[3],
        "backup_model": user[4],
        "profile_path": profile_path,
    }

@router.post("/users/{user_id}/restart")
async def restart_agent(user_id: str, db: AsyncSession = Depends(get_db)):
    """'Restart' the user's agent by sending a health-check query through Hermes.
    The Hermes CLI is stateless per invocation (no persistent daemon), so this
    simply verifies the agent can respond by running a ping-like query."""
    r = await db.execute(text("SELECT id, profile_path FROM user_profiles WHERE id::text=:uid OR phone_number=:uid"), {"uid": user_id})
    user = r.fetchone()
    if not user:
        raise HTTPException(404, "User not found")

    profile_path = user[1]
    if not profile_path or not os.path.exists(profile_path):
        raise HTTPException(400, "User profile directory does not exist")

    try:
        # Run a quick ping query to verify the agent is responsive
        resp = await hermes_profile_chat(
            user_id=user_id,
            message="ping",
            profile_dir=profile_path,
            timeout=30,
        )
        status = "ok" if resp else "no_response"
    except Exception as e:
        status = f"failed: {str(e)[:200]}"

    await db.execute(text("INSERT INTO activity_logs (user_id, action, details) VALUES (:uid, 'agent_restart', :det)"),
        {"uid": user_id, "det": f'{{"status":"{status}"}}'})

    return {
        "status": status,
        "user_id": user_id,
    }
