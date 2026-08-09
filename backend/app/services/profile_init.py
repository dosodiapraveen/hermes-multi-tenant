"""Hermes profile initializer. Creates isolated profiles + Obsidian vaults per user."""
import os, json
from pathlib import Path

PROFILES_ROOT = Path("/opt/hermes/profiles")
OBSIDIAN_ROOT = Path("/opt/hermes/obsidian")

def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o755)

def init_user_profile(user_id: str, agent_name: str = "My Assistant",
                       primary_model: str = "accounts/fireworks/models/deepseek-v4-flash-0731",
                       backup_model: str = "accounts/fireworks/models/deepseek-v4-flash-0731",
                       plan: str = "pro", is_vip: bool = False) -> dict:
    profile_dir = PROFILES_ROOT / user_id
    vault_dir = OBSIDIAN_ROOT / user_id
    for d in [profile_dir / n for n in ["skills", "memories", "plugins", "cron", "sessions", "secrets"]]:
        ensure_dirs(d)

    # Hermes config.yaml
    config = {
        "profile": {"name": f"user-{user_id[:8]}", "agent_name": agent_name},
        "model": {
            "provider": "fireworks",
            "model": primary_model,
            "backup": {"provider": "fireworks", "model": backup_model},
            "max_tokens": 4096, "temperature": 0.7,
        },
        "skills": {"obsidian": {"vault_path": str(vault_dir)}},
        "memory": {"type": "file", "path": str(profile_dir / "memories")},
        "providers": {"fireworks": {"api_key": "${FIREWORKS_API_KEY}"}},
        "tools": {
            "web_search": True,
            "terminal": plan in ("pro", "business", "vip"),
            "browser": plan in ("pro", "business", "vip"),
            "vision": plan in ("business", "vip"),
        },
        "messaging": {
            "auto_reply": True,
            "max_daily_messages": 0 if is_vip else {"trial": 50, "basic": 100, "pro": 500, "business": 2000}.get(plan, 50),
        },
    }
    import yaml
    with open(profile_dir / "config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # .env with provider key
    fw_key = os.environ.get("FIREWORKS_API_KEY", "")
    if fw_key:
        with open(profile_dir / ".env", "w") as f:
            f.write(f"FIREWORKS_API_KEY={fw_key}\nHERMES_HOME={profile_dir}\n")
        os.chmod(profile_dir / ".env", 0o600)

    # Obsidian vault
    ensure_dirs(vault_dir)
    for folder in ["Inbox", "Notes", "Projects", "Journal", "Templates"]:
        ensure_dirs(vault_dir / folder)
    ensure_dirs(vault_dir / ".obsidian" / "plugins")
    with open(vault_dir / ".obsidian" / "app.json", "w") as f:
        json.dump({"vault": {"name": agent_name + "'s Vault"}, "attachmentFolderPath": "Inbox", "newFileFolderPath": "Inbox", "newLinkFormat": "shortest", "useMarkdownLinks": True, "spellcheck": True}, f, indent=2)
    with open(vault_dir / "Inbox" / "Welcome.md", "w") as f:
        f.write(f"# Welcome, {agent_name}!\n\nThis is your personal knowledge vault.\n")

    # User skill
    with open(profile_dir / "skills" / "user-preferences.md", "w") as f:
        f.write(f"# User Preferences — {agent_name}\n\n- **Name:** {agent_name}\n- **Plan:** {plan}\n- **VIP:** {is_vip}\n- **Style:** Helpful, concise, direct\n")

    return {"profile_dir": str(profile_dir), "vault_dir": str(vault_dir), "config": config}
