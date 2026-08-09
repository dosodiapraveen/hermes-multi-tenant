# Hermes Multi-Tenant Platform — Component Breakdown

---

## 1. User Dashboard — UI & User Journey

### User Dashboard Screens

#### Screen 1: Onboarding / Setup Wizard

When a user first logs in, they see a 3-step wizard:

```
┌─────────────────────────────────────────────────────────┐
│  🎉 Welcome to Hermes!  Let's set up your agent.       │
│                                                         │
│  Step 1 of 3: Name Your Agent                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Agent Name: [My Assistant________________]      │    │
│  │  Personality: [Helpful and concise_________]     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                        [Next →]                         │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│  Step 2 of 3: Connect a Chat Platform                   │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐     │
│  │   🤖 Telegram         │  │   💬 WhatsApp         │     │
│  │                       │  │                       │     │
│  │  1. Create a bot in   │  │  Scan QR code or      │     │
│  │     @BotFather        │  │  enter API key        │     │
│  │  2. Copy the token    │  │                       │     │
│  │  3. Paste it below    │  │                       │     │
│  │                       │  │                       │     │
│  │  Token: [__________]  │  │                       │     │
│  │  [Verify & Connect]   │  │  [Connect WhatsApp]   │     │
│  └──────────────────────┘  └──────────────────────┘     │
│                                                         │
│  You can add more platforms later in Settings.          │
│                        [Next →]                         │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│  Step 3 of 3: Choose Your Model                         │
│                                                         │
│  Available Models:                                       │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ○ Claude Sonnet 4 — Best for reasoning (default)   │ │
│  │ ● GPT-5 — Best for speed                           │ │
│  │ ○ DeepSeek V4 — Best for cost efficiency            │ │
│  │ ○ Gemini 2.5 Pro — Best for long context            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Your plan includes 500K tokens/month.                  │
│                                                         │
│  [Done — Start Chatting!]                               │
└─────────────────────────────────────────────────────────┘
```

#### Screen 2: Chat Dashboard (Home)

After setup, the user lands here:

```
┌─────────────────────────────────────────────────────────┐
│  🤖 My Assistant                              [User ⚙] │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │ Connected Platforms  │  │ Usage This Month         │ │
│  │                      │  │                          │ │
│  │  ✅ Telegram @mybot  │  │ ████████░░ 82K / 500K    │ │
│  │  ⚠️ WhatsApp —       │  │ tokens used              │ │
│  │      not connected   │  │                          │ │
│  │                      │  │ Model: Claude Sonnet 4   │ │
│  │  [+ Add Platform]    │  │ Status: ● Active         │ │
│  └──────────────────────┘  └──────────────────────────┘ │
│                                                         │
│  Quick Actions:                                          │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐    │
│  │ Change │ │ Add Skill│ │ View     │ │ Upgrade   │    │
│  │ Model  │ │          │ │ History  │ │ Plan      │    │
│  └────────┘ └──────────┘ └──────────┘ └───────────┘    │
│                                                         │
│  💡 Tip: Try saying "note this" to save to your vault!  │
└─────────────────────────────────────────────────────────┘
```

#### Screen 3: Settings

```
┌─────────────────────────────────────────────────────────┐
│  Settings                                      [Save]   │
│                                                         │
│  Profile                                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Agent Name:  [My Assistant                    ]    │ │
│  │ Personality: [You are helpful and concise....]    │ │
│  │ Timezone:    [America/New_York        ▼]         │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Model                                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Provider:  [Anthropic            ▼]               │ │
│  │ Model:     [claude-sonnet-4-2026 ▼]               │ │
│  │                                                      │ │
│  │ ⚡ Warning: Different models have different costs.   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Skills (toggle on/off)                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ✅ Web Search     — Browse the internet            │ │
│  │ ✅ Voice Notes    — Save notes to your vault       │ │
│  │ ☐ Blog Scanner   — Monitor RSS feeds              │ │
│  │ ☐ Image Gen      — Generate images                │ │
│  │ [+ Install Custom Skill]                           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Platforms                                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Telegram: ● Connected  [Disconnect]  [Test]       │ │
│  │ WhatsApp: ○ Not connected  [Connect Now]           │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Screen 4: Billing / Plan

```
┌─────────────────────────────────────────────────────────┐
│  Plan & Billing                                         │
│                                                         │
│  Current Plan: Pro — $15/mo                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Basic   $5     Pro     $15    Business   $35       │ │
│  │ ┌──────┐ ┌──────────┐ ┌──────────────────┐       │ │
│  │ │1 agent│ │1 agent   │ │2 agents          │       │ │
│  │ │100K   │ │500K      │ │2M tokens         │       │ │
│  │ │tokens │ │tokens    │ │Custom model      │       │ │
│  │ │Telegram│ │WhatsApp +│ │Priority support  │       │ │
│  │ └──────┘ │Telegram   │ └──────────────────┘       │ │
│  │          │Skills     │                             │ │
│  │          └──────────┘                             │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Add tokens: $5/100K tokens                             │
│  [Change Plan] [Add Tokens]                             │
│                                                         │
│  Payment Method: Visa ••4242 [Change]                   │
└─────────────────────────────────────────────────────────┘
```

### User Journey (End-to-End)

```
Sign Up                     Onboard                  Active Use
─────────                  ────────                  ──────────
                           ┌─────────────────┐       ┌──────────────────────┐
