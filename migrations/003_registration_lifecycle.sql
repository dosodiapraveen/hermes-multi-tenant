-- Migration: Registration request lifecycle guards
-- 1) Expire stale requests (default 72h) so the admin queue can't grow forever
-- 2) Track per-email attempts so an address can't spam the queue
-- Date: 2026-08-13

-- Request becomes "expired" (void) after expires_at. New registrations for the
-- same email are allowed once an old request has passed this point.
ALTER TABLE registration_requests
  ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '72 hours');

-- Hint for periodic cleanup queries.
CREATE INDEX IF NOT EXISTS idx_regreq_expires ON registration_requests(expires_at);
CREATE INDEX IF NOT EXISTS idx_regreq_created ON registration_requests(email, created_at);
