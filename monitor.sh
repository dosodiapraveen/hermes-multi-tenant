#!/bin/bash
# Hermes Platform Monitor
BOT_TOKEN="8980557307:***"
CHAT_ID="1832518861"

alert() {
    curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID&parse_mode=HTML&text=$1" > /dev/null
}

issues=""
NL=$'\n'

api_ok=$(docker exec hermes-multi-tenant-api-1 curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health 2>/dev/null)
[ "$api_ok" = "200" ] || issues="${issues}- API returned $api_ok$NL"

db_ok=$(docker exec hermes-multi-tenant-postgres-1 pg_isready -U hermes 2>/dev/null | grep -c 'accepting')
[ "$db_ok" -gt 0 ] || issues="${issues}- DB down$NL"

used=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
[ "$used" -gt 85 ] && issues="${issues}- Disk ${used}% full$NL"

for name in api postgres redis frontend caddy; do
    docker ps --format '{{.Names}}' | grep -q "$name" || issues="${issues}- Container $name missing$NL"
done

# ── DB schema / migration health check ──
migrations_pending=$(cd /opt/hermes-multi-tenant 2>/dev/null && bash run_migrations.sh --dry-run 2>/dev/null | grep -c 'would apply')
[ -z "$migrations_pending" ] && migrations_pending=0
[ "$migrations_pending" -gt 0 ] && issues="${issues}- ${migrations_pending} DB migration(s) pending (schema drift) — run run_migrations.sh$NL"

# Verify core tables exist
for tbl in user_profiles user_accounts activity_logs audit_logs invite_links projects reminders notes; do
    exists=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -tAc "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='$tbl'" 2>/dev/null | grep -c 1)
    [ "$exists" -gt 0 ] || issues="${issues}- Missing table: $tbl (schema drift)$NL"
done

if [ -n "$issues" ]; then
    msg="<b>Alert</b> $(date +%H:%M)%0A$issues"
    alert "$msg"
    echo "ALERTS: $issues"
else
    echo "$(date -u +%Y-%m-%dT%H:%M:%S) All OK"
fi

if [ "$1" = "daily" ]; then
    u=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -tAc "SELECT count(*) FROM user_profiles")
    a=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -tAc "SELECT count(*) FROM user_profiles WHERE is_active=true")
    msg="<b>Daily Report</b>%0AUsers: $u%0AActive: $a"
    alert "$msg"
fi