┌─────────────────┐        │ 1. Name agent   │       │ Chat via Telegram    │
│ User visits      │───────▶ 2. Connect       │──────▶ │ or WhatsApp          │
│ landing page     │        │    Telegram bot │       │                      │
│                  │        │ 3. Pick model   │       │ Use skills           │
│ Signs up with    │        │ 4. Done         │       │ Save notes           │
│ email + password │        └─────────────────┘       │ Set reminders        │
│ or Google SSO   │                                   │                      │
└─────────────────┘                                   │ Occasionally visit   │
                                                      │ dashboard to:        │
                                                      │ - Change model       │
                                                      │ - Check usage        │
                                                      │ - Toggle skills      │
                                                      │ - Upgrade plan       │
                                                      └──────────────────────┘
```

### Key UI Principles

- **Zero server jargon** — Users see "model," not "provider config." No API keys, no YAML, no terminal.
- **Error states are friendly** — "Your agent is thinking..." not "Gateway timeout."
- **Mobile-first** — Most users will access the dashboard on their phone between chats.
- **Real-time status** — Green dot = agent is online and responding. Red = something's wrong.
- **Minimal choices** — 4 models max. Skills are on/off toggles, not config files.

---

## 2. Admin Dashboard

### Admin Screens

#### Screen 1: Overview

```
┌─────────────────────────────────────────────────────────┐
│  🔐 Admin Panel                              [Logout]   │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 24       │ │ 12       │ │ 185K     │ │ $412     │  │
│  │ Active   │ │ Total    │ │ Tokens   │ │ MRR      │  │
│  │ Users    │ │ Agents   │ │ Today    │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Users  │  Agents  │  Config  │  Logs  │  Billing  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Recent Activity:                                        │
│  ⏺ Alpha → changed model to Claude Sonnet 4    2m ago  │
│  ⏺ Beta → connected WhatsApp                    15m ago │
│  ⏺ Gamma → signed up                             1h ago │
│  ⏺ Delta → hit 90% token limit                   2h ago │
│                                                         │
│  System Health: 🟢 All systems operational              │
│  Hermes v0.8.3  |  Gateway v0.8.3  |  Uptime: 12d     │
└─────────────────────────────────────────────────────────┘
```

#### Screen 2: Users List

```
┌─────────────────────────────────────────────────────────┐
│  Users                                   [+ New User]    │
│                                                         │
│  Search: [_____________________________]  Filter: All ▼ │
│                                                         │
│  Name     │ Agent   │ Plan   │ Model    │ Status │ Tokens│
│  ─────────┼─────────┼────────┼──────────┼────────┼───────│
│  Alpha    │ My Bot  │ Pro $15│ Claude 4 │ 🟢     │ 82K   │
│  Beta     │ Helper  │ Basic  │ GPT-5    │ 🟢     │ 45K   │
│  Gamma    │ —       │ Trial  │ —        │ 🟡 setup│ 0     │
│  Delta    │ Assis   │ Pro $15│ DeepSeek │ 🔴 err  │ 120K  │
│                                                         │
│           Showing 4 of 24 users          [1] [2] [3]    │
└─────────────────────────────────────────────────────────┘
```

Clicking a user opens their detail panel:

```
┌─────────────────────────────────────────────────────────┐
│  User: Alpha                            [Edit] [Delete] │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Profile                                            │ │
│  │  Email: alpha@email.com  |  Created: Aug 1, 2026  │ │
│  │  Plan: Pro ($15/mo)      |  Agent: "My Bot"       │ │
│  │                                                     │ │
│  │ Configuration (read-only)                           │ │
│  │  Model: claude-sonnet-4-2026                        │ │
│  │  Provider: anthropic                                │ │
│  │  Skills: web-search ✅, voice-notes ✅              │ │
│  │  Platforms: Telegram (bot token: ...123)            │ │
│  │                                                     │ │
│  │ Quick Actions:                                       │ │
│  │ [Override Model] [Push Skill] [View Logs] [Impersonate] │
│  │                                                     │ │
│  │ Usage (Last 30 Days):                               │ │
│  │  ████████████████░░░░░░░░ 82K / 500K tokens        │ │
│  │  1,234 messages  |  12 active days  |  0 errors    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Screen 3: Config Center (Key Admin Screen)

