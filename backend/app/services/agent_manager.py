"""Hermes Agent Manager - routes user messages through AI with memory & tools."""
import os, json, logging
from pathlib import Path
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)
PROFILES_ROOT = Path("/opt/hermes/profiles")

# ── Tool definitions ──

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Save a note to the user's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Full note content"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_vault",
            "description": "Read the user's knowledge vault notes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use this for news, facts, or anything you don't know.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_knowledge_base",
            "description": "Read documents from the user's knowledge base (uploaded PDFs, docs, reports). Use this when the user asks about their uploaded documents or stored knowledge.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Set a reminder for the user. remind_at is optional (ISO datetime or natural language like 'tomorrow 2pm').",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Reminder title"},
                    "remind_at": {"type": "string", "description": "When to remind (optional, e.g. '2026-08-12T14:00')"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "Show all reminders for the user.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Project title"},
                    "description": {"type": "string", "description": "Project description"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "Show all projects for the user.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

async def call_ai(model: str, messages: list, api_key: str, timeout: int = 30, tools: list = None) -> tuple:
    """Call Fireworks AI and return (content, tool_calls)."""
    body = {"model": model, "messages": messages, "max_tokens": 4096, "temperature": 0.7}
    if tools: body["tools"] = tools
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
        )
        r.raise_for_status()
        choice = r.json()["choices"][0]
        msg = choice["message"]
        return msg.get("content", ""), msg.get("tool_calls", [])


def get_user_config(uid: str) -> dict:
    profile_dir = PROFILES_ROOT / uid
    config_path = profile_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No profile for user {uid}")
    import yaml
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_memories(uid: str) -> list:
    memories_dir = PROFILES_ROOT / uid / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(memories_dir.glob("*.json"))[-5:]
    history = []
    for f in files:
        try:
            with open(f) as fp:
                history.append(json.load(fp))
        except: pass
    return history


def save_memory(uid: str, user_msg: str, ai_msg: str):
    ts = datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')
    with open(PROFILES_ROOT / uid / "memories" / f"{ts}.json", "w") as f:
        json.dump({"role": "user", "content": user_msg, "timestamp": datetime.utcnow().isoformat()}, f)
    with open(PROFILES_ROOT / uid / "memories" / f"{ts}-resp.json", "w") as f:
        json.dump({"role": "assistant", "content": ai_msg, "timestamp": datetime.utcnow().isoformat()}, f)


def read_vault(uid: str) -> str:
    vault_dir = PROFILES_ROOT.parent / "obsidian" / uid
    notes = []
    for sub in ["Inbox", "Notes"]:
        d = vault_dir / sub
        if d.exists():
            for f in sorted(d.glob("*.md"))[-5:]:
                try:
                    notes.append(f"--- {f.name} ---\n{f.read_text()[:800]}")
                except: pass
    return "\n\n".join(notes) if notes else ""


def write_note(uid: str, title: str, content: str) -> str:
    inbox = PROFILES_ROOT.parent / "obsidian" / uid / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / f"{title.replace(' ', '-')[:50].lower()}.md"
    text = f"# {title}\n\n{content}\n\n---\nSaved by Hermes on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    path.write_text(text)
    return f"Saved to {path.name}"


def read_knowledge_base(uid: str) -> str:
    """Read uploaded documents from the user's knowledge base."""
    kb_dir = PROFILES_ROOT.parent / "obsidian" / uid / "Knowledge"
    if not kb_dir.exists():
        return "No documents in your knowledge base yet. Upload a PDF or document to get started."
    docs = []
    for f in sorted(kb_dir.iterdir())[:10]:
        if f.suffix.lower() in (".txt", ".md", ".csv"):
            docs.append(f"--- {f.name} ---\n{f.read_text()[:1500]}")
        else:
            size = f.stat().st_size
            docs.append(f"--- {f.name} ({size//1024} KB) ---\nUploaded document. Ask me about its contents.")
    return "\n\n".join(docs) if docs else "Knowledge base is empty."


async def create_reminder(uid: str, title: str, remind_at: str = None) -> str:
    """Create a reminder for a user."""
    from app.database import async_session_factory
    async with async_session_factory() as db:
        from sqlalchemy import text
        r = await db.execute(
            text("INSERT INTO reminders (user_id, title, remind_at) VALUES (:u, :t, :r) RETURNING id"),
            {"u": uid, "t": title, "r": remind_at},
        )
        await db.commit()
        rid = r.fetchone()[0]
        return f"Reminder set: {title}" + (f" for {remind_at}" if remind_at else "")


