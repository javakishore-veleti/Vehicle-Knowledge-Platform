"""Shared helpers so each framework module stays thin (just: build the agent, define how to call it).
Retrieval/fallback/result-shape for the SEARCH stage and link-discovery for the COLLECT stage live
here once.
"""
import json
import logging
import re
import time
from typing import Callable

from .. import retrieval, tools

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

    return {"framework": framework, "stage": "collect", "seedUrl": seed, "source": source,
            "error": error, "count": len(links), "links": links,
            "providers": [{"provider": framework, "label": label, "model": model_name,
                           "ok": source == "agent", "error": error,
                           "latencyMs": int((time.perf_counter() - t0) * 1000)}]}
