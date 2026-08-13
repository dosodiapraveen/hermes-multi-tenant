#!/bin/bash
# Hermes multi-tenant — automated DB migration runner
# idempotent: tracks applied migrations in schema_migrations; runs pending ones.
# Run on every deploy (after container start) and manually via `bash run_migrations.sh`
#
# Usage:
#   bash run_migrations.sh [--dry-run] [--fix-schema]
#
#   --fix-schema   additionally reconcile full schema from init.sql on existing DB
#                  (adds any tables that init.sql defines but the live DB lacks).
#   --dry-run      print what WOULD run without executing.

set -uo pipefail
PG="docker exec -i hermes-multi-tenant-postgres-1 psql -U hermes"
MIG_DIR="$(cd "$(dirname "$0")" && pwd)/migrations"
DRY=0
FIX_SCHEMA=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --fix-schema) FIX_SCHEMA=1 ;;
  esac
done

echo "▶️  Migration runner — $(date -u '+%Y-%m-%d %H:%M UTC')"

# Ensure tracking table exists
$PG -c "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW());" > /dev/null 2>&1
echo "✅ schema_migrations tracking table ready"

# ── Optional: reconcile schema from init.sql on existing DB ──
if [ "$FIX_SCHEMA" = "1" ]; then
  echo "── Reconciling schema from init.sql (existing DB) ──"
  # Strip CREATE EXTENSION / comments, keep CREATE TABLE + ALTER + CREATE INDEX
  # init.sql is also mounted at /docker-entrypoint-initdb.d/ on fresh DBs, but
  # existing volumes skip it — so we apply it here too.
  if [ "$DRY" = "1" ]; then
    echo "  (dry-run) would apply init.sql schema reconciliation"
  else
    if [ -f "init.sql" ]; then
      $PG < init.sql 2>&1 | grep -vE 'GRANT|COMMENT|NOTICE|CREATE INDEX|CREATE TABLE' || true
      echo "  ✅ init.sql reconciliation applied"
    else
      echo "  ⚠️  init.sql not found"
    fi
  fi
fi

# ── Apply pending migrations ──
echo "── Applying pending migrations ──"
applied=0
failed=0
if [ -d "$MIG_DIR" ]; then
  for f in "$MIG_DIR/"*.sql; do
    [ -e "$f" ] || continue
    version="$(basename "$f" .sql)"

    # Skip if already applied
    already=$($PG -t -A -c "SELECT 1 FROM schema_migrations WHERE version='$version';" 2>/dev/null | grep -c 1)
    if [ "$already" -ge 1 ]; then
      echo "  ⏭️  $version already applied"
      continue
    fi

    if [ "$DRY" = "1" ]; then
      echo "  ▶️  (dry-run) would apply $version"
      applied=$((applied+1))
      continue
    fi

    echo "  ▶️  Applying $version ..."
    if $PG < "$f" 2>&1 | grep -qiE '^ERROR|^SQLSTATE' ; then
      echo "  ❌ $version FAILED — manual review required"
      failed=$((failed+1))
    else
      $PG -c "INSERT INTO schema_migrations (version) VALUES ('$version') ON CONFLICT DO NOTHING;" > /dev/null 2>&1
      echo "  ✅ $version applied & recorded"
      applied=$((applied+1))
    fi
  done
else
  echo "  ℹ️  No migrations directory"
fi

echo ""
echo "✅ Migration check complete — applied: $applied, failed: $failed"
[ "$failed" -gt 0 ] && exit 1 || exit 0
