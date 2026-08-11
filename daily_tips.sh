#!/bin/bash
# Daily morning tips for all Telegram users
BOT_TOKEN="8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU"

# Get active users from DB via docker
USERS=$(docker exec hermes-multi-tenant-postgres-1 psql -U hermes -t -A -F',' \
  -c "SELECT phone_number, agent_name FROM user_profiles WHERE is_active=true AND phone_number SIMILAR TO '[0-9]+' AND LENGTH(phone_number) >= 9 AND phone_number NOT LIKE '880%' AND phone_number NOT LIKE '688%';" 2>/dev/null)

if [ -z "$USERS" ]; then echo "No users"; exit 0; fi

# 3 rotating tip sets
DAY=$(date +%d)
TIP_SET=$(( (10#$DAY) % 3 ))

case $TIP_SET in
  0)
    TIP1="📝 *Save ideas*: Try \"Save this idea to my vault\" — I'll store it in your personal knowledge base."
    TIP2="🌐 *Search the web*: Try \"Search for latest music trends\" — I'll find and summarize."
    ;;
  1)
    TIP1="📖 *Review notes*: Try \"What notes do I have?\" — I'll show everything in your vault."
    TIP2="💾 *Remember things*: Try \"Remember my project deadline is Friday\" — I won't forget."
    ;;
  2)
    TIP1="📋 *Create lists*: Try \"Make a to-do list for this week\" — I'll track it."
    TIP2="🧠 *Brain dump*: Try \"I have an idea about...\" — I'll save it organized."
    ;;
esac

echo "$USERS" | while IFS=',' read -r CHAT NAME; do
  CHAT=$(echo "$CHAT" | tr -d ' ')
  NAME=$(echo "$NAME" | tr -d '"')
  [ -z "$CHAT" ] && continue
  MSG="☀️ *Good morning${NAME:+, $NAME}!*

Here's what you can try today:

• $TIP1
• $TIP2

Just send me a message anytime! 🚀"
  curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT" -d "text=$MSG" -d "parse_mode=Markdown" > /dev/null
  echo "Sent to $CHAT"
done
