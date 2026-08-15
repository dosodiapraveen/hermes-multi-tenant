#!/bin/bash
# Robust idempotent DB migration runner.
# - Tracks applied migrations in `schema_migrations`.
# - Applies pending migrations in filename order, each inside a single transaction
#   (a failing migration rolls back and is NOT recorded).
# - Baselines legacy databases (schema applied via init.sql / old hard-coded runs)
#   when the tracking table is empty, so it doesn't re-run already-applied DDL.
set -euo pipefail
cd "$(dirname "$0")"

PSQL() { docker compose exec -T postgres psql -U hermes -d hermes -v ON_ERROR_STOP=1 "$@"; }

echo "Running database migrations..."

# 1) Ensure the tracking table exists
PSQL -c "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW());" >/dev/null

# 2) Baseline: if the tracking table is empty, the schema was applied via init.sql or an
#    older runner. Seed the current migration files as applied (safe: schema is present).
COUNT=$(PSQL -tAc "SELECT count(*) FROM schema_migrations;" | tr -d '[:space:]')
if [ "$COUNT" = "0" ]; then
  echo "schema_migrations empty -> seeding baseline (schema already present)"
  for f in migrations/[0-9][0-9][0-9]_*.sql; do
    PSQL -c "INSERT INTO schema_migrations (version) VALUES ('$(basename "$f")') ON CONFLICT DO NOTHING;" >/dev/null
  done
fi

# 3) Apply pending migrations in order (transaction each)
FAIL=0
for f in migrations/[0-9][0-9][0-9]_*.sql; do
  V=$(basename "$f")
  DONE=$(PSQL -tAc "SELECT count(*) FROM schema_migrations WHERE version='$V';" | tr -d '[:space:]')
  if [ "$DONE" != "0" ]; then
    echo "SKIP $V (already applied)"
    continue
  fi
  echo "APPLY $V"
  if PSQL -v ON_ERROR_STOP=1 -1 < "$f"; then
    PSQL -c "INSERT INTO schema_migrations (version) VALUES ('$V') ON CONFLICT DO NOTHING;" >/dev/null
    echo "  ok $V"
  else
    echo "ERROR: $V failed (rolled back, not recorded)"
    FAIL=1
  fi
done

if [ "$FAIL" = "1" ]; then
  echo "Migration run FAILED."
  exit 1
fi
echo "Migrations complete!"
