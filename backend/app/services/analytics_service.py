"""Analytics service for tracking user activity and generating insights.

Provides functionality for:
- Event tracking (messages, content creation, searches, etc.)
- Analytics aggregation (daily/weekly/monthly)
- Goal progress tracking
- Insight generation

Performance optimizations:
- TTL cache for analytics summaries (1 hour)
- Parallel query execution with asyncio.gather
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from cachetools import TTLCache
from app.database import async_session_factory

# TTL cache for analytics summaries (1 hour, max 200 users)
# Reduces DB load during frequent dashboard refreshes
_analytics_cache: TTLCache = TTLCache(maxsize=200, ttl=3600)


async def track_event(
    user_id: str,
    event_type: str,
    event_category: str,
    event_data: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """Track an analytics event for a user.

    Args:
        user_id: UUID of the user
        event_type: Specific event (e.g., 'note_created', 'search_query', 'message_sent')
        event_category: Category (message, content, search, navigation, engagement, system)
        event_data: Additional event metadata
        session_id: Session identifier
        ip_address: User IP address
        user_agent: User agent string
    """
    async with async_session_factory() as db:
        await db.execute(
            text("""
                INSERT INTO analytics_events
                (user_id, event_type, event_category, event_data, session_id, ip_address, user_agent)
                VALUES (:user_id, :event_type, :category, :data, :session_id, :ip, :ua)
            """),
            {
                "user_id": user_id,
                "event_type": event_type,
                "category": event_category,
                "data": event_data or {},
                "session_id": session_id,
                "ip": ip_address,
                "ua": user_agent
            }
        )
        await db.commit()


async def get_analytics_summary(user_id: str) -> Dict[str, Any]:
    """Get overall analytics summary for a user.

    Returns:
        Dictionary with lifetime stats and recent trends

    Performance:
        - Uses 1-hour TTL cache to reduce DB load
        - Parallel query execution with asyncio.gather (3x faster)
    """
    # Check cache first
    if user_id in _analytics_cache:
        return _analytics_cache[user_id]

    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    async def get_lifetime_stats():
        async with async_session_factory() as db:
            r = await db.execute(
                text("""
                    SELECT
                        COUNT(*) FILTER (WHERE event_category = 'content' AND event_type = 'note_created') as total_notes,
                        COUNT(*) FILTER (WHERE event_category = 'content' AND event_type = 'idea_created') as total_ideas,
                        COUNT(*) FILTER (WHERE event_category = 'content' AND event_type = 'project_created') as total_projects,
                        COUNT(*) FILTER (WHERE event_category = 'content' AND event_type = 'reminder_set') as total_reminders,
                        COUNT(*) FILTER (WHERE event_category = 'search') as total_searches,
                        COUNT(*) FILTER (WHERE event_category = 'message') as total_messages
                    FROM analytics_events
                    WHERE user_id = :uid
                """),
                {"uid": user_id}
            )
            return r.fetchone()

    async def get_month_stats():
        async with async_session_factory() as db:
            r = await db.execute(
                text("""
                    SELECT
                        COUNT(*) FILTER (WHERE event_category = 'content' AND event_type = 'note_created') as notes_this_month,
                        COUNT(*) FILTER (WHERE event_category = 'search') as searches_this_month,
                        COUNT(*) FILTER (WHERE event_category = 'message') as messages_this_month,
                        COUNT(*) FILTER (WHERE event_category = 'engagement' AND event_type = 'portal_login') as logins_this_month
                    FROM analytics_events
                    WHERE user_id = :uid AND created_at >= :start
                """),
                {"uid": user_id, "start": month_start}
            )
            return r.fetchone()

    async def get_active_goals():
        async with async_session_factory() as db:
            r = await db.execute(
                text("""
                    SELECT id, title, target_value, current_value, unit, period
                    FROM user_goals
                    WHERE user_id = :uid AND is_active = true
                    ORDER BY created_at DESC
                    LIMIT 5
                """),
                {"uid": user_id}
            )
            return [
                {
                    "id": str(row[0]),
                    "title": row[1],
                    "target": row[2],
                    "current": row[3],
                    "unit": row[4],
                    "period": row[5],
                    "progress_pct": round((row[3] / row[2] * 100) if row[2] > 0 else 0, 1)
                }
                for row in r.fetchall()
            ]

    # Execute all 3 queries in parallel (3x faster than sequential)
    lifetime, month, active_goals = await asyncio.gather(
        get_lifetime_stats(),
        get_month_stats(),
        get_active_goals(),
        return_exceptions=True
    )

    # Handle any query failures gracefully
    if isinstance(lifetime, Exception):
        lifetime = (0, 0, 0, 0, 0, 0)
    if isinstance(month, Exception):
        month = (0, 0, 0, 0)
    if isinstance(active_goals, Exception):
        active_goals = []

    result = {
        "lifetime": {
            "notes": lifetime[0] or 0,
            "ideas": lifetime[1] or 0,
            "projects": lifetime[2] or 0,
            "reminders": lifetime[3] or 0,
            "searches": lifetime[4] or 0,
            "messages": lifetime[5] or 0
        },
        "this_month": {
            "notes": month[0] or 0,
            "searches": month[1] or 0,
            "messages": month[2] or 0,
            "logins": month[3] or 0
        },
        "active_goals": active_goals
    }

    # Cache the result
    _analytics_cache[user_id] = result
    return result


async def get_daily_analytics(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get daily analytics for the past N days.

    Args:
        user_id: User UUID
        days: Number of days to retrieve (default 30)

    Returns:
        List of daily analytics dictionaries
    """
    start_date = datetime.now() - timedelta(days=days)

    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) FILTER (WHERE event_type = 'note_created') as notes,
                    COUNT(*) FILTER (WHERE event_type = 'idea_created') as ideas,
                    COUNT(*) FILTER (WHERE event_type = 'project_created') as projects,
                    COUNT(*) FILTER (WHERE event_category = 'search') as searches,
                    COUNT(*) FILTER (WHERE event_category = 'message') as messages,
                    COUNT(DISTINCT session_id) as sessions
                FROM analytics_events
                WHERE user_id = :uid AND created_at >= :start
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """),
            {"uid": user_id, "start": start_date}
        )

        return [
            {
                "date": str(row[0]),
                "notes": row[1],
                "ideas": row[2],
                "projects": row[3],
                "searches": row[4],
                "messages": row[5],
                "sessions": row[6]
            }
            for row in r.fetchall()
        ]


async def get_weekly_analytics(user_id: str, weeks: int = 12) -> List[Dict[str, Any]]:
    """Get weekly analytics for the past N weeks.

    Args:
        user_id: User UUID
        weeks: Number of weeks to retrieve (default 12)

    Returns:
        List of weekly analytics dictionaries
    """
    start_date = datetime.now() - timedelta(weeks=weeks)

    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                SELECT
                    DATE_TRUNC('week', created_at) as week_start,
                    COUNT(*) FILTER (WHERE event_type = 'note_created') as notes,
                    COUNT(*) FILTER (WHERE event_type = 'idea_created') as ideas,
                    COUNT(*) FILTER (WHERE event_type = 'project_created') as projects,
                    COUNT(*) FILTER (WHERE event_category = 'search') as searches,
                    COUNT(*) FILTER (WHERE event_category = 'message') as messages,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    COUNT(DISTINCT session_id) as sessions
                FROM analytics_events
                WHERE user_id = :uid AND created_at >= :start
                GROUP BY DATE_TRUNC('week', created_at)
                ORDER BY week_start DESC
            """),
            {"uid": user_id, "start": start_date}
        )

        return [
            {
                "week_start": str(row[0])[:10],
                "notes": row[1],
                "ideas": row[2],
                "projects": row[3],
                "searches": row[4],
                "messages": row[5],
                "active_days": row[6],
                "sessions": row[7]
            }
            for row in r.fetchall()
        ]


