#!/bin/bash
API=hermes-multi-tenant-api-1; PG=hermes-multi-tenant-postgres-1; B=https://beprepared.dev
TU=ddd0a002-1111-4000-8000-22222222f002   # throwaway id
EM=tz2@throwaway.dev; PW=TzTest2026!
HPW=$(docker exec $API python3 -c "import bcrypt;print(bcrypt.hashpw(b'$PW',bcrypt.gensalt()).decode())")
cat > /tmp/tzs.sql <<EOF
INSERT INTO user_profiles (id,agent_name,phone_number,platform,is_active) VALUES ('$TU','TzTester2','9990000061','telegram',true) ON CONFLICT (id) DO NOTHING;
INSERT INTO user_accounts (user_profile_id,email,password_hash,email_verified) VALUES ('$TU','$EM','$HPW',true) ON CONFLICT DO NOTHING;
EOF
docker cp /tmp/tzs.sql $PG:/tmp && docker exec -i $PG psql -U hermes < /tmp/tzs.sql >/dev/null
TOK=$(curl -s -X POST "$B/api/auth/user/login" -H "Content-Type: application/json" -d "{\"email\":\"$EM\",\"password\":\"$PW\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
echo "create event @18:00UTC ; reminder @22:00UTC:"
curl -s -X POST "$B/api/me/events" -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" -d "$(printf '{"title":"TzEv","event_start":"2026-08-22T18:00:00","event_end":"2026-08-22T19:00:00"}')" >/dev/null
curl -s -X POST "$B/api/me/reminders" -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" -d "$(printf '{"title":"TzRm","remind_at":"2026-08-22T22:00:00"}')" >/dev/null
echo "--- GET (18:00UTC should be 14:00ET; 22:00UTC should be 18:00ET) ---"
curl -s "$B/api/me/events" -H "Authorization: Bearer $TOK" | python3 -c 'import sys,json;[print("event",e["title"],e["event_start"]) for e in json.load(sys.stdin) if e["title"]=="TzEv"]'
curl -s "$B/api/me/reminders" -H "Authorization: Bearer $TOK" | python3 -c 'import sys,json;[print("rem",r["title"],r["remind_at"]) for r in json.load(sys.stdin) if r["title"]=="TzRm"]'
# cleanup
docker exec -i $PG psql -U hermes -c "DELETE FROM scheduled_events WHERE user_id='$TU'; DELETE FROM reminders WHERE user_id='$TU'; DELETE FROM user_accounts WHERE email='$EM'; DELETE FROM user_profiles WHERE id='$TU';" >/dev/null
echo "cleanup done"
