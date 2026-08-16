# beprepared Hermes MCP bridge

Lets a Hermes Agent profile read/write a user's beprepared.dev data
(notes / projects / reminders / events) through the **same API the web
dashboard uses**, so the agent and dashboard stay consistent.

## Layout
- `beprepared_mcp.py` — stdio MCP server exposing tools:
  `notes.list/create/update/delete`, `projects.list/create/update`,
  `reminders.list/create`, `events.list/create/update/delete`.
  Stdlib-only (urllib). Reads auth from env **`BEPREPARED_TOKEN`** (a per-user
  platform JWT) and base URL from **`BEPREPARED_BASE`** (default
  `https://beprepared.dev/api/me`).

## Register on a Hermes profile
```
hermes -p <profile> mcp add beprepared \
  --command python3 \
  --env BEPREPARED_TOKEN=<jwt> \
  --args /root/.hermes/bridge/beprepared_mcp.py     # --args MUST be last
```
Token lifecycle: bridge uses a per-user JWT. Note the platform issues ~7-day
tokens today; Phase 2 hardens this to a durable/refreshable per-user credential.

## Notes
- The platform API (`hermes-multi-tenant-api-1`) is reachable from the host
  only via the public HTTPS ingress (Caddy), **not** localhost:8000 (that port
  is AgentQueue). Hence `BEPREPARED_BASE=https://beprepared.dev`.
- Live users stay on `agent_manager.py` until the real-user migration is green.
