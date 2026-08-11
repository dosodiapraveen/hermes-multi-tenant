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


async def search_web(query: str, num_results: int = 5) -> tuple:
    """Search via SearXNG and scrape the top result. Returns (search_results, page_content)."""
    import asyncio
    try:
        import httpx, re
        search_lines = []
        page_content = ""
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get("http://searxng:8080/search", params={"q": query, "format": "json", "language": "en", "categories": "general", "pageno": 1})
            if r.status_code != 200:
                raise Exception(f"SearXNG returned {r.status_code}")
            data = r.json()
            results = data.get("results", [])
            for res in results[:num_results]:
                title = res.get("title", "")
                url = res.get("url", "")
                snippet = res.get("content", "")[:200]
                search_lines.append(f"- {title}\n  {snippet}\n  {url}")

            # Scrape the top result for actual content (fast timeout, best-effort)
            if results:
                top_url = results[0].get("url", "")
                if top_url:
                    try:
                        import re
                        r2 = await c.get(top_url, follow_redirects=True, timeout=5,
                            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
                        text = r2.text
                        # Remove scripts and styles
                        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
                        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
                        # Get all visible text
                        text = re.sub(r"<[^>]+>", "\n", text)
                        text = re.sub(r"\n\s*\n", "\n", text).strip()
                        # Take first 2000 chars of meaningful content
                        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 20]
                        page_content = "\n".join(lines[:80])[:2500]
                    except:
                        page_content = ""  # Scraping failed, use search snippets only

        search_text = "\n\n".join(search_lines) if search_lines else "No results found."
        if page_content:
            search_text += f"\n\n--- Page content from {results[0].get('url','')} ---\n{page_content}"
        return search_text, page_content
    except Exception as e:
        # Fallback to Wikipedia
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
                snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))[:200]
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                results.append(f"- {title}\n  {snippet}\n  {url}")
            text = "\n\n".join(results) if results else "No results found."
            return text, ""
        except:
            return "Search failed. Please try again.", ""

async def hermes_profile_chat(user_id: str, message: str, timeout: int = 60, profile_dir: str = None) -> str:
    """Process a user message through their isolated profile with memory, vault, and tools."""
    uid = profile_dir.split("/")[-1] if profile_dir else user_id
    cfg = get_user_config(uid)
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    model = cfg.get("model", {}).get("model", "accounts/fireworks/models/deepseek-v4-flash-0731")

    memories = load_memories(uid)
    vault = read_vault(uid)
    agent_name = cfg.get("profile", {}).get("agent_name", "Agent")

    system = f"You are {agent_name}, a helpful AI assistant with web search, vault read/write, and memory tools."
    system += f"\n\nCurrent vault notes:\n{vault}" if vault else ""

    messages = [{"role": "system", "content": system}]
    for m in memories[-10:]:
        if isinstance(m, dict) and "content" in m:
            messages.append({"role": m.get("role", "user"), "content": m["content"]})
    messages.append({"role": "user", "content": message})

    # Auto-trigger web_search for search-like queries (model often refuses)
    search_triggers = ["search", "look up", "lookup", "find", "what is", "who is",
                       "top ", "latest", "news about", "weather", "how to",
                       "tell me about", "show me"]
    msg_lower = message.lower()
    should_search = any(t in msg_lower for t in search_triggers)

    if should_search:
        # Run search, feed results to model for analysis (no memory needed)
        results, page_content = await search_web(message, 5)
        context = f"Search results for query '{message}':\n{results}"
        if page_content:
            context += f"\n\n--- Content from top result ---\n{page_content}"
        context += "\n\nUsing the information above, provide a thorough answer. Include specific details, data, and links. If the search results contain the answer, present it directly."
        search_messages = [messages[0], {"role": "system", "content": context}, {"role": "user", "content": message}]
        content, tool_calls = await call_ai(model, search_messages, api_key, timeout)
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
