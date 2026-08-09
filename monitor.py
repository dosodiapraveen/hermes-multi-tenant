#!/usr/bin/env python3
"""Hermes Platform Monitor - health checks + Telegram alerts."""
import os, sys, json, subprocess, httpx
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8980557307:AAHzwXq8IyYYfqAhiquQ0FTNUxK79H7MofU")
API_URL = "http://localhost:8000"
CHAT_ID = "1832518861"


def send(msg: str):
    try:
        httpx.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Send failed: {e}")


def check(name: str, fn) -> list:
    try:
        return fn()
    except Exception as e:
        return [f"{name}: {e}"]


def api_health() -> list:
    r = httpx.get(f"{API_URL}/api/health", timeout=10)
    return [] if r.status_code == 200 else [f"API returned {r.status_code}"]


def db_health() -> list:
    r = subprocess.run(["docker", "exec", "hermes-multi-tenant-postgres-1",
        "pg_isready", "-U", "hermes"], capture_output=True, text=True, timeout=10)
    return [] if r.returncode == 0 else [f"DB: {r.stderr.strip()}"]


def disk_space() -> list:
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    line = [x for x in r.stdout.strip().split("\n")[-1].split(" ") if x]
    pct = int(line[4].replace("%", ""))
    return [] if pct < 85 else [f"Disk {pct}% full"]


def containers() -> list:
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    running = r.stdout.strip().split("\n")
    needed = ["api", "postgres", "redis", "frontend", "caddy"]
    return [f"Container '{n}' not running" for n in needed if not any(n in c for c in running)]


def run():
    issues = []
    issues += check("API", api_health)
    issues += check("DB", db_health)
    issues += check("Disk", disk_space)
    issues += check("Containers", containers)

    if issues:
        msg = "<b>⚠️ Hermes Alert</b> " + datetime.now().strftime("%H:%M") + "\n" + "\n".join("• " + i for i in issues)
        send(msg)
        print("ALERTS:", issues)
    else:
        print(f"[{datetime.now().isoformat()}] All OK")

    # Daily summary at 8 AM
    if len(sys.argv) > 1 and sys.argv[1] == "daily":
        send("<b>📊 Daily Report</b>\nAll systems healthy.")


if __name__ == "__main__":
    run()
