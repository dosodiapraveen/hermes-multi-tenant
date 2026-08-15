-- Migration 008: Onboarding and Tutorial System
-- First-time user experience, interactive tutorials, progress tracking

-- =============================================================================
-- ONBOARDING TABLES
-- =============================================================================

-- Onboarding progress tracking
CREATE TABLE IF NOT EXISTS onboarding_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,

    -- Wizard completion
    wizard_completed BOOLEAN DEFAULT FALSE,
    wizard_completed_at TIMESTAMPTZ,
    wizard_skipped BOOLEAN DEFAULT FALSE,

    -- Checklist items (JSON for flexibility)
    checklist_items JSONB DEFAULT '{
        "create_first_note": false,
        "set_reminder": false,
        "try_search": false,
        "connect_telegram": false,
        "create_project": false,
        "use_template": false,
        "complete_conversation": false
    }',

    checklist_completed_count INTEGER DEFAULT 0,
    checklist_total INTEGER DEFAULT 7,
    checklist_dismissed BOOLEAN DEFAULT FALSE,

    -- Progress milestones
    first_note_at TIMESTAMPTZ,
    first_reminder_at TIMESTAMPTZ,
    first_search_at TIMESTAMPTZ,
    first_project_at TIMESTAMPTZ,
    first_template_at TIMESTAMPTZ,

    -- Overall completion
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_onboarding_user ON onboarding_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_completed ON onboarding_progress(onboarding_completed);

-- Tutorial progress (for interactive tutorials)
CREATE TABLE IF NOT EXISTS tutorial_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    tutorial_id TEXT NOT NULL,

    -- Progress tracking
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    skipped BOOLEAN DEFAULT FALSE,

    -- Step completion tracking
    steps_completed JSONB DEFAULT '[]',

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, tutorial_id)
);

CREATE INDEX IF NOT EXISTS idx_tutorial_progress_user ON tutorial_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_tutorial_progress_tutorial ON tutorial_progress(tutorial_id);

-- Help center content views (track what users search for)
CREATE TABLE IF NOT EXISTS help_center_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('search','view_faq','view_video','view_usecase','feedback')),
    content_id TEXT,
    search_query TEXT,
    helpful BOOLEAN,
    feedback_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_help_activity_user ON help_center_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_help_activity_type ON help_center_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_help_activity_created ON help_center_activity(created_at DESC);

-- Record migration
INSERT INTO schema_migrations (version) VALUES ('008_onboarding_and_examples')
ON CONFLICT (version) DO NOTHING;
