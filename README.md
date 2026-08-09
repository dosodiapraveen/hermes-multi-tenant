# Hermes Multi-Tenant Platform

Host, manage, and scale Hermes Agent instances for multiple users. Isolated profiles, central management, user self-service dashboard.

## Project Structure

```
/
├── plan/                          # Architecture and design docs
│   ├── architecture-plan.md       # System architecture, infrastructure, scaling
│   └── breakdown.md               # UI specs, security, upgrades, component details
│
├── design/
│   ├── design-system.md           # Colors, typography, spacing, components
│   └── mockups/
│       ├── user-app.html          # Mobile user dashboard (6 screens)
│       └── admin-dashboard.html   # Desktop admin panel (7 screens)
│
├── screenshots/                   # Rendered mockup images
│   ├── mockup-01-home.png
│   ├── mockup-02-settings.png
│   ├── mockup-03-models.png
│   ├── mockup-04-skills.png
│   ├── mockup-05-platforms.png
│   ├── mockup-06-billing.png
│   ├── admin-01-dashboard.png
│   ├── admin-02-users.png
│   ├── admin-03-onboarding.png
│   ├── admin-04-config.png
│   ├── admin-05-skills.png
│   ├── admin-06-upgrades.png
│   └── admin-07-logs.png
│
├── src/                           # Source code (coming next)
│   ├── backend/                   # FastAPI management API
│   ├── frontend/                  # Vue/React dashboard
│   └── cli/                       # Manage CLI tool
│
└── README.md
```

## Design

- **Palette:** Purple (#6C5CE7) + Teal (#00CEC9)
- **Font:** Inter
- **Mobile-first** user dashboard, desktop admin panel
- B2C: Clean, trust-oriented, minimal friction
- Admin: Data-dense, actionable, real-time

## Architecture

- **Single VM launch** (Hetzner €9/mo for 10-30 users)
- **Profile-based isolation** — each user = one Hermes profile. No Docker per user.
- **Management layer** — CLI + web dashboard for admin (config push, upgrades, monitoring)
- **User portal** — mobile web app for agent setup, model selection, platform connection

## Next: MVP Build

Backend (FastAPI + auth + profile management) → Frontend → CLI tools.
