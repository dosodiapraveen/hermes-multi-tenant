-- Migration: Separate session tokens from verification tokens
-- Security fix: Use dedicated columns for different auth purposes
-- - verification_token: email verification only (24h expiry)
-- - reset_token: password reset only (1h expiry)
-- - session_token: login sessions with expiration (7 days default)
-- Date: 2026-08-13

-- Add dedicated session token columns to user_accounts
ALTER TABLE user_accounts
  ADD COLUMN IF NOT EXISTS session_token TEXT,
  ADD COLUMN IF NOT EXISTS session_expires TIMESTAMPTZ;

-- Add index for fast session lookup
CREATE INDEX IF NOT EXISTS idx_user_accounts_session
  ON user_accounts(session_token)
  WHERE session_token IS NOT NULL;

-- Clear any existing verification tokens being used as session tokens
-- (Forces all users to re-login, but necessary for security)
UPDATE user_accounts
SET verification_token = NULL
WHERE email_verified = true;

-- Add activation token for post-approval password setup flow
ALTER TABLE registration_requests
  ADD COLUMN IF NOT EXISTS setup_token TEXT,
  ADD COLUMN IF NOT EXISTS setup_token_expires TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_regreq_setup_token
  ON registration_requests(setup_token)
  WHERE setup_token IS NOT NULL;

-- Extend verification token expiry to match request lifecycle (72h)
-- This prevents the deadlock where verification expires before request
COMMENT ON COLUMN registration_requests.verification_expires IS
  'Verification link expires in 72 hours to match registration request lifecycle';
