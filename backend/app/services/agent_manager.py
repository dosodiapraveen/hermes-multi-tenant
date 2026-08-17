"""Hermes Agent Manager - routes user messages through AI with memory & tools.

Performance optimizations:
- Async file I/O with aiofiles
- TTL caching for user context (memories, vault, config)
- Async HTTP calls (no blocking requests)
- Smart search triggering with intent classification
"""
import os, json, logging, asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, AsyncGenerator
import httpx
import aiofiles
import aiofiles.os
from cachetools import TTLCache

logger = logging.getLogger(__name__)
PROFILES_ROOT = Path("/opt/hermes/profiles")

# TTL caches for user context (30 second TTL to balance freshness vs performance)
_config_cache: TTLCache = TTLCache(maxsize=100, ttl=60)  # Config changes rarely
_memories_cache: TTLCache = TTLCache(maxsize=100, ttl=30)
_vault_cache: TTLCache = TTLCache(maxsize=100, ttl=30)
_kb_cache: TTLCache = TTLCache(maxsize=100, ttl=30)
_personality_cache: TTLCache = TTLCache(maxsize=100, ttl=60)


async def get_user_personality(uid: str) -> Optional[str]:
    """Load user personality from DB with caching."""
    if uid in _personality_cache:
        return _personality_cache[uid]
    from app.database import async_session_factory
    from sqlalchemy import text
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT personality FROM user_profiles WHERE id::text=:u"), {"u": uid})
        row = r.fetchone()
        personality = (row[0] if row else None) or None
        _personality_cache[uid] = personality
        return personality


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
    {
        "type": "function",
        "function": {
            "name": "create_dashboard_note",
            "description": "Save a note to the user's dashboard and vault. Use this when the user says 'save a note' or 'add a note'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content"},
                    "category": {"type": "string", "description": "Category like General, Work, Personal (optional)"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dashboard_notes",
            "description": "Show all notes from the user's dashboard.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_detail",
            "description": "Get details and research for a specific project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The project ID from list_projects"},
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_user_data",
            "description": "Semantically search across the user's own data (notes, projects, research, ideas, reminders, vault). Use for 'what did I write about X' or to recall the user's own stored information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"}
                },
                "required": ["query"],
            },
        },
    },
]

FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"


async def call_ai(model: str, messages: list, api_key: str, timeout: int = 30, tools: list = None) -> tuple:
    """Call Fireworks AI and return (content, tool_calls)."""
    body = {"model": model, "messages": messages, "max_tokens": 4096, "temperature": 0.7}
    if tools: body["tools"] = tools
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(
            FIREWORKS_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
        )
        r.raise_for_status()
        choice = r.json()["choices"][0]
        msg = choice["message"]
        return msg.get("content", ""), msg.get("tool_calls", [])


async def call_ai_stream(
    model: str, messages: list, api_key: str, timeout: int = 60, tools: list = None
) -> AsyncGenerator[dict, None]:
    """Stream tokens from Fireworks AI. Yields dicts with type: token|tool_call|done."""
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
        "stream": True,
    }
    if tools:
        body["tools"] = tools

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Track accumulated tool calls (streamed incrementally)
    tool_calls_acc: dict = {}

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", FIREWORKS_URL, headers=headers, json=body) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                if line == "data: [DONE]":
                    # Yield accumulated tool calls if any
                    if tool_calls_acc:
                        for tc in tool_calls_acc.values():
                            yield {"type": "tool_call", "tool_call": tc}
                    yield {"type": "done"}
                    return

                try:
                    data = json.loads(line[6:])  # Skip "data: "
                    delta = data.get("choices", [{}])[0].get("delta", {})

                    # Handle content tokens
                    if "content" in delta and delta["content"]:
                        yield {"type": "token", "content": delta["content"]}

                    # Handle tool calls (streamed incrementally)
                    if "tool_calls" in delta:
                        for tc_delta in delta["tool_calls"]:
                            idx = tc_delta.get("index", 0)
                            if idx not in tool_calls_acc:
                                tool_calls_acc[idx] = {
                                    "id": tc_delta.get("id", ""),
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""},
                                }
                            tc = tool_calls_acc[idx]
                            if tc_delta.get("id"):
                                tc["id"] = tc_delta["id"]
                            fn = tc_delta.get("function", {})
                            if fn.get("name"):
                                tc["function"]["name"] = fn["name"]
                            if fn.get("arguments"):
                                tc["function"]["arguments"] += fn["arguments"]

                except json.JSONDecodeError:
                    continue


