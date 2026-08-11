#!/bin/bash
# Re-engagement: sends to users inactive >3 days at their local 9 AM
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"
DAYS_INACTIVE=3
CURRENT_UTC_HOUR=$(date -u +%H)

MESSAGES=(
  "👋 It's been a while! Here's what you can try:\n📝 *\"Save a note about...\"*\n🌐 *\"Search for latest trends\"*\n📖 *\"What notes do I have?\"*"
  "☀️ Good morning! Quick reminder:\n📝 Save ideas to your vault\n🌐 Search the web\n💾 I remember our chats"
  "🎯 Try this today:\n📝 *\"Save this idea\"*\n🌐 *\"Search for...\"*\n📖 *\"Show me my notes\"*"
)
IDX=$((10#$(date +%d) % ${#MESSAGES[@]}))
MSG="${MESSAGES[$IDX]}"

# Fetch users with timezone info
docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A -F'|' \
  -c "SELECT up.phone_number, up.agent_name, up.timezone
      FROM user_profiles up
      WHERE up.is_active=true AND up.platform='telegram'
      AND (
        SELECT MAX(al.created_at) FROM activity_logs al WHERE al.user_id::text = up.id::text
      ) < NOW() - INTERVAL '$DAYS_INACTIVE days'
      AND up.id::text IN (
        SELECT al.user_id::text FROM activity_logs al GROUP BY al.user_id
      );" 2>/dev/null | while IFS='|' read -r chat_id name tz; do
  if [ -z "$chat_id" ] || [ "$chat_id" = " " ]; then continue; fi
  [ -z "$tz" ] && tz="UTC"
  
  # Calculate local hour
  local_hour=$(TZ="$tz" date +%H 2>/dev/null)
  [ -z "$local_hour" ] && local_hour="$CURRENT_UTC_HOUR"
  
  # Only send if local time is 8-10 AM (morning window)
  if [ "$local_hour" -ge 8 ] && [ "$local_hour" -le 10 ]; then
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
      -d "chat_id=$chat_id" \
      -d "text=$MSG" \
      -d "parse_mode=Markdown" \
      -o /dev/null
    echo "  Sent to $name ($tz, local $local_hour:00)"
  fi
  sleep 1
done

echo "Re-engagement check complete"
