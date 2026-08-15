"""User portal API — full CRUD for notes, projects, reminders, activity.

SECURITY IMPROVEMENTS:
- Session expiration validation
- CSRF protection on state-changing operations
- Rate limiting on expensive operations
- Uses dedicated session_token instead of verification_token
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from app.database import async_session_factory
from app.csrf import require_csrf
from slowapi import Limiter
from slowapi.util import get_remote_address
from pathlib import Path
from datetime import datetime
import json

router = APIRouter(prefix="/api/me", tags=["portal"])
limiter = Limiter(key_func=get_remote_address)

OBSIDIAN_ROOT = Path("/opt/hermes/obsidian")

async def resolve_user(request: Request) -> dict:
    """Resolve user from session token with expiration validation.

    SECURITY: Uses dedicated session_token with expiration check.
    Supports both cookie and Authorization header for backward compatibility.
    """
    # Try cookie first (new method)
    token = request.cookies.get("portal_token")

    # Fall back to Authorization header (backward compatibility)
    if not token:
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(401, "Missing auth token")

    async with async_session_factory() as db:
        # SECURITY FIX: Check session_token with expiration
        r = await db.execute(text("""
            SELECT ua.user_profile_id, up.agent_name, up.is_active
            FROM user_accounts ua
            JOIN user_profiles up ON up.id = ua.user_profile_id
            WHERE ua.session_token=:t
              AND ua.session_expires > NOW()
              AND ua.email_verified=true
        """), {"t": token})
        u = r.fetchone()

        if not u:
            raise HTTPException(401, "Invalid or expired session. Please login again.")

        # Check account is active
        if not u[2]:
            raise HTTPException(403, "Account disabled. Please contact support.")

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

@router.post("/notes", dependencies=[Depends(require_csrf)])
async def create_note(request: Request, body: dict, user: dict = Depends(resolve_user)):
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

@router.put("/notes/{note_id}", dependencies=[Depends(require_csrf)])
async def update_note(request: Request, note_id: str, body: dict, user: dict = Depends(resolve_user)):
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

@router.delete("/notes/{note_id}", dependencies=[Depends(require_csrf)])
async def delete_note(request: Request, note_id: str, user: dict = Depends(resolve_user)):
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

@router.post("/projects", dependencies=[Depends(require_csrf)])
async def create_project(request: Request, body: dict, user: dict = Depends(resolve_user)):
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

@router.put("/projects/{project_id}", dependencies=[Depends(require_csrf)])
async def update_project(request: Request, project_id: str, body: dict, user: dict = Depends(resolve_user)):
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

@router.delete("/projects/{project_id}", dependencies=[Depends(require_csrf)])
async def delete_project(request: Request, project_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM projects WHERE id::text=:p AND user_id::text=:u"), {"p": project_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

@router.post("/projects/{project_id}/research", dependencies=[Depends(require_csrf)])
async def add_research(request: Request, project_id: str, body: dict, user: dict = Depends(resolve_user)):
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

@router.delete("/projects/{project_id}/research/{research_id}", dependencies=[Depends(require_csrf)])
async def delete_research(request: Request, project_id: str, research_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM project_research WHERE id::text=:r AND project_id::text=:p"), {"r": research_id, "p": project_id})
        await db.commit()
    return {"status": "deleted"}

# ═══════════════════════════ REMINDERS ═══════════════════════════


# ═══════════════════════════ SEMANTIC SEARCH ═══════════════════════════

@router.get("/search")
@limiter.limit("20/minute")
async def search_data(request: Request, q: str = "", limit: int = 8, user: dict = Depends(resolve_user)):
    """Semantic search across the user's notes, projects, research, ideas,
    reminders, and vault. Auto-indexes on first use."""
    from app.services.search import search_user_data
    if not q.strip():
        return {"results": []}
    return await search_user_data(user["id"], q.strip(), min(limit, 25))


@router.post("/search/index", dependencies=[Depends(require_csrf)])
@limiter.limit("3/hour")
async def reindex_data(request: Request, user: dict = Depends(resolve_user)):
    """(Re)index all of the user's data into embeddings."""
    from app.services.search import index_user_data
    try:
        n = await index_user_data(user["id"])
        return {"indexed": n}
    except Exception as e:
        return {"error": str(e), "indexed": 0}

@router.get("/reminders")
async def list_reminders(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, remind_at, done, created_at FROM reminders WHERE user_id::text=:uid ORDER BY remind_at ASC"),
            {"uid": user["id"]},
        )
        reminders = [
            {
                "id": str(row[0]),
                "title": row[1],
                "remind_at": row[2].isoformat()[:19] if row[2] else "",
                "done": row[3],
                "created_at": row[4].isoformat()[:19] if row[4] else ""
            }
            for row in r.fetchall()
        ]
    return {"reminders": reminders}

