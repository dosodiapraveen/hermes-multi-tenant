#!/usr/bin/env python3
"""
Low-key, non-annoying feedback loop for heavy users.
- ROTATES question wording across a healthy pool (never the same every time).
- BACKS OFF (asks less often) for users who use the system regularly / were just asked.
Intended to run at most once every ~3 days per user.
"""
import subprocess, sys, json, datetime, random, os

TOK = subprocess.run(["docker", "exec", "hermes-multi-tenant-api-1", "printenv", "TELEGRAM_BOT_TOKEN"],
                     capture_output=True, text=True).stdout.strip()
STATE_FILE = "/opt/hermes/hermes/.fb_state.json"
USERS = [  # chat_id, name
    ("1832518861", "Prav"),
    ("8805031496", "Jess"),
    ("6889342821", "Ellie"),
]

POOL = [
    "Hi {name}! Quick, totally optional question so I can serve you better — anything you'd like me or the dashboard to do differently? No rush.",
    "Hey {name} — if you could change one thing about your assistant or the dashboard, what would it be? Completely optional, reply whenever.",
    "{name}, I'd love a small piece of feedback when you have a sec: what's the most useful thing I do for you, and what's the most annoying/missing?",
    "Quick check-in, {name}: is there any feature or task you wish I'd just handle for you? No pressure — one line is plenty.",
    "How's it going, {name}? Anything I can do better — faster, smarter, or something you expected me to do and I didn't?",
]

def state():
    try:
        return json.load(open(STATE_FILE))
    except Exception:
        return {}

def save(st):
    json.dump(st, open(STATE_FILE, "w"))
    os.chmod(STATE_FILE, 0o600)

def recent_activity(chat_user_id, days=3):
    # count user webhook messages in the last N days via audit_logs
    q = ("SELECT COUNT(*) FROM audit_logs WHERE user_id::text IN ("
         f"SELECT id FROM user_profiles WHERE phone_number='{chat_user_id}')"
         f" AND timestamp > now() - interval '{days} days'")
    r = subprocess.run(["docker", "exec", "hermes-multi-tenant-postgres-1", "psql", "-U", "hermes", "-tAc", q],
                       capture_output=True, text=True).stdout.strip()
    try:
        return int(r or 0)
    except Exception:
        return 0

today = datetime.date.today().isoformat()
st = state()
sent_any = False
for chat_id, name in USERS:
    u = st.get(chat_id, {})
    last = u.get("last", "")

    # 1) Wording: rotate through the pool by how many times this user was asked
    idx = u.get("asked", 0) % len(POOL)
    msg = POOL[idx].format(name=name)

    # 2) Backoff: skip if asked very recently (<4 days)
    if last and last >= (datetime.date.today() - datetime.timedelta(days=4)).isoformat():
        print(f"{chat_id} skipped (recently asked)"); continue
    # 3) Backoff: if they use the system regularly (active in last 3 days), 
    #    stretch the cadence -> gradually less frequent for engaged users.
    if recent_activity(chat_id) >= 3:
        print(f"{chat_id} skipped (regular user, backing off)"); continue

    r = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{TOK}/sendMessage",
                        "-d", f"chat_id={chat_id}", "-d", f"text={msg}"], capture_output=True, text=True)
    ok = '"ok":true' in r.stdout
    print(f"{chat_id} {name} -> {'ok' if ok else 'FAIL ' + r.stdout[:80]}")
    st[chat_id] = {"last": today, "asked": u.get("asked", 0) + 1}
    sent_any = True

save(st)
sys.exit(0)
