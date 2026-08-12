# Monitoring & Observability Guide

This guide explains the monitoring and logging infrastructure implemented in Phase 1 of the security improvements plan.

## Overview

The Hermes platform uses a comprehensive observability stack:

- **Structured Logging**: JSON-formatted logs with request correlation
- **Audit Logging**: Security event tracking in database
- **APM (Sentry)**: Error tracking and performance monitoring
- **Log Aggregation (Loki)**: Centralized log collection and querying
- **Dashboards (Grafana)**: Visual analytics and alerting

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Add to your `.env` file:

```bash
# Logging
LOG_LEVEL=INFO
JSON_LOGS=true

# Sentry (optional but recommended)
SENTRY_DSN=https://your-project@sentry.io/123456
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 3. Run Database Migration

Apply the audit logging schema:

```bash
# Connect to your database
psql $DATABASE_URL -f migrations/001_audit_logging.sql
```

### 4. Start Logging Stack (Optional)

For local development with Grafana/Loki:

```bash
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d
```

Access Grafana at `http://localhost:3000` (default: admin/admin)

## Structured Logging

### Log Format

All logs are output in JSON format with standard fields:

```json
{
  "timestamp": "2026-08-12T10:30:45.123456Z",
  "level": "info",
  "event": "user_login_success",
  "request_id": "abc123-def456-ghi789",
  "user_id": "user-uuid-here",
  "ip_address": "192.168.1.1",
  "email": "user@example.com"
}
```

### Request Correlation

Every HTTP request gets a unique `request_id` that appears in:
- All log entries for that request
- Response headers (`X-Request-ID`)
- Audit logs
- Sentry events

This enables tracing a single request through the entire system.

### Viewing Logs

**Docker containers:**
```bash
# View structured logs
docker logs hermes-backend -f | jq

# Filter by event type
docker logs hermes-backend | jq 'select(.event == "user_login_success")'

# Filter by user
docker logs hermes-backend | jq 'select(.user_id == "your-user-id")'
```

**Local development:**
```bash
# Human-readable console logs
LOG_LEVEL=DEBUG JSON_LOGS=false uvicorn app.main:app --reload
```

## Audit Logging

### What Gets Audited

The `audit_logs` table records:

**Authentication Events:**
- User login (success/failure)
- Admin login (success/failure)
- Email verification
- Password reset requests
- Password reset completions
- User registration

**Webhook Events:**
- Signature verification failures
- Message processing
- Document uploads

**Future (Phase 2+):**
- Admin user operations (create/update/delete)
- API key management
- Model overrides
- Data exports

### Querying Audit Logs

```sql
-- Recent failed login attempts
SELECT timestamp, ip_address, details
FROM audit_logs
WHERE event_type = 'login_failed'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- User activity timeline
SELECT timestamp, event_type, ip_address, details
FROM audit_logs
WHERE user_id = 'user-uuid-here'
ORDER BY timestamp DESC
LIMIT 50;

-- Security alerts (warnings and errors)
SELECT timestamp, event_type, severity, ip_address, details
FROM audit_logs
WHERE severity IN ('warning', 'error', 'critical')
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- Brute force detection (5+ failed logins from same IP)
SELECT ip_address, COUNT(*) as attempts,
       MIN(timestamp) as first_attempt,
       MAX(timestamp) as last_attempt
FROM audit_logs
WHERE event_type = 'login_failed'
  AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
HAVING COUNT(*) >= 5
ORDER BY attempts DESC;
```

### Audit Log Retention

Audit logs are retained indefinitely by default. To set up automatic cleanup:

```sql
-- Delete logs older than 1 year
DELETE FROM audit_logs
WHERE timestamp < NOW() - INTERVAL '1 year';

-- Archive to separate table before deleting
INSERT INTO audit_logs_archive
SELECT * FROM audit_logs
WHERE timestamp < NOW() - INTERVAL '1 year';
```

## Sentry Integration

### Setup

1. Create a Sentry account at https://sentry.io
2. Create a new project for "hermes-api"
3. Copy the DSN to your `.env` file:

```bash
SENTRY_DSN=https://abc123@o12345.ingest.sentry.io/67890
SENTRY_ENVIRONMENT=production
```

4. Restart your backend: `docker-compose restart backend`

### Features Enabled

- **Automatic Error Capture**: All unhandled exceptions
- **Performance Monitoring**: 10% of requests sampled
- **Breadcrumbs**: Logs leading up to errors
- **User Context**: User ID and email attached to errors
- **Release Tracking**: Version information for each deployment

### Viewing Errors

1. Go to your Sentry dashboard
2. View "Issues" to see all errors
3. Click on an issue to see:
   - Stack trace
   - User context (ID, email)
   - Request details (URL, headers, body)
   - Breadcrumbs (logs before error)
   - Performance data

### Performance Monitoring

Sentry captures performance data for slow endpoints:

- Request duration
- Database query times
- External API calls
- Memory usage

Set sample rate in `.env`:
```bash
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of requests
```

## Grafana & Loki

### Starting the Stack

