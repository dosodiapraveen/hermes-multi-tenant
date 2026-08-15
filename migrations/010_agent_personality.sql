-- Agent personality (SOUL.md) — user-editable identity/tone file injected into the agent prompt
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS personality TEXT;
