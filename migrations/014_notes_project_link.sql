-- Project-scoped notes: explicitly link a note to a project (Ellie's request:
-- notes tagged to a project should group under that project, not just the Notes list).
ALTER TABLE notes ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES projects(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_notes_project ON notes(project_id);

-- Backfill: associate existing notes whose category matches a project title
-- (the old loose tagging) onto their matching project.
UPDATE notes n
SET project_id = p.id
FROM projects p
WHERE n.project_id IS NULL
  AND p.user_id = n.user_id
  AND LOWER(TRIM(COALESCE(n.category, ''))) = LOWER(TRIM(p.title));
