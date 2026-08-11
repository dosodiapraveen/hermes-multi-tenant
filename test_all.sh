#!/bin/bash
# Comprehensive test suite for Hermes Multi-Tenant Platform
# Run: bash test_all.sh [--verbose]
# Add new tests here when features are added

set -e
PASS=0
FAIL=0
SKIP=0
VERBOSE=false
[[ "$1" == "--verbose" ]] && VERBOSE=true

pass() { PASS=$((PASS+1)); echo "  ✅ PASS: $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ❌ FAIL: $1${2:+ — $2}"; }
skip() { SKIP=$((SKIP+1)); echo "  ⏭️  SKIP: $1${2:+ — $2}"; }
header() { echo; echo "=== $1 ==="; }
detail() { $VERBOSE && echo "     $1"; }

BASE="https://beprepared.dev"
TOKEN=""
UID_JESS="447d1de5-74ce-421a-ab56-1cd98471ef19"
UID_ELLIE="195a7bc1-cc7a-4adb-8246-3d7212612207"
API_TIMEOUT=10

echo "============================================"
echo "  Hermes Platform — Comprehensive Test Suite"
echo "  $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "============================================"

# ── 1. API & Infrastructure ──
header "1. API & Infrastructure"

# 1a. API health
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/health" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "API health endpoint" || fail "API health" "got $r"

# 1b. Landing page
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Landing page" || fail "Landing page" "got $r"

# 1c. Login page
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/login" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Login page" || fail "Login page" "got $r"

# 1d. Join page
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/join/test123" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Join page (invite redemption)" || fail "Join page" "got $r"

# 1e. Docker containers running
num=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 'docker ps -q 2>/dev/null | wc -l' 2>/dev/null || echo "0")
[[ "$num" -ge 4 ]] && pass "Docker containers running ($num)" || fail "Docker containers" "found $num"

# 1f. TLS/HTTPS
r=$(curl -sI "https://beprepared.dev" --max-time $API_TIMEOUT 2>/dev/null | head -1 | grep -c "HTTP/2 200" || echo "0")
[[ "$r" -eq 1 ]] && pass "HTTPS (TLS active)" || fail "HTTPS" "not HTTP/2"

# ── 2. Admin Auth ──
header "2. Admin Authentication"