async def list_reminders(uid: str) -> str:
    from app.database import async_session_factory
    async with async_session_factory() as db:
        from sqlalchemy import text
        r = await db.execute(
            text("SELECT title, remind_at, done FROM reminders WHERE user_id::text=:u ORDER BY created_at DESC LIMIT 10"),
            {"u": uid},
        )
        rows = r.fetchall()
        if not rows:
            return "No reminders."
        return "\n".join(f"{'✅' if row[2] else '⏳'} {row[0]}{' at ' + str(row[1])[:16] if row[1] else ''}" for row in rows)


async def create_project(uid: str, title: str, description: str = "") -> str:
    from app.database import async_session_factory
    async with async_session_factory() as db:
        from sqlalchemy import text
        await db.execute(
            text("INSERT INTO projects (user_id, title, description) VALUES (:u, :t, :d)"),
            {"u": uid, "t": title, "d": description},
        )
        await db.commit()
        return f"Project created: {title}"


async def list_projects(uid: str) -> str:
    from app.database import async_session_factory
    async with async_session_factory() as db:
        from sqlalchemy import text
        r = await db.execute(
            text("SELECT title, status FROM projects WHERE user_id::text=:u ORDER BY created_at DESC LIMIT 10"),
            {"u": uid},
        )
        rows = r.fetchall()
        if not rows:
            return "No projects."
        emojis = {"active": "🟢", "paused": "🟡", "done": "✅", "archived": "📦"}
        return "\n".join(f"{emojis.get(row[1], '•')} {row[0]} ({row[1]})" for row in rows)


async def search_web(query: str, num_results: int = 5) -> tuple:
    """Search using Brave Search API. Returns (formatted_results, sources_list)."""
    import asyncio, os
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return await _search_fallback(query, num_results)
    try:
        import httpx
        headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=12) as c:
            r = await c.get("https://api.search.brave.com/res/v1/web/search", params={"q": query, "count": num_results}, headers=headers)
            if r.status_code != 200:
                raise Exception(f"Brave returned {r.status_code}")
            data = r.json()
            results = (data.get("web", {}) or {}).get("results", []) or []
            lines = []
            sources = []
            for i, res in enumerate(results[:num_results]):
                title = res.get("title", "")
                desc = res.get("description", "")[:200]
                url = res.get("url", "")
                lines.append(f"- {title}\n  {desc}\n  {url}")
                sources.append(f"{i+1}. {title} - {url}")
            text = "\n\n".join(lines) if lines else "No results found."
            sources_text = "\n".join(sources)
            return text, sources_text
    except Exception as e:
        return await _search_fallback(query, num_results)

async def _search_fallback(query: str, num_results: int = 5) -> tuple:
    """Fallback search using Wikipedia when Gemini is unavailable."""
    import asyncio
    try:
        import requests
        headers = {"User-Agent": "HermesAgent/1.0 (hermes@beprepared.dev)"}
        r = requests.get("https://en.wikipedia.org/w/api.php", params={
            "action": "query", "list": "search", "srsearch": query,
            "format": "json", "srlimit": num_results
        }, headers=headers, timeout=8)
        results = []
        for item in r.json().get("query", {}).get("search", []):
            title = item.get("title", "")
            snippet = requests.utils.unquote(item.get("snippet", "").replace("&amp;", "&"))
            import re
            snippet = re.sub(r"<[^>]+>", "", snippet)[:200]
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            results.append(f"- {title}\n  {snippet}\n  {url}")
        text = "\n\n".join(results) if results else "No results found."
        return text, ""
    except:
        return "Search unavailable. Please try again.", ""

