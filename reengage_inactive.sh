#!/bin/bash
# Re-engagement: Send messages to users inactive >3 days
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"
DAYS_INACTIVE=3
MESSAGES=(
  "👋 It's been a while! Here are a few things you can try:\n📝 *\"Save a note about...\"* - I'll store it in your vault\n🌐 *\"Search for latest trends\"* - I'll find and summarize\n📖 *\"What notes do I have?\"* - I'll read your vault"
  "☀️ Hey there! Just checking in. Did you know you can:\n- 📝 Save ideas to your personal vault\n- 🌐 Search the web for anything\n- 💾 I remember our conversations\n\n👉 Try sending *\"Save a note about my weekend plans\"*"
  "🎯 Quick tip: Your agent is always here. Try:\n📝 *\"Save this idea for later\"*\n🌐 *\"Search for...\"*\n📖 *\"Show me my notes\"*\n\nI'm just a message away!"
)

# Get users inactive for >3 days (by checking activity_logs)
USERS=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A -F',' \
  -c "SELECT up.phone_number, up.agent_name FROM user_profiles up
      WHERE up.is_active=true AND up.phone_number ~ '^[0-9]+$'
      AND LENGTH(up.phone_number) >= 9
      AND (
        SELECT MAX(al.created_at) FROM activity_logs al WHERE al.user_id::text = up.id::text
      ) < NOW() - INTERVAL '3 days'
      AND up.id::text IN (
        SELECT al.user_id::text FROM activity_logs al GROUP BY al.user_id
      );" 2>/dev/null)

if [ -z "$USERS" ]; then
  echo "No inactive users found"
  exit 0
fi

# Pick message based on day of month
IDX=$((10#$(date +%d) % ${#MESSAGES[@]}))
MSG="${MESSAGES[$IDX]}"

echo "$USERS" | while IFS=',' read -r chat_id name; do
  if [ -n "$chat_id" ] && [ "$chat_id" != " " ]; then
    PERSONALIZED="${MSG/your agent/$name's agent}"
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
      -d "chat_id=$chat_id" \
      -d "text=$PERSONALIZED" \
      -d "parse_mode=Markdown" \
      -o /dev/null -w "%{http_code}" 2>/dev/null
    echo "  Sent to $chat_id ($name)"
    sleep 1  # Rate limit
  fi
done

echo "Re-engagement complete"
