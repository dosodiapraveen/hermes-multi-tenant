#!/bin/bash
# Hermes Platform Restore Script
# Usage: ./restore.sh <backup-file.tar.gz>
# Copies backup to server, restores everything

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    echo "  Restores PostgreSQL DB, user profiles, Obsidian vaults, and config"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

RESTORE_DIR="/tmp/hermes-restore-$(date +%s)"
mkdir -p "${RESTORE_DIR}"

echo "Extracting backup..."
tar xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"

echo "Restoring PostgreSQL..."
DB_DUMP=$(ls "${RESTORE_DIR}"/db-*.sql.gz 2>/dev/null | head -1)
if [ -n "${DB_DUMP}" ]; then
    gunzip -c "${DB_DUMP}" | docker exec -i hermes-multi-tenant-postgres-1 psql -U hermes
    echo "  Database restored"
fi

echo "Restoring user profiles and vaults..."
PFILE=$(ls "${RESTORE_DIR}"/profiles-*.tar.gz 2>/dev/null | head -1)
if [ -n "${PFILE}" ]; then
    tar xzf "${PFILE}" -C /opt/hermes
    echo "  Profiles and vaults restored"
fi

echo "Restoring .env config..."
ENV_FILE=$(ls "${RESTORE_DIR}"/env-*.txt 2>/dev/null | head -1)
if [ -n "${ENV_FILE}" ]; then
    cp "${ENV_FILE}" /opt/hermes-multi-tenant/.env
    echo "  .env config restored (restart required)"
fi

rm -rf "${RESTORE_DIR}"
echo ""
echo "Restore complete! Run: docker compose restart api"
echo "To restore on a new server:"
echo "  1. Set up Docker + PostgreSQL"
echo "  2. Run: docker compose up -d postgres"
echo "  3. Run: ./restore.sh backup-file.tar.gz"
echo "  4. Run: docker compose up -d"