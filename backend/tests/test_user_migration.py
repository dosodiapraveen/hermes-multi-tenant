#!/usr/bin/env python3
"""
test_user_migration.py — repeatable end-to-end migration test (the "Prav" path).

Creates a THROWAWAY agent configured exactly like a migrated user (Hermes runtime
+ beprepared MCP bridge + long-lived agent_token), then validates:

  1. Dashboard CRUD via the API (the exact endpoints the UI calls): create,
     update, delete for notes / events / reminders / projects.
  2. chat -> dashboard: the agent (via the bridge) creates notes/events/reminders
     and they land in the user's dashboard data (DB).
  3. dashboard -> agent: an event created via the dashboard API is visible to the
     agent (the agent lists it).
  4. UX (chat): replies are CLEAN (no CLI banner, ASCII box, reasoning box,
     session summary, resume hints) and DELIVERABLE (no >4096 text).
  5. Latency: times each agent turn and reports it.
  6. UX (dashboard): every dashboard endpoint returns 200 + valid JSON.

Run ON the server (has docker + host access). Safe: fully cleans up and verifies
the baseline is restored. NEVER touches real users.
"""
import json, os, subprocess, sys, time, re, uuid, urllib.request, urllib.error

BASE = "https://beprepared.dev"
APIC = "hermes-multi-tenant-api-1"
PG   = "hermes-multi-tenant-postgres-1"
HM   = "/opt/hermes/hermes/profiles"
USRCONF = "/opt/hermes/hermes"

PASS, FAIL = 0, 0
def check(name, cond, detail="", latency=None):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    lat = f"  ({latency:.1f}s)" if latency is not None else ""
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}{lat}" + (f"  — {detail}" if detail and not cond else ""))

def run(cmd, timeout=180):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode

def psql(q):
    o, e, c = run(f"docker exec -i {PG} psql -U hermes -tA -c {shq(q)}")
    return o.strip()

def shq(s): return "'" + str(s).replace("'", "'\\''") + "'"

def api(method, path, token, data=None):
    h = {"Authorization": f"Bearer {token}"}
    body = None
    if data is not None:
        body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}