async def get_user_config(uid: str) -> dict:
    """Load user config with caching."""
    if uid in _config_cache:
        return _config_cache[uid]

    profile_dir = PROFILES_ROOT / uid
    config_path = profile_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No profile for user {uid}")

    import yaml
    async with aiofiles.open(config_path, 'r') as f:
        content = await f.read()
        config = yaml.safe_load(content)
        _config_cache[uid] = config
        return config


async def load_memories(uid: str) -> list:
    """Load user memories with caching and async I/O."""
    if uid in _memories_cache:
        return _memories_cache[uid]

    memories_dir = PROFILES_ROOT / uid / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)

    # Get file list (this is fast, sync is OK)
    files = sorted(memories_dir.glob("*.json"))[-5:]

    # Read files concurrently
    async def read_memory(f: Path) -> Optional[dict]:
        try:
            async with aiofiles.open(f, 'r') as fp:
                content = await fp.read()
                return json.loads(content)
        except Exception:
            return None

    tasks = [read_memory(f) for f in files]
    results = await asyncio.gather(*tasks)
    history = [m for m in results if m is not None]

    _memories_cache[uid] = history
    return history


async def save_memory(uid: str, user_msg: str, ai_msg: str):
    """Save memory asynchronously and invalidate cache."""
    ts = datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')
    memories_dir = PROFILES_ROOT / uid / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)

    user_data = json.dumps({"role": "user", "content": user_msg, "timestamp": datetime.utcnow().isoformat()})
    ai_data = json.dumps({"role": "assistant", "content": ai_msg, "timestamp": datetime.utcnow().isoformat()})

    async with aiofiles.open(memories_dir / f"{ts}.json", "w") as f:
        await f.write(user_data)
    async with aiofiles.open(memories_dir / f"{ts}-resp.json", "w") as f:
        await f.write(ai_data)

    # Invalidate cache so next load gets fresh data
    _memories_cache.pop(uid, None)


async def read_vault(uid: str) -> str:
    """Read vault notes with caching and async I/O."""
    if uid in _vault_cache:
        return _vault_cache[uid]

    vault_dir = PROFILES_ROOT.parent / "obsidian" / uid
    notes = []

    async def read_note(f: Path) -> Optional[str]:
        try:
            async with aiofiles.open(f, 'r') as fp:
                content = await fp.read()
                return f"--- {f.name} ---\n{content[:800]}"
        except Exception:
            return None

    for sub in ["Inbox", "Notes"]:
        d = vault_dir / sub
        if d.exists():
            files = sorted(d.glob("*.md"))[-5:]
            tasks = [read_note(f) for f in files]
            results = await asyncio.gather(*tasks)
            notes.extend([n for n in results if n is not None])

    result = "\n\n".join(notes) if notes else ""
    _vault_cache[uid] = result
    return result


async def write_note(uid: str, title: str, content: str) -> str:
    """Write note asynchronously and invalidate cache."""
    inbox = PROFILES_ROOT.parent / "obsidian" / uid / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / f"{title.replace(' ', '-')[:50].lower()}.md"
    text = f"# {title}\n\n{content}\n\n---\nSaved by Hermes on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

    async with aiofiles.open(path, 'w') as f:
        await f.write(text)

    # Invalidate vault cache
    _vault_cache.pop(uid, None)
    return f"Saved to {path.name}"


