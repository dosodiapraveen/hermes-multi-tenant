# Hermes Multi-Tenant Platform — Architecture v2

## Stack Overview

| Layer | Choice | Why |
|-------|--------|-----|
| **Backend** | FastAPI | Input validation (Pydantic), async, fast to build |
| **Database** | PostgreSQL | Concurrent writes, Row-Level Security, encryption at rest |
| **Auth** | Supabase Auth (open source) | JWT + RBAC + MFA built in. Self-hostable. RLS at DB level. |
| **Frontend** | Vue 3 (admin dashboard) | Reactive, composable, good DX |
| **HTTPS** | Caddy | Auto TLS, simpler than Nginx |
| **Runtime** | Docker Compose | Easy deploy, consistent env |

## Why Supabase Auth Instead of Building JWT

| Building JWT ourselves | Supabase Auth |
|------------------------|---------------|
| Must implement token generation | Handles it |
| Must handle refresh token rotation | Built-in |
| Must implement password hashing | Built-in (bcrypt) |
| Must handle session management | Built-in |
| Must build admin/user role system | Built-in RBAC |
| Must implement rate limiting on auth | Built-in |
| Must handle MFA (eventually) | Built-in |
| Risk: one bug = auth bypass | Battle-tested by thousands of apps |

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                      Internet                              │
│  User (WhatsApp/Telegram)    Admin (Web)                   │
└────────┬────────────────────────────────────┬──────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────┐          ┌──────────────────────────┐
│   WhatsApp API /    │          │    Caddy (Reverse Proxy) │
│   Telegram API      │          │    Auto-TLS, HTTPS       │
└──────────┬──────────┘          └───────────┬──────────────┘
           │                                 │
           ▼                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Gateway       │  │ Admin API    │  │ Onboarding API   │  │
│  │ (msg routing) │  │ (users,      │  │ (invite link     │  │
│  │               │  │  config,     │  │  redemption,     │  │
│  │ WhatsApp →    │  │  stats)      │  │  WhatsApp        │  │
│  │ profile       │  │              │  │  onboarding)     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                           │                                 │
│            ┌──────────────┴──────────────┐                  │
│            │     Supabase Client          │                  │
│            │  (JWT validation, RLS proxy) │                  │
│            └──────────────┬──────────────┘                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Supabase       │ │  PostgreSQL  │ │    Redis          │
│   Auth           │ │  + RLS       │ │  (rate limiting,  │
│   (session mgmt) │ │              │ │   session cache)  │
│   JWT issuance   │ │  Users       │ │                   │
│   RBAC           │ │  Profiles    │ │                   │
│   MFA            │ │  Invite links│ │                   │
│   SSO            │ │  Logs        │ │                   │
└──────────────────┘ │  Billing     │ └──────────────────┘
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────────┐
                     │  Hermes Profiles │
                     │  (filesystem)    │
                     │                  │
                     │  ~/.hermes/      │
                     │  profiles/       │
                     │  ├── user_1/     │
                     │  ├── user_2/     │
                     │  └── ...        │
                     └──────────────────┘
```

## Data Model (PostgreSQL)

### Users Table (Managed by Supabase Auth + Extended by Us)

```sql
-- Supabase auth.users handles: id, email, password_hash, created_at, etc.

-- Our extension table:
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  phone_number TEXT UNIQUE,
  agent_name TEXT NOT NULL DEFAULT 'My Assistant',
  plan TEXT NOT NULL DEFAULT 'trial' CHECK (plan IN ('trial', 'basic', 'pro', 'business', 'vip')),
  trial_ends_at TIMESTAMPTZ,
  is_vip BOOLEAN DEFAULT FALSE,
  primary_model TEXT NOT NULL DEFAULT 'claude-sonnet-4-2026',
  backup_model TEXT NOT NULL DEFAULT 'accounts/fireworks/models/deepseek-v4',
  model_overridden_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row-Level Security: users can only see their own profile
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_self_access ON user_profiles
  FOR ALL USING (auth.uid() = id);

CREATE POLICY admin_all_access ON user_profiles
  FOR ALL USING (is_admin());
