#!/bin/bash
# Server deployment helper. Run from the repo root on the server:
#   bash deploy.sh
# Pulls latest, initializes submodules (design-system), rebuilds + restarts.
set -euo pipefail
cd "$(dirname "$0")"

echo "→ git pull"
git pull --ff-only

echo "→ git submodule update --init --recursive"
git submodule update --init --recursive

echo "→ docker compose up -d --build"
docker compose up -d --build

echo "→ migrations"
bash run_migrations.sh --fix-schema || true

echo "✓ Deploy complete"
