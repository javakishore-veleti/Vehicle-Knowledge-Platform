"""The 'haystack' framework — a real Haystack 2.x RAG Pipeline over our retrieval.

Pipeline: a custom @component retriever (wraps our pgvector/mongodb search as Haystack
Documents) -> PromptBuilder -> OpenAIGenerator pointed at Groq's OpenAI-compatible endpoint
(free). Falls back to an extractive answer if Haystack/Groq is unavailable, so the endpoint
never hard-fails.
"""
import logging
import os
import time
from typing import Optional

# Haystack phones home usage stats by default; opt out for a localhost service.
os.environ.setdefault("HAYSTACK_TELEMETRY_ENABLED", "False")

from .frameworks import _extractive_answer, _retrieve

log = logging.getLogger("vehicle-explore")

HS_MODEL = os.getenv("VKP_HAYSTACK_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

_PROMPT = (
    "You are a vehicle shopping assistant. Using ONLY the sources below, answer the question "
    "concisely (2-4 sentences) and cite sources as [n]. If the sources do not answer it, say so.\n"
    "{% for doc in documents %}[{{ loop.index }}] {{ doc.meta.source }}\n{{ doc.content }}\n{% endfor %}\n"
    "Question: {{ query }}\nAnswer:"
)


def _build_pipeline(results: list[dict]):
    from haystack import Document, Pipeline, component
    from haystack.components.builders import PromptBuilder
    from haystack.components.generators import OpenAIGenerator
    from haystack.utils import Secret

    docs = [Document(content=r["snippet"], meta={"source": r["sourceUrl"]}) for r in results[:6]]

    @component
    class PreRetriever:
        """Returns documents already retrieved by our vector search (retrieval ran upstream)."""
        @component.output_types(documents=list)
        def run(self, query: str):
            return {"documents": docs}

    pipe = Pipeline()
    pipe.add_component("retriever", PreRetriever())
    pipe.add_component("prompt_builder", PromptBuilder(template=_PROMPT, required_variables=["query"]))
    pipe.add_component("generator", OpenAIGenerator(
        api_key=Secret.from_token(os.getenv("GROQ_API_KEY", "")),
        model=HS_MODEL, api_base_url=GROQ_BASE_URL,
        generation_kwargs={"temperature": 0.2}))
    pipe.connect("retriever.documents", "prompt_builder.documents")
    pipe.connect("prompt_builder.prompt", "generator.prompt")
    return pipe


def _run_pipeline(query: str, results: list[dict]) -> str:
    pipe = _build_pipeline(results)
    out = pipe.run({"retriever": {"query": query}, "prompt_builder": {"query": query}})
    replies = out.get("generator", {}).get("replies") or []
    if not replies:
        raise RuntimeError("haystack generator returned no replies")
    return replies[0].strip()


def run(query: str, company_id: Optional[str], top_k: int, store: str,
        use_llm: bool = True, provider_ids=None) -> tuple[str, str, list[dict], list[dict]]:
    results = _retrieve(query, company_id, top_k, store)
    if not results:
        return "No relevant vehicle content was found for this query.", "none", [], []

    t0 = time.perf_counter()
    if use_llm and os.getenv("GROQ_API_KEY"):
        try:
            answer, source, ok, error = _run_pipeline(query, results), "llm", True, None
        except Exception as e:  # noqa: BLE001 — never hard-fail the endpoint
            log.warning("haystack pipeline failed (%s); extractive fallback", e)
            answer, source, ok, error = _extractive_answer(results), "extractive", False, str(e)[:160]
    else:
        answer, source, ok, error = _extractive_answer(results), "extractive", False, "GROQ_API_KEY not set"

    answers = [{
        "provider": "haystack", "label": "Haystack · RAG Pipeline (Groq)", "model": HS_MODEL,
        "answer": answer if ok else None, "ok": ok, "error": error,
        "promptTokens": None, "completionTokens": None, "totalTokens": None,
        "finishReason": None, "costUsd": None, "latencyMs": int((time.perf_counter() - t0) * 1000),
    }]
    return answer, source, results, answers
