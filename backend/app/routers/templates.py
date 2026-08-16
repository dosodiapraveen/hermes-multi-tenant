"""Templates API endpoints for project, workflow, and conversation templates.

Provides endpoints for:
- Browsing project templates
- Browsing workflow templates
- Browsing conversation examples
- Applying templates to create new content
- Template usage tracking
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from typing import Optional
from app.database import async_session_factory
from app.csrf import require_csrf

router = APIRouter(prefix="/api/templates", tags=["templates"])


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


# =============================================================================
# PROJECT TEMPLATES
# =============================================================================

@router.get("/projects")
async def list_project_templates(
    category: Optional[str] = None,
    industry: Optional[str] = None
):
    """List all project templates with optional filtering.

    Query params:
        category: Filter by category (productivity, development, business, personal, education)
        industry: Filter by industry (general, students, developers, entrepreneurs)
    """
    async with async_session_factory() as db:
        conditions = ["is_active = true"]
        params = {}

        if category:
            conditions.append("category = :cat")
            params["cat"] = category

        if industry:
            conditions.append("industry = :ind")
            params["ind"] = industry

        where_clause = " AND ".join(conditions)

        r = await db.execute(
            text(f"""
                SELECT id, title, description, category, industry, template_data,
                       default_tasks, default_research_topics, icon, color, tags,
                       is_featured, usage_count
                FROM project_templates
                WHERE {where_clause}
                ORDER BY is_featured DESC, usage_count DESC, title ASC
            """),
            params
        )

        templates = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "category": row[3],
                "industry": row[4],
                "template_data": row[5],
                "default_tasks": row[6] or [],
                "default_research_topics": row[7] or [],
                "icon": row[8],
                "color": row[9],
                "tags": row[10] or [],
                "is_featured": row[11],
                "usage_count": row[12]
            }
            for row in r.fetchall()
        ]

        return {"templates": templates}


@router.post("/projects/{template_id}/apply", dependencies=[Depends(require_csrf)])
async def apply_project_template(
    request: Request,
    template_id: str,
    body: dict,
    user: dict = Depends(resolve_user)
):
    """Apply a project template to create a new project.

    Body:
        title: Optional custom title (defaults to template title)
        description: Optional custom description
    """
    async with async_session_factory() as db:
        # Get template
        t_r = await db.execute(
            text("""
                SELECT title, description, template_data, default_tasks, default_research_topics
                FROM project_templates
                WHERE id = :tid AND is_active = true
            """),
            {"tid": template_id}
        )
        template = t_r.fetchone()

        if not template:
            raise HTTPException(404, "Template not found")

        # Create project from template
        title = body.get("title") or template[0]
        description = body.get("description") or template[1]

        p_r = await db.execute(
            text("""
                INSERT INTO projects (user_id, title, description, status)
                VALUES (:uid, :title, :desc, 'active')
                RETURNING id, created_at
            """),
            {"uid": user["id"], "title": title, "desc": description}
        )
        project_row = p_r.fetchone()
        project_id = str(project_row[0])

        # Add default research topics if any (batch INSERT for efficiency)
        research_topics = template[4] or []
        if research_topics:
            topics_to_insert = research_topics[:5]  # Limit to 5
            # Build batch INSERT with multiple VALUES
            values_clauses = ", ".join(
                f"(:pid, :title_{i}, '')" for i in range(len(topics_to_insert))
            )
            params = {"pid": project_id}
            for i, topic in enumerate(topics_to_insert):
                params[f"title_{i}"] = topic
            await db.execute(
                text(f"""
                    INSERT INTO project_research (project_id, title, content)
                    VALUES {values_clauses}
                """),
                params
            )

        # Track template usage and increment count atomically
        await db.execute(
            text("""
                WITH usage_insert AS (
                    INSERT INTO template_usage (user_id, template_type, template_id, created_item_id)
                    VALUES (:uid, 'project', :tid, :pid)
                    RETURNING template_id
                )
                UPDATE project_templates
                SET usage_count = usage_count + 1
                WHERE id = (SELECT template_id FROM usage_insert)
            """),
            {"uid": user["id"], "tid": template_id, "pid": project_id}
        )

        await db.commit()

        return {
            "success": True,
            "project_id": project_id,
            "title": title,
            "description": description,
            "research_topics_added": len(research_topics),
            "created_at": str(project_row[1])[:19]
        }


# =============================================================================
# WORKFLOW TEMPLATES
# =============================================================================

@router.get("/workflows")
async def list_workflow_templates(workflow_type: Optional[str] = None):
    """List all workflow templates with optional filtering.

    Query params:
        workflow_type: Filter by type (standup, review, brainstorm, planning, retrospective, custom)
    """
    async with async_session_factory() as db:
        conditions = ["is_active = true"]
        params = {}

        if workflow_type:
            conditions.append("workflow_type = :wtype")
            params["wtype"] = workflow_type

        where_clause = " AND ".join(conditions)

        r = await db.execute(
            text(f"""
                SELECT id, title, description, workflow_type, steps, prompts,
                       expected_duration_minutes, icon, difficulty, tags,
                       is_featured, usage_count
                FROM workflow_templates
                WHERE {where_clause}
                ORDER BY is_featured DESC, usage_count DESC, title ASC
            """),
            params
        )

        workflows = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "workflow_type": row[3],
                "steps": row[4] or [],
                "prompts": row[5] or [],
                "expected_duration_minutes": row[6],
                "icon": row[7],
                "difficulty": row[8],
                "tags": row[9] or [],
                "is_featured": row[10],
                "usage_count": row[11]
            }
            for row in r.fetchall()
        ]

        return {"workflows": workflows}


@router.post("/workflows/{workflow_id}/track", dependencies=[Depends(require_csrf)])
async def track_workflow_usage(
    request: Request,
    workflow_id: str,
    body: dict,
    user: dict = Depends(resolve_user)
):
    """Track usage of a workflow template.

    Body:
        completed: Whether the workflow was completed
        feedback_rating: Optional rating (1-5)
        feedback_text: Optional feedback text
    """
    async with async_session_factory() as db:
        # Verify workflow exists
        w_r = await db.execute(
            text("SELECT id FROM workflow_templates WHERE id = :wid AND is_active = true"),
            {"wid": workflow_id}
        )

        if not w_r.fetchone():
            raise HTTPException(404, "Workflow not found")

        # Track usage
        await db.execute(
            text("""
                INSERT INTO template_usage
                (user_id, template_type, template_id, completed, feedback_rating, feedback_text)
                VALUES (:uid, 'workflow', :wid, :completed, :rating, :feedback)
            """),
            {
                "uid": user["id"],
                "wid": workflow_id,
                "completed": body.get("completed", False),
                "rating": body.get("feedback_rating"),
                "feedback": body.get("feedback_text")
            }
        )

        # Increment usage count
        await db.execute(
            text("UPDATE workflow_templates SET usage_count = usage_count + 1 WHERE id = :wid"),
            {"wid": workflow_id}
        )

        await db.commit()

        return {"success": True}


# =============================================================================
# CONVERSATION EXAMPLES
# =============================================================================

@router.get("/conversations")
async def list_conversation_examples(category: Optional[str] = None):
    """List all conversation examples with optional filtering.

    Query params:
        category: Filter by category (brainstorm, planning, learning, reflection, research, creative)
    """
    async with async_session_factory() as db:
        conditions = ["is_active = true"]
        params = {}

        if category:
            conditions.append("category = :cat")
            params["cat"] = category

        where_clause = " AND ".join(conditions)

        r = await db.execute(
            text(f"""
                SELECT id, title, description, category, starter_prompt,
                       example_response, follow_up_prompts, icon, difficulty,
                       tags, is_featured, usage_count
                FROM conversation_examples
                WHERE {where_clause}
                ORDER BY is_featured DESC, usage_count DESC, title ASC
            """),
            params
        )

        examples = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "category": row[3],
                "starter_prompt": row[4],
                "example_response": row[5],
                "follow_up_prompts": row[6] or [],
                "icon": row[7],
                "difficulty": row[8],
                "tags": row[9] or [],
                "is_featured": row[10],
                "usage_count": row[11]
            }
            for row in r.fetchall()
        ]

        return {"examples": examples}


@router.post("/conversations/{example_id}/track", dependencies=[Depends(require_csrf)])
async def track_conversation_usage(
    request: Request,
    example_id: str,
    user: dict = Depends(resolve_user)
):
    """Track usage of a conversation example."""
    async with async_session_factory() as db:
        # Verify example exists
        e_r = await db.execute(
            text("SELECT id FROM conversation_examples WHERE id = :eid AND is_active = true"),
            {"eid": example_id}
        )

        if not e_r.fetchone():
            raise HTTPException(404, "Example not found")

        # Track usage
        await db.execute(
            text("""
                INSERT INTO template_usage (user_id, template_type, template_id)
                VALUES (:uid, 'conversation', :eid)
            """),
            {"uid": user["id"], "eid": example_id}
        )

        # Increment usage count
        await db.execute(
            text("UPDATE conversation_examples SET usage_count = usage_count + 1 WHERE id = :eid"),
            {"eid": example_id}
        )

        await db.commit()

        return {"success": True}


# =============================================================================
# USER TEMPLATE USAGE
# =============================================================================

@router.get("/usage")
async def get_template_usage(user: dict = Depends(resolve_user)):
    """Get user's template usage history."""
    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT template_type, template_id, created_item_id, completed,
                       feedback_rating, feedback_text, created_at
                FROM template_usage
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT 50
            """),
            {"uid": user["id"]}
        )

        usage = [
            {
                "template_type": row[0],
                "template_id": str(row[1]),
                "created_item_id": str(row[2]) if row[2] else None,
                "completed": row[3],
                "feedback_rating": row[4],
                "feedback_text": row[5],
                "created_at": str(row[6])[:19]
            }
            for row in r.fetchall()
        ]

        return {"usage": usage}
