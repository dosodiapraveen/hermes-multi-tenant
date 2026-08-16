-- Per-user agent runtime selector: 'agent' (agent_manager, default/rollback) or 'hermes' (real Hermes runtime).
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS runtime TEXT NOT NULL DEFAULT 'agent';