```

### Invite Links Table

```sql
CREATE TABLE invite_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,              -- short code for URL
  label TEXT NOT NULL,                    -- "Dr. Ananya Sharma"
  agent_name TEXT NOT NULL DEFAULT 'My Assistant',
  plan TEXT NOT NULL DEFAULT 'pro',
  trial_days INTEGER NOT NULL DEFAULT 7,  -- NULL = no expiry (VIP)
  is_vip BOOLEAN DEFAULT FALSE,
  claimed_by UUID REFERENCES auth.users(id),
  claimed_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,                  -- link itself expires
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE invite_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY admin_manage_links ON invite_links
  FOR ALL USING (is_admin());
```

### API Keys Table

```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider TEXT NOT NULL,                  -- 'anthropic', 'openai', 'fireworks'
  key_encrypted TEXT NOT NULL,             -- AES-256 encrypted
  key_prefix TEXT NOT NULL,                -- first 8 chars for identification
  is_active BOOLEAN DEFAULT TRUE,
  monthly_token_limit BIGINT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY only_admin_access_keys ON api_keys
  FOR ALL USING (is_admin());
```

### Logs Table

```sql
CREATE TABLE activity_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,                    -- 'message', 'model_switch', 'trial_expiring'
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partition by month for performance
```

## Security Architecture

### Layer 1: Network

```
Internet → Cloud Firewall → Caddy (TLS termination) → FastAPI
                                                          │
                                                          ▼
                                                    PostgreSQL (private network, no public port)
```

- VPC with private subnets
- PostgreSQL accessible only from the app server
- Redis accessible only from the app server
- All traffic is HTTPS (Caddy auto-TLS)

### Layer 2: Authentication (Supabase Auth)

**Who accesses what:**

| User Type | Can Access | Authentication |
|-----------|-----------|----------------|
| **Admin** (you) | Dashboard, all APIs, user overrides, config push, logs | Supabase Auth + MFA |
| **Regular user** | Their own settings page only | Supabase Auth (email+password or Google SSO) |
| **WhatsApp/Telegram user** | Only their agent via messaging | Phone number matching (no web login needed) |

**JWT flow:**

```
1. Admin logs in via Supabase Auth UI
2. Supabase issues JWT with role claim ('admin' or 'user')
3. FastAPI middleware validates JWT on every request
4. Supabase SDK verifies token signature
5. RLS policies enforce data access at database level

Admin JWT: { sub: "user-id", role: "admin", email: "prav@..." }
User JWT:  { sub: "user-id", role: "user", aud: "authenticated" }
```

### Layer 3: Database (Row-Level Security)

PostgreSQL RLS ensures that **even if the API has a bug**, data is still isolated:

```sql
-- A user can ONLY see their own profile
-- An admin can see ALL profiles
-- These are enforced at the database, not just the application

