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

log = logging.getLogger("vehicle-explore.haystack_agent")

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


# ===== collect + index stages (classic-roster, registered with agentic_stages) =====
from . import agentic_stages, tools as _tools  # noqa: E402
from .agentic_stages import COLLECT_INSTRUCTIONS, INDEX_INSTRUCTIONS  # noqa: E402


def _chat_generator():
    from haystack.components.generators.chat import OpenAIChatGenerator
    from haystack.utils import Secret
    return OpenAIChatGenerator(api_key=Secret.from_token(os.getenv("GROQ_API_KEY", "")),
                               model=HS_MODEL, api_base_url=GROQ_BASE_URL,
                               generation_kwargs={"temperature": 0.2})


def _collect(seed: str) -> str:
    from haystack.components.agents import Agent
    from haystack.dataclasses import ChatMessage
    from haystack.tools import tool

    @tool
    def fetch_page(url: str) -> dict:
        """Fetch a web page; returns {url, title, links:[{url,type}], images:[...]}."""
        return _tools.fetch_page(url)

    agent = Agent(chat_generator=_chat_generator(), tools=[fetch_page], system_prompt=COLLECT_INSTRUCTIONS)
    agent.warm_up()
    res = agent.run(messages=[ChatMessage.from_user(
        f"Seed URL: {seed}\nDiscover and return the relevant vehicle resource links as JSON.")])
    msgs = res.get("messages", [])
    return msgs[-1].text if msgs else ""


def _chunk(content: str) -> str:
    from haystack.dataclasses import ChatMessage
    res = _chat_generator().run(messages=[
        ChatMessage.from_system(INDEX_INSTRUCTIONS),
        ChatMessage.from_user(f"CONTENT:\n{content}\n\nReturn the chunks as a JSON array of strings.")])
    replies = res.get("replies", [])
    return replies[0].text if replies else ""


def collect(ctx: dict) -> dict:
    return agentic_stages.collect_flow("haystack", "Haystack", HS_MODEL, _collect, ctx)


def index(ctx: dict) -> dict:
    return agentic_stages.index_flow("haystack", "Haystack", HS_MODEL, _chunk, ctx)


agentic_stages.register_collect("haystack", collect)
agentic_stages.register_index("haystack", index)
