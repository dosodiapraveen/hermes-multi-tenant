"""User portal API — full CRUD for notes, projects, reminders, activity."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from app.database import async_session_factory
from pathlib import Path
from datetime import datetime
import json

router = APIRouter(prefix="/api/me", tags=["portal"])

OBSIDIAN_ROOT = Path("/opt/hermes/obsidian")

async def resolve_user(request: Request) -> dict:
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

# ═══════════════════════════ NOTES ═══════════════════════════

@router.get("/notes")
async def list_notes(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, content, category, updated_at FROM notes WHERE user_id::text=:uid ORDER BY updated_at DESC LIMIT 50"),
            {"uid": user["id"]},
        )
        notes = [{"id": str(row[0]), "title": row[1], "content": row[2], "category": row[3], "updated_at": str(row[4])[:19]} for row in r.fetchall()]
    # Also include vault notes
    vault_notes = []
    inbox = OBSIDIAN_ROOT / user["id"] / "Inbox"
    if inbox.exists():
        for f in sorted(inbox.glob("*.md"), reverse=True)[:10]:
            text_content = f.read_text()
            title = text_content.split("\n")[0].replace("# ", "").strip()[:60]
            vault_notes.append({"id": f"vault_{f.name}", "title": title, "content": text_content[:300], "category": "Vault", "updated_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")})
    return {"notes": notes + vault_notes, "user": user["name"]}

@router.post("/notes")
async def create_note(body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    category = (body.get("category") or "General").strip()
    if not title:
        raise HTTPException(400, "Title required")
    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO notes (user_id, title, content, category) VALUES (:u, :t, :c, :cat) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "c": content, "cat": category},
        )
        await db.commit()
        row = r.fetchone()
        return {"id": str(row[0]), "title": title, "content": content, "category": category, "created_at": str(row[1])[:19]}

@router.put("/notes/{note_id}")
async def update_note(note_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM notes WHERE id::text=:n AND user_id::text=:u"), {"n": note_id, "u": user["id"]})
        if not r.fetchone():
            raise HTTPException(404, "Note not found")
        sets = []
        params = {"n": note_id}
        if "title" in body: sets.append("title=:t"); params["t"] = body["title"]
        if "content" in body: sets.append("content=:c"); params["c"] = body["content"]
        if "category" in body: sets.append("category=:cat"); params["cat"] = body["category"]
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE notes SET {', '.join(sets)} WHERE id::text=:n"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM notes WHERE id::text=:n AND user_id::text=:u"), {"n": note_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

# ═══════════════════════════ PROJECTS ═══════════════════════════

@router.get("/projects")
async def list_projects(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, description, status, updated_at FROM projects WHERE user_id::text=:uid ORDER BY updated_at DESC"),
            {"uid": user["id"]},
        )
        projects = [{"id": str(row[0]), "title": row[1], "description": row[2], "status": row[3], "updated_at": str(row[4])[:19] if row[4] else ""} for row in r.fetchall()]
    return {"projects": projects}

@router.post("/projects")
async def create_project(body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    if not title:
        raise HTTPException(400, "Title required")
    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO projects (user_id, title, description) VALUES (:u, :t, :d) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "d": description},
        )
        await db.commit()
        row = r.fetchone()
        return {"id": str(row[0]), "title": title, "description": description, "status": "active", "created_at": str(row[1])[:19]}

@router.get("/projects/{project_id}")
async def get_project(project_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, description, status, created_at, updated_at FROM projects WHERE id::text=:p AND user_id::text=:u"),
            {"p": project_id, "u": user["id"]},
        )
        p = r.fetchone()
        if not p: raise HTTPException(404, "Project not found")
        # Get research notes
        rr = await db.execute(text("SELECT id, title, content, created_at FROM project_research WHERE project_id::text=:p ORDER BY created_at DESC"), {"p": project_id})
        research = [{"id": str(row[0]), "title": row[1], "content": row[2], "created_at": str(row[3])[:19]} for row in rr.fetchall()]
        return {
            "id": str(p[0]), "title": p[1], "description": p[2], "status": p[3],
            "created_at": str(p[4])[:19], "updated_at": str(p[5])[:19] if p[5] else "",
            "research": research,
        }

@router.put("/projects/{project_id}")
async def update_project(project_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM projects WHERE id::text=:p AND user_id::text=:u"), {"p": project_id, "u": user["id"]})
        if not r.fetchone(): raise HTTPException(404, "Project not found")
        sets = []; params = {"p": project_id}
        for field in ["title", "description", "status"]:
            if field in body: sets.append(f"{field}=:{field[0]}"); params[field[0]] = body[field]
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE projects SET {', '.join(sets)} WHERE id::text=:p"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM projects WHERE id::text=:p AND user_id::text=:u"), {"p": project_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

@router.post("/projects/{project_id}/research")
async def add_research(project_id: str, body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    if not title: raise HTTPException(400, "Title required")
    async with async_session_factory() as db:
        # Verify project belongs to user
        r = await db.execute(text("SELECT id FROM projects WHERE id::text=:p AND user_id::text=:u"), {"p": project_id, "u": user["id"]})
        if not r.fetchone(): raise HTTPException(404, "Project not found")
        rr = await db.execute(
            text("INSERT INTO project_research (project_id, title, content) VALUES (:p, :t, :c) RETURNING id, created_at"),
            {"p": project_id, "t": title, "c": content},
        )
        # Update project's updated_at
        await db.execute(text("UPDATE projects SET updated_at=NOW() WHERE id::text=:p"), {"p": project_id})
        await db.commit()
        row = rr.fetchone()
        return {"id": str(row[0]), "title": title, "content": content, "created_at": str(row[1])[:19]}

@router.delete("/projects/{project_id}/research/{research_id}")
async def delete_research(project_id: str, research_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM project_research WHERE id::text=:r AND project_id::text=:p"), {"r": research_id, "p": project_id})
        await db.commit()
    return {"status": "deleted"}