async def read_knowledge_base(uid: str) -> str:
    """Read knowledge base with caching and async I/O."""
    if uid in _kb_cache:
        return _kb_cache[uid]

    kb_dir = PROFILES_ROOT.parent / "obsidian" / uid / "Knowledge"
    if not kb_dir.exists():
        result = "No documents in your knowledge base yet. Upload a PDF or document to get started."
        _kb_cache[uid] = result
        return result

    docs = []

    async def read_doc(f: Path) -> str:
        if f.suffix.lower() in (".txt", ".md", ".csv"):
            try:
                async with aiofiles.open(f, 'r') as fp:
                    content = await fp.read()
                    return f"--- {f.name} ---\n{content[:1500]}"
            except Exception:
                return f"--- {f.name} ---\n[Error reading file]"
        else:
            try:
                stat = f.stat()
                return f"--- {f.name} ({stat.st_size//1024} KB) ---\nUploaded document. Ask me about its contents."
            except Exception:
                return f"--- {f.name} ---\nUploaded document."

    files = sorted(kb_dir.iterdir())[:10]
    tasks = [read_doc(f) for f in files]
    docs = await asyncio.gather(*tasks)

    result = "\n\n".join(docs) if docs else "Knowledge base is empty."
    _kb_cache[uid] = result
    return result


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




async def create_dashboard_note(uid: str, title: str, content: str, category: str = "General") -> str:
    """Create a note in the user's dashboard DB and sync to vault."""
    from app.database import async_session_factory
    from sqlalchemy import text as sqltext
    from pathlib import Path
    from datetime import datetime
    async with async_session_factory() as db:
        r = await db.execute(
            sqltext("INSERT INTO notes (user_id, title, content, category) VALUES (:u, :t, :c, :cat) RETURNING id"),
            {"u": uid, "t": title, "c": content, "cat": category},
        )
        await db.commit()
        nid = r.fetchone()[0]
    # Sync to vault
    try:
        inbox = Path("/opt/hermes/obsidian") / uid / "Inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        path = inbox / f"{title.replace(chr(32), chr(45))[:50].lower()}.md"
        path.write_text(f"# {title}\n\n{content}\n\n---\nFrom dashboard")
    except Exception:
        pass
    return f"Note saved: {title} (in {category})"


async def list_dashboard_notes(uid: str) -> str:
    from app.database import async_session_factory
    from sqlalchemy import text as sqltext
    async with async_session_factory() as db:
        r = await db.execute(
            sqltext("SELECT title, category, updated_at FROM notes WHERE user_id::text=:u ORDER BY updated_at DESC LIMIT 10"),
            {"u": uid},
        )
        rows = r.fetchall()
        if not rows:
            return "No dashboard notes."
        return "\n".join(f"📝 {row[0]} ({row[1]}) - {str(row[2])[:10]}" for row in rows)

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
    """Fallback search using Wikipedia - now fully async."""
    import re
    from urllib.parse import unquote
    try:
        headers = {"User-Agent": "HermesAgent/1.0 (hermes@beprepared.dev)"}
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get("https://en.wikipedia.org/w/api.php", params={
                "action": "query", "list": "search", "srsearch": query,
                "format": "json", "srlimit": num_results
            }, headers=headers)
            r.raise_for_status()
            data = r.json()

        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            snippet = unquote(item.get("snippet", "").replace("&amp;", "&"))
            snippet = re.sub(r"<[^>]+>", "", snippet)[:200]
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            results.append(f"- {title}\n  {snippet}\n  {url}")
        text = "\n\n".join(results) if results else "No results found."
        return text, ""
    except Exception as e:
        logger.warning(f"Wikipedia search fallback failed: {e}")
        return "Search unavailable. Please try again.", ""

