"""The 'openai-agents' framework — OpenAI Agents SDK (https://openai.github.io/openai-agents-python).

search: retrieve indexed chunks, then run an Agent (Runner.run_sync) that answers with [n] citations.
Model = OpenAI if OPENAI_API_KEY is set, else free Groq via the SDK's OpenAI-compatible model. Falls
back to an extractive answer if the SDK/model is unavailable, so the endpoint never hard-fails.

collect / index stages: registered later (this module will grow agent-driven implementations).
"""
import logging
import os
import time
from typing import Optional

from .. import config, registry, retrieval

log = logging.getLogger("agentic")

_INSTRUCTIONS = (
    "You are a vehicle shopping assistant. Answer the user's question using ONLY the provided "
    "SOURCES, concisely (2-4 sentences), and cite sources as [n]. If the sources don't answer it, say so."
)


def _build_agent():
    """Create an Agent bound to OpenAI (preferred) or Groq (free fallback). Tracing is disabled so
    the SDK never phones home."""
    from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled
    set_tracing_disabled(True)

    if config.OPENAI_API_KEY:
        return Agent(name="Vehicle Search Analyst", instructions=_INSTRUCTIONS, model=config.OPENAI_MODEL)
    if config.GROQ_API_KEY:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=config.GROQ_BASE_URL, api_key=config.GROQ_API_KEY)
        model = OpenAIChatCompletionsModel(model=config.GROQ_MODEL, openai_client=client)
        return Agent(name="Vehicle Search Analyst", instructions=_INSTRUCTIONS, model=model)
    raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")


def search(ctx: dict) -> dict:
    query = ctx["query"]
    results = retrieval.retrieve(query, ctx.get("companyId"), ctx.get("topK", 5))
    if not results:
        return {"framework": "openai-agents", "stage": "search", "answer":
                "No relevant vehicle content was found.", "answerSource": "none", "count": 0,
                "results": [], "answers": []}

    context = retrieval.context_block(results)
    t0 = time.perf_counter()
    ok, error, answer = False, None, None
    if ctx.get("useLlm", True):
        try:
            from agents import Runner
            agent = _build_agent()
            result = Runner.run_sync(agent, f"Question: {query}\n\nSOURCES:\n{context}")
            answer, ok = str(result.final_output).strip(), True
        except Exception as e:  # noqa: BLE001 — never hard-fail
            log.warning("openai-agents search failed (%s); extractive fallback", e)
            error = str(e)[:160]
    if not ok:
        top = " ".join(results[0]["snippet"].split())
        answer = f"Based on {len(results)} source(s): {top[:300]}"

    model = config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL
    answers = [{"provider": "openai-agents", "label": "OpenAI Agents SDK", "model": model,
                "answer": answer if ok else None, "ok": ok, "error": error,
                "latencyMs": int((time.perf_counter() - t0) * 1000)}]
    return {"framework": "openai-agents", "stage": "search",
            "answer": answer, "answerSource": "llm" if ok else "extractive",
            "count": len(results), "results": results, "answers": answers}


registry.register("openai-agents", "search", search)
