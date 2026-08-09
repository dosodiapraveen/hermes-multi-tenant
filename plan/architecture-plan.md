# Hermes Multi-Tenant Hosting Platform — Architecture Plan

## Requirements Summary

1. **Multi-tenant**: Isolated agents per user, no data mingling
2. **Cost-effective**: Cloud hosting, minimal waste
3. **Central management**: Single-point upgrades for version, skills, config
4. **User portal**: Users create/configure agents via UI, no server access
5. **Channel connectivity**: WhatsApp and Telegram per user
6. **Model flexibility**: Admin controls available models, users pick from list

---

## Core Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Management Dashboard         │
                    │   (Admin Panel + User Portal)        │
                    └──┬──────────────┬───────────────────┘
                       │              │
             ┌─────────▼──┐    ┌──────▼──────────┐
             │ Admin APIs  │    │  User APIs      │
             │ (config,    │    │ (profile mgmt,  │
             │  users,     │    │  channel connect)│
             │  upgrades)  │    └──────┬──────────┘
             └─────────┬──┘           │
                       │              │
              ┌────────▼──────────────▼───────────┐
              │         Hermes Gateway             │
              │  (message routing by chat ID)      │
              │  listens on Telegram + WhatsApp    │
              └────────┬──────────────┬────────────┘
                       │              │
              ┌────────▼──┐    ┌──────▼──────────┐
              │  Profile 1 │    │   Profile 2     │    ... Profile N
              │  (User A)  │    │   (User B)      │
              │  ┌──────┐  │    │  ┌──────┐       │
              │  │Memory│  │    │  │Memory│       │
              │  │Skills│  │    │  │Skills│       │
              │  │Config│  │    │  │Config│       │
              │  └──────┘  │    │  └──────┘       │
              └────────────┘    └──────────────────┘
                          │
              ┌───────────▼────────────┐
              │  Shared Skill Library  │
              │  (centrally managed)   │
              └────────────────────────┘
```

## Key Design Decisions

### Profile-Based Isolation (not containers)

Each user gets a Hermes **profile** — not a separate Docker container. Hermes natively supports profiles with isolated:

- `~/.hermes/profiles/<user>/config.yaml`
- `~/.hermes/profiles/<user>/skills/`
- `~/.hermes/profiles/<user>/state.db` (session store)
- `~/.hermes/profiles/<user>/memories/`

**Why profiles over containers:**
- Single Hermes process — lower memory (1 Hermes = ~200MB RAM vs Docker per user = ~500MB+)
- Single upgrade point — update Hermes once, all profiles inherit
- Native routing — the gateway maps chat IDs to profiles at the config level
- Profiles consume ~2-5MB each of disk (just config + small SQLite DBs)

**When to add a second VM:** Around 50-100 users or when the single process hits rate limits.

### Gateway Routing

Hermes gateway already supports multi-platform, multi-profile routing. The gateway config maps each incoming message to a profile:

```yaml
gateway:
  telegram:
    bots:
      - token: "BOT_TOKEN_1"
        profile: "user_alpha"
      - token: "BOT_TOKEN_2"
        profile: "user_beta"
  whatsapp:
    accounts:
      - phone: "+1234567890"
        profile: "user_alpha"
```

Each user gets their own Telegram bot token (create via BotFather) or WhatsApp Business API account. The gateway routes their messages to the right profile. Data never crosses between profiles.

---

## Infrastructure & Hosting

### Option 1: Single VM (Recommended for Launch)

| Provider | Spec | Cost | Users Supported |
|----------|------|------|-----------------|
| **Hetzner** CX22 | 2 vCPU, 4GB RAM | ~€9/mo | 10-30 users |
| **Hetzner** CX32 | 4 vCPU, 8GB RAM | ~€18/mo | 30-80 users |
| **DigitalOcean** Basic | 4GB, 2 vCPU | $24/mo | 20-50 users |

**Software stack on VM:**
- Ubuntu 24.04 LTS
- Hermes (installed via pip/git)
- Nginx + Let's Encrypt (for dashboard)
- Python FastAPI (management API)
- Simple Vue dashboard (static files)
- SQLite (user database, scales fine for <200 users)

### Option 2: Docker Compose (Easier Upgrades)

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    volumes:
      - profiles:/home/hermes/.hermes/profiles
      - shared_skills:/home/hermes/.hermes/skills
      - config:/home/hermes/.hermes/config.yaml
    restart: unless-stopped
  
  dashboard:
    build: ./dashboard
    ports:
      - "8080:80"
    volumes:
      - profiles:/data/profiles
      - user_db:/data/users.sqlite
  
  gateway:
    image: nousresearch/hermes-gateway:latest
    depends_on: [hermes]
```

**Upgrade process:** `docker compose pull && docker compose up -d` — zero config change needed.

---

## Profile Management & Data Isolation

### Directory Structure