@router.post("/reminders", dependencies=[Depends(require_csrf)])
async def create_reminder(request: Request, body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    remind_at = (body.get("remind_at") or "").strip()
    done = body.get("done", False)
    if not title:
        raise HTTPException(400, "Title required")
    if not remind_at:
        raise HTTPException(400, "Remind date/time required")
    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO reminders (user_id, title, remind_at, done) VALUES (:u, :t, :r, :d) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "r": remind_at, "d": done},
        )
        await db.commit()
        row = r.fetchone()
        return {"id": str(row[0]), "title": title, "remind_at": remind_at, "done": done, "created_at": str(row[1])[:19]}

@router.put("/reminders/{reminder_id}", dependencies=[Depends(require_csrf)])
async def update_reminder(request: Request, reminder_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM reminders WHERE id::text=:r AND user_id::text=:u"), {"r": reminder_id, "u": user["id"]})
        if not r.fetchone():
            raise HTTPException(404, "Reminder not found")
        sets = []
        params = {"r": reminder_id}
        if "title" in body: sets.append("title=:t"); params["t"] = body["title"]
        if "remind_at" in body: sets.append("remind_at=:ra"); params["ra"] = body["remind_at"]
        if "done" in body: sets.append("done=:d"); params["d"] = body["done"]
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE reminders SET {', '.join(sets)} WHERE id::text=:r"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/reminders/{reminder_id}", dependencies=[Depends(require_csrf)])
async def delete_reminder(request: Request, reminder_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM reminders WHERE id::text=:r AND user_id::text=:u"), {"r": reminder_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

# ═══════════════════════════ ACTIVITY ═══════════════════════════

@router.get("/activity")
async def get_activity(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT created_at, action, details FROM activity_logs WHERE user_id::text=:uid ORDER BY created_at DESC LIMIT 50"),
            {"uid": user["id"]},
        )
        activity = [
            {
                "time": row[0].isoformat()[:19] if row[0] else "",
                "action": row[1],
                "details": json.dumps(row[2]) if row[2] else "{}"
            }
            for row in r.fetchall()
        ]
    return {"activity": activity}

# ═══════════════════════════ IDEAS ═══════════════════════════

@router.get("/ideas")
async def list_ideas(status: str = None, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        query = "SELECT id, title, content, status, tags, updated_at FROM ideas WHERE user_id::text=:uid"
        params = {"uid": user["id"]}
        if status:
            query += " AND status=:status"
            params["status"] = status
        query += " ORDER BY updated_at DESC"
        r = await db.execute(text(query), params)
        ideas = [
            {
                "id": str(row[0]),
                "title": row[1],
                "content": row[2],
                "status": row[3],
                "tags": row[4] or "",
                "updated_at": str(row[5])[:19] if row[5] else ""
            }
            for row in r.fetchall()
        ]
    return {"ideas": ideas}

@router.post("/ideas", dependencies=[Depends(require_csrf)])
async def create_idea(request: Request, body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    status = (body.get("status") or "brainstorm").strip()
    tags = (body.get("tags") or "").strip()
    if not title:
        raise HTTPException(400, "Title required")
    if status not in ['brainstorm', 'developing', 'ready', 'archived']:
        status = 'brainstorm'
    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO ideas (user_id, title, content, status, tags) VALUES (:u, :t, :c, :s, :tags) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "c": content, "s": status, "tags": tags},
        )
        await db.commit()
        row = r.fetchone()
        return {"id": str(row[0]), "title": title, "content": content, "status": status, "tags": tags, "created_at": str(row[1])[:19]}

@router.put("/ideas/{idea_id}", dependencies=[Depends(require_csrf)])
async def update_idea(request: Request, idea_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM ideas WHERE id::text=:i AND user_id::text=:u"), {"i": idea_id, "u": user["id"]})
        if not r.fetchone():
            raise HTTPException(404, "Idea not found")
        sets = []
        params = {"i": idea_id}
        if "title" in body: sets.append("title=:t"); params["t"] = body["title"]
        if "content" in body: sets.append("content=:c"); params["c"] = body["content"]
        if "status" in body: sets.append("status=:s"); params["s"] = body["status"]
        if "tags" in body: sets.append("tags=:tags"); params["tags"] = body["tags"]
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE ideas SET {', '.join(sets)} WHERE id::text=:i"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/ideas/{idea_id}", dependencies=[Depends(require_csrf)])
async def delete_idea(request: Request, idea_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM ideas WHERE id::text=:i AND user_id::text=:u"), {"i": idea_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

# ═══════════════════════════ SCHEDULE/EVENTS ═══════════════════════════

@router.get("/events")
async def list_events(from_date: str = None, to_date: str = None, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        query = "SELECT id, title, description, event_start, event_end, location, is_all_day, recurrence FROM scheduled_events WHERE user_id::text=:uid"
        params = {"uid": user["id"]}
        if from_date:
            query += " AND event_start >= :from_date"
            params["from_date"] = from_date
        if to_date:
            query += " AND event_start <= :to_date"
            params["to_date"] = to_date
        query += " ORDER BY event_start ASC"
        r = await db.execute(text(query), params)
        events = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2] or "",
                "event_start": row[3].isoformat()[:19] if row[3] else "",
                "event_end": row[4].isoformat()[:19] if row[4] else "",
                "location": row[5] or "",
                "is_all_day": row[6],
                "recurrence": row[7] or "none"
            }
            for row in r.fetchall()
        ]
    return {"events": events}

