"""Collect + index stages for the CLASSIC frameworks (langgraph/crewai/llamaindex/haystack), so the
full roster covers all three stages. Search stays in frameworks.py; this adds the agentic crawl
(collect) + agentic chunking (index) with a tiny per-framework registry mirroring the agentic-service.

Each framework module registers collect/index callables here; main.py dispatches
/api/vehicle-explore/{framework}/{collect|index}.
"""
import json
import logging
import re
import time
from typing import Callable

from . import agentic_indexer, config, platform, tools

log = logging.getLogger("vehicle-explore")

COLLECT_INSTRUCTIONS = (
    "You are a vehicle resource scout. Given a seed URL, call the fetch_page tool to discover its "
    "links, then return ONLY a JSON array (no prose) of the most relevant vehicle resource links "
    "(vehicle/model pages, brochures, images), at most 15 items, each: "
    '{"url": "...", "type": "page|image|document", "title": "..."}.'
)
INDEX_INSTRUCTIONS = (
    "You are a content indexer. Split the given web content into clean, self-contained chunks for "
    "semantic search: each chunk a coherent passage about one vehicle/topic, with navigation, menus, "
    "and boilerplate removed. Return ONLY a JSON array of strings (the chunk texts), at most 12."
)

# --- tiny registry: framework -> stage callable ---
_COLLECT: dict[str, Callable] = {}
_INDEX: dict[str, Callable] = {}


def register_collect(fw: str, fn: Callable) -> None:
    _COLLECT[fw] = fn


def register_index(fw: str, fn: Callable) -> None:
    _INDEX[fw] = fn


def collect_frameworks() -> list[str]:
    return sorted(_COLLECT)


def index_frameworks() -> list[str]:
    return sorted(_INDEX)


def dispatch_collect(fw: str, ctx: dict) -> dict:
    return _COLLECT[fw](ctx)


def dispatch_index(fw: str, ctx: dict) -> dict:
    return _INDEX[fw](ctx)


# --- parsers ---
def parse_links(text: str) -> list[dict]:
    m = re.search(r"\[.*]", text or "", re.DOTALL)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return []
    out = []
    for it in arr:
        if isinstance(it, str):           # some models emit an array of JSON-encoded strings
            try:
                it = json.loads(it)
            except Exception:  # noqa: BLE001
                continue
        if isinstance(it, dict) and it.get("url"):
            out.append({"url": str(it["url"]), "type": it.get("type") or "page",
                        "title": str(it.get("title") or "")[:200]})
    return out


def parse_chunks(text: str) -> list[str]:
    m = re.search(r"\[.*]", text or "", re.DOTALL)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return []
    return [str(c) for c in arr if isinstance(c, str) and c.strip()]


def _naive_chunks(content: str, size: int = 600, overlap: int = 80) -> list[str]:
    words, out, step = content.split(), [], max(1, 600 - 80)
    for i in range(0, len(words), step):
        out.append(" ".join(words[i:i + size]))
        if len(out) >= 12:
            break
    return out


# --- stage flows (mirror the agentic-service shape) ---
def collect_flow(framework: str, label: str, model_name: str,
                 agent_collect: Callable[[str], str], ctx: dict) -> dict:
    seed = (ctx.get("seedUrl") or "").strip()
    if not seed:
        raise ValueError("seedUrl is required for the collect stage")
    t0, source, error, links = time.perf_counter(), "agent", None, []
    try:
        links = parse_links(agent_collect(seed))
        if not links:
            raise RuntimeError("agent returned no parseable links")
    except Exception as e:  # noqa: BLE001
        log.warning("%s collect failed (%s); direct-fetch fallback", framework, e)
        source, error = "fallback", str(e)[:160]
        try:
            links = [{"url": l["url"], "type": l["type"], "title": ""}
                     for l in tools.fetch_page(seed)["links"][:15]]
        except Exception as e2:  # noqa: BLE001
            error = f"{error}; fallback failed: {e2}"[:200]
    # OPT-IN: persist discovered links into company_resource_graph (mirrors the discover DAG callback).
    persisted = None
    if ctx.get("persist") and ctx.get("companyResourceId") and ctx.get("parentResourceGraphId"):
        try:
            persisted = platform.record_graph(
                ctx.get("companyId") or "", ctx["companyResourceId"], ctx["parentResourceGraphId"],
                [l["url"] for l in links], "DISCOVERED" if source == "agent" else "FAILED")
        except Exception as e:  # noqa: BLE001
            persisted = {"error": str(e)[:160]}

    return {"framework": framework, "stage": "collect", "seedUrl": seed, "source": source,
            "error": error, "count": len(links), "links": links, "persisted": persisted,
            "providers": [{"provider": framework, "label": label, "model": model_name,
                           "ok": source == "agent", "error": error,
                           "latencyMs": int((time.perf_counter() - t0) * 1000)}]}


def index_flow(framework: str, label: str, model_name: str,
               agent_chunk: Callable[[str], str], ctx: dict) -> dict:
    content = (ctx.get("content") or "").strip()
    if not content:
        raise ValueError("content is required for the index stage")
    company_id = ctx.get("companyId") or "agentic-demo"
    source_url = ctx.get("sourceUrl") or "agentic://content"
    table = ctx.get("table") or config.VECTOR_TABLE
    t0, source, error, chunks = time.perf_counter(), "agent", None, []
    try:
        chunks = parse_chunks(agent_chunk(content))
        if not chunks:
            raise RuntimeError("agent returned no parseable chunks")
    except Exception as e:  # noqa: BLE001
        log.warning("%s index failed (%s); fixed-window fallback", framework, e)
        source, error = "fallback", str(e)[:160]
        chunks = _naive_chunks(content)
    # OPT-IN: report to the indexing-service ledger when triggered through it (indexLogId supplied).
    log_id, ledger = ctx.get("indexLogId"), None
    if log_id:
        try:
            platform.index_callback(log_id, "IN_PROGRESS")
        except Exception:  # noqa: BLE001
            pass

    written = agentic_indexer.index_chunks(table, company_id, source_url, chunks)

    if log_id:
        try:
            ledger = platform.index_callback(log_id, "INDEXED", chunks=written,
                                             run_ref=f"agentic-{framework}")
        except Exception as e:  # noqa: BLE001
            ledger = {"error": str(e)[:160]}

    return {"framework": framework, "stage": "index", "table": table, "companyId": company_id,
            "sourceUrl": source_url, "source": source, "error": error,
            "chunksWritten": written, "chunkCount": len(chunks), "ledger": ledger,
            "providers": [{"provider": framework, "label": label, "model": model_name,
                           "ok": source == "agent", "error": error,
                           "latencyMs": int((time.perf_counter() - t0) * 1000)}]}
