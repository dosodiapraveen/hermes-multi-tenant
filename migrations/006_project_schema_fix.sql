-- Fix projects schema (stray reminder columns) + ensure updated_at on reminders
ALTER TABLE projects DROP COLUMN IF EXISTS remind_at;
ALTER TABLE projects DROP COLUMN IF EXISTS done;
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