```
~/.hermes/
├── profiles/
│   ├── user_alpha/
│   │   ├── config.yaml          # User-specific config
│   │   ├── state.db             # Sessions (isolated)
│   │   ├── memories/
│   │   │   ├── memory.json      # User's memory (isolated)
│   │   │   └── user_profile.json
│   │   └── skills/
│   │       └── user_custom/     # User's custom skills
│   ├── user_beta/
│   └── ...
├── skills/
│   ├── global/                   # Admin-managed global skills
│   │   ├── blogwatcher.md
│   │   ├── voice-notes.md
│   │   └── ...
│   └── ...
└── config.yaml                   # Base config (admin)
```

### Isolation Guarantee

| Layer | Isolation Mechanism |
|-------|-------------------|
| Sessions | Separate SQLite DB per profile (`state.db`) |
| Memory | Separate JSON files per profile |
| Skills | Profile-level directory + global symlinks |
| Config | Separate `config.yaml` per profile |
| API Tokens | Each user gets their own Telegram bot / WhatsApp account |
| Files | All file operations scoped to profile's workdir |

### What Users CANNOT See

- Other users' chat history
- Other users' memory/knowledge base
- Other users' config (API keys, model settings)
- Other users' Telegram bot tokens
- Server-level credentials

---

## Central Management System

### Admin Capabilities

| Feature | Implementation |
|---------|---------------|
| **Create user** | CLI: `manage users create --name "Alpha" --telegram-token "..."` → Creates profile + gateway entry |
| **Delete user** | CLI: `manage users delete alpha` → Removes profile + gateway config |
| **Push config update** | CLI: `manage config set model.default "claude-sonnet-4" --all` → Updates every profile's config.yaml |
| **Update Hermes version** | `git pull && pip install -e . && hermes gateway restart` → All profiles use new version |
| **Push global skills** | Admin edits skills in `~/.hermes/skills/global/` → All profiles auto-inherit on next load |
| **Monitor usage** | Dashboard shows: tokens consumed/user, active users, errors, latency |
| **Set available models** | Define a whitelist in base config. Users pick from the list. |
| **View logs** | Per-user log streaming via dashboard |

### User Capabilities (via Web Dashboard)

| Feature | Implementation |
|---------|---------------|
| **Connect Telegram** | Enter bot token (from BotFather) → gateway auto-configures |
| **Connect WhatsApp** | QR code scan or API key entry |
| **Choose model** | Dropdown of admin-approved models (e.g., Claude Sonnet, GPT-5, DeepSeek) |
| **Basic personality** | Text field: "You are a helpful assistant that speaks like a pirate" |
| **View usage** | Monthly token count, active conversations |
| **Chat history** | Read-only view of recent conversations |
| **Enable/disable skills** | Toggle from a list of available global skills |
| **Add custom instructions** | Free-text field that becomes the system prompt |

### CLI Commands for Admin (via `manage` tool)

```bash
# User management
manage users create --name "alpha" --model "claude-sonnet-4"
manage users delete --name "alpha"
manage users list
manage users show --name "alpha"

# Config management
manage config set --key "model.provider" --value "anthropic" --all
manage config set --key "model.default" --value "gpt-5" --user "alpha"
manage config set --key "stt.enabled" --value "false" --all
manage config diff --user "alpha" --user "beta"  # Compare configs

# Skill management
manage skills install --skill "blogwatcher" --all
manage skills install --skill "excalidraw" --user "alpha"
manage skills list --all
manage skills update --all

# Version management
manage version current
manage version upgrade
manage version rollback

# Monitoring
manage stats users
manage stats usage --user "alpha"
manage logs tail --user "beta"  # Live log streaming
```

---

## Skills Management Architecture

```
Admin edits skill
        │
        ▼
┌──────────────────────┐
│  ~/.hermes/skills/   │  ← Global skills (shared across profiles)
│  global/              │
│  ├── blogwatcher.md  │
│  └── voice-notes.md  │
└──────────┬───────────┘
           │
           │ Hermes reads from both directories
           ▼
┌─────────────────────────────────────┐
│  Profile loads:                     │
│  global/ + profile/ = full skill set│
└─────────────────────────────────────┘
```

- Global skills are shared via a config path or symlink
- Users can toggle global skills on/off
- Custom skills stay in the user's profile directory
- Skill updates to global = instant across all profiles (next message)

---

## Configuration Template System

Each profile's `config.yaml` merges:

```yaml
# Base config (admin-managed, pushed to all)
model:
  provider: openai       # Admin can swap all users at once
  default: gpt-5
stt:
  enabled: true
tts:
  provider: edge

# Profile overrides (user-specific, never overwritten by push)
gateway:
  telegram:
    bot_token: "xxx"     # Unique per user
profile:
  name: "Alpha's Agent"
  personality: "Helpful and concise"
```

Config push only touches base-level keys. User-specific settings are protected. The `manage config set` command always knows which keys are "admin-overridable" vs "user-owned."

---

## Cost Breakdown (Launch Phase)

### Monthly Operating Costs

