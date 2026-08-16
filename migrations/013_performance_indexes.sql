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

-- Analyze tables to update statistics after adding indexes
ANALYZE user_accounts;
ANALYZE reminders;
ANALYZE activity_logs;
ANALYZE user_profiles;
ANALYZE notes;
ANALYZE projects;
ANALYZE ideas;
ANALYZE user_data_embeddings;
