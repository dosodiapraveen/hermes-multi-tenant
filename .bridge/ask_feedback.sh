#!/bin/bash
# Send a brief, low-key, OPTIONAL improvement question to each heavy user (Telegram).
# Intended to run at most once every ~3 days so as not to be annoying.
TOK=$(docker exec hermes-multi-tenant-api-1 printenv TELEGRAM_BOT_TOKEN 2>/dev/null)
[ -z "$TOK" ] && echo "NO_TOKEN" && exit 1
MSG="Hi! Quick, totally optional question so I can serve you better — is there anything you'd like me (or the dashboard) to do better or differently? No rush; reply whenever you like. 🙂"
for ID in 1832518861 8805031496 6889342821; do
  R=$(curl -s "https://api.telegram.org/bot$TOK/sendMessage" --data chat_id=$ID --data text="$MSG")
  echo "$ID -> $(echo "$R" | grep -o '"ok":[a-z]*' | head -1)"
done
