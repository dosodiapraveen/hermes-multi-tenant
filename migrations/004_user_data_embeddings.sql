-- Migration: Semantic search embeddings for user data.
-- Stores one embedding (JSONB) per user content blob. Cosine similarity is
-- computed in Python (per-user data is small) — no pgvector required.
-- Date: 2026-08-13

CREATE TABLE IF NOT EXISTS user_data_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,          -- note | project | research | idea | reminder | vault
    source_id TEXT NOT NULL,            -- id of the source row (or file name for vault)
    title TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    embedding JSONB NOT NULL,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_emb_user ON user_data_embeddings(user_id);
