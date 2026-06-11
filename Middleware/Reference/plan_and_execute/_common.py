"""Shared, framework-agnostic helpers for the Plan-and-Execute reference implementations.

Every reference module implements the SAME three phases — plan -> execute -> synthesize — but expresses
the orchestration in its own framework's idioms. To keep the modules focused on the *framework* part,
retrieval and answer-synthesis are injected as callables:

    retrieve(subquery: str) -> list[dict]          # one semantic search; each dict has sourceUrl/snippet/score
    synthesize(query: str, results: list[dict]) -> str

So each file only has to show: how that framework builds the planner, runs it to get the sub-queries,
fans out the retrievals, and produces the final answer.
"""
import json
import re

PLAN_PROMPT = (
    "You are a query planner for a vehicle-knowledge search engine. Decompose the user's question into "
    "2 to 6 focused, self-contained sub-queries — one per distinct facet or entity (a specific brand + "
    "attribute). Each must be answerable by a single semantic search. If the question is already simple, "
    "return just one. Return ONLY a JSON array of strings.\n\nQuestion: {q}"
)


def parse_steps(raw: str, fallback: str) -> list[str]:
    """Tolerantly parse an LLM reply into a list of sub-queries (handles ```json fences / prose)."""
    if not raw:
        return [fallback]
    m = re.search(r"\[.*\]", raw, re.S)
    text = m.group(0) if m else raw
    try:
        parsed = json.loads(text)
    except Exception:  # noqa: BLE001
        return [fallback]
    steps = [str(s).strip() for s in parsed if isinstance(s, str) and str(s).strip()]
    return steps[:6] if steps else [fallback]


def merge(result_lists, cap: int) -> list[dict]:
    """Union of per-sub-query results, deduped by (sourceUrl, snippet), best score first."""
    best: dict[str, dict] = {}
    for results in result_lists:
        for r in results or []:
            key = f"{r.get('sourceUrl')}|{(r.get('snippet') or '')[:80]}"
            cur = best.get(key)
            if cur is None or (r.get("score") or 0) > (cur.get("score") or 0):
                best[key] = r
    return sorted(best.values(), key=lambda r: r.get("score") or 0, reverse=True)[:cap]
