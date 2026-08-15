-- One-time expiring dashboard access tokens for existing agents.
-- Admin generates a fresh random token per click; consumed on successful registration.
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS signup_token TEXT;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS signup_expires TIMESTAMPTZ;
