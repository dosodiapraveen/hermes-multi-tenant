#!/bin/bash
# Morning tips - sends at each user's local 8-9 AM
# Runs hourly via cron; only users at local 8-9 AM get the message
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"

# 3 rotating tip sets
TIP_SET=$(( (10#$(date +%d)) % 3 ))
case $TIP_SET in
  0)
    TIP1="📝 *Save ideas*: Try \"Save this idea to my vault\" — I'll store it."
    TIP2="🌐 *Search the web*: Try \"Search for latest music trends\" — I'll find and summarize."
    ;;
  1)
    TIP1="📖 *Review notes*: Try \"What notes do I have?\" — I'll show your vault."
    TIP2="💾 *Remember things*: Try \"Remember my project deadline is Friday\" — I won't forget."
    ;;
  2)
    TIP1="📋 *Create lists*: Try \"Make a to-do list for this week\" — I'll track it."
    TIP2="🧠 *Brain dump*: Try \"I have an idea about...\" — I'll save it organized."
    ;;
esac

# Fetch active users with timezone info
docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A -F'|' \
  -c "SELECT phone_number, agent_name, COALESCE(timezone,'UTC')
      FROM user_profiles WHERE is_active=true AND platform='telegram';" 2>/dev/null |
while IFS='|' read -r chat_id name tz; do
  [ -z "$chat_id" ] || [ "$chat_id" = " " ] && continue
  
  local_hour=$(TZ="$tz" date +%H 2>/dev/null)
  [ -z "$local_hour" ] && local_hour=$(date -u +%H)
  
  # Only send at local 8-9 AM
  if [ "$local_hour" -ge 8 ] && [ "$local_hour" -le 9 ]; then
    MSG="☀️ *Good morning${name:+, $name}!*
    
Here's what you can try today:

• $TIP1
• $TIP2

Just send me a message anytime! 🚀"
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
      -d "chat_id=$chat_id" -d "text=$MSG" -d "parse_mode=Markdown" > /dev/null
    echo "Sent tip to $name ($tz, local $local_hour:00)"
  fi
  sleep 1
done
