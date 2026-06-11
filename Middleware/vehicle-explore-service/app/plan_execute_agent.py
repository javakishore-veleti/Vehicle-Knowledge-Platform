"""'plan-execute' framework — Plan-and-Execute for compound comparison queries.

PLAN    : an LLM decomposes the question into focused sub-queries (one per facet / entity).
EXECUTE : retrieve for each sub-query over the indexed chunks; merge + dedup the sources.
SYNTHESIZE: generate one cited answer over the union (re-uses providers via frameworks.synthesize).

Best for multi-part questions ("compare towing, hybrid options and price of Toyota vs Ford vs GMC")
that a single retrieval can't cover. It degrades gracefully: when the question is simple or no planner
LLM is available, it falls back to a single retrieval (i.e. plain RAG) rather than failing.
"""
import json
import logging
import re
from contextvars import ContextVar
from typing import Optional

from . import frameworks, providers

log = logging.getLogger("vehicle-explore.plan_execute_agent")

MAX_STEPS = 6

# The plan produced for the current request — surfaced by main.py as response["planSteps"].
LAST_PLAN: ContextVar[list] = ContextVar("plan_execute_last_plan", default=[])

PLAN_PROMPT = (
    "You are a query planner for a vehicle-knowledge search engine. Decompose the user's question "
    "into 2 to {max} focused, self-contained sub-queries — one per distinct facet or entity (e.g. a "
    "specific brand + attribute). Each sub-query must be answerable by a single semantic search over "
    "vehicle content. If the question is already simple / single-facet, return just one sub-query. "
    "Return ONLY a JSON array of strings, no prose.\n\nQuestion: {q}"
)


def _plan(query: str) -> list[str]:
    raw = providers.complete(PLAN_PROMPT.format(q=query, max=MAX_STEPS), max_tokens=300)
    if not raw:
        return [query]
    text = raw.strip()
    m = re.search(r"\[.*\]", text, re.S)   # tolerate ```json fences / prose around the array
    if m:
        text = m.group(0)
    try:
        parsed = json.loads(text)
    except Exception:  # noqa: BLE001
        return [query]
    steps = [str(s).strip() for s in parsed if isinstance(s, str) and str(s).strip()]
    return steps[:MAX_STEPS] if steps else [query]


def _merge(result_lists: list[list[dict]], cap: int) -> list[dict]:
    """Union of per-step results, deduped by (sourceUrl, snippet), best score first."""
    best: dict[str, dict] = {}
    for results in result_lists:
        for r in results:
            key = f"{r.get('sourceUrl')}|{(r.get('snippet') or '')[:80]}"
            cur = best.get(key)
            if cur is None or (r.get("score") or 0) > (cur.get("score") or 0):
                best[key] = r
    merged = sorted(best.values(), key=lambda r: r.get("score") or 0, reverse=True)
    return merged[:cap]


def run(query: str, company_id: Optional[str], top_k: int, store: str,
        use_llm: bool = True, provider_ids: Optional[list[str]] = None
        ) -> tuple[str, str, list[dict], list[dict]]:
    steps = _plan(query)
    LAST_PLAN.set(steps)
    log.info("plan-execute: %d step(s) for query %r", len(steps), query[:80])

    # EXECUTE — retrieve per sub-query (retrieval mode/store already set by frameworks.run)
    per_step = [frameworks._retrieve(sq, company_id, top_k, store) for sq in steps]
    cap = max(top_k, min(12, top_k * len(steps)))   # bound the synthesis context
    results = _merge(per_step, cap)

    # SYNTHESIZE — one cited answer over the union of facets
    answer, source, answers = frameworks.synthesize(query, results, use_llm, provider_ids)
    return answer, source, results, answers
