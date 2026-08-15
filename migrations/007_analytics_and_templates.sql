-- Migration 007: Analytics and Templates Infrastructure
-- User analytics, event tracking, conversation insights, templates system

-- =============================================================================
-- ANALYTICS TABLES
-- =============================================================================

-- User analytics aggregates (daily/weekly/monthly)
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    period_type TEXT NOT NULL CHECK (period_type IN ('daily','weekly','monthly')),
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Message & conversation metrics
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0,
    conversations_started INTEGER DEFAULT 0,
    avg_response_time_seconds DECIMAL(10,2),

    -- Content creation metrics
    notes_created INTEGER DEFAULT 0,
    ideas_created INTEGER DEFAULT 0,
    projects_created INTEGER DEFAULT 0,
    reminders_set INTEGER DEFAULT 0,
    events_scheduled INTEGER DEFAULT 0,

    -- Search & usage metrics
    search_queries INTEGER DEFAULT 0,
    vault_searches INTEGER DEFAULT 0,
    portal_logins INTEGER DEFAULT 0,
    feature_usage JSONB DEFAULT '{}',

    -- Engagement metrics
    active_days INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    total_time_minutes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, period_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_user_analytics_user ON user_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analytics_period ON user_analytics(period_type, period_start DESC);

-- Fine-grained analytics events log
CREATE TABLE IF NOT EXISTS analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL CHECK (event_category IN ('message','content','search','navigation','engagement','system')),
    event_data JSONB DEFAULT '{}',
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_user ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_category ON analytics_events(event_category);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created ON analytics_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session ON analytics_events(session_id);

-- AI conversation insights
CREATE TABLE IF NOT EXISTS conversation_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Topic analysis
    top_topics JSONB DEFAULT '[]',
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    conversation_themes TEXT[],

    -- Patterns
    most_active_hour INTEGER,
    most_active_day TEXT,
    avg_message_length INTEGER,
    question_count INTEGER DEFAULT 0,

    -- AI metrics
    model_used TEXT,
    total_tokens INTEGER DEFAULT 0,

    insights_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_insights_user ON conversation_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_insights_period ON conversation_insights(period_start DESC);

-- User goals and progress tracking
CREATE TABLE IF NOT EXISTS user_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    goal_type TEXT NOT NULL CHECK (goal_type IN ('weekly_notes','monthly_searches','daily_engagement','custom')),
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'count',
    period TEXT NOT NULL CHECK (period IN ('daily','weekly','monthly','yearly','custom')),
    start_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_goals_user ON user_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_user_goals_active ON user_goals(is_active, end_date);

-- =============================================================================
-- TEMPLATES TABLES
-- =============================================================================

-- Project templates (reusable blueprints)
CREATE TABLE IF NOT EXISTS project_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('productivity','development','business','personal','education')),
    industry TEXT NOT NULL DEFAULT 'general',

    -- Template content
    template_data JSONB NOT NULL DEFAULT '{}',
    default_tasks TEXT[] DEFAULT '{}',
    default_research_topics TEXT[] DEFAULT '{}',

    -- Metadata
    icon TEXT DEFAULT '📋',
    color TEXT DEFAULT '#6C5CE7',
    tags TEXT[] DEFAULT '{}',

    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,

    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_templates_category ON project_templates(category);
CREATE INDEX IF NOT EXISTS idx_project_templates_active ON project_templates(is_active, is_featured);

-- Workflow templates (repeatable processes)
CREATE TABLE IF NOT EXISTS workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    workflow_type TEXT NOT NULL CHECK (workflow_type IN ('standup','review','brainstorm','planning','retrospective','custom')),

    -- Workflow structure
    steps JSONB NOT NULL DEFAULT '[]',
    prompts TEXT[] DEFAULT '{}',
    expected_duration_minutes INTEGER,

    -- Metadata
    icon TEXT DEFAULT '🔄',
    difficulty TEXT DEFAULT 'beginner' CHECK (difficulty IN ('beginner','intermediate','advanced')),
    tags TEXT[] DEFAULT '{}',

    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,

    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_templates_type ON workflow_templates(workflow_type);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_active ON workflow_templates(is_active, is_featured);

-- Conversation examples (starter prompts)
CREATE TABLE IF NOT EXISTS conversation_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('brainstorm','planning','learning','reflection','research','creative')),

    -- Example content
    starter_prompt TEXT NOT NULL,
    example_response TEXT,
    follow_up_prompts TEXT[] DEFAULT '{}',

    -- Metadata
    icon TEXT DEFAULT '💬',
    difficulty TEXT DEFAULT 'beginner' CHECK (difficulty IN ('beginner','intermediate','advanced')),
    tags TEXT[] DEFAULT '{}',

    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,

    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_examples_category ON conversation_examples(category);
CREATE INDEX IF NOT EXISTS idx_conversation_examples_active ON conversation_examples(is_active, is_featured);

-- Template usage tracking
CREATE TABLE IF NOT EXISTS template_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    template_type TEXT NOT NULL CHECK (template_type IN ('project','workflow','conversation')),
    template_id UUID NOT NULL,

    -- Usage metadata
    created_item_id UUID,
    completed BOOLEAN DEFAULT FALSE,
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_text TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_template_usage_user ON template_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_template_usage_template ON template_usage(template_type, template_id);
CREATE INDEX IF NOT EXISTS idx_template_usage_created ON template_usage(created_at DESC);

-- Record migration
INSERT INTO schema_migrations (version) VALUES ('007_analytics_and_templates')
ON CONFLICT (version) DO NOTHING;
