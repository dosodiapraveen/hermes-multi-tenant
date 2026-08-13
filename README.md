# Hermes Multi-Tenant Platform

AI agent platform — each user gets an isolated Hermes agent with their own profile, memories, skills, and Obsidian vault.

## Architecture

```
Caddy (HTTPS) → Frontend (Vue SPA) → API (FastAPI) → PostgreSQL
                 → Telegram Bot    →                → Redis
```

## Quick Deploy

### Prerequisites
- Ubuntu 24.04 server with Docker + Docker Compose
- Domain pointing to server (e.g., `beprepared.dev`)
- API keys in `.env` (see `.env.example`)

### Setup

```bash
# Clone
git clone https://github.com/dosodiapraveen/hermes-multi-tenant.git
cd hermes-multi-tenant

# Configure
cp .env.example .env
# Edit .env with your keys (see below)

# Deploy
docker compose up -d --build
```

### Required .env Values

| Variable | Where to get it |
|----------|-----------------|
| `DB_PASSWORD` | Generate a random password |
| `DATABASE_URL` | `postgresql+asyncpg://hermes:${DB_PASSWORD}@postgres:5432/hermes` |
| `FIREWORKS_API_KEY` | https://app.fireworks.ai |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase publishable key |
| `TELEGRAM_BOT_TOKEN` | @BotFather on Telegram |
| `RESEND_API_KEY` | https://resend.com (optional — onboarding emails) |
| `PUBLIC_URL` | `https://beprepared.dev` |

## Services

| Service | Port | Access |
|---------|------|--------|
| API | 8000 | Internal only (via Caddy) |
| Frontend | 80 | Internal only (via Caddy) |
| Caddy | 443 | Public (HTTPS) |
| PostgreSQL | 5432 | Internal only |
| Redis | 6379 | Internal only |

## User Onboarding

1. **Admin** creates invite link in admin dashboard
2. **User** clicks invite link → sees onboarding page
3. **User** taps Telegram button → bot activates profile automatically
4. **User** sends any message → isolated agent responds

### Linking Existing Users to Telegram
```bash
# Admin generates one-tap link for a user
curl -X POST https://beprepared.dev/api/admin/users/{user_id}/telegram-link \
  -H "Authorization: Bearer $TOKEN"
```
Share the returned `link_url` with the user — they tap to connect.

## Daily Operations

| Time | Task | Description |
|------|------|-------------|
| Every 5 min | Health check | API, DB, disk, containers → Telegram alert |
| Every min | **Reminder worker** | Fires due reminders via Telegram + marks done |
| 12:00 AM | **Security scan** | Open ports, permissions, Docker audit, SSH attempts |
| 3:00 AM | Backup | Full DB + profiles + vaults (14-day retention) |
| 8:00 AM | Usage report | Daily stats sent to admin |
| 8:30 AM | Morning tips | Proactive engagement sent to all Telegram users |

## Restore

```bash
# Copy backup to server, then:
./restore.sh /opt/hermes/backups/hermes-backup-YYYYMMDD-HHMMSS.tar.gz
docker compose restart api
```

## Security

- **Caddy** auto-renews TLS via Let's Encrypt
- **JWT auth** with Supabase validation + dev fallback
- **Rate limiting** via slowapi (30 req/min)
- **Security scan** runs daily at midnight
- **.env** must be chmod 600

## Scaling

To add a new server:

```bash
# 1. Provision Ubuntu 24.04
# 2. Install Docker + Docker Compose
# 3. Clone repo
# 4. Copy .env from existing server (sensitive!)
# 5. docker compose up -d --build
# 6. Restore latest backup: ./restore.sh <backup-file>
```
