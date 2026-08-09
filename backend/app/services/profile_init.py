"""
Hermes profile initializer.
Creates an isolated Hermes Agent profile + Obsidian vault for each user.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional

PROFILES_ROOT = Path("/opt/hermes/profiles")
OBSIDIAN_ROOT = Path("/opt/hermes/obsidian")
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/root/.hermes"))


def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o755)


def create_hermes_config(
    profile_dir: Path,
    user_id: str,
    agent_name: str,
    primary_model: str,
    backup_model: str,
    plan: str,
    is_vip: bool,
) -> dict:
    """Create the Hermes Agent config.yaml for this user's profile."""
    config = {
        "profile": {
            "name": f"user-{user_id[:8]}",
            "agent_name": agent_name,
        },
        "model": {
            "provider": "fireworks",
            "model": primary_model,
            "backup": {
                "provider": "fireworks",
                "model": backup_model,
            },
            "max_tokens": 4096,
            "temperature": 0.7,
        },
        "skills": {
            "obsidian": {
                "vault_path": str(OBSIDIAN_ROOT / user_id),
            },
        },
        "memory": {
            "type": "file",
            "path": str(profile_dir / "memories"),
        },
        "tools": {
            "web_search": True,
            "terminal": True,
            "browser": plan in ("pro", "business", "vip"),
            "vision": plan in ("business", "vip"),
        },
        "messaging": {
            "auto_reply": True,
            "max_daily_messages": 0 if is_vip else {"trial": 50, "basic": 100, "pro": 500, "business": 2000}.get(plan, 50),
        },
    }

    config_path = profile_dir / "config.yaml"
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    os.chmod(config_path, 0o644)
    return config


def create_obsidian_vault(vault_dir: Path, agent_name: str):
    """Create an Obsidian vault with default structure."""
    ensure_dirs(vault_dir)
    
    # Standard folders
    for folder in ["Inbox", "Notes", "Projects", "Journal", "Templates"]:
        ensure_dirs(vault_dir / folder)

    # .obsidian config
    obsidian_dir = vault_dir / ".obsidian"
    ensure_dirs(obsidian_dir)
    ensure_dirs(obsidian_dir / "plugins")

    # Vault config
    vault_config = {
        "vault": {"name": f"{agent_name}'s Vault"},
        "attachmentFolderPath": "Inbox",
        "newFileFolderPath": "Inbox",
        "newLinkFormat": "shortest",
        "useMarkdownLinks": True,
        "showLineNumber": False,
        "spellcheck": True,
    }
    with open(obsidian_dir / "app.json", "w") as f:
        json.dump(vault_config, f, indent=2)

    # Appearance
    with open(obsidian_dir / "appearance.json", "w") as f:
        json.dump({"accentColor": "#6C5CE7", "theme": "obsidian", "baseFontSize": 14}, f, indent=2)

    # Hotkeys  
    with open(obsidian_dir / "hotkeys.json", "w") as f:
        json.dump([], f)

    # Welcome note
    welcome = f"""# Welcome, {agent_name}!

This is your personal knowledge vault. Use it to:

- 📥 **Capture ideas** quickly in the Inbox
- 📝 **Take notes** during meetings and research
- 📁 **Organize projects** in the Projects folder
- 📓 **Journal daily** in the Journal folder

Your Hermes Agent has access to this vault and can
search, read, and create notes for you.

*Start by saying: "Take a note" or "Save this thought"*
"""
    with open(vault_dir / "Inbox" / "Welcome.md", "w") as f:
        f.write(welcome)


def init_user_profile(
    user_id: str,
    agent_name: str = "My Assistant",
    primary_model: str = "accounts/fireworks/models/deepseek-v4-flash-0731",
    backup_model: str = "accounts/fireworks/models/deepseek-v4-flash-0731",
    plan: str = "pro",
    is_vip: bool = False,
) -> dict:
    """
    Initialize a complete user profile:
    1. Hermes Agent config
    2. Skills directory
    3. Memories directory
    4. Obsidian vault
    """
    profile_dir = PROFILES_ROOT / user_id
    vault_dir = OBSIDIAN_ROOT / user_id
    skills_dir = profile_dir / "skills"
    memories_dir = profile_dir / "memories"
    plugins_dir = profile_dir / "plugins"
    cron_dir = profile_dir / "cron"

    # Create directories
    for d in [profile_dir, skills_dir, memories_dir, plugins_dir, cron_dir]:
        ensure_dirs(d)

    # Create config
    config = create_hermes_config(profile_dir, user_id, agent_name, primary_model, backup_model, plan, is_vip)

    # Create Obsidian vault
    create_obsidian_vault(vault_dir, agent_name)

    # Create a skill placeholder for this user
    skill_file = skills_dir / "user-preferences.md"
    with open(skill_file, "w") as f:
        f.write(f"""# User Preferences — {agent_name}

Follow these preferences when interacting with this user:

- **Name:** {agent_name}
- **Plan:** {plan}
- **VIP:** {is_vip}
- **Style:** Helpful, concise, direct
- **Vault:** {vault_dir}
""")

    return {
        "profile_dir": str(profile_dir),
        "vault_dir": str(vault_dir),
        "config": config,
    }


if __name__ == "__main__":
    # Test
    result = init_user_profile("test-user-123", "Test Agent")
    print(json.dumps(result, indent=2))
    print(f"\nProfile created at: {result['profile_dir']}")
    print(f"Vault created at: {result['vault_dir']}")
