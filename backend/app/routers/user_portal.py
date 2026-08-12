"""User-facing portal API — notes, reminders, projects, activity."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from app.database import async_session_factory
from pathlib import Path
from datetime import datetime
import json

router = APIRouter(prefix="/api/me", tags=["portal"])

OBSIDIAN_ROOT = Path("/opt/hermes/obsidian")

async def resolve_user(request: Request) -> dict:
    """Extract user from Bearer token (from user_accounts login)."""
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(401, "Missing auth token")
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT ua.user_profile_id, up.agent_name FROM user_accounts ua JOIN user_profiles up ON up.id=ua.user_profile_id WHERE ua.verification_token=:t AND ua.email_verified=true"),
            {"t": token},
        )
        u = r.fetchone()
        if not u:
            raise HTTPException(401, "Invalid or expired token")
        return {"id": str(u[0]), "name": u[1]}


@router.get("/notes")
async def list_notes(user: dict = Depends(resolve_user)):
    """List recent vault notes."""
    inbox = OBSIDIAN_ROOT / user["id"] / "Inbox"
    notes = []
    if inbox.exists():
        for f in sorted(inbox.glob("*.md"), reverse=True)[:20]:
            text = f.read_text()
            title = text.split("\n")[0].replace("# ", "").strip()[:60]
            notes.append({"title": title, "file": f.name, "preview": text[:200]})
    return {"notes": notes, "user": user["name"]}


@router.get("/reminders")
async def list_reminders(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, remind_at, done FROM reminders WHERE user_id::text=:uid ORDER BY remind_at NULLS LAST, created_at DESC LIMIT 20"),
            {"uid": user["id"]},
        )
        reminders = [{"id": str(row[0]), "title": row[1], "remind_at": str(row[2]) if row[2] else None, "done": row[3]} for row in r.fetchall()]
    return {"reminders": reminders}


@router.get("/projects")
async def list_projects(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, description, status FROM projects WHERE user_id::text=:uid ORDER BY created_at DESC LIMIT 20"),
            {"uid": user["id"]},
        )
        projects = [{"id": str(row[0]), "title": row[1], "description": row[2], "status": row[3]} for row in r.fetchall()]
    return {"projects": projects}


@router.get("/activity")
async def recent_activity(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT created_at, action, details FROM activity_logs WHERE user_id::text=:uid ORDER BY created_at DESC LIMIT 20"),
            {"uid": user["id"]},
        )
        activity = [{"time": str(row[0]), "action": row[1], "details": row[2]} for row in r.fetchall()]
    return {"activity": activity}
