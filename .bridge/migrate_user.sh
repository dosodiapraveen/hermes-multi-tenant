#!/bin/bash
# Migrate a user to the real Hermes runtime (copy of Prav's proved setup).
# Usage: migrate_user.sh <user_profile_id> <agent_name>
set -e
UID_="$1"; NAME="$2"
API=hermes-multi-tenant-api-1; PG=hermes-multi-tenant-postgres-1
HSV=/opt/hermes/hermes/profiles

# 1) mint a long-lived per-user agent_token and store it
TOK=$(docker exec "$API" python3 -c 'import secrets;print(secrets.token_urlsafe(32))')
docker exec "$PG" psql -q -U hermes -c "UPDATE user_accounts SET agent_token='$TOK' WHERE user_profile_id='$UID_';"

# 2) create the Hermes profile from the working template (model+bridge+SOUL+reasoning)
rm -rf "$HSV/$UID_"
cp -r "$HSV/phase1test" "$HSV/$UID_"

# 3) point the bridge at THIS user's agent_token
sed -i "s|BEPREPARED_TOKEN:.*|BEPREPARED_TOKEN: $TOK|" "$HSV/$UID_/config.yaml"

# 4) switch the user to the Hermes runtime (rollback = runtime='agent')
docker exec "$PG" psql -q -U hermes -c "UPDATE user_profiles SET runtime='hermes' WHERE id='$UID_';"

echo "MIGRATED $NAME ($UID_)  runtime=hermes"