SELECT * FROM user_profiles;  
-- User sees: 1 row (their own)
-- Admin sees: N rows (all)
```

This is a defense-in-depth layer. The API could accidentally omit a `WHERE user_id = ?` clause and RLS would still prevent data leaks.

### Layer 4: Secrets (API Keys)

```
┌────────────────────────────────────────────┐
│  ~/.hermes/.env (root:root, chmod 600)     │
│                                             │
│  SUPABASE_URL=https://...                   │
│  SUPABASE_SERVICE_ROLE_KEY=...              │
│  ANTHROPIC_API_KEY=sk-ant-...              │
│  OPENAI_API_KEY=sk-...                     │
│  ENCRYPTION_KEY=... (AES-256 for DB keys)  │
└────────────────────────────────────────────┘
```

API keys stored in the database are **AES-256 encrypted at rest**. The encryption key lives only in `.env`. Even if the database is dumped, the keys are unreadable.

### Layer 5: Rate Limiting

```
Redis-based rate limiting:
- 30 messages/min per user (WhatsApp/Telegram)
- 100 API calls/min per admin (dashboard)
- 5 login attempts before 15-min lockout (Supabase handles this)
- 10 invite link generations/hour per admin
```

## Supabase Auth — Open Source Details

| Feature | Available? | Self-Hosted? |
|---------|-----------|-------------|
| Email + password login | ✅ | ✅ |
| Google / GitHub SSO | ✅ | ✅ |
| Magic link (passwordless) | ✅ | ✅ |
| MFA (TOTP) | ✅ | ✅ |
| Role-based access control | ✅ | ✅ |
| Row-Level Security in PostgreSQL | ✅ | ✅ |
| Rate limiting on auth | ✅ | ✅ |
| Audit logs | ✅ | ✅ |
| Session management | ✅ | ✅ |

**Self-hosting:** `supabase/self-hosted` Docker image. Run on the same VM. All open source.

**Or use cloud (free tier):** Up to 50,000 users, 500MB database, built-in auth UI. Free for MVP.

## Updated Directory Structure

```
/opt/hermes-platform/
├── docker-compose.yml
├── Caddyfile
├── .env                          # Secrets (root:root, 600)
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app
│   │   ├── config.py             # Settings from .env
│   │   ├── database.py           # Supabase/PostgreSQL client
│   │   ├── auth.py               # JWT validation middleware
│   │   ├── routers/
│   │   │   ├── admin.py          # Admin API
│   │   │   ├── users.py          # User settings API
│   │   │   ├── invite.py         # Invite link generation + redemption
│   │   │   └── webhook.py        # WhatsApp/Telegram webhooks
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── invite.py
│   │   │   └── api_key.py
│   │   └── services/
│   │       ├── hermes_manager.py  # Profile creation, config push
│   │       ├── model_router.py    # Primary → backup fallback
│   │       └── encryption.py      # AES-256 for API keys
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Users.vue
│   │   │   ├── InviteLinks.vue
│   │   │   └── Settings.vue
│   │   └── components/
│   └── Dockerfile
└── hermes/
    └── profiles/                  # Created at runtime
```

## Key Flows with This Architecture

### User Onboarding Via Invite Link

```
1. Admin creates invite link with label + trial duration
   → FastAPI: INSERT INTO invite_links (code, label, trial_days)
   → Supabase RLS: only admin role can insert
   
2. Admin copies link and sends to user via WhatsApp

3. User clicks link → WhatsApp Business API sends message
   → FastAPI webhook receives WhatsApp message
   → Gateway checks: phone number known? → No
   → Matches invite link code from URL parameter
   → Creates user in Supabase Auth (passwordless, just phone)
   → INSERT INTO user_profiles (phone, agent_name, plan, trial_ends_at)
   → Creates Hermes profile directory
   → Activates: phone → profile mapping in gateway
   → Triggers conversational onboarding (2 messages)
```

### Message Processing

```
1. User sends WhatsApp message
2. WhatsApp Business API → webhook → FastAPI
3. Gateway looks up phone number → finds profile
4. FastAPI calls Anthropic API with primary model
5. If 429/503/timeout → retry with backup model
6. Logs activity to PostgreSQL
7. Sends response via WhatsApp API
8. Checks trial expiry (if expiring soon, appends payment notice)
```

### Admin Config Push

```
1. Admin changes default model on dashboard
   → FastAPI: UPDATE user_profiles SET primary_model = ?
   (with WHERE role != 'admin' for "all users")
   
2. Or admin pushes to specific user:
   → FastAPI: UPDATE user_profiles SET primary_model = ? WHERE id = ?
   
3. Change takes effect immediately — next message uses new model
4. No restart needed. No profile files changed.
```

## Security Audit Checklist (Pre-Launch)

| Check | Status |
|-------|--------|
| PostgreSQL: only accessible from app server (no public port) | ⬜ |
| Supabase RLS policies enabled on all tables | ⬜ |
| API keys encrypted at rest in database | ⬜ |
| `.env` file: root-owned, chmod 600 | ⬜ |
| JWT validation on every API route | ⬜ |
| Rate limiting on auth endpoints (Supabase handles) | ⬜ |
| Rate limiting on API endpoints (FastAPI middleware) | ⬜ |
| CORS configured to only allow dashboard domain | ⬜ |
| HTTPS only (Caddy auto-enforces) | ⬜ |
| Input validation on all endpoints (Pydantic handles) | ⬜ |
| Logging enabled for all admin actions | ⬜ |
| Failed login monitoring (Supabase handles) | ⬜ |