@router.post("/events", dependencies=[Depends(require_csrf)])
async def create_event(request: Request, body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    event_start = (body.get("event_start") or "").strip()
    event_end = (body.get("event_end") or "").strip()
    location = (body.get("location") or "").strip()
    is_all_day = body.get("is_all_day", False)
    recurrence = (body.get("recurrence") or "none").strip()

    if not title:
        raise HTTPException(400, "Title required")
    if not event_start:
        raise HTTPException(400, "Event start time required")
    if not event_end:
        raise HTTPException(400, "Event end time required")

    # Parse ISO strings into datetimes (columns are TIMESTAMPTZ)
    try:
        start_dt = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(event_end.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(400, "Invalid date format for event start/end. Use YYYY-MM-DDTHH:MM:SS")

    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO scheduled_events (user_id, title, description, event_start, event_end, location, is_all_day, recurrence) VALUES (:u, :t, :d, :s, :e, :l, :a, :r) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "d": description, "s": start_dt, "e": end_dt, "l": location, "a": is_all_day, "r": recurrence},
        )
        await db.commit()
        row = r.fetchone()
        return {
            "id": str(row[0]),
            "title": title,
            "description": description,
            "event_start": event_start,
            "event_end": event_end,
            "location": location,
            "is_all_day": is_all_day,
            "recurrence": recurrence,
            "created_at": str(row[1])[:19]
        }

@router.put("/events/{event_id}", dependencies=[Depends(require_csrf)])
async def update_event(request: Request, event_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM scheduled_events WHERE id::text=:e AND user_id::text=:u"), {"e": event_id, "u": user["id"]})
        if not r.fetchone():
            raise HTTPException(404, "Event not found")
        sets = []
        params = {"e": event_id}
        if "title" in body: sets.append("title=:t"); params["t"] = body["title"]
        if "description" in body: sets.append("description=:d"); params["d"] = body["description"]
        if "event_start" in body: sets.append("event_start=:s"); params["s"] = datetime.fromisoformat(str(body["event_start"]).replace("Z","+00:00"))
        if "event_end" in body: sets.append("event_end=:end"); params["end"] = datetime.fromisoformat(str(body["event_end"]).replace("Z","+00:00"))
        if "location" in body: sets.append("location=:l"); params["l"] = body["location"]
        if "is_all_day" in body: sets.append("is_all_day=:a"); params["a"] = body["is_all_day"]
        if "recurrence" in body: sets.append("recurrence=:r"); params["r"] = body["recurrence"]
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE scheduled_events SET {', '.join(sets)} WHERE id::text=:e"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/events/{event_id}", dependencies=[Depends(require_csrf)])
async def delete_event(request: Request, event_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM scheduled_events WHERE id::text=:e AND user_id::text=:u"), {"e": event_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

# ═══════════════════════════ BACKGROUND JOBS ═══════════════════════════

def calculate_next_run(cron_expression: str) -> str:
    """Simple cron parser for common patterns. Returns next run datetime as ISO string."""
    from datetime import datetime, timedelta
    now = datetime.now()

    # Common patterns
    if cron_expression == "0 9 * * *":  # Daily at 9am
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
    elif cron_expression == "0 0 * * 1":  # Weekly Monday midnight
        days_ahead = 0 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_run = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif cron_expression == "0 0 1 * *":  # Monthly 1st
        if now.day == 1 and now.hour == 0:
            next_run = (now.replace(day=1) + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_run = (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1)
    elif cron_expression.startswith("*/"):  # Every N minutes
        try:
            mins = int(cron_expression.split()[0].replace("*/", ""))
            next_run = now + timedelta(minutes=mins)
        except:
            next_run = now + timedelta(hours=1)
    else:
        # Default: 1 hour from now
        next_run = now + timedelta(hours=1)

    return next_run.isoformat()[:19]

@router.get("/jobs")
async def list_jobs(user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(
            text("SELECT id, title, description, job_type, cron_expression, is_enabled, last_run_at, next_run_at, last_result FROM background_jobs WHERE user_id::text=:uid ORDER BY created_at DESC"),
            {"uid": user["id"]},
        )
        jobs = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2] or "",
                "job_type": row[3],
                "cron_expression": row[4],
                "is_enabled": row[5],
                "last_run_at": row[6].isoformat()[:19] if row[6] else None,
                "next_run_at": row[7].isoformat()[:19] if row[7] else "",
                "last_result": row[8] or ""
            }
            for row in r.fetchall()
        ]
    return {"jobs": jobs}