```
┌─────────────────────────────────────────────────────────┐
│  Config Center                                           │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Global Settings (Applied to all profiles)          │ │
│  │                                                     │ │
│  │  Model Provider: [Anthropic       ▼]               │ │
│  │  Default Model:  [claude-sonnet-4-2026 ▼]          │ │
│  │  Available Models:                                  │ │
│  │    ☑ claude-sonnet-4-2026                          │ │
│  │    ☑ gpt-5                                         │ │
│  │    ☑ deepseek-v4                                   │ │
│  │    ☐ gemini-2.5-pro                                │ │
│  │                                                     │ │
│  │  STT: ● enabled  ○ disabled                        │ │
│  │  TTS: ● enabled (Edge TTS)  ○ disabled             │ │
│  │                                                     │ │
│  │  Default Skills (all new users get these):          │ │
│  │    ☑ web-search  ☑ voice-notes                     │ │
│  │    ☐ blogwatcher  ☐ image-gen                      │ │
│  │                                                     │ │
│  │  [Push to All Profiles]  [Preview Diff]             │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Per-User Overrides                                 │ │
│  │                                                     │ │
│  │  User Alpha: model=claude-sonnet-4 (manual override)│ │
│  │  User Beta:  stt.enabled=false (manual override)    │ │
│  │                                                     │ │
│  │  [Clear All Overrides]  [Bulk Override ▼]          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Config Push History                                │ │
│  │  Aug 7: Changed default model → Claude Sonnet 4    │ │
│  │         Applied to 22 profiles. 2 overridden.      │ │
│  │  Aug 5: Updated available models list              │ │
│  │         Applied to all 24 profiles.                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Screen 4: Version & Upgrades

```
┌─────────────────────────────────────────────────────────┐
│  System Management                                       │
│                                                         │
│  Current Version:                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Hermes: v0.8.3  (latest: v0.8.4)   [Upgrade]     │ │
│  │  Gateway: v0.8.3  (latest: v0.8.4)  [Upgrade]     │ │
│  │                                                     │ │
│  │  Changelog (v0.8.4):                                │ │
│  │  • New tool: computer_use                           │ │
│  │  • Improved memory compression                      │ │
│  │  • Bug fix: gateway crash on long messages          │ │
│  │                                                     │ │
│  │  [Upgrade All]  [Test on 1 User First]              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Skills Library:                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Installed Global Skills (11)                       │ │
│  │                                                     │ │
│  │  ✅ web-search      v1.2  — [Update Available]     │ │
│  │  ✅ voice-notes     v1.0  — Latest                 │ │
│  │  ✅ blogwatcher     v2.0  — Latest                 │ │
│  │  ☐ excalidraw       — [Install]                    │ │
│  │                                                     │ │
│  │  [Install from Library]  [Update All Skills]        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  API Key Pool:                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Anthropic: ● Active  |  Tokens remaining: 1.2M   │ │
│  │  OpenAI:    ● Active  |  Tokens remaining: 4.5M   │ │
│  │  DeepSeek:  ○ Not configured                       │ │
│  │                                                     │ │
│  │  [Add Provider Key]  [View Usage by User]           │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Admin Key Actions