def _should_trigger_search(message: str) -> bool:
    """Smart search triggering - only trigger for queries that genuinely need web search.

    Avoids triggering on common conversational phrases that happen to contain trigger words.
    """
    msg_lower = message.lower().strip()

    # Skip very short messages (unlikely to be real search queries)
    if len(msg_lower) < 10:
        return False

    # Explicit search intent - high confidence
    explicit_search = [
        "search for ", "search the web", "look up ", "google ",
        "find information about", "find out about", "research ",
    ]
    if any(msg_lower.startswith(t) or f" {t}" in msg_lower for t in explicit_search):
        return True

    # Current events/news - needs web search
    current_events = [
        "latest news", "recent news", "today's news", "current news",
        "what happened", "breaking news", "news about",
        "current price", "stock price", "weather in", "weather today",
        "score of", "game score", "match result",
    ]
    if any(t in msg_lower for t in current_events):
        return True

    # Factual questions that need current data
    factual_current = [
        "who is the current", "who is the president", "who won",
        "what is the latest", "what are the latest",
        "how much does", "how much is", "current status of",
    ]
    if any(t in msg_lower for t in factual_current):
        return True

    # DON'T trigger on conversational phrases
    conversational_skip = [
        "how are you", "how is your", "how is it going",
        "what is your name", "what are you", "who are you",
        "tell me about yourself", "show me what you can",
        "what is the meaning", "what is love", "what is life",
        "find my notes", "find my", "search my",  # User's own data, not web
    ]
    if any(t in msg_lower for t in conversational_skip):
        return False

    # Questions starting with these usually need web data
    if msg_lower.startswith(("what is ", "who is ", "where is ", "when did ", "when was ")):
        # But not if they're about the agent or user's data
        if any(x in msg_lower for x in ["my ", "your ", "you ", "i "]):
            return False
        return True

    return False


async def _execute_tool(uid: str, name: str, args: dict) -> str:
    """Execute a single tool and return the result string."""
    if name == "save_note":
        return await write_note(uid, args.get("title", "Note"), args.get("content", ""))
    elif name == "read_vault":
        return await read_vault(uid) or "Vault is empty"
    elif name == "web_search":
        result, _ = await search_web(args.get("query", ""))
        return result
    elif name == "read_knowledge_base":
        return await read_knowledge_base(uid)
    elif name == "create_reminder":
        return await create_reminder(uid, args.get("title", ""), args.get("remind_at"))
    elif name == "list_reminders":
        return await list_reminders(uid)
    elif name == "create_project":
        return await create_project(uid, args.get("title", ""), args.get("description", ""))
    elif name == "list_projects":
        return await list_projects(uid)
    elif name == "create_dashboard_note":
        return await create_dashboard_note(uid, args.get("title", ""), args.get("content", ""), args.get("category", "General"))
    elif name == "list_dashboard_notes":
        return await list_dashboard_notes(uid)
    elif name == "search_user_data":
        from app.services.search import search_user_data as _search
        try:
            _r = await _search(uid, args.get("query", ""), limit=6)
            _results = _r.get("results", [])
            if not _results:
                return "No matches found in your data."
            _out = ["Here's what I found in your data:"]
            for _it in _results[:6]:
                _out.append(f"• [{_it.get('type','')}] {_it.get('title','')}: {_it.get('content','')[:180].replace(chr(10),' ')} (score {_it.get('score','')})")
            return "\n".join(_out)
        except Exception as _e:
            return f"Search error: {_e}"
    elif name == "get_project_detail":
        pid = args.get("project_id", "")
        from app.database import async_session_factory
        from sqlalchemy import text as sqltext
        async with async_session_factory() as db:
            r = await db.execute(sqltext("SELECT title, description, status, updated_at FROM projects WHERE id::text=:p AND user_id::text=:u"), {"p": pid, "u": uid})
            p = r.fetchone()
            if not p:
                return "Project not found"
            rr = await db.execute(sqltext("SELECT title, content FROM project_research WHERE project_id::text=:p ORDER BY created_at DESC"), {"p": pid})
            research = "\n".join(f"📄 {row[0]}: {row[1][:200]}" for row in rr.fetchall()) or "No research"
            return f"📋 {p[0]}\n{p[1]}\nStatus: {p[2]}\nUpdated: {str(p[3])[:10]}\n\nResearch:\n{research}"
    else:
        return "Done."