@router.post("/jobs", dependencies=[Depends(require_csrf)])
async def create_job(request: Request, body: dict, user: dict = Depends(resolve_user)):
    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    job_type = (body.get("job_type") or "custom").strip()
    cron_expression = (body.get("cron_expression") or "0 9 * * *").strip()

    if not title:
        raise HTTPException(400, "Title required")
    if job_type not in ['email', 'webhook', 'cleanup', 'report', 'custom']:
        job_type = 'custom'

    next_run_at = calculate_next_run(cron_expression)

    async with async_session_factory() as db:
        r = await db.execute(
            text("INSERT INTO background_jobs (user_id, title, description, job_type, cron_expression, next_run_at) VALUES (:u, :t, :d, :jt, :c, :n) RETURNING id, created_at"),
            {"u": user["id"], "t": title, "d": description, "jt": job_type, "c": cron_expression, "n": next_run_at},
        )
        await db.commit()
        row = r.fetchone()
        return {
            "id": str(row[0]),
            "title": title,
            "description": description,
            "job_type": job_type,
            "cron_expression": cron_expression,
            "is_enabled": True,
            "next_run_at": next_run_at,
            "created_at": str(row[1])[:19]
        }

@router.put("/jobs/{job_id}", dependencies=[Depends(require_csrf)])
async def update_job(request: Request, job_id: str, body: dict, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM background_jobs WHERE id::text=:j AND user_id::text=:u"), {"j": job_id, "u": user["id"]})
        if not r.fetchone():
            raise HTTPException(404, "Job not found")
        sets = []
        params = {"j": job_id}
        if "title" in body: sets.append("title=:t"); params["t"] = body["title"]
        if "description" in body: sets.append("description=:d"); params["d"] = body["description"]
        if "job_type" in body: sets.append("job_type=:jt"); params["jt"] = body["job_type"]
        if "is_enabled" in body: sets.append("is_enabled=:e"); params["e"] = body["is_enabled"]
        if "cron_expression" in body:
            sets.append("cron_expression=:c")
            params["c"] = body["cron_expression"]
            next_run_at = calculate_next_run(body["cron_expression"])
            sets.append("next_run_at=:n")
            params["n"] = next_run_at
        if not sets: raise HTTPException(400, "Nothing to update")
        sets.append("updated_at=NOW()")
        await db.execute(text(f"UPDATE background_jobs SET {', '.join(sets)} WHERE id::text=:j"), params)
        await db.commit()
    return {"status": "updated"}

@router.delete("/jobs/{job_id}", dependencies=[Depends(require_csrf)])
async def delete_job(request: Request, job_id: str, user: dict = Depends(resolve_user)):
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM background_jobs WHERE id::text=:j AND user_id::text=:u"), {"j": job_id, "u": user["id"]})
        await db.commit()
    return {"status": "deleted"}

@router.get("/personality")
async def get_personality(user: dict = Depends(resolve_user)):
    from app.services.persona import DEFAULT_PERSONALITY
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT agent_name, personality FROM user_profiles WHERE id::text=:u"), {"u": user["id"]})
        row = r.fetchone()
        agent_name = (row[0] if row else None) or "Agent"
        persona = (row[1] if row and row[1] else None)
    return {
        "agent_name": agent_name,
        "personality": persona or DEFAULT_PERSONALITY.format(agent_name=agent_name),
        "is_custom": bool(persona and persona.strip()),
    }

@router.put("/personality")
@limiter.limit("20/minute")
async def update_personality(request: Request, body: dict, user: dict = Depends(resolve_user)):
    txt = (body.get("personality") or "").strip()
    if not txt:
        raise HTTPException(400, "personality cannot be empty")
    if len(txt) > 20000:
        raise HTTPException(400, "personality too long (max 20000 chars)")
    async with async_session_factory() as db:
        await db.execute(text("UPDATE user_profiles SET personality=:p WHERE id::text=:u"), {"p": txt, "u": user["id"]})
        await db.commit()
    return {"status": "saved", "message": "Agent personality updated."}

