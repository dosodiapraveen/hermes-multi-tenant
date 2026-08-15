"""Onboarding API endpoints for first-time user experience.

Provides endpoints for:
- Onboarding progress tracking
- Wizard completion
- Checklist management
- Tutorial progress
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from app.database import async_session_factory
from app.csrf import require_csrf

router = APIRouter(prefix="/api/me/onboarding", tags=["onboarding"])


async def resolve_user(request: Request) -> dict:
    """Resolve user from session token with expiration validation."""
    # Try cookie first (new method)
    token = request.cookies.get("portal_token")

    # Fall back to Authorization header (backward compatibility)
    if not token:
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(401, "Missing auth token")

    async with async_session_factory() as db:
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

        if not u[2]:
            raise HTTPException(403, "Account disabled. Please contact support.")

        return {"id": str(u[0]), "name": u[1]}


# =============================================================================
# ONBOARDING ENDPOINTS
# =============================================================================

@router.get("")
async def get_onboarding_status(user: dict = Depends(resolve_user)):
    """Get user's onboarding progress and checklist status."""
    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT wizard_completed, wizard_completed_at, wizard_skipped,
                       checklist_items, checklist_completed_count, checklist_total,
                       checklist_dismissed, onboarding_completed, onboarding_completed_at,
                       first_note_at, first_reminder_at, first_search_at,
                       first_project_at, first_template_at
                FROM onboarding_progress
                WHERE user_id = :uid
            """),
            {"uid": user["id"]}
        )
        row = r.fetchone()

        if not row:
            # Create initial onboarding record
            await db.execute(
                text("""
                    INSERT INTO onboarding_progress (user_id)
                    VALUES (:uid)
                """),
                {"uid": user["id"]}
            )
            await db.commit()

            return {
                "wizard_completed": False,
                "wizard_skipped": False,
                "checklist_items": {
                    "create_first_note": False,
                    "set_reminder": False,
                    "try_search": False,
                    "connect_telegram": False,
                    "create_project": False,
                    "use_template": False,
                    "complete_conversation": False
                },
                "checklist_completed_count": 0,
                "checklist_total": 7,
                "checklist_dismissed": False,
                "onboarding_completed": False,
                "milestones": {}
            }

        return {
            "wizard_completed": row[0],
            "wizard_completed_at": str(row[1])[:19] if row[1] else None,
            "wizard_skipped": row[2],
            "checklist_items": row[3],
            "checklist_completed_count": row[4],
            "checklist_total": row[5],
            "checklist_dismissed": row[6],
            "onboarding_completed": row[7],
            "onboarding_completed_at": str(row[8])[:19] if row[8] else None,
            "milestones": {
                "first_note_at": str(row[9])[:19] if row[9] else None,
                "first_reminder_at": str(row[10])[:19] if row[10] else None,
                "first_search_at": str(row[11])[:19] if row[11] else None,
                "first_project_at": str(row[12])[:19] if row[12] else None,
                "first_template_at": str(row[13])[:19] if row[13] else None
            }
        }


@router.post("/wizard/complete", dependencies=[Depends(require_csrf)])
async def complete_wizard(request: Request, body: dict, user: dict = Depends(resolve_user)):
    """Mark onboarding wizard as completed or skipped.

    Body:
        skipped: Boolean indicating if wizard was skipped (default false)
    """
    skipped = body.get("skipped", False)

    async with async_session_factory() as db:
        # Ensure onboarding record exists
        await db.execute(
            text("""
                INSERT INTO onboarding_progress (user_id, wizard_completed, wizard_skipped, wizard_completed_at)
                VALUES (:uid, :completed, :skipped, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    wizard_completed = :completed,
                    wizard_skipped = :skipped,
                    wizard_completed_at = NOW(),
                    updated_at = NOW()
            """),
            {"uid": user["id"], "completed": not skipped, "skipped": skipped}
        )
        await db.commit()

        return {"success": True, "wizard_completed": not skipped, "wizard_skipped": skipped}


@router.post("/checklist/{item}", dependencies=[Depends(require_csrf)])
async def update_checklist_item(
    request: Request,
    item: str,
    body: dict,
    user: dict = Depends(resolve_user)
):
    """Update a checklist item status.

    Path params:
        item: Checklist item key (create_first_note, set_reminder, etc.)

    Body:
        completed: Boolean (default true)
    """
    valid_items = {
        "create_first_note", "set_reminder", "try_search",
        "connect_telegram", "create_project", "use_template", "complete_conversation"
    }

    if item not in valid_items:
        raise HTTPException(400, f"Invalid checklist item. Must be one of: {', '.join(valid_items)}")

    completed = body.get("completed", True)

    async with async_session_factory() as db:
        # Ensure onboarding record exists
        await db.execute(
            text("INSERT INTO onboarding_progress (user_id) VALUES (:uid) ON CONFLICT (user_id) DO NOTHING"),
            {"uid": user["id"]}
        )

        # Update checklist item
        await db.execute(
            text(f"""
                UPDATE onboarding_progress
                SET checklist_items = jsonb_set(
                    checklist_items,
                    '{{{item}}}',
                    to_jsonb(:completed)
                ),
                checklist_completed_count = (
                    SELECT COUNT(*)
                    FROM jsonb_each(
                        jsonb_set(checklist_items, '{{{item}}}', to_jsonb(:completed))
                    )
                    WHERE value::text = 'true'
                ),
                updated_at = NOW()
                WHERE user_id = :uid
            """),
            {"uid": user["id"], "completed": completed}
        )

        # Update milestone timestamp if applicable
        milestone_map = {
            "create_first_note": "first_note_at",
            "set_reminder": "first_reminder_at",
            "try_search": "first_search_at",
            "create_project": "first_project_at",
            "use_template": "first_template_at"
        }

        if item in milestone_map and completed:
            milestone_field = milestone_map[item]
            await db.execute(
                text(f"""
                    UPDATE onboarding_progress
                    SET {milestone_field} = COALESCE({milestone_field}, NOW())
                    WHERE user_id = :uid
                """),
                {"uid": user["id"]}
            )

        await db.commit()

        return {"success": True, "item": item, "completed": completed}


@router.post("/checklist/dismiss", dependencies=[Depends(require_csrf)])
async def dismiss_checklist(request: Request, user: dict = Depends(resolve_user)):
    """Dismiss the onboarding checklist."""
    async with async_session_factory() as db:
        await db.execute(
            text("""
                UPDATE onboarding_progress
                SET checklist_dismissed = true, updated_at = NOW()
                WHERE user_id = :uid
            """),
            {"uid": user["id"]}
        )
        await db.commit()

        return {"success": True}


@router.post("/complete", dependencies=[Depends(require_csrf)])
async def complete_onboarding(request: Request, user: dict = Depends(resolve_user)):
    """Mark entire onboarding as completed."""
    async with async_session_factory() as db:
        await db.execute(
            text("""
                UPDATE onboarding_progress
                SET onboarding_completed = true,
                    onboarding_completed_at = NOW(),
                    updated_at = NOW()
                WHERE user_id = :uid
            """),
            {"uid": user["id"]}
        )
        await db.commit()

        return {"success": True}


# =============================================================================
# TUTORIAL PROGRESS
# =============================================================================

@router.get("/tutorials/{tutorial_id}")
async def get_tutorial_progress(tutorial_id: str, user: dict = Depends(resolve_user)):
    """Get progress for a specific tutorial."""
    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT current_step, total_steps, completed, skipped,
                       steps_completed, started_at, completed_at, last_activity_at
                FROM tutorial_progress
                WHERE user_id = :uid AND tutorial_id = :tid
            """),
            {"uid": user["id"], "tid": tutorial_id}
        )
        row = r.fetchone()

        if not row:
            return {
                "tutorial_id": tutorial_id,
                "current_step": 0,
                "total_steps": 0,
                "completed": False,
                "skipped": False,
                "steps_completed": [],
                "started": False
            }

        return {
            "tutorial_id": tutorial_id,
            "current_step": row[0],
            "total_steps": row[1],
            "completed": row[2],
            "skipped": row[3],
            "steps_completed": row[4] or [],
            "started_at": str(row[5])[:19] if row[5] else None,
            "completed_at": str(row[6])[:19] if row[6] else None,
            "last_activity_at": str(row[7])[:19] if row[7] else None,
            "started": True
        }


