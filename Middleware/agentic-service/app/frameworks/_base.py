"""Shared helpers so each framework module stays thin (just: build the agent, define how to call it).
Retrieval/fallback/result-shape for the SEARCH stage and link-discovery for the COLLECT stage live
here once.
"""
import json
import logging
import re
import time
from typing import Callable

from .. import config, indexer, platform, retrieval, tools

log = logging.getLogger("agentic")

INSTRUCTIONS = (
    "You are a vehicle shopping assistant. Answer the user's question using ONLY the provided "
    "SOURCES, concisely (2-4 sentences), and cite sources as [n]. If the sources don't answer it, say so."
)

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


def run_search(framework: str, label: str, model_name: str,
               agent_call: Callable[[str, str], str], ctx: dict) -> dict:
    """Retrieve indexed chunks, then `agent_call(query, sources_block) -> answer`. Falls back to an
    extractive summary if the agent raises, so the endpoint never hard-fails. Returns the uniform
    search result dict (framework, stage, answer, answerSource, count, results, answers)."""
    query = ctx["query"]
    results = retrieval.retrieve(query, ctx.get("companyId"), ctx.get("topK", 5))
    if not results:
        return {"framework": framework, "stage": "search", "answer":
                "No relevant vehicle content was found.", "answerSource": "none",
                "count": 0, "results": [], "answers": []}

    context = retrieval.context_block(results)
    t0 = time.perf_counter()
    ok, error, answer = False, None, None
    if ctx.get("useLlm", True):
        try:
            answer, ok = agent_call(query, context).strip(), True
        except Exception as e:  # noqa: BLE001 — never hard-fail the endpoint
            log.warning("%s search failed (%s); extractive fallback", framework, e)
            error = str(e)[:160]
    if not ok:
        top = " ".join(results[0]["snippet"].split())
        answer = f"Based on {len(results)} source(s): {top[:300]}"

    answers = [{"provider": framework, "label": label, "model": model_name,
                "answer": answer if ok else None, "ok": ok, "error": error,
                "latencyMs": int((time.perf_counter() - t0) * 1000)}]
    return {"framework": framework, "stage": "search", "answer": answer,
            "answerSource": "llm" if ok else "extractive", "count": len(results),
            "results": results, "answers": answers}


def parse_links(text: str) -> list[dict]:
    """Tolerantly extract a JSON array of {url,type,title} from an agent's text output."""
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


def run_collect(framework: str, label: str, model_name: str,
                agent_collect: Callable[[str], str], ctx: dict) -> dict:
    """Run a collect-stage agent: `agent_collect(seed_url) -> text` (the agent fetches + curates and
    returns a JSON array of links). Parses it; if the agent fails or returns nothing usable, falls
    back to a direct fetch_page of the seed. Returns the uniform collect result dict."""
    seed = (ctx.get("seedUrl") or "").strip()
    if not seed:
        raise ValueError("seedUrl is required for the collect stage")

    t0 = time.perf_counter()
    source, error, links = "agent", None, []
    try:
        links = parse_links(agent_collect(seed))
        if not links:
            raise RuntimeError("agent returned no parseable links")
    except Exception as e:  # noqa: BLE001 — never hard-fail; degrade to a direct fetch
        log.warning("%s collect failed (%s); direct-fetch fallback", framework, e)
        source, error = "fallback", str(e)[:160]
        try:
            page = tools.fetch_page(seed)
            links = [{"url": l["url"], "type": l["type"], "title": ""} for l in page["links"][:15]]
        except Exception as e2:  # noqa: BLE001
            error = f"{error}; fallback failed: {e2}"[:200]

    # OPT-IN: persist the discovered links into company_resource_graph (real pipeline step) when the
    # caller supplies the graph ids. Mirrors the vkp_discover_resources DAG callback.
    persisted = None
    if ctx.get("persist") and ctx.get("companyResourceId") and ctx.get("parentResourceGraphId"):
        try:
            persisted = platform.record_graph(
                ctx.get("companyId") or "", ctx["companyResourceId"], ctx["parentResourceGraphId"],
                [l["url"] for l in links], "DISCOVERED" if source == "agent" else "FAILED")
        except Exception as e:  # noqa: BLE001 — best-effort
            persisted = {"error": str(e)[:160]}

    return {"framework": framework, "stage": "collect", "seedUrl": seed, "source": source,
            "error": error, "count": len(links), "links": links, "persisted": persisted,
            "providers": [{"provider": framework, "label": label, "model": model_name,
                           "ok": source == "agent", "error": error,
                           "latencyMs": int((time.perf_counter() - t0) * 1000)}]}


def parse_chunks(text: str) -> list[str]:
    """Tolerantly extract a JSON array of strings (chunk texts) from an agent's output."""
    m = re.search(r"\[.*]", text or "", re.DOTALL)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return []
    return [str(c) for c in arr if isinstance(c, str) and c.strip()]


def _naive_chunks(content: str, size: int = 600, overlap: int = 80) -> list[str]:
    """Deterministic fixed-window fallback when the agent can't produce chunks."""
    words = content.split()
    out, step = [], max(1, size - overlap)
    for i in range(0, len(words), step):
        out.append(" ".join(words[i:i + size]))
        if len(out) >= 12:
            break
    return out


def run_index(framework: str, label: str, model_name: str,
              agent_chunk: Callable[[str], str], ctx: dict) -> dict:
    """Run an index-stage agent: `agent_chunk(content) -> text` (a JSON array of curated chunk
    strings). Embed + write the chunks into the search table (scoped by company_id) so they become
    immediately searchable. Falls back to fixed-window chunking if the agent fails."""
    content = (ctx.get("content") or "").strip()
    if not content:
        raise ValueError("content is required for the index stage")
    company_id = ctx.get("companyId") or "agentic-demo"
    source_url = ctx.get("sourceUrl") or "agentic://content"
    table = ctx.get("table") or config.INDEX_TABLE

    t0 = time.perf_counter()
    source, error, chunks = "agent", None, []
    try:
        chunks = parse_chunks(agent_chunk(content))
        if not chunks:
            raise RuntimeError("agent returned no parseable chunks")
    except Exception as e:  # noqa: BLE001 — degrade to deterministic chunking
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

    written = indexer.index_chunks(table, company_id, source_url, chunks)

    if log_id:
        try:
            ledger = platform.index_callback(log_id, "INDEXED", chunks=written,
                                             run_ref=f"agentic-{framework}")
        except Exception as e:  # noqa: BLE001 — best-effort
            ledger = {"error": str(e)[:160]}

    return {"framework": framework, "stage": "index", "table": table, "companyId": company_id,
            "sourceUrl": source_url, "source": source, "error": error,
            "chunksWritten": written, "chunkCount": len(chunks), "ledger": ledger,
            "providers": [{"provider": framework, "label": label, "model": model_name,
                           "ok": source == "agent", "error": error,
                           "latencyMs": int((time.perf_counter() - t0) * 1000)}]}