async def hermes_profile_chat(user_id: str, message: str, timeout: int = 60, profile_dir: str = None) -> str:
    """Process a user message through their isolated profile with memory, vault, and tools."""
    uid = profile_dir.split("/")[-1] if profile_dir else user_id
    cfg = get_user_config(uid)
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    model = cfg.get("model", {}).get("model", "accounts/fireworks/models/deepseek-v4-flash-0731")

    memories = load_memories(uid)
    vault = read_vault(uid)
    kb = read_knowledge_base(uid)
    agent_name = cfg.get("profile", {}).get("agent_name", "Agent")

    system = f"You are {agent_name}, a helpful AI assistant with web search, vault read/write, knowledge base, and memory tools."
    system += f"\n\n📚 Your knowledge base contains:\n{kb}" if kb and "No documents" not in kb else ""
    system += f"\n\n📝 Your vault:\n{vault}" if vault else ""

    messages = [{"role": "system", "content": system}]
    for m in memories[-10:]:
        if isinstance(m, dict) and "content" in m:
            messages.append({"role": m.get("role", "user"), "content": m["content"]})
    messages.append({"role": "user", "content": message})

    # Auto-trigger web_search for search-like queries (model often refuses)
    search_triggers = ["search", "look up", "lookup", "find", "what is", "who is",
                       "top ", "latest", "news about", "weather", "how to",
                       "tell me about", "show me", "how is", "what are",
                       "landscape", "overview", "current state", "market",
                       "trends in", "analysis of", "status of"]
    msg_lower = message.lower()
    should_search = any(t in msg_lower for t in search_triggers)

    if should_search:
        # Brave search → DeepSeek analyzes and presents naturally
        results, sources = await search_web(message, 5)
        context = f"Search results for: {message}\n\n{results}"
        if sources:
            context += f"\n\nSources:\n{sources}"
        context += "\n\nUsing the search results above, answer the user's question directly and naturally. Include specific data, names, numbers, and link to sources. Do not mention that you searched."
        search_messages = [messages[0], {"role": "system", "content": context}, {"role": "user", "content": message}]
        content, tool_calls = await call_ai(model, search_messages, api_key, timeout)
        if not content or len(content) < 20:
            retry = [{"role": "system", "content": "Answer the question using this data. Be direct and include details."}]
            retry.append({"role": "user", "content": f"Data:\n{results}\n\nQuestion: {message}"})
            content, _ = await call_ai(model, retry, api_key, timeout)
        save_memory(uid, message, content or "Search completed.")
        return content or "Search completed."
    else:
        # Normal flow - let model decide if it needs tools
        content, tool_calls = await call_ai(model, messages, api_key, timeout, tools=TOOLS)

        # Handle tool calls
        if tool_calls:
            messages.append({"role": "assistant", "content": content if content else None, "tool_calls": tool_calls})
            for tc in tool_calls:
                try:
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    args_raw = fn.get("arguments", "{}")
                    args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                    if name == "save_note":
                        result = write_note(uid, args.get("title", "Note"), args.get("content", ""))
                    elif name == "read_vault":
                        result = read_vault(uid) or "Vault is empty"
                    elif name == "web_search":
                        result, _ = await search_web(args.get("query", ""))
                    elif name == "read_knowledge_base":
                        result = read_knowledge_base(uid)
                    elif name == "create_reminder":
                        result = await create_reminder(uid, args.get("title", ""), args.get("remind_at"))
                    elif name == "list_reminders":
                        result = await list_reminders(uid)
                    elif name == "create_project":
                        result = await create_project(uid, args.get("title", ""), args.get("description", ""))
                    elif name == "list_projects":
                        result = await list_projects(uid)
                    else:
                        result = "Done."
                except Exception as e:
                    result = f"Error: {e}"
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": result})
            # Get final response after tool execution
            content, _ = await call_ai(model, messages, api_key, timeout)

    save_memory(uid, message, content or "")
    return content or "Done."


async def hermes_profile_chat_with_fallback(user_id: str, message: str, timeout: int = 60, profile_dir: str = None) -> str:
    try:
        return await hermes_profile_chat(user_id, message, timeout, profile_dir)
    except Exception as e:
        logger.warning(f"Primary model failed for {user_id}: {e}. Trying backup.")
        uid = profile_dir.split("/")[-1] if profile_dir else user_id
        try:
            cfg = get_user_config(uid)
            backup_model = cfg.get("model", {}).get("backup", {}).get("model", "")
            if backup_model:
                api_key = os.environ.get("FIREWORKS_API_KEY", "")
                content, _ = await call_ai(backup_model, [{"role": "user", "content": message}], api_key, timeout)
                return content
        except Exception as e2:
            logger.error(f"Backup also failed: {e2}")
        return "Service temporarily unavailable. Please try again."


def profile_exists(user_id: str) -> bool:
    return (PROFILES_ROOT / user_id).exists()


def get_user_profile_dir(user_id: str) -> str:
    return str(PROFILES_ROOT / user_id)


async def update_user_model_config(user_id: str, primary_model: str = None, backup_model: str = None):
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
    skills_dir = PROFILES_ROOT / user_id / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    path = skills_dir / f"{skill_name.replace(' ', '-').lower()}.md"
    path.write_text(content)
    return str(path)


async def write_global_skill_template(skill_name: str, content: str) -> dict:
    results = {}
    for d in PROFILES_ROOT.iterdir():
        if d.is_dir():
            try:
                path = await write_user_skill(d.name, skill_name, content)
                results[d.name] = str(path)
            except Exception as e:
                results[d.name] = f"error: {e}"
    return results