@router.post("/tutorials/{tutorial_id}/step", dependencies=[Depends(require_csrf)])
async def update_tutorial_step(
    request: Request,
    tutorial_id: str,
    body: dict,
    user: dict = Depends(resolve_user)
):
    """Update tutorial progress to a specific step.

    Body:
        current_step: Current step number
        total_steps: Total steps in tutorial
        completed: Whether tutorial is completed
        skipped: Whether tutorial was skipped
    """
    current_step = body.get("current_step", 0)
    total_steps = body.get("total_steps", 1)
    completed = body.get("completed", False)
    skipped = body.get("skipped", False)

    async with async_session_factory() as db:
        await db.execute(
            text("""
                INSERT INTO tutorial_progress
                (user_id, tutorial_id, current_step, total_steps, completed, skipped, last_activity_at)
                VALUES (:uid, :tid, :step, :total, :completed, :skipped, NOW())
                ON CONFLICT (user_id, tutorial_id) DO UPDATE SET
                    current_step = :step,
                    total_steps = :total,
                    completed = :completed,
                    skipped = :skipped,
                    completed_at = CASE WHEN :completed OR :skipped THEN NOW() ELSE tutorial_progress.completed_at END,
                    last_activity_at = NOW()
            """),
            {
                "uid": user["id"],
                "tid": tutorial_id,
                "step": current_step,
                "total": total_steps,
                "completed": completed,
                "skipped": skipped
            }
        )
        await db.commit()

        return {"success": True, "current_step": current_step, "completed": completed, "skipped": skipped}
