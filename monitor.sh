#!/bin/bash
# Hermes Platform Monitor
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"
CHAT_ID="1832518861"

alert() {
    curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID&parse_mode=HTML&text=$1" > /dev/null
}

issues=""

api_ok=$(docker exec hermes-multi-tenant-api-1 curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health 2>/dev/null)
[ "$api_ok" = "200" ] || issues="$issues- API returned $api_ok"$'\n'

db_ok=$(docker exec hermes-multi-tenant-postgres-1 pg_isready -U hermes 2>/dev/null | grep -c 'accepting')
[ "$db_ok" -gt 0 ] || issues="$issues- DB down"$'\n'

used=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
[ "$used" -gt 85 ] && issues="$issues- Disk ${used}% full"$'\n'

for name in api postgres redis frontend caddy; do
    docker ps --format '{{.Names}}' | grep -q "$name" || issues="$issues- Container $name missing"$'\n'
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
