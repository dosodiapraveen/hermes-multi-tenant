# Phase 1 Verification Checklist

This document provides step-by-step verification for the Phase 1 Monitoring & Audit Logging implementation.

## Prerequisites

1. Updated `.env` file with logging configuration
2. Database migration applied
3. Dependencies installed (`pip install -r backend/requirements.txt`)
4. Containers rebuilt if using Docker

## Verification Steps

### 1. Structured Logging ✓

**Test:** Verify JSON-formatted logs appear in output

```bash
# Start the backend
docker-compose up -d api

# View logs
docker logs api -f | tail -20
```

**Expected Output:**
```json
{
  "timestamp": "2026-08-12T10:30:45.123456Z",
  "level": "info",
  "event": "request_started",
  "request_id": "abc123-def456",
  "method": "GET",
  "path": "/api/health"
}
```

**Verification:**
- [ ] Logs are in JSON format
- [ ] Each log has `timestamp`, `level`, `event` fields
- [ ] Request ID appears in logs
- [ ] No errors during startup

---

### 2. Request Correlation ✓

**Test:** Verify all logs for a single request share the same request_id

```bash
# Make a request
curl http://localhost:8000/api/health

# Check logs
docker logs api | tail -50 | jq 'select(.request_id != null)'
```

**Expected Output:**
Multiple log entries with the same `request_id`:
```json
{"request_id": "abc-123", "event": "request_started", ...}
{"request_id": "abc-123", "event": "request_completed", ...}
```

**Verification:**
- [ ] Single request generates multiple logs
- [ ] All logs for one request have same `request_id`
- [ ] Response includes `X-Request-ID` header

---

### 3. Audit Logs Table ✓

**Test:** Verify audit_logs table exists with correct schema

```bash
# Connect to database
docker exec -it postgres psql -U hermes -d hermes

# Check table
\d audit_logs

# Check indexes
\di audit_logs*
```

**Expected Output:**
```
                                      Table "public.audit_logs"
   Column    |           Type           | Nullable |                 Default
-------------+--------------------------+----------+-----------------------------------------
 id          | bigint                   | not null | nextval('audit_logs_id_seq'::regclass)
 event_type  | text                     | not null |
 severity    | text                     | not null |
 user_id     | text                     |          |
 ip_address  | text                     |          |
 user_agent  | text                     |          |
 request_id  | text                     |          |
 admin_email | text                     |          |
 details     | jsonb                    |          | '{}'::jsonb
 timestamp   | timestamp with time zone | not null | now()
```

**Verification:**
- [ ] Table `audit_logs` exists
- [ ] All expected columns present
- [ ] Indexes created (6 indexes total)
- [ ] Severity check constraint exists

---

### 4. Login Audit Logging ✓

**Test:** Failed login creates audit log entry

```bash
# Attempt failed login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'

# Check audit logs
docker exec postgres psql -U hermes -d hermes -c \
  "SELECT event_type, severity, details FROM audit_logs ORDER BY timestamp DESC LIMIT 5;"
```

**Expected Output:**
```
     event_type      | severity |                    details
---------------------+----------+-----------------------------------------------
 admin_login_failed  | warning  | {"email": "test@example.com"}
```

**Verification:**
- [ ] Failed login creates audit log entry
- [ ] Event type is `admin_login_failed` or `login_failed`
- [ ] Severity is `warning`
- [ ] Details include email address
- [ ] IP address captured

---

### 5. Successful Login Audit Log ✓

**Test:** Successful login creates audit log with correct data

```bash
# Login with correct credentials (adjust based on your setup)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hermes.io","password":"your_password"}'

# Check audit logs
docker exec postgres psql -U hermes -d hermes -c \
  "SELECT timestamp, event_type, severity, admin_email, ip_address
   FROM audit_logs
   WHERE event_type='admin_login'
   ORDER BY timestamp DESC LIMIT 1;"
```

**Expected Output:**
```
        timestamp        |  event_type  | severity |   admin_email    | ip_address
-------------------------+--------------+----------+------------------+------------
 2026-08-12 10:45:23.456 | admin_login  | info     | admin@hermes.io  | 172.18.0.1
```

**Verification:**
- [ ] Successful login creates audit log
- [ ] Event type is `admin_login`
- [ ] Severity is `info`
- [ ] Admin email captured
- [ ] IP address captured

---

### 6. Enhanced Activity Logs ✓

**Test:** Verify activity_logs has new columns

```bash
docker exec postgres psql -U hermes -d hermes -c "\d activity_logs"
```

**Expected Output:**
```
   Column    |           Type           | Nullable |                  Default
-------------+--------------------------+----------+-------------------------------------------
 id          | bigint                   | not null | nextval('activity_logs_id_seq'::regclass)
 user_id     | text                     |          |
 action      | text                     | not null |
 details     | jsonb                    |          | '{}'::jsonb
 request_id  | text                     |          |  ← NEW
 ip_address  | text                     |          |  ← NEW
 admin_id    | text                     |          |  ← NEW
 created_at  | timestamp with time zone | not null | now()
```

**Verification:**
- [ ] `request_id` column exists
- [ ] `ip_address` column exists
- [ ] `admin_id` column exists

---

### 7. Sentry Integration (Optional) ✓

**Test:** Verify Sentry initialization if DSN configured

```bash
# Check if Sentry initialized
docker logs api | grep "sentry_initialized"
```

**Expected Output:**
```json
{
  "timestamp": "2026-08-12T10:00:00Z",
  "level": "info",
  "event": "sentry_initialized",
  "environment": "production"
}
```

**Verification:**
- [ ] Sentry initialization log appears
- [ ] No Sentry errors in logs
- [ ] Dashboard shows events (if DSN configured)

