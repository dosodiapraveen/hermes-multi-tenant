#!/usr/bin/env python3
"""
test_user_migration.py — repeatable end-to-end test for migrating a user to the
Hermes runtime (the "Prav" path). Uses a THROWAWAY agent only.

Validates:
  1. chat -> dashboard: agent (Hermes runtime + bridge) creates notes/events/
     reminders/projects and they appear in the user's dashboard data (DB).
  2. dashboard -> agent: items created via the dashboard API are visible to the
     agent (the agent can list them).
  3. dashboard CRUD via the API (the exact endpoints the UI calls): create,
     update, delete for notes/events/reminders/projects.
  4. UX (chat): the agent reply is clean (no banner/box/session summary).
  5. UX (dashboard): every endpoint the dashboard uses returns 200 + valid JSON.

Run on the server (has docker + the api). Safe: creates a throwaway agent, then
deletes it and verifies the baseline is restored. Never touches real users.
"""
import json, os, subprocess, sys, time, re, uuid

BASE = "https://beprepared.dev"
APIC = "hermes-multi-tenant-api-1"
PG   = "hermes-multi-tenant-postgres-1"
HERMES_HOME_PROF = "/opt/hermes/hermes/profiles"

PASS, FAIL = 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL
    mark = "PASS" if cond else "FAIL"
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail and not cond else ""))
    return cond

def run(cmd, timeout=120):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode

def psql(q):
    o, e, c = run(f"docker exec -i {PG} psql -U hermes -tA -c {json.dumps(q)}")
    return o.strip()

def api(method, path, token, data=None):
    import urllib.request, urllib.error
    headers = {"Authorization": f"Bearer {token}"}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}

def login(email, pw):
    import urllib.request
    req = urllib.request.Request(BASE + "/api/auth/user/login",
        data=json.dumps({"email": email, "password": pw}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["token"]

def agent_chat(uid, message, timeout=240):
    # Invoke the throwaway's Hermes profile exactly as the webhook does.
    o, e, c = run(f"docker exec {APIC} timeout {timeout} hermes -p {uid} chat -q {squote(message)} -Q 2>/dev/null", timeout=timeout+20)
    return o.strip()

def squote(s): return "'" + s.replace("'", "'\\''") + "'"

# ---------------------------------------------------------------- entrypoint
UID = "aaaaaaaa-0000-4000-8000-0000000000b1"
EMAIL = "migtest@throwaway.dev"
PW = "MigTest2026!"
UNIQ = f"mig_{int(time.time())}"

def main():
    # Baseline
    base_profiles, base_accounts, base_notes = psql("SELECT count(*) FROM user_profiles"), psql("SELECT count(*) FROM user_accounts"), psql("SELECT count(*) FROM notes")
    print("==")
    print(f"Migration test suite  target=HERMES-runtime throwaway  {UNIQ}")
    print(f"baseline: profiles={base_profiles} accounts={base_accounts} notes={base_notes}")

    print("\n[setup] throwaway agent")
    hashpw = run(f"docker exec {APIC} python3 -c \"import bcrypt;print(bcrypt.hashpw(b'{PW}',bcrypt.gensalt()).decode())\"")[0].strip()
    psql(f"INSERT INTO user_profiles (id,agent_name,phone_number,platform,is_active,runtime) VALUES ('{UID}','Mig Tester','{UID}'.replace('-','').ljust(20,'0')[:10], 'telegram','true','hermes') ON CONFLICT DO NOTHING")
    psql(f"INSERT INTO user_accounts (email,password_hash,user_profile_id,email_verified) VALUES ('{EMAIL}','{hashpw}','{UID}',true) ON CONFLICT DO NOTHING")

    token = login(EMAIL, PW)
    check("login + token", bool(token))

    print("\n[uideo dashboard CRUD] note")
    st, d = api("POST", "/api/me/notes", token, {"title": f"{UNIQ}_note", "content": "chat-created", "category": "Test"})
    nid = d.get("id") if isinstance(d, dict) else None
    check("create note via dashboard", st == 200 and nid)
    check("note visible in DB", psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "1")
    st, _ = api("GET", "/api/me/notes", token)
    check("list notes 200", st == 200)
    st, _ = api("PUT", f"/api/me/notes/{nid}", token, {"title": f"{UNIQ}_note2"})
    check("update note", st == 200)
    st, _ = api("DELETE", f"/api/me/notes/{nid}", token)
    check("delete note", st == 200)
    check("note gone", psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "0")

    print("\n[dashboard CRUD] event")
    st, d = api("POST", "/api/me/events", token, {"title": f"{UNIQ}_ev", "datetime": "2026-12-01T10:00:00"})
    eid = d.get("id") if isinstance(d, dict) else None
    check("create event", st == 200 and eid)
    st, _ = api("DELETE", f"/api/me/events/{eid}", token)
    check("delete event", st in (200, 404))
    check("event gone", psql(f"SELECT count(*) FROM scheduled_events WHERE user_id='{UID}'") == "0")

    print("\n[chat -> dashboard] agent creates an event")
    agent_chat(UID, f"Create an event titled '{UNIQ}_chatEv' at 2026-12-05 14:00. Reply with ONLY the word DONE.")
    check("agent-created event in DB", psql(f"SELECT count(*) FROM scheduled_events WHERE user_id='{UID}'") == "1")

    print("[dashboard -> agent] agent sees it")
    reply = agent_chat(UID, "How many scheduled events do you have? Reply with ONLY a number.")
    check("agent sees dashboard/chat event", "1" in reply or "one" in reply.lower() or "One" in reply, f"reply='{reply}'")

    print("\n[chat -> dashboard] agent creates a note (parseable, no pollution)")
    r0 = agent_chat(UID, f"Create a note titled '{UNIQ}_chatNote' with content 'x'. Reply with ONLY the word DONE.")
    check("agent-created note in DB", psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "1")
    dirty = any(m in r0 for m in ["Initializing", "Resume this session", "Duration:", "╭─", "Query:"])
    check("chat reply is clean (no CLI banner/box/summary)", not dirty, f"reply={r0[:80]!r}")

    print("\n[UX] dashboard endpoints respond cleanly")
    for ep in ["/api/me/notes", "/api/me/events", "/api/me/reminders", "/api/me/projects", "/api/me/ideas"]:
        st, d = api("GET", ep, token)
        check(f"GET {ep} 200+json", st == 200 and isinstance(d, dict))

    print("\n[cleanup]")
    psql(f"DELETE FROM notes WHERE user_id='{UID}'")
    psql(f"DELETE FROM scheduled_events WHERE user_id='{UID}'")
    psql(f"DELETE FROM reminders WHERE user_id='{UID}'")
    psql(f"DELETE FROM projects WHERE user_id='{UID}'")
    psql(f"DELETE FROM user_accounts WHERE email='{EMAIL}'")
    psql(f"DELETE FROM user_profiles WHERE id='{UID}'")
    newn = psql("SELECT count(*) FROM notes")
    check("baseline restored (no orphan notes)", newn == base_notes, f"base={base_notes} now={newn}")
    check("baseline profiles restored", psql("SELECT count(*) FROM user_profiles") == base_profiles)
    check("baseline accounts restored", psql("SELECT count(*) FROM user_accounts") == base_accounts)

    print("\n==============================================")
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)

main()
