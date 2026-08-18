#!/usr/bin/env python3
"""Timezone-aware morning message loop.

Usage: morning_msg.py <group>   where group in {et, bst}

- Sends a short morning message to each user whose timezone group matches <group>.
- Starts on the configured start_date (Wednesday). Capability nudge is the default
  message type; it adapts to user engagement over time.
- A per-user custom morning message (set by the user) overrides the default.
- State is kept in morning_state.json so a run never double-sends a user.
"""
import json, os, sys, subprocess, datetime, urllib.request, urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(BASE_DIR, "morning_config.json")
STATE = os.path.join(BASE_DIR, "morning_state.json")

# Rotating message templates by type. 'capability' is the starting type.
TEMPLATES = {
    "capability": "Morning, {name}! Just a heads-up — I can summarize your week, prep a to-do, find a note, or research anything you need. Reply with what you'd like. (You can change or turn off this message anytime.)",
    "brief": "Morning, {name}! ☀️ Here's today: {brief}. Anything to add? Reply \"change my morning message\" to make this yours.",
    "stat": "Morning, {name}! Quick stat: {stat}. Want me to act on it?",
    "habit": "Morning, {name}! A gentle nudge on {habit}. Want a reminder or help with it?",
    "optimizer": "Morning, {name}! {optim}. Just ask and I'll handle it.",
}
CYCLE = ["capability", "brief", "stat", "habit", "optimizer"]

def get_token():
    r = subprocess.run(["docker", "exec", "hermes-multi-tenant-api-1", "printenv", "TELEGRAM_BOT_TOKEN"],
                       capture_output=True, text=True)
    return r.stdout.strip()

def send(chat_id, text):
    tok = get_token()
    url = "https://api.telegram.org/bot%s/sendMessage" % tok
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data)) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "err": str(e)}

def recent_messages(user_chat, days=3):
    # engagement proxy: how many messages has this user sent recently
    try:
        sql = ("SELECT count(*) FROM audit_logs WHERE details->>'chat_id'='" + str(user_chat) +
               "' AND timestamp > now() - interval '%d days'" % days)
        r = subprocess.run(["docker", "exec", "-i", "hermes-multi-tenant-postgres-1", "psql", "-U", "hermes", "-tAc", sql],
                           capture_output=True, text=True)
        try:
            return int(r.stdout.strip() or "0")
        except ValueError:
            return 0
    except Exception:
        return 0

def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "et"
    cfg = json.load(open(CFG))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"last_sent": {}, "custom": {}, "type": {}}
    today = datetime.date.today()
    start = datetime.date.fromisoformat(cfg["start_date"])
    if today < start:
        print("not yet: %s < start_date %s" % (today, start))
        return
    changed = False
    for user, info in cfg["users"].items():
        if info["tz"] != group:
            continue
        if state["last_sent"].get(user) == str(today):
            continue  # already sent today
        # custom override wins
        if state["custom"].get(user):
            text = state["custom"][user]
        else:
            # adapt message type by engagement: engaged users rotate to fresh type
            typ = state["type"].get(user, "capability")
            text = TEMPLATES[typ].format(name=user, brief="your day looks clear", stat="no new activity yet",
                                         habit="your skincare routine", optim="you have a light day")
        res = send(info["chat_id"], text)
        state["last_sent"][user] = str(today)
        changed = True
        # rotate type for next time if the user is engaged
        if recent_messages(info["chat_id"]) >= 1:
            state["type"][user] = CYCLE[(CYCLE.index(state["type"].get(user, "capability")) + 1) % len(CYCLE)]
        print("%s (%s) -> ok=%s" % (user, info["tz"], res.get("ok")))
    if changed:
        json.dump(state, open(STATE, "w"), indent=2)

if __name__ == "__main__":
    main()
