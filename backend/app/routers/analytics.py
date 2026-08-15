"""Analytics API endpoints for user insights and goal tracking.

Provides endpoints for:
- Analytics summary and historical data
- Daily/weekly/monthly breakdowns
- Goal creation and progress tracking
- Feature adoption metrics
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from datetime import datetime
from app.csrf import require_csrf
from app.services import analytics_service

router = APIRouter(prefix="/api/me/analytics", tags=["analytics"])


async def resolve_user(request: Request) -> dict:
    """Resolve user from session token with expiration validation.

    SECURITY: Uses dedicated session_token with expiration check.
    Supports both cookie and Authorization header for backward compatibility.
    """
    from sqlalchemy import text
    from app.database import async_session_factory

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
# ANALYTICS ENDPOINTS
# =============================================================================

@router.get("/summary")
async def get_summary(user: dict = Depends(resolve_user)):
    """Get overall analytics summary with lifetime and monthly stats."""
    summary = await analytics_service.get_analytics_summary(user["id"])
    return summary


@router.get("/daily")
async def get_daily(days: int = 30, user: dict = Depends(resolve_user)):
    """Get daily analytics for the past N days.

    Query params:
        days: Number of days to retrieve (default 30, max 365)
    """
    if days < 1 or days > 365:
        raise HTTPException(400, "Days must be between 1 and 365")

    daily_data = await analytics_service.get_daily_analytics(user["id"], days)
    return {"days": daily_data, "period_days": days}


@router.get("/weekly")
async def get_weekly(weeks: int = 12, user: dict = Depends(resolve_user)):
    """Get weekly analytics for the past N weeks.

    Query params:
        weeks: Number of weeks to retrieve (default 12, max 52)
    """
    if weeks < 1 or weeks > 52:
        raise HTTPException(400, "Weeks must be between 1 and 52")

    weekly_data = await analytics_service.get_weekly_analytics(user["id"], weeks)
    return {"weeks": weekly_data, "period_weeks": weeks}


@router.get("/feature-adoption")
async def get_feature_adoption(user: dict = Depends(resolve_user)):
    """Get feature adoption metrics showing usage by feature category."""
    adoption = await analytics_service.get_feature_adoption(user["id"])
    return {"features": adoption}


# =============================================================================
# GOALS ENDPOINTS
# =============================================================================

@router.get("/goals")
async def list_goals(user: dict = Depends(resolve_user)):
    """List all active goals for the user."""
    from sqlalchemy import text
    from app.database import async_session_factory

    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT id, title, description, goal_type, target_value, current_value,
                       unit, period, start_date, end_date, is_active, completed_at, created_at
                FROM user_goals
                WHERE user_id = :uid
                ORDER BY is_active DESC, created_at DESC
            """),
            {"uid": user["id"]}
        )

        goals = [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "goal_type": row[3],
                "target_value": row[4],
                "current_value": row[5],
                "unit": row[6],
                "period": row[7],
                "start_date": str(row[8])[:10] if row[8] else None,
                "end_date": str(row[9])[:10] if row[9] else None,
                "is_active": row[10],
                "completed_at": str(row[11])[:19] if row[11] else None,
                "created_at": str(row[12])[:19],
                "progress_pct": round((row[5] / row[4] * 100) if row[4] > 0 else 0, 1)
            }
            for row in r.fetchall()
        ]

        return {"goals": goals}


@router.post("/goals", dependencies=[Depends(require_csrf)])
async def create_goal(request: Request, body: dict, user: dict = Depends(resolve_user)):
    """Create a new goal.

    Body:
        title: Goal title (required)
        goal_type: Type (weekly_notes, monthly_searches, daily_engagement, custom)
        target_value: Target value to reach (required)
        period: Period (daily, weekly, monthly, yearly, custom)
        description: Optional description
        end_date: Optional end date (ISO format)
    """
    title = (body.get("title") or "").strip()
    goal_type = body.get("goal_type", "custom")
    target_value = body.get("target_value")
    period = body.get("period", "weekly")
    description = body.get("description", "")
    end_date_str = body.get("end_date")

    if not title:
        raise HTTPException(400, "Title required")
    if not target_value or target_value < 1:
        raise HTTPException(400, "Target value must be >= 1")

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(400, "Invalid end_date format")

    goal = await analytics_service.create_goal(
        user["id"],
        goal_type,
        title,
        target_value,
        period,
        description,
        end_date
    )

    return goal


@router.put("/goals/{goal_id}", dependencies=[Depends(require_csrf)])
async def update_goal_progress(
    request: Request,
    goal_id: str,
    body: dict,
    user: dict = Depends(resolve_user)
):
    """Update goal progress.

    Body:
        current_value: New current value
    """
    new_value = body.get("current_value")
    if new_value is None or new_value < 0:
        raise HTTPException(400, "current_value must be >= 0")

    success = await analytics_service.update_goal_progress(user["id"], goal_id, new_value)

    if not success:
        raise HTTPException(404, "Goal not found")

    return {"success": True, "current_value": new_value}


@router.delete("/goals/{goal_id}", dependencies=[Depends(require_csrf)])
async def delete_goal(request: Request, goal_id: str, user: dict = Depends(resolve_user)):
    """Delete (deactivate) a goal."""
    from sqlalchemy import text
    from app.database import async_session_factory

    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                UPDATE user_goals
                SET is_active = false, updated_at = NOW()
                WHERE id = :gid AND user_id = :uid
                RETURNING id
            """),
            {"gid": goal_id, "uid": user["id"]}
        )
        await db.commit()

        if not r.fetchone():
            raise HTTPException(404, "Goal not found")

        return {"success": True}


# =============================================================================
# EVENT TRACKING ENDPOINT (for frontend)
# =============================================================================

@router.post("/track", dependencies=[Depends(require_csrf)])
async def track_event(request: Request, body: dict, user: dict = Depends(resolve_user)):
    """Track a user event from the frontend.

    Body:
        event_type: Event type (e.g., 'page_view', 'button_click')
        event_category: Category (message, content, search, navigation, engagement, system)
        event_data: Optional additional data
    """
    event_type = body.get("event_type")
    event_category = body.get("event_category")
    event_data = body.get("event_data", {})

    if not event_type or not event_category:
        raise HTTPException(400, "event_type and event_category required")

    # Get session info from request
    session_id = request.cookies.get("portal_token", "")[:16]  # Truncate for privacy
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    await analytics_service.track_event(
        user["id"],
        event_type,
        event_category,
        event_data,
        session_id,
        ip_address,
        user_agent
    )

    return {"success": True}
