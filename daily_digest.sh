#!/bin/bash
# Daily digest - sends a summary of yesterday's activity at each user's local 8 AM
# Runs hourly; only users at local 8 AM get the digest
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"

docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A -F'|' \
  -c "SELECT phone_number, agent_name, COALESCE(timezone,'UTC'), id::text
      FROM user_profiles WHERE is_active=true
      AND phone_number ~ '^[0-9]+$' AND LENGTH(phone_number) >= 9;" 2>/dev/null |
while IFS='|' read -r chat_id name tz uid; do
  [ -z "$chat_id" ] || [ "$chat_id" = " " ] && continue
  
  local_hour=$(TZ="$tz" date +%H 2>/dev/null)
  [ -z "$local_hour" ] && local_hour=$(date -u +%H)
  
  # Only send at local 8 AM
  if [ "$local_hour" -ne 8 ]; then continue; fi

  # Count yesterday's activity
  yesterday=$(date -u -d '1 day ago' +%Y-%m-%d)
  stats=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A \
    -c "SELECT COUNT(*), COALESCE(SUM((details->>'tokens')::int),0) FROM activity_logs
        WHERE user_id::text='$uid' AND created_at::date = '$yesterday'::date;" 2>/dev/null)
  msgs=$(echo "$stats" | cut -d'|' -f1)
  tokens=$(echo "$stats" | cut -d'|' -f2)
  [ -z "$msgs" ] && msgs=0
  [ -z "$tokens" ] && tokens=0

  # Get most recent note from vault
  latest_note=""
  vault_dir="/opt/hermes/obsidian/$uid/Inbox"
  if [ -d "$vault_dir" ]; then
    latest=$(ls -t "$vault_dir"/*.md 2>/dev/null | head -1)
    if [ -n "$latest" ]; then
      title=$(head -1 "$latest" 2>/dev/null | sed 's/^# //')
      latest_note="📝 Latest note: ${title:-$(basename "$latest" .md)}"
    fi
  fi

  # Build digest message
  MSG="📊 *Your Daily Digest - $(date -u +'%B %d')*
  
Yesterday's activity:
• 💬 *$msgs messages* sent
• 🔍 Searches and notes processed
$([ -n "$latest_note" ] && echo "• $latest_note")

*Ready for today?* Just send me a message! 🚀"

  curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$chat_id" -d "text=$MSG" -d "parse_mode=Markdown" > /dev/null
  echo "Sent digest to $name ($tz, local $local_hour:00, $msgs msgs)"
  sleep 1
done