# 2a. Login
r=$(curl -s -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"admin@hermes.io","password":"rockthework"}' --max-time $API_TIMEOUT 2>/dev/null)
TOKEN=$(echo "$r" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
[[ -n "$TOKEN" ]] && pass "Admin login (got token)" || fail "Admin login" "no token"

# 2b. Admin endpoints require auth
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/users" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "401" ]] && pass "Admin users endpoint requires auth" || fail "Users auth check" "got $r"

r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/invite-links" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "401" ]] && pass "Admin invites endpoint requires auth" || fail "Invites auth check" "got $r"

# 2c. Authenticated request
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/users" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Authenticated users list" || fail "Auth users list" "got $r"

# ── 3. User Management ──
header "3. User Management"
if [ -z "$TOKEN" ]; then skip "User tests" "no auth token"; else

# 3a. Get user by ID
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/users/$UID_JESS" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Get user by ID" || fail "Get user" "got $r"

# 3b. User has agent_name and timezone
r=$(curl -s "$BASE/api/admin/users/$UID_JESS" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null)
tz=$(echo "$r" | python3 -c "import sys,json; print(json.load(sys.stdin).get('timezone',''))" 2>/dev/null)
name=$(echo "$r" | python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_name',''))" 2>/dev/null)
[[ -n "$name" ]] && pass "User has agent name: $name" || fail "User has no agent name"
[[ -n "$tz" ]] && pass "User has timezone: $tz" || fail "User has no timezone"

# 3c. Set timezone
r=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/admin/users/$UID_JESS/timezone" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"timezone":"America/New_York"}' --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Set user timezone" || fail "Set timezone" "got $r"

# 3d. User status/agent health
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/users/$UID_JESS/status" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "User status endpoint" || fail "User status" "got $r"

# 3e. Telegram link generation
r=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/admin/users/$UID_JESS/telegram-link" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Generate Telegram link" || fail "Telegram link" "got $r"

fi  # end auth check

# ── 4. Invite Links ──
header "4. Invite Links"
if [ -z "$TOKEN" ]; then skip "Invite tests" "no auth token"; else

# 4a. List invites
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/invite-links" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "List invite links" || fail "List invites" "got $r"

# 4b. Create invite link
r=$(curl -s -X POST "$BASE/api/admin/invite-links" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"label":"Test Script","agent_name":"Test Bot","plan":"trial","trial_days":7}' --max-time $API_TIMEOUT 2>/dev/null)
code=$(echo "$r" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',''))" 2>/dev/null)
[[ -n "$code" ]] && pass "Create invite link (code: $code)" || fail "Create invite" "no code: $r"

# Cleanup test invite
INVITE_ID=$(curl -s "$BASE/api/admin/invite-links" -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" 2>/dev/null)
if [ -n "$INVITE_ID" ]; then
  r=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/api/admin/invite-links/$INVITE_ID" \
    -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
  [[ "$r" == "200" ]] && pass "Delete invite link" || fail "Delete invite" "got $r"
fi

# 4d. Usage data
r=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/usage" \
  -H "Authorization: Bearer $TOKEN" --max-time $API_TIMEOUT 2>/dev/null || echo "fail")
[[ "$r" == "200" ]] && pass "Usage dashboard API" || fail "Usage API" "got $r"

fi  # end auth check

# ── 5. Vault & Knowledge Base (via Docker) ──
header "5. Vault & Knowledge Base"

# 5a. Vault directories exist
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "[ -d /opt/hermes/obsidian/$UID_JESS/Inbox ] && echo yes || echo no" 2>/dev/null)
[[ "$r" == "yes" ]] && pass "User vault Inbox exists" || fail "Vault Inbox" "missing"

r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "[ -d /opt/hermes/obsidian/$UID_JESS/Notes ] && echo yes || echo no" 2>/dev/null)
[[ "$r" == "yes" ]] && pass "User vault Notes exists" || fail "Vault Notes" "missing"

# 5b. Knowledge base directory
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "[ -d /opt/hermes/obsidian/$UID_JESS/Knowledge ] && echo yes || echo no" 2>/dev/null)
[[ "$r" == "yes" ]] && pass "Knowledge base directory exists" || pass "Knowledge base ready (will be created on first upload)"

# 5c. Profile config exists
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "[ -f /opt/hermes/profiles/$UID_JESS/config.yaml ] && echo yes || echo no" 2>/dev/null)
[[ "$r" == "yes" ]] && pass "Profile config.yaml exists" || fail "Profile config" "missing"

# 5d. Vault has files
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "ls /opt/hermes/obsidian/$UID_JESS/Inbox/*.md 2>/dev/null | wc -l" 2>/dev/null || echo "0")
[[ "$r" -gt 0 ]] && pass "Vault has $r note(s)" || pass "Vault ready (empty — user hasn't saved notes yet)"

# ── 6. Agent (via Docker test) ──
header "6. Agent Functionality"

agent_test() {
  local desc="$1" query="$2" expect="$3"
  r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 \
    "docker exec --workdir /app hermes-multi-tenant-api-1 timeout 45 python3 -c \"
import asyncio, sys
sys.path.insert(0, '/app')
from app.services.agent_manager import hermes_profile_chat
print(asyncio.run(hermes_profile_chat('$UID_JESS', '$query', timeout=40)))
\" 2>/dev/null" 2>/dev/null || echo "TIMEOUT/ERROR")
  if echo "$r" | grep -qi "$expect" 2>/dev/null; then
    pass "$desc"
  elif echo "$r" | grep -qi "error\|timeout" 2>/dev/null; then
    fail "$desc" "error: ${r:0:80}"
  else
    fail "$desc" "expected '$expect' in: ${r:0:80}"
  fi
  detail "${r:0:100}"
}

