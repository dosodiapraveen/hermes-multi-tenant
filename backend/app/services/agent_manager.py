"""Hermes Agent Manager - routes user messages through AI with memory & tools."""
import os, json, logging
from pathlib import Path
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)
PROFILES_ROOT = Path("/opt/hermes/profiles")


async def call_ai(model: str, messages: list, api_key: str, timeout: int = 30) -> str:
    """Call Fireworks AI chat completions API."""
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": 2048, "temperature": 0.7}
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def get_user_config(user_id: str) -> dict:
    """Load user profile config."""
    profile_dir = PROFILES_ROOT / user_id
    config_path = profile_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No profile for user {user_id}")
    import yaml
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_memories(user_id: str) -> list:
    """Load conversation history from user's memory."""
    memories_dir = PROFILES_ROOT / user_id / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(memories_dir.glob("*.json"))[-5:]  # last 5 memories
    history = []
    for f in files:
        try:
            with open(f) as fp:
                history.append(json.load(fp))
        except: pass
    return history


def save_memory(user_id: str, user_msg: str, ai_msg: str):
    """Save conversation turn to user's memory."""
    mem_file = PROFILES_ROOT / user_id / "memories" / f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')}.json"
    with open(mem_file, "w") as f:
        json.dump({"role": "user", "content": user_msg, "timestamp": datetime.utcnow().isoformat()}, f)
    resp_file = PROFILES_ROOT / user_id / "memories" / f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')}-resp.json"
    with open(resp_file, "w") as f:
        json.dump({"role": "assistant", "content": ai_msg, "timestamp": datetime.utcnow().isoformat()}, f)


def read_vault(user_id: str) -> str:
    """Read recent notes from user's Obsidian vault."""
    vault_dirs = [
        PROFILES_ROOT.parent / "obsidian" / user_id / "Inbox",
        PROFILES_ROOT.parent / "obsidian" / user_id / "Notes",
    ]
    notes = []
    for d in vault_dirs:
        if d.exists():
            for f in sorted(d.glob("*.md"))[-3:]:
                try:
                    notes.append(f"--- {f.name} ---\n{f.read_text()[:500]}")
                except: pass
    return "\n\n".join(notes) if notes else ""


def write_vault_note(user_id: str, title: str, content: str):
    """Save a note to user's Obsidian vault Inbox."""
    inbox = PROFILES_ROOT.parent / "obsidian" / user_id / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / f"{title.replace(' ', '-')[:50]}.md"
    path.write_text(f"# {title}\n\n{content}\n\n---\nSaved by Hermes on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")


async def hermes_profile_chat(user_id: str, message: str, timeout: int = 60) -> str:
    """Process a user message through their isolated profile with memory, vault, and tools."""
    cfg = get_user_config(user_id)
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    model = cfg.get("model", {}).get("model", "accounts/fireworks/models/deepseek-v4-flash-0731")

    # Build system prompt with user context
    memories = load_memories(user_id)
    vault = read_vault(user_id)
    agent_name = cfg.get("profile", {}).get("agent_name", "Agent")
    tools_enabled = cfg.get("tools", {})
    max_msgs = cfg.get("messaging", {}).get("max_daily_messages", 0)

    system = f"You are {agent_name}, a helpful AI assistant.\n"
    system += f"Your user's knowledge vault contains these recent notes:\n{vault}\n" if vault else ""
    system += f"\nAvailable tools: " + ", ".join(k for k, v in tools_enabled.items() if v) if any(tools_enabled.values()) else ""

    messages = [{"role": "system", "content": system}]
    # Add memory context
    for m in memories[-10:]:
        if isinstance(m, dict) and "content" in m:
            messages.append({"role": m.get("role", "user"), "content": m["content"]})
    messages.append({"role": "user", "content": message})

    resp = await call_ai(model, messages, api_key, timeout)
    save_memory(user_id, message, resp)
    return resp


async def hermes_profile_chat_with_fallback(user_id: str, message: str, timeout: int = 60) -> str:
    """Process message with automatic fallback to backup model."""
    try:
        return await hermes_profile_chat(user_id, message, timeout)
    except Exception as e:
        logger.warning(f"Primary model failed for {user_id}: {e}. Trying backup.")
        cfg = get_user_config(user_id)
        backup_model = cfg.get("model", {}).get("backup", {}).get("model", "")
        if backup_model:
            try:
                api_key = os.environ.get("FIREWORKS_API_KEY", "")
                messages = [{"role": "user", "content": message}]
                return await call_ai(backup_model, messages, api_key, timeout)
            except Exception as e2:
                logger.error(f"Backup also failed: {e2}")
        return "Service temporarily unavailable. Please try again."


def profile_exists(user_id: str) -> bool:
    return (PROFILES_ROOT / user_id).exists()


def get_user_profile_dir(user_id: str) -> str:
    return str(PROFILES_ROOT / user_id)


async def update_user_model_config(user_id: str, primary_model: str = None, backup_model: str = None):
    """Update a user's model configuration."""
    profile_dir = PROFILES_ROOT / user_id
    config_path = profile_dir / "config.yaml"
    import yaml
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {"model": {}}
    if "model" not in cfg: cfg["model"] = {}
    if primary_model: cfg["model"]["model"] = primary_model
    if backup_model: cfg["model"]["backup"] = {"model": backup_model, "provider": "fireworks"}
    with open(config_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)


async def write_user_skill(user_id: str, skill_name: str, content: str) -> str:
    """Add or update a skill for a specific user."""
    skills_dir = PROFILES_ROOT / user_id / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    path = skills_dir / f"{skill_name.replace(' ', '-').lower()}.md"
    path.write_text(content)
    return str(path)


async def write_global_skill_template(skill_name: str, content: str) -> dict:
    """Add a skill template to all user profiles."""
    results = {}
    for d in PROFILES_ROOT.iterdir():
        if d.is_dir():
            try:
                path = await write_user_skill(d.name, skill_name, content)
                results[d.name] = str(path)
            except Exception as e:
                results[d.name] = f"error: {e}"
    return results