| Item | Cost | Notes |
|------|------|-------|
| **VM** (Hetzner CX22) | ~€9 | 2 vCPU, 4GB RAM. Handles 10-30 users. |
| **Domain + SSL** | ~$1 | DuckDNS or Namecheap + Let's Encrypt |
| **Telegram bot tokens** | Free | Unlimited from BotFather |
| **WhatsApp API** | ~$0 | WhatsApp Business API is free for low volume |
| **Model API costs** | Pass-through | Users pay their own API key, or you bundle it |
| **Total base** | **~$11/mo** | For up to 30 users |

### Per-User API Cost (if you bundle model access)

Using a provider like OpenRouter or direct API:
- Claude Sonnet: ~$3-5/user/month at 100K tokens/day
- GPT-5 mini: ~$1-2/user/month
- DeepSeek V4: ~$0.50-1/user/month

**At 20 users: $11 VM + $20-100 API = $31-111/mo total**

### Pricing to Users

| Tier | Features | Price |
|------|----------|-------|
| **Basic** | 1 agent, Telegram, 100K tokens/mo | $5/mo |
| **Pro** | WhatsApp + Telegram, 500K tokens, custom skills | $15/mo |
| **Business** | Priority, 2M tokens, custom model | $35/mo |

**At 20 users (mix): ~$200-400/mo revenue vs $30-110/mo cost → 60-80% margin**

---

## Build vs Buy

### Existing Options (Don't Build These From Scratch)

| Option | What It Is | Cost | Limitations |
|--------|-----------|------|-------------|
| **Agent 37** | White-label Hermes hosting | $3.99/mo per agent | Managed by them. Less control over upgrades. |
| **xCloud** | Managed Hermes hosting | ~$10-20/mo per instance | Enterprise-focused. Less flexibility. |
| **Self-hosted profiles** | DIY with Hermes native profiles | ~$11/mo total | Requires building the management layer. Full control. |

**Recommendation:** Self-host with profiles. The multi-tenant management layer is the value you're building — it's the product. Agent 37/xCloud sell infrastructure, not management capabilities.

### What You Need to Build

| Component | Build or Use | Effort |
|-----------|-------------|--------|
| **Hermes installation** | Use existing | 0 |
| **Profile management** | CLI scripts (~200 lines Python) | 1 day |
| **Gateway config** | Use Hermes gateway natively | 0 |
| **Admin dashboard** | Simple FastAPI + Vue (~500 lines) | 3-5 days |
| **User portal** | Same dashboard, user views | 2-3 days |
| **Config push system** | Python script reading/writing YAML | 1 day |
| **Skills sync** | Symlinks + file copy | 0.5 day |
| **Billing/subscriptions** | Stripe/LemonSqueezy integration | 2 days |
| **Monitoring** | Prometheus + Grafana or simple logs | 2 days |

**Total build time: ~10-14 days for MVP**

---

## Build Sequence (Recommended)

### Week 1: Infrastructure + Core
- [ ] Set up Hetzner VM with Docker
- [ ] Install Hermes with profiles
- [ ] Create profile management CLI (`manage` tool)
- [ ] Test multi-profile isolation
- [ ] Set up gateway with 2 test users

### Week 2: Management Dashboard
- [ ] Build admin API (user CRUD, config push, logs)
- [ ] Build simple web dashboard (Vue/React)
- [ ] Build user portal (model selection, channel connect)
- [ ] Implement config template system
- [ ] Set up global skills directory + sync

### Week 3: User Flows + Polish
- [ ] Telegram bot token flow (user creates bot → enters token → linked)
- [ ] WhatsApp connect flow
- [ ] Billing integration
- [ ] Usage monitoring dashboard
- [ ] Onboarding docs

---

## Scaling Path

| Stage | Users | Infrastructure | Monthly Cost | Revenue Potential |
|-------|-------|---------------|-------------|-------------------|
| **Launch** | 10-30 | 1 Hetzner VM (€9) | ~$11 + API | $200-800 |
| **Growth** | 30-100 | 2 VMs + Docker | ~$30-50 | $1,500-5,000 |
| **Scale** | 100-500 | 3-5 VMs, load-balanced | ~$100-200 | $5,000-25,000 |
| **Enterprise** | 500+ | Kubernetes, dedicated infra | $500-2000 | $25,000+ |

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Profile isolation breach** | Each profile runs with its own env vars. File system access is scoped. Gateway never exposes cross-profile data. |
| **Gateway overload at scale** | Profiles don't add per-message overhead. 10 vs 100 profiles use the same gateway process. |
| **User uploads malicious skill** | Global skill directory is admin-only. User custom skills live in their profile dir only. No symlinks from user skills to system. |
| **Config push breaks a profile** | Every push creates a backup. `manage config rollback --user "alpha"` restores last working config. |
| **API key theft** | Each user has their own API key or a revocable sub-key. Admin can revoke per user without affecting others. |
| **Version upgrade breaks profiles** | Profiles are backwards-compatible with Hermes config. Test on 1 profile before rolling to all. |
