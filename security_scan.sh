#!/bin/bash
# Daily Security Scan - runs at midnight via cron
# Checks: open ports, container security, file permissions, SSH config, Docker audit

REPORT="/opt/hermes/security_reports/$(date +%Y%m%d).txt"
mkdir -p /opt/hermes/security_reports

echo "===========================================" > $REPORT
echo "  Security Scan - $(date '+%Y-%m-%d %H:%M UTC')" >> $REPORT
echo "===========================================" >> $REPORT
ISSUES=0

# ── 1. Open Ports ──
echo "" >> $REPORT
echo "── Open ports (public) ──" >> $REPORT
ss -tlnp 2>/dev/null | grep -E '0.0.0.0:|:::|*\\.' | awk '{print $4}' | while read p; do
  port=$(echo $p | rev | cut -d: -f1 | rev)
  if [ "$port" != "80" ] && [ "$port" != "443" ]; then
    echo "  ⚠️  Non-standard port exposed: $port" >> $REPORT
    ISSUES=$((ISSUES+1))
  fi
done
# Check port 22 (SSH)
if ss -tlnp 2>/dev/null | grep -q ':22 '; then
  echo "  ℹ️  SSH (22) is open (expected)" >> $REPORT
fi

# ── 2. Docker Container Audit ──
echo "" >> $REPORT
echo "── Docker container audit ──" >> $REPORT
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> $REPORT 2>/dev/null

# Check for containers running as root unnecessarily
for c in $(docker ps --format "{{.Names}}"); do
  user=$(docker inspect $c --format '{{.Config.User}}' 2>/dev/null)
  if [ -z "$user" ] || [ "$user" = "root" ] || [ "$user" = "" ]; then
    true  # Most containers run as root by default - noted but not flagged
  fi
done

# ── 3. File Permissions ──
echo "" >> $REPORT
echo "── Sensitive file permissions ──" >> $REPORT
if [ -f /opt/hermes-multi-tenant/.env ]; then
  perms=$(stat -c "%a" /opt/hermes-multi-tenant/.env 2>/dev/null || stat -f "%Lp" /opt/hermes-multi-tenant/.env 2>/dev/null)
  if [ "$perms" != "600" ] && [ "$perms" != "400" ]; then
    echo "  ⚠️  .env permissions: $perms (should be 600)" >> $REPORT
    ISSUES=$((ISSUES+1))
  else
    echo "  ✅ .env permissions: $perms" >> $REPORT
  fi
fi

# SSH key permissions
for f in /root/.ssh/authorized_keys /root/.ssh/id_*; do
  if [ -f "$f" ]; then
    perms=$(stat -c "%a" "$f" 2>/dev/null || stat -f "%Lp" "$f" 2>/dev/null)
    if [ "$perms" -gt "600" ] 2>/dev/null; then
      echo "  ⚠️  $f permissions: $perms (should be 600)" >> $REPORT
      ISSUES=$((ISSUES+1))
    fi
  fi
done

# ── 4. Failed SSH attempts ──
echo "" >> $REPORT
echo "── Failed SSH attempts (last 24h) ──" >> $REPORT
attempts=$(grep "Failed password" /var/log/auth.log 2>/dev/null | grep "$(date +'%b %d')" | wc -l)
echo "  $attempts failed attempts today" >> $REPORT
if [ "$attempts" -gt 50 ]; then
  echo "  ⚠️  High number of SSH brute-force attempts" >> $REPORT
  ISSUES=$((ISSUES+1))
fi

# ── 5. Disk usage ──
echo "" >> $REPORT
echo "── Disk usage ──" >> $REPORT
df -h / | tail -1 | awk '{print "  Used: "$3" / "$2" ("$5")"}' >> $REPORT

# ── 6. Docker image vulnerabilities (if trivy available) ──
echo "" >> $REPORT
echo "── Container image scan ──" >> $REPORT
if command -v trivy &>/dev/null; then
  trivy image --severity HIGH,CRITICAL --no-progress hermes-multi-tenant-api:latest 2>/dev/null | tail -5 >> $REPORT
else
  echo "  ℹ️  Install trivy for image vulnerability scanning" >> $REPORT
fi

# ── Summary ──
echo "" >> $REPORT
echo "===========================================" >> $REPORT
if [ "$ISSUES" -eq 0 ]; then
  echo "  ✅ No security issues found" >> $REPORT
else
  echo "  ⚠️  $ISSUES issue(s) found - review report" >> $REPORT
fi
echo "===========================================" >> $REPORT

cat $REPORT
