-- Long-lived per-user agent token for the Hermes MCP bridge (Option 1).
-- Separate from the short-lived session_token; independently rotatable.
ALTER TABLE user_accounts ADD COLUMN IF NOT EXISTS agent_token TEXT;