async def create_goal(
    user_id: str,
    goal_type: str,
    title: str,
    target_value: int,
    period: str,
    description: str = "",
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a new user goal.

    Args:
        user_id: User UUID
        goal_type: Type of goal (weekly_notes, monthly_searches, etc.)
        title: Goal title
        target_value: Target value to reach
        period: Period (daily, weekly, monthly, yearly, custom)
        description: Optional description
        end_date: Optional end date

    Returns:
        Created goal dictionary
    """
    async with async_session_factory() as db:
        r = await db.execute(
            text("""
                INSERT INTO user_goals
                (user_id, goal_type, title, description, target_value, period, end_date)
                VALUES (:uid, :type, :title, :desc, :target, :period, :end_date)
                RETURNING id, created_at
            """),
            {
                "uid": user_id,
                "type": goal_type,
                "title": title,
                "desc": description,
                "target": target_value,
                "period": period,
                "end_date": end_date
            }
        )
        await db.commit()
        row = r.fetchone()

        return {
            "id": str(row[0]),
            "title": title,
            "target_value": target_value,
            "current_value": 0,
            "period": period,
            "created_at": str(row[1])[:19]
        }


async def update_goal_progress(user_id: str, goal_id: str, new_value: int) -> bool:
    """Update the current value of a goal.

    Args:
        user_id: User UUID
        goal_id: Goal UUID
        new_value: New current value

    Returns:
        True if updated successfully
    """
    async with async_session_factory() as db:
        # Check if goal reached target
        check_r = await db.execute(
            text("""
                SELECT target_value FROM user_goals
                WHERE id = :gid AND user_id = :uid
            """),
            {"gid": goal_id, "uid": user_id}
        )
        target_row = check_r.fetchone()

        if not target_row:
            return False

        target = target_row[0]
        completed_at = datetime.now() if new_value >= target else None

        await db.execute(
            text("""
                UPDATE user_goals
                SET current_value = :val,
                    completed_at = :completed,
                    is_active = CASE WHEN :val >= target_value THEN false ELSE is_active END,
                    updated_at = NOW()
                WHERE id = :gid AND user_id = :uid
            """),
            {"val": new_value, "gid": goal_id, "uid": user_id, "completed": completed_at}
        )
        await db.commit()

        return True


async def get_feature_adoption(user_id: str) -> Dict[str, int]:
    """Get feature adoption metrics showing usage by feature category.

    Uses UNION ALL for single query execution instead of 6 subqueries.

    Args:
        user_id: User UUID

    Returns:
        Dictionary mapping feature names to usage counts
    """
    async with async_session_factory() as db:
        # Single query with UNION ALL - more efficient than 6 subqueries
        r = await db.execute(
            text("""
                SELECT 'notes' as feature, COUNT(*) as cnt
                FROM notes WHERE user_id::text = :uid
                UNION ALL
                SELECT 'ideas', COUNT(*)
                FROM ideas WHERE user_id::text = :uid
                UNION ALL
                SELECT 'projects', COUNT(*)
                FROM projects WHERE user_id::text = :uid
                UNION ALL
                SELECT 'reminders', COUNT(*)
                FROM reminders WHERE user_id::text = :uid
                UNION ALL
                SELECT 'events', COUNT(*)
                FROM scheduled_events WHERE user_id::text = :uid
                UNION ALL
                SELECT 'searches', COUNT(*)
                FROM analytics_events WHERE user_id::text = :uid AND event_category = 'search'
            """),
            {"uid": user_id}
        )

        result = {
            "notes": 0,
            "ideas": 0,
            "projects": 0,
            "reminders": 0,
            "events": 0,
            "searches": 0
        }
        for row in r.fetchall():
            result[row[0]] = row[1] or 0

        return result
