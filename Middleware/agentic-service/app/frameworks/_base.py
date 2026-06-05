"""Shared helpers for the search stage, so each framework module stays thin (just: build the
agent, define how to call it). Retrieval + extractive fallback + the result shape live here once.
"""
import logging
import time
from typing import Callable

from .. import retrieval

log = logging.getLogger("agentic")

INSTRUCTIONS = (
    "You are a vehicle shopping assistant. Answer the user's question using ONLY the provided "
    "SOURCES, concisely (2-4 sentences), and cite sources as [n]. If the sources don't answer it, say so."
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
