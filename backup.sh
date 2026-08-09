#!/bin/bash
# Hermes Platform Backup Script
# Backs up: PostgreSQL DB, user profiles, Obsidian vaults, config
# Restore on a new server: run this on the old server, transfer the file, run restore.sh

set -e
BACKUP_DIR="/opt/hermes/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/hermes-backup-${TIMESTAMP}.tar.gz"
RETENTION_DAYS=14

mkdir -p "${BACKUP_DIR}"

# 1. Dump PostgreSQL
echo "Backing up PostgreSQL..."
docker exec hermes-multi-tenant-postgres-1 pg_dump -U hermes --clean --if-exists > "${BACKUP_DIR}/db-${TIMESTAMP}.sql"
gzip "${BACKUP_DIR}/db-${TIMESTAMP}.sql"
echo "  DB dump: ${BACKUP_DIR}/db-${TIMESTAMP}.sql.gz"

# 2. Backup profiles and vaults
echo "Backing up user profiles and vaults..."
tar czf "${BACKUP_DIR}/profiles-${TIMESTAMP}.tar.gz" \
    -C /opt/hermes profiles obsidian 2>/dev/null || true

# 3. Backup .env config
cp /opt/hermes-multi-tenant/.env "${BACKUP_DIR}/env-${TIMESTAMP}.txt" 2>/dev/null || true

# 4. Create single combined archive
echo "Creating combined backup..."
tar czf "${BACKUP_FILE}" -C "${BACKUP_DIR}" \
    "db-${TIMESTAMP}.sql.gz" \
    "profiles-${TIMESTAMP}.tar.gz" \
    "env-${TIMESTAMP}.txt" 2>/dev/null

# 5. Clean up temp files
rm -f "${BACKUP_DIR}/db-${TIMESTAMP}.sql.gz" \
      "${BACKUP_DIR}/profiles-${TIMESTAMP}.tar.gz" \
      "${BACKUP_DIR}/env-${TIMESTAMP}.txt"

# 6. Remove backups older than retention
find "${BACKUP_DIR}" -name "hermes-backup-*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup complete: ${BACKUP_FILE}"
echo "Size: $(du -h "${BACKUP_FILE}" | cut -f1)"
echo "Retention: ${RETENTION_DAYS} days"
ls -lh "${BACKUP_DIR}/" 2>/dev/null | tail -5