def login(email, pw):
    req = urllib.request.Request(BASE + "/api/auth/user/login",
        data=json.dumps({"email": email, "password": pw}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["token"]

def agent_chat(uid, message, timeout=260):
    t = time.time()
    r = subprocess.run(
        ["docker", "exec", APIC, "bash", "-lc",
         f'HERMES_HOME={USRCONF} timeout {timeout} hermes -p "$1" chat -q "$2" -Q --reasoning none',
         "_", uid, message],
        capture_output=True, text=True, timeout=timeout+20)
    raw = r.stdout or ""
    idx = raw.rfind("session_id:")
    ans = raw[idx:] if idx >= 0 else raw
    nl = ans.find("\n"); ans = ans[nl+1:] if nl != -1 else ""
    return ans.strip(), time.time() - t

BAD_PATTERNS = ["Initializing agent", "Resume this session", "Duration:", "Messages:", "session_id:",
                "Query:", "╭", "╰", "┌", "└", "┐", "┘"]

def clean_reply(r):
    return not any(b in r for b in BAD_PATTERNS)

# ------------------------------------------------------------------ main
UID   = "aaaaaaaa-0000-4000-8000-00000000c001"
EMAIL = "migtest@throwaway.dev"
PW    = "MigTest2026!"
PHONE = "9990" + str(int(time.time()) % 1000000).zfill(6)
UNIQ  = "mig_" + str(int(time.time()))

def main():
    base_p, base_a, base_n = psql("SELECT count(*) FROM user_profiles"), psql("SELECT count(*) FROM user_accounts"), psql("SELECT count(*) FROM notes")
    print("=" * 60)
    print(f"MIGRATION TEST  target=Hermes runtime  throwaway=({UID})  {UNIQ}")
    print(f"baseline: profiles={base_p} accounts={base_a} notes={base_n}")

    print("\n-- setup (throwaway, Hermes runtime) --")
    hpw = run(f"docker exec {APIC} python3 -c \"import bcrypt;print(bcrypt.hashpw(b'{PW}',bcrypt.gensalt()).decode())\"")[0].strip()
    psql(f"INSERT INTO user_profiles (id,agent_name,phone_number,platform,is_active,runtime) VALUES ('{UID}','Mig Tester','{PHONE}','telegram',true,'hermes') ON CONFLICT DO NOTHING")
    psql(f"INSERT INTO user_accounts (email,password_hash,user_profile_id,email_verified) VALUES ('{EMAIL}','{hpw}','{UID}',true) ON CONFLICT DO NOTHING")
    # long-lived agent_token (Option-1 auth)
    atok = run("docker exec %s python3 -c \"import secrets;print(secrets.token_urlsafe(32))\"" % APIC)[0].strip()
    psql(f"UPDATE user_accounts SET agent_token='{atok}' WHERE user_profile_id='{UID}'")
    # Hermes profile from the proven template + point bridge at the token
    run(f"mkdir -p {HM}/{UID} && cp -r {HM}/phase1test/. {HM}/{UID}/ 2>/dev/null")
    run(f"sed -i -E 's|BEPREPARED_TOKEN:.*|BEPREPARED_TOKEN: {atok}|' {HM}/{UID}/config.yaml 2>/dev/null")
    token = login(EMAIL, PW)
    check("login + token", bool(token))

    print("\n-- DASHBOARD CRUD (API = what the UI calls) --")
    st, d = api("POST", "/api/me/notes", token, {"title": f"{UNIQ}_note", "content": "x", "category": "Test"})
    nid = d.get("id") if isinstance(d, dict) else None
    check("create note", st == 200 and nid)
    check("note in DB", psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "1")
    st, _ = api("PUT", f"/api/me/notes/{nid}", token, {"title": f"{UNIQ}_note2"})
    check("update note", st == 200)
    st, _ = api("DELETE", f"/api/me/notes/{nid}", token)
    check("delete note", st == 200 and psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "0")
    st, d = api("POST", "/api/me/events", token, {"title": f"{UNIQ}_ev", "event_start": "2026-12-01T10:00:00", "event_end": "2026-12-01T11:00:00"})
    eid = d.get("id") if isinstance(d, dict) else None
    check("create event", st == 200 and eid, detail=f"st={st} d={d}")
    st, _ = api("DELETE", f"/api/me/events/{eid}", token)
    check("delete event", st in (200, 404))
    st, d = api("POST", "/api/me/reminders", token, {"title": f"{UNIQ}_rem", "remind_at": "2026-12-01T10:00:00-05:00"})
    check("create reminder", st == 200, detail=f"st={st} d={d}")
    st, d = api("POST", "/api/me/projects", token, {"title": f"{UNIQ}_proj"})
    check("create project", st == 200)

    print("\n-- FAST-PATH (instant DB read, no agent loop) --")
    t0 = time.time()
    o, e, c = run(
        f"docker exec {APIC} python3 -c \"import asyncio;from app.routers.webhook import try_fast_path;"
        f"r=asyncio.run(try_fast_path('{UID}','what is in my schedule'));print(repr((r or '')[:120]))\"",
        timeout=30)
    el = (time.time() - t0) * 1000
    check("fast-path: schedule answered <2s (0 model calls)",
          c == 0 and el < 2000, detail=f"{el:.0f}ms -> {o.strip()}")

    print("\n-- TIMEZONE (offset-aware round-trip) --")
    # An event created at an explicit offset must be returned as the SAME absolute
    # instant (offset-aware), not naive-UTC (+4h) and not re-encoded.
    from datetime import datetime as _dt, timezone as _tz
    def _utc_hour(iso):
        try:
            return _dt.fromisoformat(iso.replace("Z", "+00:00")).astimezone(_tz.utc).hour
        except Exception:
            return -1
    def _aware(iso):
        return bool(iso) and any(c in iso[-6:] for c in "Z+-")
    api("POST", "/api/me/events", token, {"title": f"{UNIQ}_tzEv",
        "event_start": "2026-12-01T14:00:00-05:00", "event_end": "2026-12-01T15:00:00-05:00"})
    _, evs = api("GET", "/api/me/events", token, {})
    ev = next((e for e in (evs.get("events", []) if isinstance(evs, dict) else []) if e.get("title") == f"{UNIQ}_tzEv"), {})
    es = ev.get("event_start", "")
    check("tz: event offset-aware", _aware(es) and _utc_hour(es) == 19, detail=f"ret={es} (expect ...T19:00:00Z)")  # 14:00-05:00 == 19:00Z
    api("POST", "/api/me/reminders", token, {"title": f"{UNIQ}_tzRm", "remind_at": "2026-12-01T14:00:00+01:00"})
    _, rms = api("GET", "/api/me/reminders", token, {})
    rm = next((r for r in (rms.get("reminders", []) if isinstance(rms, dict) else []) if r.get("title") == f"{UNIQ}_tzRm"), {})
    rs = rm.get("remind_at", "")
    check("tz: reminder offset-aware (BST-like)", _aware(rs) and _utc_hour(rs) == 13, detail=f"ret={rs} (expect ...T13:00:00Z)")  # 14:00+01:00 == 13:00Z

    print("\n-- CHAT -> DASHBOARD (agent via bridge) --")
    r, lat = agent_chat(UID, f"Create an event titled '{UNIQ}_chatEv' at 2026-12-05 14:00. Reply with ONLY: DONE")
    check("agent creates event -> DB", psql(f"SELECT count(*) FROM scheduled_events WHERE user_id='{UID}'") == "1", latency=lat)
    r, lat = agent_chat(UID, f"Create a note titled '{UNIQ}_chatNote' with content hello. Reply with ONLY: DONE")
    check("agent creates note -> DB", psql(f"SELECT count(*) FROM notes WHERE user_id='{UID}'") == "1", latency=lat)
    check("agent reply is CLEAN", clean_reply(r), detail=repr(r[:80]))

    print("\n-- DASHBOARD -> AGENT visibility --")
    st, d = api("POST", "/api/me/events", token, {"title": f"{UNIQ}_dashEv", "event_start": "2026-12-09T09:00:00", "event_end": "2026-12-09T10:00:00"})
    check("add event via dashboard", st == 200)
    r, lat = agent_chat(UID, "List your scheduled events. Reply with ONLY their titles, comma separated.")
    check("agent sees dashboard event", UNIQ and "dashEv" in r, detail=repr(r[:120]), latency=lat)

    print("\n-- latency of a reminders question --")
    r, lat = agent_chat(UID, "What are my reminders? Reply briefly.")
    print(f"  [info] reminders turn latency={lat:.1f}s, reply len={len(r)}")
    check("reminders turn < 30s", lat < 30, latency=lat)
    check("reminders reply clean + present", bool(r) and clean_reply(r), detail=repr(r[:80]))
    check("reminders reply deliverable (<=4096)", len(r) <= 4000)

    print("\n-- UX: dashboard endpoints --")
    for ep in ["/api/me/notes", "/api/me/events", "/api/me/reminders", "/api/me/projects", "/api/me/ideas"]:
        st, d = api("GET", ep, token)
        check(f"GET {ep} 200+json", st == 200 and isinstance(d, (dict, list)), detail=f"st={st}")

    print("\n-- cleanup --")
    for t in [f"notes WHERE user_id='{UID}'", f"scheduled_events WHERE user_id='{UID}'", f"reminders WHERE user_id='{UID}'", f"projects WHERE user_id='{UID}'", f"user_accounts WHERE user_profile_id='{UID}'", f"user_profiles WHERE id='{UID}'"]:
        psql(f"DELETE FROM {t}")
    run(f"rm -rf {HM}/{UID}")
    check("no orphan notes", psql("SELECT count(*) FROM notes") == base_n, f"base={base_n} now={psql('SELECT count(*) FROM notes')}")
    check("profiles baseline", psql("SELECT count(*) FROM user_profiles") == base_p)
    check("accounts baseline", psql("SELECT count(*) FROM user_accounts") == base_a)

    print("=" * 60)
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)

main()