| Action | One-Click? | How |
|--------|-----------|-----|
| Change model for all users | ✅ | Config Center → Change default → Push to All |
| Change model for one user | ✅ | User detail → Override Model |
| Push new skill to all | ✅ | Skills Library → Install → Push to All |
| Upgrade Hermes version | ✅ | System → Upgrade → Choose rollout strategy |
| Add API key | ✅ | System → Key Pool → Add Provider |
| Create user | ✅ | Users → New User → fills in profile + gateway entry |
| Suspend user | ✅ | Users → Suspend → gateway stops routing to them |
| View logs | ✅ | Users → View Logs → real-time stream |

---

## 3. Secure System Architecture

### Data Flow Diagram

```
                         ┌──────────────────────────┐
                         │     Internet             │
                         │                          │
                         │  User chats via          │
                         │  Telegram / WhatsApp      │
                         └────────┬─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │      Cloud Firewall          │
                    │  (Only ports 80, 443, 22)   │
                    │  Rate limiting: 100 req/min   │
                    └────────┬────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │         Nginx Reverse Proxy   │
              │  (SSL termination, auth)     │
              │                              │
              │  /api/* → FastAPI backend     │
              │  / → static Vue dashboard    │
              │  /ws/* → WebSocket (logs)    │
              └──────────┬───────────────────┘
                         │
              ┌──────────▼───────────────────┐
              │     FastAPI Backend            │
              │                                │
              │  Endpoints:                    │
              │  POST /api/auth/login          │
              │  POST /api/users               │
              │  POST /api/config/push         │
              │  GET  /api/logs/{user_id}      │
              │  POST /api/upgrade             │
              │                                │
              │  Auth: JWT + API key           │
              └──────────┬────────────────────┘
                         │
              ┌──────────▼───────────────────┐
              │     Hermes Agent Process       │
              │                                │
              │  Profiles/                     │
              │  ├── user_alpha/               │
              │  │   ├── config.yaml           │
              │  │   ├── state.db (encrypted) │
              │  │   └── memories/             │
              │  ├── user_beta/               │
              │  └── ...                      │
              │                                │
              │  Gateway listens on ports:     │
              │  Telegram webhook: 8443        │
              │  WhatsApp webhook: 8444        │
              └────────────────────────────────┘
```

### Security Layers

#### Layer 1: Network

```
┌─────────────────────────────────────────────┐
│  Cloud Firewall Rules                        │
│                                             │
│  ✅ SSH (port 22)    → Admin IP only        │
│  ✅ HTTPS (443)      → Everyone (dashboard) │
│  ✅ Telegram webhook → Telegram IPs only    │
│  ✅ WhatsApp webhook → Meta IPs only        │
│  ❌ All other ports closed                  │
└─────────────────────────────────────────────┘
```

#### Layer 2: Authentication

| Feature | Implementation |
|---------|---------------|
| **Admin login** | Password + 2FA (TOTP). Or SSO (Google Workspace). |
| **User login** | Email+password or Google SSO. Session expires in 7 days. |
| **API keys** | Admin generates revocable keys for `manage` CLI. |
| **Telegram bots** | Each user's bot token is stored encrypted in their profile config. |
| **WhatsApp** | WhatsApp Business API credentials stored encrypted. |

#### Layer 3: Data Isolation

```
User A sends message to Telegram
         │
         ▼
Gateway receives → looks up bot token
         │
         ▼
Matches profile "user_alpha"
         │
         ▼
Routes to profile's isolated session DB
         │
         ▼
Profile loads its OWN:
  - config.yaml (can't see others')
  - state.db (can't see others')
  - memories/ (can't see others')
  - skills/ (global + user's own only)
         │
         ▼
Response goes back through gateway → back to User A's bot
```

**Isolation guarantees:**
- Profiles are separate filesystem directories. Hermes never reads across profile boundaries.
- The gateway maps one-to-one: bot token → profile. No token can route to multiple profiles.
- Session DBs are per-profile. No shared state.
- Memory files are per-profile. No shared knowledge.
- File system permissions: profiles owned by the Hermes system user. No other profile can read them.

#### Layer 4: Secrets Management