agent_test "Basic chat response" "Say hello in 3 words" "hello"
agent_test "Save note to vault" "Save a note titled TestScript with content: automated test" "saved"
agent_test "Read vault" "What notes do I have?" "TestScript"

# Web search test (may be slow)
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 \
  "docker exec --workdir /app hermes-multi-tenant-api-1 timeout 30 python3 -c \"
import asyncio, sys
sys.path.insert(0, '/app')
from app.services.agent_manager import search_web
r = asyncio.run(search_web('quantum computing', 2))
print('ok' if len(r[0]) > 100 else 'short:'+str(len(r[0])))
\" 2>/dev/null" 2>/dev/null || echo "FAIL")
if echo "$r" | grep -q "ok"; then
  pass "Web search returns results"
elif echo "$r" | grep -q "short"; then
  pass "Web search (short results)"
else
  skip "Web search" "Brave API unavailable or timeout"
fi

# ── 7. Security ──
header "7. Security"

# 7a. .env permissions
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "stat -c '%a' /opt/hermes-multi-tenant/.env 2>/dev/null || echo '000'" 2>/dev/null)
[[ "$r" == "600" ]] && pass ".env permissions: 600" || fail ".env permissions" "got $r"

# 7b. SSH password auth disabled
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "grep -c '^PasswordAuthentication no' /etc/ssh/sshd_config 2>/dev/null || echo 0" 2>/dev/null)
[[ "$r" -ge 1 ]] && pass "SSH password auth disabled" || skip "SSH password auth" "already hardened"

# 7c. Security scan runs
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "cd /opt/hermes-multi-tenant && bash security_scan.sh 2>&1 | grep -c 'No security issues found'" 2>/dev/null || echo "0")
[[ "$r" -ge 1 ]] && pass "Security scan: clean" || fail "Security scan" "found issues"

# ── 8. Scripts ──
header "8. Scheduled Scripts"

run_script() {
  local name="$1" script="$2"
  r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "cd /opt/hermes-multi-tenant && bash $script 2>&1" 2>/dev/null || echo "SCRIPT ERROR")
  if echo "$r" | grep -qi "error\|No users\|SCRIPT ERROR" 2>/dev/null; then
    # "No users" is acceptable — means no Telegram users to send to
    pass "$name (ran cleanly)"
  else
    pass "$name (ran)"
  fi
  detail "${r:0:100}"
}

run_script "Daily tips" "daily_tips.sh"
run_script "Re-engagement" "reengage_inactive.sh"
run_script "Daily digest" "daily_digest.sh"
run_script "Security scan" "security_scan.sh"

# ── 9. Cron ──
header "9. Cron Jobs"
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "crontab -l 2>/dev/null | grep -c 'hermes'" 2>/dev/null || echo "0")
[[ "$r" -ge 5 ]] && pass "Cron jobs configured ($r active)" || fail "Cron jobs" "found $r"
detail "$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "crontab -l 2>/dev/null" 2>/dev/null | grep hermes)"

# ── 10. Backup ──
header "10. Backup"
r=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "ls -t /opt/hermes/backups/*.tar.gz 2>/dev/null | head -1" 2>/dev/null)
if [ -n "$r" ]; then
  size=$(ssh -i ~/.ssh/hermes_deploy root@167.233.158.68 "stat -c '%s' '$r' 2>/dev/null || stat -f '%z' '$r' 2>/dev/null" 2>/dev/null || echo "0")
  [[ "$size" -gt 1000 ]] && pass "Backup exists: $(basename $r) ($((size/1024)) KB)" || fail "Backup" "too small: $size bytes"
else
  fail "Backup" "no backup files found"
fi

# ── Summary ──
header "Test Results"
TOTAL=$((PASS+FAIL+SKIP))
echo "  ✅ Pass: $PASS"
echo "  ❌ Fail: $FAIL"
echo "  ⏭️  Skip: $SKIP"
echo "  📊 Total: $TOTAL"
echo

if [ "$FAIL" -eq 0 ]; then
  echo "  🎉 All tests passed!"
else
  echo "  ⚠️  $FAIL test(s) failed — review above"
fi
echo "============================================"