async def hermes_profile_chat_stream(
    user_id: str, message: str, timeout: int = 60, profile_dir: str = None, personality: str = None
) -> AsyncGenerator[dict, None]:
    """Streaming chat handler. Yields SSE-compatible events."""
    uid = profile_dir.split("/")[-1] if profile_dir else user_id
    api_key = os.environ.get("FIREWORKS_API_KEY", "")

    from app.services.persona import DEFAULT_PERSONALITY

    # Send loading status
    yield {"event": "status", "data": {"status": "loading", "message": "Loading context..."}}

    # Load ALL context in ONE parallel gather
    personality_coro = (
        asyncio.sleep(0, result=personality)
        if (personality and personality.strip())
        else get_user_personality(user_id)
    )

    results = await asyncio.gather(
        get_user_config(uid),
        load_memories(uid),
        read_vault(uid),
        read_knowledge_base(uid),
        personality_coro,
        return_exceptions=True,
    )

    cfg = results[0] if not isinstance(results[0], Exception) else {}
    memories = results[1] if not isinstance(results[1], Exception) else []
    vault = results[2] if not isinstance(results[2], Exception) else ""
    kb = results[3] if not isinstance(results[3], Exception) else ""
    db_personality = results[4] if not isinstance(results[4], Exception) else None

    model = cfg.get("model", {}).get("model", "accounts/fireworks/models/deepseek-v4-flash-0731")
    agent_name = cfg.get("profile", {}).get("agent_name", "Agent")

    if not (personality and personality.strip()):
        personality = db_personality

    # Build system prompt
    if personality and personality.strip():
        system = f"You are {agent_name}.\n\n{personality.strip()}"
        system += f"\n\n(This is your personality/SOUL file. Follow it as written in every reply.)"
    else:
        system = DEFAULT_PERSONALITY.format(agent_name=agent_name)
        system += f"\n\nYou are {agent_name}, running with the default personality above. Use your tools (web search, vault, notes, projects, reminders)."

    system += f"\n\n📚 Your knowledge base contains:\n{kb}" if kb and "No documents" not in kb else ""
    system += f"\n\n📝 Your vault:\n{vault}" if vault else ""

    messages = [{"role": "system", "content": system}]
    for m in memories[-10:]:
        if isinstance(m, dict) and "content" in m:
            messages.append({"role": m.get("role", "user"), "content": m["content"]})
    messages.append({"role": "user", "content": message})

    # Check if this needs web search
    should_search = _should_trigger_search(message)

    if should_search:
        yield {"event": "status", "data": {"status": "searching", "message": "Searching the web..."}}
        search_results, sources = await search_web(message, 5)
        context = f"Search results for: {message}\n\n{search_results}"
        if sources:
            context += f"\n\nSources:\n{sources}"
        context += "\n\nUsing the search results above, answer the user's question directly and naturally. Include specific data, names, numbers, and link to sources. Do not mention that you searched."
        messages = [messages[0], {"role": "system", "content": context}, {"role": "user", "content": message}]

    yield {"event": "status", "data": {"status": "thinking", "message": "Thinking..."}}

    # Stream the response
    full_response = ""
    tool_calls_received = []

    async for chunk in call_ai_stream(model, messages, api_key, timeout, tools=None if should_search else TOOLS):
        if chunk["type"] == "token":
            full_response += chunk["content"]
            yield {"event": "chunk", "data": {"token": chunk["content"]}}
        elif chunk["type"] == "tool_call":
            tool_calls_received.append(chunk["tool_call"])
        elif chunk["type"] == "done":
            break

    # Handle tool calls if any
    if tool_calls_received:
        messages.append({"role": "assistant", "content": full_response if full_response else None, "tool_calls": tool_calls_received})

        for tc in tool_calls_received:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args_raw = fn.get("arguments", "{}")

            yield {"event": "tool_start", "data": {"tool": name, "arguments": args_raw}}

            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                result = await _execute_tool(uid, name, args)
            except Exception as e:
                result = f"Error: {e}"

            yield {"event": "tool_result", "data": {"tool": name, "result": result[:500]}}
            messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": result})

        # Stream final response after tool execution
        yield {"event": "status", "data": {"status": "thinking", "message": "Processing results..."}}
        full_response = ""
        async for chunk in call_ai_stream(model, messages, api_key, timeout, tools=None):
            if chunk["type"] == "token":
                full_response += chunk["content"]
                yield {"event": "chunk", "data": {"token": chunk["content"]}}
            elif chunk["type"] == "done":
                break

    # Save memory
    await save_memory(uid, message, full_response or "")

    yield {"event": "complete", "data": {"response": full_response or "Done."}}


