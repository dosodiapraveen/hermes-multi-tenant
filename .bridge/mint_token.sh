#!/bin/bash
# Mint a long-lived agent_token for the throwaway user and re-point the bridge.
set -e
SESS=$(curl -s -X POST "https://beprepared.dev/api/auth/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"bridgetest@throwaway.dev","password":"BridgeTest2026!"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
AT=$(curl -s -X GET "https://beprepared.dev/api/me/agent-token" -H "Authorization: Bearer $SESS" | python3 -c 'import sys,json;print(json.load(sys.stdin)["agent_token"])')
echo "agent_token len: ${#AT} (long-lived, opaque)"
# Re-point the phase1test MCP bridge env to the long-lived agent token.
hermes -p phase1test config set mcp_servers.beprepared.env.BEPREPARED_TOKEN "$AT"
echo "bridge token updated to agent_token; token saved to /tmp/agent_tok.txt"
echo "$AT" > /tmp/agent_tok.txt