| Secret | Where Stored | Encrypted? |
|--------|-------------|------------|
| API keys (Anthropic, OpenAI) | `.env` file, root-owned, 600 permissions | ✅ At rest |
| Telegram bot tokens | Profile `config.yaml` | ✅ AES-256 |
| User passwords | Database | ✅ bcrypt |
| WhatsApp credentials | Profile `config.yaml` | ✅ AES-256 |
| SSL certificates | Let's Encrypt | ✅ Auto-renewed |

#### Layer 5: Rate Limiting & Abuse Prevention

| Measure | Limit |
|---------|-------|
| Messages per user per minute | 30 |
| API calls from dashboard | 100/min per IP |
| Login attempts | 5 before 15-min lockout |
| New user signups per hour | 10 from same IP |
| Token usage per user per day | Plan limit + 20% buffer |

---

## 4. Upgrade Methodology

### Type 1: Config Changes (Most Frequent)

**Example:** Change default model from GPT-5 to Claude Sonnet 4 for all users.

```
Admin clicks "Push to All Profiles" in Config Center
         │
         ▼
FastAPI backend receives request with admin JWT
         │
         ▼
Script iterates over all profiles in ~/.hermes/profiles/*/
         │
         ▼
For each profile:
  1. Read current config.yaml
  2. Apply the change (merge, not overwrite)
  3. Write new config.yaml
  4. Skip users with manual overrides (flag in DB)
  5. Log the change
         │
         ▼
Response: "Updated 22 profiles. 2 skipped (manual overrides)."
```

**Implementation (simplified):**

```python
def push_config(key: str, value: Any, user_filter: str = "all"):
    profiles = get_profiles(user_filter)
    results = {"updated": [], "skipped": []}
    
    for profile in profiles:
        if profile.has_override(key):
            results["skipped"].append(profile.name)
            continue
        
        config = yaml.safe_load(profile.config_path.read_text())
        set_nested_key(config, key, value)
        profile.config_path.write_text(yaml.dump(config))
        results["updated"].append(profile.name)
    
    # Trigger gateway to reload configs
    hermes_gateway.reload()
    
    return results
```

**Config change types:**

| Change | Safe to push live? | Notes |
|--------|-------------------|-------|
| Model (same provider) | ✅ Yes | Next message uses new model |
| Provider change | ✅ Yes | May need API key test first |
| STT/TTS toggle | ✅ Yes | Takes effect immediately |
| Skill enable/disable | ✅ Yes | Profiles reload skills on next start |
| Available models list | ✅ Yes | Only affects user dropdown options |
| Temperature/max tokens | ✅ Yes | Next response uses new params |

### Type 2: Hermes Version Upgrade (Rare)

**Example:** Upgrade from v0.8.3 to v0.8.4.

```
Three rollout strategies:
```

**Strategy A — Direct Upgrade (1-30 users):**

```bash
# 1. Backup
cp -r ~/.hermes/profiles ~/backup/profiles-$(date +%Y%m%d)

# 2. Pull new version
cd ~/hermes-agent
git pull origin main
pip install -e .

# 3. Restart gateway (downtime ~30 seconds)
hermes gateway restart

# 4. Verify
manage version current  # Should show v0.8.4
manage test --user "alpha"  # Send test message
```

**Strategy B — Canary Rollout (30-100 users):**

```bash
# 1. Test on 1 user first
manage profile clone "alpha" "canary-test"
manage version upgrade --profile "canary-test"
# Manually test the canary profile

# 2. If good, upgrade all
manage version upgrade --all

# 3. If bad, rollback
manage version rollback --all
```

**Strategy C — Blue-Green (100+ users):**

```
Current VM (blue)        New VM (green)
  Hermes v0.8.3           Hermes v0.8.4
  profiles/               profiles/ (copied)
  
  1. Clone profiles to green VM
  2. Upgrade green to v0.8.4
  3. Test green internally
  4. Swap gateway DNS → green
  5. Keep blue running for 24h rollback window
  6. If all good → decommission blue
```

### Type 3: Global Skill Updates

```
Admin updates a skill file in ~/.hermes/skills/global/
         │
         ▼
Edit the .md file directly (or via dashboard editor)
         │
         ▼
All profiles that have the skill enabled will use the new version
on their next agent response (skills are loaded at session start)
         │
         ▼
If you want to force immediate reload:
manage skills reload --all
```

---

