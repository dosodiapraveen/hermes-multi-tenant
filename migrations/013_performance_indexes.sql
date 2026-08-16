-- Performance indexes for faster queries
-- Addresses slow user resolution and common query patterns

-- Index for session token lookups (used on every portal API request)
CREATE INDEX IF NOT EXISTS idx_user_accounts_session_token
ON user_accounts(session_token)
WHERE session_token IS NOT NULL;

-- Index for agent token lookups (used for API authentication)
CREATE INDEX IF NOT EXISTS idx_user_accounts_agent_token
ON user_accounts(agent_token)
WHERE agent_token IS NOT NULL;

-- Composite index for reminder polling (user + remind_at for scheduled checks)
CREATE INDEX IF NOT EXISTS idx_reminders_user_remind_at
ON reminders(user_id, remind_at)
WHERE done = false AND remind_at IS NOT NULL;

-- Composite index for activity logs queries (user + time range)
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_created
ON activity_logs(user_id, created_at DESC);

-- Index for user profile phone number lookups (Telegram webhook)
CREATE INDEX IF NOT EXISTS idx_user_profiles_phone_number
ON user_profiles(phone_number)
WHERE phone_number IS NOT NULL;

-- Index for notes by user (dashboard queries)
CREATE INDEX IF NOT EXISTS idx_notes_user_updated
ON notes(user_id, updated_at DESC);

-- Index for projects by user (dashboard queries)
CREATE INDEX IF NOT EXISTS idx_projects_user_updated
ON projects(user_id, updated_at DESC);

-- Index for ideas by user (dashboard queries)
CREATE INDEX IF NOT EXISTS idx_ideas_user_updated
ON ideas(user_id, updated_at DESC);

-- Index for user data embeddings search
CREATE INDEX IF NOT EXISTS idx_user_data_embeddings_user
ON user_data_embeddings(user_id);

-- Index for analytics events (frequent filtering by category/type)
CREATE INDEX IF NOT EXISTS idx_analytics_events_category_type
ON analytics_events(event_category, event_type, user_id);

-- Index for template usage queries
CREATE INDEX IF NOT EXISTS idx_template_usage_user_type
ON template_usage(user_id, template_type);

-- Index for registration requests status lookup
CREATE INDEX IF NOT EXISTS idx_registration_requests_status
ON registration_requests(status)
WHERE status IN ('pending', 'approved');

-- Index for scheduled events by user (calendar queries)
CREATE INDEX IF NOT EXISTS idx_scheduled_events_user
ON scheduled_events(user_id, event_start);

-- Index for background jobs by user
CREATE INDEX IF NOT EXISTS idx_background_jobs_user
ON background_jobs(user_id);

-- Partial index for active scheduled events
CREATE INDEX IF NOT EXISTS idx_scheduled_events_upcoming
ON scheduled_events(user_id, event_start)
WHERE event_start >= CURRENT_DATE;

-- Analyze tables to update statistics after adding indexes
ANALYZE user_accounts;
ANALYZE reminders;
ANALYZE activity_logs;
ANALYZE user_profiles;
ANALYZE notes;
ANALYZE projects;
ANALYZE ideas;
ANALYZE user_data_embeddings;
ANALYZE analytics_events;
ANALYZE template_usage;
ANALYZE registration_requests;
ANALYZE scheduled_events;
ANALYZE background_jobs;