async def hermes_profile_chat(user_id: str, message: str, timeout: int = 60, profile_dir: str = None, personality: str = None) -> str:
    """Process a user message through their isolated profile with memory, vault, and tools."""
    uid = profile_dir.split("/")[-1] if profile_dir else user_id
    api_key = os.environ.get("FIREWORKS_API_KEY", "")

    from app.services.persona import DEFAULT_PERSONALITY

    # Load ALL context in ONE parallel gather for maximum performance
    # If personality is already provided, skip the DB lookup
    personality_coro = (
        asyncio.sleep(0, result=personality)
        if (personality and personality.strip())
        else get_user_personality(user_id)
    )

    results = await asyncio.gather(
        get_user_config(uid),
        load_memories(uid),
        read_vault(uid),
        read_knowledge_base(uid),
        personality_coro,
        return_exceptions=True,
    )

    # Unpack results, handling any exceptions
    cfg = results[0] if not isinstance(results[0], Exception) else {}
    memories = results[1] if not isinstance(results[1], Exception) else []
    vault = results[2] if not isinstance(results[2], Exception) else ""
    kb = results[3] if not isinstance(results[3], Exception) else ""
    db_personality = results[4] if not isinstance(results[4], Exception) else None

    model = cfg.get("model", {}).get("model", "accounts/fireworks/models/deepseek-v4-flash-0731")
    agent_name = cfg.get("profile", {}).get("agent_name", "Agent")

    # Use provided personality, or DB personality, or None
    if not (personality and personality.strip()):
        personality = db_personality

    if personality and personality.strip():
        system = f"You are {agent_name}.\n\n{personality.strip()}"
        system += f"\n\n(This is your personality/SOUL file. Follow it as written in every reply.)"
    else:
        system = DEFAULT_PERSONALITY.format(agent_name=agent_name)
        system += f"\n\nYou are {agent_name}, running with the default personality above. Use your tools (web search, vault, notes, projects, reminders)."

    system += f"\n\n📚 Your knowledge base contains:\n{kb}" if kb and "No documents" not in kb else ""
    system += f"\n\n📝 Your vault:\n{vault}" if vault else ""

    messages = [{"role": "system", "content": system}]
    for m in memories[-10:]:
        if isinstance(m, dict) and "content" in m:
            messages.append({"role": m.get("role", "user"), "content": m["content"]})
    messages.append({"role": "user", "content": message})

    # Smart search triggering - avoids unnecessary web searches
    should_search = _should_trigger_search(message)

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
        await save_memory(uid, message, content or "Search completed.")
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
                    result = await _execute_tool(uid, name, args)
                except Exception as e:
                    result = f"Error: {e}"
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": result})
            # Get final response after tool execution
            content, _ = await call_ai(model, messages, api_key, timeout)

    await save_memory(uid, message, content or "")
    return content or "Done."


async def hermes_profile_chat_with_fallback(user_id: str, message: str, timeout: int = 60, profile_dir: str = None) -> str:
    try:
        return await hermes_profile_chat(user_id, message, timeout, profile_dir)
    except Exception as e:
        logger.warning(f"Primary model failed for {user_id}: {e}. Trying backup.")
        uid = profile_dir.split("/")[-1] if profile_dir else user_id
        try:
            cfg = await get_user_config(uid)
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
        async with aiofiles.open(config_path, 'r') as f:
            content = await f.read()
            cfg = yaml.safe_load(content) or {}
    else:
        cfg = {"model": {}}

    if "model" not in cfg:
        cfg["model"] = {}
    if primary_model:
        cfg["model"]["model"] = primary_model
    if backup_model:
        cfg["model"]["backup"] = {"model": backup_model, "provider": "fireworks"}

    async with aiofiles.open(config_path, "w") as f:
        await f.write(yaml.dump(cfg, default_flow_style=False))

    # Invalidate config cache
    _config_cache.pop(user_id, None)


async def write_user_skill(user_id: str, skill_name: str, content: str) -> str:
    skills_dir = PROFILES_ROOT / user_id / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    path = skills_dir / f"{skill_name.replace(' ', '-').lower()}.md"
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)
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
