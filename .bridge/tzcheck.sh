#!/bin/bash
set -e
API=hermes-multi-tenant-api-1; PG=hermes-multi-tenant-postgres-1; B=https://beprepared.dev
TID=eee0b003-2222-4000-8000-33333333f003   # throwaway
EM=tz3@throwaway.dev; PW=TzTest2026!
HPW=$(docker exec "$API" python3 -c "import bcrypt;print(bcrypt.hashpw(b'$PW',bcrypt.gensalt()).decode())")
printf "INSERT INTO user_profiles (id, agent_name, phone_number, platform, is_active) VALUES ('%s','Tz Tester','999%s','telegram',true) ON CONFLICT DO NOTHING;\nINSERT INTO user_accounts (email,password_hash,email_verified,user_profile_id) VALUES ('%s','%s',true,'%s') ON CONFLICT DO NOTHING;\n" "$TID" "$(date +%H%M%S)" "$EM" "$HPW" "$TID" > /tmp/tz.sql
docker cp /tmp/tz.sql "$PG":/tmp/ >/dev/null 2>&1
docker exec -i "$PG" psql -U hermes < /tmp/tz.sql >/dev/null 2>&1
TOK=$(curl -s -X POST "$B/api/auth/user/login" -H 'Content-Type: application/json' -d "{\"email\":\"$EM\",\"password\":\"$PW\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
curl -s -X POST "$B/api/me/events" -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' -d '{"title":"TzEv","event_start":"2026-12-01T14:00:00-05:00","event_end":"2026-12-01T15:00:00-05:00"}' >/dev/null
curl -s -X POST "$B/api/me/reminders" -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' -d '{"title":"TzRm","remind_at":"2026-12-01T14:00:00+01:00"}' >/dev/null
echo "EV:(expect 19:00:00+00:00)"; curl -s "$B/api/me/events" -H "Authorization: Bearer $TOK" | python3 -c 'import sys,json;d=json.load(sys.stdin);print([x["event_start"] for x in d.get("events",[]) if x["title"]=="TzEv"])'
echo "RM:(expect 13:00:00+00:00)"; curl -s "$B/api/me/reminders" -H "Authorization: Bearer $TOK" | python3 -c 'import sys,json;d=json.load(sys.stdin);print([x["remind_at"] for x in d.get("reminders",[]) if x["title"]=="TzRm"])'
docker exec -i "$PG" psql -U hermes -c "DELETE FROM user_accounts WHERE email='$EM'; DELETE FROM user_profiles WHERE id='$TID';" >/dev/null 2>&1
echo CLEANED
