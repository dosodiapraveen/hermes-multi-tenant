-- Migration: Admin-approval registration flow
-- Stores user registration requests until an admin approves (assigns an agent)
-- or rejects them. Email must be verified before admin can approve.
-- Date: 2026-08-13

CREATE TABLE IF NOT EXISTS registration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    agent_name TEXT DEFAULT '',
    use_case TEXT DEFAULT '',
    plan_requested TEXT NOT NULL DEFAULT 'pro',
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected')),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token TEXT,
    verification_expires TIMESTAMPTZ,
    -- Fields populated on approval:
    assigned_profile_id UUID,
    activation_token TEXT,
    activation_expires TIMESTAMPTZ,
    review_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_regreq_status ON registration_requests(status);
CREATE INDEX IF NOT EXISTS idx_regreq_email ON registration_requests(email);
