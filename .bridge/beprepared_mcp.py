#!/usr/bin/env python3
"""beprepared MCP bridge server.

Exposes beprepared.dev user data (notes/projects/reminders/events) to a Hermes
agent as MCP tools. Each tool calls the platform HTTP API on localhost with the
acting user's JWT (BEPREPARED_TOKEN from the environment), so the agent reads and
writes the SAME data the user sees in their web dashboard.

Protocol: MCP stdio (JSON-RPC 2.0 over stdin/stdout). stdlib only.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = os.environ.get("BEPREPARED_BASE", "https://beprepared.dev/api/me").rstrip("/")
TOKEN = os.environ.get("BEPREPARED_TOKEN", "")
TZ = ZoneInfo(os.environ.get("BEPREPARED_TZ", "America/New_York"))


def _to_local(iso):
    """UTC/offset ISO -> user-local 'YYYY-MM-DD HH:MM' for the agent to read."""
    if not iso:
        return iso
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return d.astimezone(TZ).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso


def _from_local(iso):
    """Agent's naive local input -> offset-aware ISO so the API stores the right UTC instant."""
    if not iso:
        return iso
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return iso
    if d.tzinfo is None:
        d = d.replace(tzinfo=TZ)
    return d.isoformat()


def _localize(body, fields):
    """Rewrite offset-aware API times in a response body to user-local times."""
    try:
        data = json.loads(body)
    except ValueError:
        return body
    for item in data.get("events", data.get("reminders", [])):
        for f in fields:
            if f in item:
                item[f] = _to_local(item[f])
    return json.dumps(data)


def call(method, path, payload=None):
    if not TOKEN:
        return {"error": "BEPREPARED_TOKEN not set for this profile"}
    url = BASE.rstrip("/") + path
    data = None
    headers = {"Authorization": "Bearer " + TOKEN, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"status": r.getcode(), "body": r.read().decode()}
    except urllib.error.HTTPError as e:
        return {"error": "HTTP %s" % e.code, "body": e.read().decode()[:500]}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


TOOLS = [
    {"name": "notes_list", "description": "List the user's notes.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "notes_create", "description": "Create a note for the user.", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "category": {"type": "string"}}, "required": ["title"]}},
    {"name": "notes_delete", "description": "Delete a note (id or vault_<file>).", "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
    {"name": "notes_update", "description": "Update one or more fields of an existing note by id (title/content/category). To APPEND to an existing note, call notes_list first to get its current content+id, combine with the new text, then send the FULL combined content here. ALWAYS use this for 'add to / update a note' — never create a new note for that.", "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}, "category": {"type": "string"}}, "required": ["id"]}},
    {"name": "projects_list", "description": "List the user's projects.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "projects_create", "description": "Create a project.", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}}, "required": ["title"]}},
    {"name": "reminders_list", "description": "List the user's reminders.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "reminders_create", "description": "Create a reminder.", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "remind_at": {"type": "string"}, "description": {"type": "string"}}, "required": ["title", "remind_at"]}},
    {"name": "events_list", "description": "List the user's events.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "events_create", "description": "Create an event.", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}, "event_start": {"type": "string"}, "event_end": {"type": "string"}, "location": {"type": "string"}}, "required": ["title", "event_start"]}},
]


def dispatch(name, args):
    a = args or {}
    if name == "notes_list":
        return call("GET", "/notes")
    if name == "notes_create":
        return call("POST", "/notes", {k: a.get(k) for k in ("title", "content", "category") if k in a})
    if name == "notes_delete":
        return call("DELETE", "/notes/%s" % a.get("id"))
    if name == "notes_update":
        return call("PUT", "/notes/%s" % a.get("id"), {k: a.get(k) for k in ("title", "content", "category") if k in a})
    if name == "projects_list":
        return call("GET", "/projects")
    if name == "projects_create":
        return call("POST", "/projects", {k: a.get(k) for k in ("title", "description") if k in a})
    if name == "reminders_list":
        r = call("GET", "/reminders")
        if "body" in r:
            r["body"] = _localize(r["body"], ("remind_at", "created_at"))
        return r
    if name == "reminders_create":
        a = dict(a)
        if a.get("remind_at"):
            a["remind_at"] = _from_local(a["remind_at"])
        return call("POST", "/reminders", {k: a.get(k) for k in ("title", "remind_at", "description") if k in a})
    if name == "events_list":
        r = call("GET", "/events")
        if "body" in r:
            r["body"] = _localize(r["body"], ("event_start", "event_end"))
        return r
    if name == "events_create":
        a = dict(a)
        if a.get("event_start"):
            a["event_start"] = _from_local(a["event_start"])
        if a.get("event_end"):
            a["event_end"] = _from_local(a["event_end"])
        return call("POST", "/events", {k: a.get(k) for k in ("title", "description", "event_start", "event_end", "location") if k in a})
    return {"error": "unknown tool: %s" % name}


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "beprepared-bridge", "version": "0.1.0"}}}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        res = dispatch(msg.get("params", {}).get("name", ""), msg.get("params", {}).get("arguments"))
        return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}
    return {"jsonrpc": "2.0", "id": mid, "result": {}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        out = handle(msg)
        if out is not None:
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
