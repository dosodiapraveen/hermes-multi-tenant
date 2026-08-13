"""Semantic search over a user's data (notes, projects, research, ideas,
reminders, vault) using Fireworks qwen3-embedding-8b + cosine similarity.

Embeddings are stored as JSONB so no pgvector/container change is required.
Per-user data is small, so brute-force cosine over that user's rows is fast.
"""
import asyncio
import json
import math
import os
from typing import Any, List

import httpx
from sqlalchemy import text

from app.database import async_session_factory

EMBED_MODEL = "accounts/fireworks/models/qwen3-embedding-8b"
EMBED_DIM = 1536  # qwen3-embedding-8b output dim (if different, we pad/truncate)


def _get_api_key() -> str:
    return (os.environ.get("FIREWORKS_API_KEY") or os.environ.get("LLM_API_KEY") or "").strip()


async def _embed_batch(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts via Fireworks. Returns list of vectors (dim EMBED_DIM)."""
    key = _get_api_key()
    if not key:
        raise RuntimeError("No Fireworks API key configured")
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            "https://api.fireworks.ai/inference/v1/embeddings",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": EMBED_MODEL, "input": texts},
        )
        r.raise_for_status()
        data = r.json()
        vectors = [d["embedding"] for d in data.get("data", [])]
    # Normalize to fixed dim
    out = []
    for v in vectors:
        v = v[:EMBED_DIM]
        if len(v) < EMBED_DIM:
            v = v + [0.0] * (EMBED_DIM - len(v))
        out.append(v)
    return out


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


async def _collect_blobs(uid: str, db) -> List[dict]:
    """Gather all searchable text blobs for a user across sources."""
    blobs: List[dict] = []
    cur = await db.execute(text(
        "SELECT id::text, title, content FROM notes WHERE user_id::text=:u"
    ), {"u": uid})
    for row in cur.fetchall():
        blobs.append({"type": "note", "sid": row[0], "title": row[1] or "",
                      "content": f"{row[1] or ''}\n{row[2] or ''}"})

    cur = await db.execute(text(
        "SELECT id::text, title, description FROM projects WHERE user_id::text=:u"
    ), {"u": uid})
    for row in cur.fetchall():
        blobs.append({"type": "project", "sid": row[0], "title": row[1] or "",
                      "content": f"{row[1] or ''}\n{row[2] or ''}"})

    cur = await db.execute(text(
        "SELECT pr.id::text, pr.title, pr.content FROM project_research pr "
        "JOIN projects p ON p.id=pr.project_id WHERE p.user_id::text=:u"
    ), {"u": uid})
    for row in cur.fetchall():
        blobs.append({"type": "research", "sid": row[0], "title": row[1] or "",
                      "content": f"{row[1] or ''}\n{row[2] or ''}"})

    cur = await db.execute(text(
        "SELECT id::text, title, content FROM ideas WHERE user_id::text=:u"
    ), {"u": uid})
    for row in cur.fetchall():
        blobs.append({"type": "idea", "sid": row[0], "title": row[1] or "",
                      "content": f"{row[1] or ''}\n{row[2] or ''}"})

    cur = await db.execute(text(
        "SELECT id::text, title FROM reminders WHERE user_id::text=:u"
    ), {"u": uid})
    for row in cur.fetchall():
        blobs.append({"type": "reminder", "sid": row[0], "title": row[1] or "",
                      "content": row[1] or ""})

    # Vault markdown files (Inbox)
    try:
        from pathlib import Path
        inbox = Path("/opt/hermes/obsidian") / uid / "Inbox"
        if inbox.exists():
            for f in sorted(inbox.glob("*.md")):
                text_content = f.read_text(errors="ignore")
                title = text_content.split("\n")[0].replace("#", "").strip()[:120] or f.stem
                blobs.append({"type": "vault", "sid": f.name, "title": title,
                              "content": text_content[:4000]})
    except Exception:
        pass

    return blobs


async def index_user_data(uid: str) -> int:
    """(Re)index all of a user's data into embeddings. Returns count indexed."""
    async with async_session_factory() as db:
        blobs = await _collect_blobs(uid, db)
        if not blobs:
            return 0
        texts = [b["content"][:4000] or b["title"] for b in blobs]
        vectors = await _embed_batch(texts)
        for b, vec in zip(blobs, vectors):
            await db.execute(text("""
                INSERT INTO user_data_embeddings
                  (user_id, source_type, source_id, title, content, embedding, indexed_at)
                VALUES (:u, :t, :sid, :title, :content, :emb, NOW())
                ON CONFLICT (user_id, source_type, source_id)
                DO UPDATE SET title=EXCLUDED.title, content=EXCLUDED.content,
                              embedding=EXCLUDED.embedding, indexed_at=NOW()
            """), {"u": uid, "t": b["type"], "sid": b["sid"],
                   "title": b["title"], "content": b["content"][:4000],
                   "emb": json.dumps(vec)})
        await db.commit()
    return len(blobs)


async def search_user_data(uid: str, query: str, limit: int = 8) -> dict:
    """Semantic search across a user's indexed data. Auto-indexes if empty."""
    async with async_session_factory() as db:
        # Auto-index if the user has no embeddings yet
        n = await db.execute(text(
            "SELECT COUNT(*) FROM user_data_embeddings WHERE user_id::text=:u"
        ), {"u": uid})
        if (n.fetchone()[0] or 0) == 0:
            try:
                await index_user_data(uid)
            except Exception as e:
                return {"results": [], "error": f"Indexing failed: {e}"}

        qvec = (await _embed_batch([query]))[0]

        r = await db.execute(text("""
            SELECT source_type, source_id, title, content, embedding
            FROM user_data_embeddings WHERE user_id::text=:u
        """), {"u": uid})
        rows = r.fetchall()

        scored = []
        for row in rows:
            embed_col = row[4]
            # asyncpg auto-decodes JSONB to a Python list; guard for str too
            if isinstance(embed_col, str):
                vec = json.loads(embed_col)
            else:
                vec = embed_col or []
            score = _cosine(qvec, vec)
            scored.append({
                "type": row[0], "id": row[1], "title": row[2],
                "content": row[3], "score": round(score, 4),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        # Keep only reasonably relevant results, then top N
        results = [
            {k: s[k] for k in ("type", "id", "title", "content", "score")}
            for s in scored[:limit]
        ]
        return {"results": results}