## 5. Scaling — Adding More Agents to the Pool

### Horizontal Scaling Strategy

```
Phase 1: Single VM    Phase 2: Split Gateway  Phase 3: Full Cluster
(1-30 users)          (30-100 users)          (100+ users)

┌──────────┐          ┌──────────┐ ┌──────────┐ ┌── LB ──┐
│ Hermes   │          │ Gateway  │ │ Hermes 1 │ │        │
│ Gateway  │          │ Node     │ │ Profiles │ │Gateway │── Hermes 1
│ Profiles │          │   │      │ │ 1-50    │ │ │  Node │── Hermes 2
│ All      │          │   │      │ └──────────┘ │        │── Hermes 3
└──────────┘          │   ▼      │ ┌──────────┐ └────────┘
                      │ ┌──────┐ │ │ Hermes 2 │
                      │ │Redis │ │ │ Profiles │
                      │ │Cache │ │ │ 51-100  │
                      │ └──────┘ │ └──────────┘
                      └──────────┘
```

### Adding Users at Each Stage

**Phase 1 (single VM):**

```bash
# Admin runs this (or dashboard does it)
manage users create --name "newuser" --model "claude-sonnet-4"

# What happens:
# 1. Creates ~/.hermes/profiles/newuser/ directory
# 2. Writes config.yaml with defaults + user's model choice
# 3. Adds gateway entry for their Telegram bot token
# 4. Reloads gateway
# 5. Sends welcome message to admin

# Time: ~2 seconds. No downtime for existing users.
```

**Phase 2 (30+ users — split profiles across VMs):**

```yaml
# gateway config routes by profile name to VM
routing:
  user_alpha: 
    host: "10.0.0.1:8080"  # Hermes VM 1
  user_beta:
    host: "10.0.0.1:8080"  # Hermes VM 1
  user_gamma:
    host: "10.0.0.2:8080"  # Hermes VM 2
```

When a VM gets full, the admin simply:

```bash
# 1. Provision new VM
# 2. Install Hermes
# 3. Move some profiles over
manage profile migrate --from "vm1" --to "vm2" --users "user_delta,user_epsilon"
# 4. Update gateway routing config
# 5. Done — no downtime
```

**Phase 3 (100+ — Docker/Kubernetes):**

```yaml
# docker-compose scaled
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    volumes:
      - profile_data:/profiles
    deploy:
      replicas: 3  # 3 instances, profiles distributed
    environment:
      - HERMES_PROFILES_PATH=/profiles
      - HERMES_NODE_ID=node-${HOSTNAME}
```

### Auto-Scaling Trigger

| Metric | Action |
|--------|--------|
| CPU > 70% consistently | Add another Hermes node |
| RAM > 80% | Move 20% of profiles to another node |
| Gateway latency > 2s | Scale gateway horizontally |
| User count hits 80% of current capacity | Pre-provision next node |

### Profile Migration (Live)

```bash
# Move a user from one VM to another without them noticing
manage profile migrate \
  --user "alpha" \
  --from "vm1.hermes.internal" \
  --to "vm2.hermes.internal"

# What happens:
# 1. Rsync profile data to new VM
# 2. Gateway starts routing alpha to new VM
# 3. Old VM's alpha profile kept for 24h (rollback window)
# 4. After 24h: cleanup old copy
# User sees zero downtime — at most 1 missed message during routing switch
```

---

## Implementation Priority

| Priority | Component | Time | Why First |
|----------|-----------|------|-----------|
| **P0** | User profile system + isolation | 2 days | Foundation. Without this, nothing else works. |
| **P0** | Config template + merge system | 1 day | Must be able to push configs. |
| **P1** | Admin dashboard (basic) | 3 days | Need to see what's happening. |
| **P1** | User onboarding flow | 2 days | Users must be able to get started. |
| **P2** | User dashboard (settings) | 2 days | Users need to change models, connect platforms. |
| **P2** | Gateway routing config | 1 day | Multi-profile message routing. |
| **P3** | Upgrade system | 1 day | Version management. |
| **P3** | Billing | 2 days | Revenue. |
| **P4** | Monitoring & logging | 2 days | Observability. |
| **P4** | Auto-scaling | 2 days | Growth path. |

**Total: 16 days for full platform**
**MVP (P0 + P1): 8 days**
