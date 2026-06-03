"""AI framework router. The framework name is part of the URL
(/api/vehicle-explore/{framework}/search) so requests can route to different agent
implementations. 'langgraph' is the implemented retrieve->synthesize pipeline; the others are
registered but not yet implemented.

Retrieval runs against pgvector (default) or mongodb (Atlas Vector Search). The answer is
LLM-backed (OpenAI) when a key/quota is available, and falls back to an extractive summary
otherwise — same contract either way.
"""
import logging
from typing import Optional

from . import config
from .search import search_chunks

log = logging.getLogger("vehicle-explore")

IMPLEMENTED = {"langgraph"}
KNOWN = {"langgraph", "crewai", "llamaindex", "haystack"}


def _retrieve(query: str, company_id: Optional[str], top_k: int, store: str) -> list[dict]:
    if store == "mongodb":
        from .mongo_search import search_chunks_mongo  # imported lazily so pg-only runs need no Mongo
        return search_chunks_mongo(query, company_id, top_k)
    return search_chunks(query, company_id, top_k)


def _extractive_answer(results: list[dict]) -> str:
    top = " ".join(results[0]["snippet"].split())
    return f"Based on {len(results)} matching source(s): {top[:300]}"


def _llm_answer(query: str, results: list[dict]) -> str:
    from openai import OpenAI

    kwargs: dict = {"api_key": config.LLM_API_KEY}
    if config.LLM_BASE_URL:
        kwargs["base_url"] = config.LLM_BASE_URL   # OpenAI-compatible provider (Groq/Azure/etc.)
    client = OpenAI(**kwargs)
    context = "\n\n".join(f"[{i + 1}] {r['sourceUrl']}\n{r['snippet']}" for i, r in enumerate(results))
    messages = [
        {"role": "system", "content": (
            "You are a vehicle research assistant. Answer the user's question using ONLY the "
            "provided sources. Cite sources inline as [n]. Be concise (2-4 sentences). If the "
            "sources don't contain the answer, say so briefly.")},
        {"role": "user", "content": f"Question: {query}\n\nSources:\n{context}"},
    ]
    resp = client.chat.completions.create(
        model=config.LLM_MODEL, messages=messages, temperature=0.2, max_tokens=300)
    return resp.choices[0].message.content.strip()


def synthesize_answer(query: str, results: list[dict], use_llm: bool = True) -> tuple[str, str]:
    """Returns (answer, answerSource). answerSource ∈ {llm, extractive, none}."""
    if not results:
        return "No relevant vehicle content was found for this query.", "none"
    if use_llm and config.LLM_ENABLED and config.LLM_API_KEY:
        try:
            return _llm_answer(query, results), "llm"
        except Exception as e:  # noqa: BLE001 — quota/network/etc. -> graceful fallback
            log.warning("LLM answer failed (%s); falling back to extractive", e)
    return _extractive_answer(results), "extractive"


def run(framework: str, query: str, company_id: Optional[str], top_k: int,
        store: str, use_llm: bool = True) -> tuple[str, str, list[dict]]:
    if framework == "langgraph":
        from . import langgraph_agent  # real LangGraph StateGraph (lazy import)
        return langgraph_agent.run(query, company_id, top_k, store, use_llm)
    # Fallback simple pipeline (not reached: only 'langgraph' is in IMPLEMENTED).
    results = _retrieve(query, company_id, top_k, store)
    answer, source = synthesize_answer(query, results, use_llm)
    return answer, source, results