**To trigger test error:**
```bash
# This endpoint doesn't exist, will cause 404 (should appear in Sentry)
curl http://localhost:8000/api/trigger-error
```

---

### 8. Webhook Signature Validation Logging ✓

**Test:** Invalid webhook secret creates audit log

```bash
# Send request with invalid secret
curl -X POST http://localhost:8000/api/webhook/telegram \
  -H "X-Telegram-Bot-Api-Secret-Token: invalid" \
  -H "Content-Type: application/json" \
  -d '{}'

# Check audit logs
docker exec postgres psql -U hermes -d hermes -c \
  "SELECT event_type, severity, details FROM audit_logs
   WHERE event_type='webhook_signature_failed'
   ORDER BY timestamp DESC LIMIT 1;"
```

**Expected Output:**
```
       event_type         | severity |                details
--------------------------+----------+----------------------------------------
 webhook_signature_failed | warning  | {"platform": "telegram", "reason": ...}
```

**Verification:**
- [ ] Invalid signature creates audit log
- [ ] Severity is `warning`
- [ ] Platform (telegram) captured
- [ ] IP address logged

---

### 9. Slow Request Detection ✓

**Test:** Requests >1 second generate warning log

```bash
# Make slow request (if you have a slow endpoint)
# Or check logs for any existing slow requests
docker logs api | jq 'select(.event == "slow_request_detected")'
```

**Expected Output:**
```json
{
  "event": "slow_request_detected",
  "level": "warning",
  "duration_ms": 1250.45,
  "threshold_ms": 1000,
  "path": "/api/some/slow/endpoint"
}
```

**Verification:**
- [ ] Slow requests logged with duration
- [ ] Threshold_ms shown (1000)
- [ ] Path included in log

---

### 10. Grafana Loki Stack (Optional) ✓

**Test:** Start logging stack and verify connectivity

```bash
# Start logging stack
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d

# Check all services running
docker ps | grep -E "loki|promtail|grafana"

# Verify Loki is ready
curl http://localhost:3100/ready

# Verify Grafana is accessible
curl http://localhost:3000/login
```

**Access Grafana:**
1. Open http://localhost:3000
2. Login: `admin` / `admin` (or your configured password)
3. Go to "Explore"
4. Select "Loki" datasource
5. Query: `{container_name=~".*api.*"}`

**Verification:**
- [ ] Loki responding on port 3100
- [ ] Promtail running without errors
- [ ] Grafana accessible on port 3000
- [ ] Loki datasource configured
- [ ] Logs visible in Explore view

---

## Performance Verification

### 11. Logging Overhead ✓

**Test:** Measure performance impact

```bash
# Benchmark without logging (not recommended, just for testing)
# Set LOG_LEVEL=CRITICAL to minimize logging
docker exec api sh -c 'LOG_LEVEL=CRITICAL python -m pytest --benchmark'

# Benchmark with logging
docker exec api sh -c 'LOG_LEVEL=INFO python -m pytest --benchmark'
```

**Expected:**
- Overhead < 10ms per request
- No memory leaks
- CPU impact < 5%

**Verification:**
- [ ] Response time increase < 10ms
- [ ] No error rate increase
- [ ] Memory usage stable

---

## Rollback Procedure

If Phase 1 causes issues, rollback:

### Quick Rollback (Disable Sentry)

```bash
# Remove Sentry DSN from .env
sed -i '/SENTRY_DSN/d' .env

# Restart backend
docker-compose restart api
```

### Full Rollback (Remove Logging)

```bash
# Restore old main.py (if you have backup)
git checkout main backend/app/main.py backend/app/routers/user_auth.py

# Remove audit logging from database
docker exec postgres psql -U hermes -d hermes -c "DROP TABLE IF EXISTS audit_logs CASCADE;"

# Restart
docker-compose restart api
```

---

## Common Issues

### Issue: Audit logs table missing

**Solution:**
```bash
docker exec postgres psql -U hermes -d hermes -f /docker-entrypoint-initdb.d/init.sql
# Or run migration:
docker exec postgres psql -U hermes -d hermes < migrations/001_audit_logging.sql
```

### Issue: Logs not in JSON format

**Solution:**
```bash
# Check .env file
grep JSON_LOGS .env
# Should show: JSON_LOGS=true

# Restart backend
docker-compose restart api
```

### Issue: Sentry not capturing errors

**Solution:**
```bash
# Verify DSN in container
docker exec api env | grep SENTRY

# Check initialization log
docker logs api | grep sentry_initialized

# If missing, check .env file and restart
```

### Issue: Request ID not appearing

**Solution:**
```bash
# Verify middleware is registered
docker exec api python -c "from app.main import app; print([m for m in app.user_middleware])"

# Should include LoggingMiddleware
```

---

## Success Criteria

Phase 1 is successfully implemented when:

- [x] Structured logging operational (JSON format)
- [x] Request correlation IDs present in all logs
- [x] Audit logs table created with indexes
- [x] Failed login attempts logged to audit_logs
- [x] Successful logins logged with user context
- [x] Webhook events logged with IP and details
- [x] Sentry captures exceptions (if configured)
- [x] Grafana shows logs from Loki (if enabled)
- [x] Performance overhead < 10ms per request
- [x] No data loss during migration

---

## Next Steps

Once Phase 1 is verified:

1. Monitor production for 1 week
2. Review audit logs for patterns
3. Set up Grafana dashboards
4. Configure Sentry alerts
5. Proceed to **Phase 2: Cookie-based Auth + CSRF**

---

## Documentation

- Full monitoring guide: `docs/MONITORING.md`
- Implementation plan: See original security improvements plan
- Rollback procedures: This document, "Rollback Procedure" section
