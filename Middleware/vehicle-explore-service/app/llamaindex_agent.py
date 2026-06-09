"""The 'llamaindex' framework — a real LlamaIndex RetrieverQueryEngine over our retrieval.

Our vector search (pgvector/mongodb) is wrapped as a LlamaIndex `BaseRetriever`; a
`RetrieverQueryEngine` then runs LlamaIndex's response synthesizer over the retrieved nodes,
with the LLM = Groq (free) via the LiteLLM bridge. Falls back to an extractive answer if
LlamaIndex/Groq is unavailable, so the endpoint never hard-fails.
"""
import logging
import os
import time
from typing import Optional

from .frameworks import _extractive_answer, _retrieve

log = logging.getLogger("vehicle-explore.llamaindex_agent")

LI_MODEL = os.getenv("VKP_LLAMAINDEX_MODEL", "groq/llama-3.3-70b-versatile")

_QA_TMPL = (
    "You are a vehicle shopping assistant. Using ONLY the context below, answer the question "
    "concisely (2-4 sentences) and cite sources as [n]. If the context does not answer it, say so.\n"
    "---------------------\n{context_str}\n---------------------\n"
    "Question: {query_str}\nAnswer: "
)


def _run_engine(query: str, results: list[dict]) -> str:
    from llama_index.core import get_response_synthesizer
    from llama_index.core.prompts import PromptTemplate
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
    from llama_index.llms.litellm import LiteLLM

    nodes = [
        NodeWithScore(
            node=TextNode(text=r["snippet"], metadata={"source": r["sourceUrl"], "n": i + 1}),
            score=float(r.get("score") or 0.0))
        for i, r in enumerate(results[:6])
    ]

    class _PreRetriever(BaseRetriever):
        def _retrieve(self, query_bundle: QueryBundle):  # noqa: D401 — LlamaIndex hook
            return nodes

    llm = LiteLLM(model=LI_MODEL, api_key=os.getenv("GROQ_API_KEY", ""), temperature=0.2)
    synth = get_response_synthesizer(
        llm=llm, response_mode="compact", text_qa_template=PromptTemplate(_QA_TMPL))
    engine = RetrieverQueryEngine(retriever=_PreRetriever(), response_synthesizer=synth)
    return str(engine.query(query)).strip()


def run(query: str, company_id: Optional[str], top_k: int, store: str,
        use_llm: bool = True, provider_ids=None) -> tuple[str, str, list[dict], list[dict]]:
    results = _retrieve(query, company_id, top_k, store)
    if not results:
        return "No relevant vehicle content was found for this query.", "none", [], []

    t0 = time.perf_counter()
    if use_llm and os.getenv("GROQ_API_KEY"):
        try:
            answer, source, ok, error = _run_engine(query, results), "llm", True, None
        except Exception as e:  # noqa: BLE001 — never hard-fail the endpoint
            log.warning("llamaindex engine failed (%s); extractive fallback", e)
            answer, source, ok, error = _extractive_answer(results), "extractive", False, str(e)[:160]
    else:
        answer, source, ok, error = _extractive_answer(results), "extractive", False, "GROQ_API_KEY not set"

    answers = [{
        "provider": "llamaindex", "label": "LlamaIndex · RetrieverQueryEngine (Groq)", "model": LI_MODEL,
        "answer": answer if ok else None, "ok": ok, "error": error,
        "promptTokens": None, "completionTokens": None, "totalTokens": None,
        "finishReason": None, "costUsd": None, "latencyMs": int((time.perf_counter() - t0) * 1000),
    }]
    return answer, source, results, answers


# ===== collect + index stages (classic-roster, registered with agentic_stages) =====
from . import agentic_stages, tools as _tools  # noqa: E402
from .agentic_stages import COLLECT_INSTRUCTIONS, INDEX_INSTRUCTIONS  # noqa: E402


def _llm():
    from llama_index.llms.litellm import LiteLLM
    return LiteLLM(model=LI_MODEL, api_key=os.getenv("GROQ_API_KEY", ""), temperature=0.2)


def _collect(seed: str) -> str:
    from llama_index.core.agent import ReActAgent
    from llama_index.core.tools import FunctionTool

    def fetch_page(url: str) -> dict:
        """Fetch a web page; returns {url, title, links:[{url,type}], images:[...]}."""
        return _tools.fetch_page(url)

    agent = ReActAgent.from_tools([FunctionTool.from_defaults(fn=fetch_page)], llm=_llm(),
                                  verbose=False, context=COLLECT_INSTRUCTIONS, max_iterations=6)
    return str(agent.chat(f"Seed URL: {seed}. Discover and return the relevant vehicle resource links as JSON."))


def _chunk(content: str) -> str:
    return str(_llm().complete(
        f"{INDEX_INSTRUCTIONS}\n\nCONTENT:\n{content}\n\nReturn the chunks as a JSON array of strings."))


def collect(ctx: dict) -> dict:
    return agentic_stages.collect_flow("llamaindex", "LlamaIndex", LI_MODEL, _collect, ctx)


def index(ctx: dict) -> dict:
    return agentic_stages.index_flow("llamaindex", "LlamaIndex", LI_MODEL, _chunk, ctx)


agentic_stages.register_collect("llamaindex", collect)
agentic_stages.register_index("llamaindex", index)
