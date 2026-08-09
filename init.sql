CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS invite_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT 'My Assistant',
    plan TEXT NOT NULL CHECK (plan IN ('trial','basic','pro','business','vip')),
    trial_days INTEGER DEFAULT 7,
    is_vip BOOLEAN DEFAULT FALSE,
    claimed_by UUID, claimed_at TIMESTAMPTZ, expires_at TIMESTAMPTZ,
    created_by TEXT NOT NULL DEFAULT 'admin',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id TEXT UNIQUE, phone_number TEXT UNIQUE,
    agent_name TEXT NOT NULL DEFAULT 'My Assistant',
    plan TEXT NOT NULL DEFAULT 'trial' CHECK (plan IN ('trial','basic','pro','business','vip')),
    is_vip BOOLEAN NOT NULL DEFAULT FALSE, trial_ends_at TIMESTAMPTZ,
    primary_model TEXT NOT NULL DEFAULT 'claude-sonnet-4-2026',
    backup_model TEXT NOT NULL DEFAULT 'accounts/fireworks/models/deepseek-v4',
    model_overridden_at TIMESTAMPTZ, is_active BOOLEAN NOT NULL DEFAULT TRUE,
    profile_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL CHECK (provider IN ('anthropic','openai','fireworks','google')),
    key_encrypted TEXT NOT NULL, key_prefix TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE, monthly_token_limit BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT, action TEXT NOT NULL,
    details JSONB DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invite_code ON invite_links(code);
CREATE INDEX IF NOT EXISTS idx_user_phone ON user_profiles(phone_number);