```bash
# Start logging stack
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d

# Check status
docker ps | grep -E "loki|promtail|grafana"

# View logs
docker logs hermes-loki
docker logs hermes-promtail
docker logs hermes-grafana
```

### Accessing Grafana

1. Open `http://localhost:3000`
2. Login (default: `admin` / `admin`)
3. Change password on first login
4. Navigate to "Explore" → Select "Loki" datasource

### Query Examples

**View all backend logs:**
```logql
{container_name=~".*hermes-backend.*"}
```

**Filter by log level:**
```logql
{container_name=~".*hermes-backend.*"} |= "level" | json | level="error"
```

**Find failed logins:**
```logql
{container_name=~".*hermes-backend.*"} | json | event="user_login_failed"
```

**Trace a specific request:**
```logql
{container_name=~".*hermes-backend.*"} | json | request_id="abc123-def456"
```

**Count errors by type:**
```logql
sum by (event) (count_over_time({container_name=~".*hermes-backend.*"}
  | json | level="error" [1h]))
```

### Creating Dashboards

1. Go to "Dashboards" → "New Dashboard"
2. Add panel with query
3. Configure visualization (graph, table, stat)
4. Save dashboard

**Recommended Panels:**
- Error rate over time
- Requests per second
- Average response time
- Failed login attempts
- Top error types

### Setting Up Alerts

1. Edit a dashboard panel
2. Click "Alert" tab
3. Define alert condition (e.g., error rate > 10/min)
4. Configure notification channels (email, Slack, PagerDuty)

Example alert rule:
```logql
sum(rate({container_name=~".*hermes-backend.*"}
  | json | level="error" [5m])) > 10
```

## Log Retention

### Loki Retention

Configured in `loki-config.yml`:
```yaml
limits_config:
  retention_period: 720h  # 30 days
```

To change retention:
1. Edit `loki-config.yml`
2. Restart Loki: `docker-compose -f docker-compose.logging.yml restart loki`

### Database Audit Logs

No automatic retention. Set up a cron job for cleanup:

```bash
# Add to crontab
0 2 * * * psql $DATABASE_URL -c "DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '1 year';"
```

## Performance Impact

Logging overhead is minimal:

- **Structured logging**: <2ms per request
- **Audit logging**: <5ms per event (async database insert)
- **Sentry**: <3ms per request (when sampled)
- **Total**: <10ms overhead per request

For high-traffic systems, consider:
- Reducing Sentry sample rate: `SENTRY_TRACES_SAMPLE_RATE=0.01`
- Async audit logging (already implemented)
- Log sampling for very high volumes

## Troubleshooting

### Logs Not Appearing in Grafana

1. Check Promtail is running:
   ```bash
   docker logs hermes-promtail
   ```

2. Verify Loki is receiving logs:
   ```bash
   curl http://localhost:3100/ready
   ```

3. Check Promtail configuration:
   ```bash
   docker exec hermes-promtail cat /etc/promtail/config.yml
   ```

### Sentry Not Capturing Errors

1. Verify DSN is set:
   ```bash
   docker exec hermes-backend env | grep SENTRY
   ```

2. Check Sentry initialization in logs:
   ```bash
   docker logs hermes-backend | grep sentry_initialized
   ```

3. Test with a manual error:
   ```python
   import sentry_sdk
   sentry_sdk.capture_message("Test error")
   ```

### Database Migration Fails

If audit_logs table already exists:
```sql
-- Drop and recreate
DROP TABLE IF EXISTS audit_logs CASCADE;
-- Then run migration again
```

## Best Practices

### 1. Always Include Context

When logging, include relevant context:
```python
logger.info("user_action",
    user_id=user_id,
    action="create_note",
    note_id=note_id
)
```

### 2. Use Appropriate Log Levels

- `DEBUG`: Detailed diagnostic info (not in production)
- `INFO`: Normal operations, successful actions
- `WARNING`: Unexpected but handled (failed login, invalid input)
- `ERROR`: Error conditions that need attention
- `CRITICAL`: System failures requiring immediate action

### 3. Don't Log Sensitive Data

Never log:
- Passwords (even hashed)
- API keys
- Session tokens
- Credit card numbers
- Full email addresses in public logs (mask: us***@example.com)

### 4. Use Request Correlation

Access request_id in handlers:
```python
from fastapi import Request

@app.get("/api/users")
async def get_users(request: Request):
    request_id = getattr(request.state, "request_id", None)
    logger.info("fetching_users", request_id=request_id)
```

### 5. Monitor Your Monitors

Set up alerts for:
- Loki disk usage (>80%)
- Promtail lag (>1 minute)
- Sentry quota usage (approaching limit)

## Next Steps

After Phase 1 is verified, move to:
- **Phase 2**: Cookie-based auth + CSRF (see plan)
- **Phase 3**: API key encryption
- **Phase 4**: Data encryption
- **Phase 5**: Encrypted backups

## Support

For issues or questions:
- Check Sentry errors first
- Query audit_logs for security events
- Review Grafana dashboards for patterns
- Check structured logs for detailed traces
