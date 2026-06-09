"""The 'crewai' framework — a real CrewAI multi-agent crew over our retrieval.

Retrieval runs once (pgvector/mongodb), then a sequential 2-agent crew processes the sources:
  1) Vehicle Research Analyst — extracts the sourced facts relevant to the question.
  2) Vehicle Shopping Advisor — writes a concise, cited answer from those facts.
LLM = Groq (free) via CrewAI/litellm. Falls back to an extractive answer if CrewAI/Groq is
unavailable, so the endpoint never hard-fails.
"""
import logging
import os
import time
from typing import Optional

# CrewAI emits telemetry by default; opt out for a localhost service.
os.environ.setdefault("CREWAI_TELEMETRY_OPT_OUT", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from . import config
from .frameworks import _extractive_answer, _retrieve

log = logging.getLogger("vehicle-explore.crewai_agent")

CREW_MODEL = os.getenv("VKP_CREWAI_MODEL", "groq/llama-3.3-70b-versatile")


def _disable_cache_breakpoints() -> None:
    """CrewAI tags messages with a `cache_breakpoint` key for prompt caching, but only its
    Anthropic adapter strips/translates it — the litellm path leaks it to the provider, and
    Groq rejects the unknown property. The executors re-import `mark_cache_breakpoint` from the
    module on each call, so neutralizing it here (to identity) suppresses the marker globally."""
    import crewai.llms.cache as _cache
    _cache.mark_cache_breakpoint = lambda message: message


def _run_crew(query: str, context: str) -> str:
    from crewai import Agent, Crew, LLM, Process, Task

    _disable_cache_breakpoints()
    llm = LLM(model=CREW_MODEL, api_key=os.getenv("GROQ_API_KEY", ""), temperature=0.2)
    researcher = Agent(
        role="Vehicle Research Analyst",
        goal="Extract the precise, sourced vehicle facts relevant to the shopper's question.",
        backstory="You read automaker content and pull out exact facts (models, trims, prices, MPG) with [n] source markers.",
        llm=llm, verbose=False, allow_delegation=False)
    advisor = Agent(
        role="Vehicle Shopping Advisor",
        goal="Write a concise, cited answer for the shopper using only the researched facts.",
        backstory="You turn researched facts into a clear 2-4 sentence answer, citing sources as [n].",
        llm=llm, verbose=False, allow_delegation=False)

    research = Task(
        description=f"From these SOURCES, list the facts relevant to the question: '{query}'.\n\nSOURCES:\n{context}",
        expected_output="A short bullet list of sourced facts, each with a [n] marker.",
        agent=researcher)
    answer = Task(
        description=f"Using only the researched facts, answer concisely (2-4 sentences), citing sources as [n]. "
                    f"If the facts don't answer it, say so. Question: {query}",
        expected_output="A concise, cited answer.",
        agent=advisor, context=[research])

    crew = Crew(agents=[researcher, advisor], tasks=[research, answer], process=Process.sequential, verbose=False)
    return str(crew.kickoff()).strip()


def run(query: str, company_id: Optional[str], top_k: int, store: str,
        use_llm: bool = True, provider_ids=None) -> tuple[str, str, list[dict], list[dict]]:
    results = _retrieve(query, company_id, top_k, store)
    if not results:
        return "No relevant vehicle content was found for this query.", "none", [], []

    context = "\n".join(f"[{i + 1}] {r['sourceUrl']}\n{r['snippet']}" for i, r in enumerate(results[:6]))
    t0 = time.perf_counter()
    if use_llm and os.getenv("GROQ_API_KEY"):
        try:
            answer, source, ok, error = _run_crew(query, context), "llm", True, None
        except Exception as e:  # noqa: BLE001 — never hard-fail the endpoint
            log.warning("crewai crew failed (%s); extractive fallback", e)
            answer, source, ok, error = _extractive_answer(results), "extractive", False, str(e)[:160]
    else:
        answer, source, ok, error = _extractive_answer(results), "extractive", False, "GROQ_API_KEY not set"

    answers = [{
        "provider": "crewai", "label": "CrewAI · 2-agent (Groq)", "model": CREW_MODEL,
        "answer": answer if ok else None, "ok": ok, "error": error,
        "promptTokens": None, "completionTokens": None, "totalTokens": None,
        "finishReason": None, "costUsd": None, "latencyMs": int((time.perf_counter() - t0) * 1000),
    }]
    return answer, source, results, answers


# ===== collect + index stages (classic-roster, registered with agentic_stages) =====
import json as _json  # noqa: E402

from . import agentic_stages, tools as _tools  # noqa: E402
from .agentic_stages import COLLECT_INSTRUCTIONS, INDEX_INSTRUCTIONS  # noqa: E402


def _llm():
    from crewai import LLM
    _disable_cache_breakpoints()
    return LLM(model=CREW_MODEL, api_key=os.getenv("GROQ_API_KEY", ""), temperature=0.2)


def _collect(seed: str) -> str:
    from crewai import Agent, Crew, Process, Task
    from crewai.tools import tool

    @tool("fetch_page")
    def fetch_page(url: str) -> str:
        """Fetch a web page; returns its title, links, and images as a JSON string."""
        return _json.dumps(_tools.fetch_page(url))

    scout = Agent(role="Vehicle Resource Scout", goal="Discover the most relevant vehicle resource links.",
                  backstory="You crawl automaker sites and curate their vehicle/model/brochure links.",
                  llm=_llm(), tools=[fetch_page], verbose=False, allow_delegation=False)
    task = Task(description=f"{COLLECT_INSTRUCTIONS}\n\nSeed URL: {seed}",
                expected_output="A JSON array of link objects {url,type,title}.", agent=scout)
    return str(Crew(agents=[scout], tasks=[task], process=Process.sequential, verbose=False).kickoff()).strip()


def _chunk(content: str) -> str:
    from crewai import Agent, Crew, Process, Task
    indexer = Agent(role="Vehicle Content Indexer", goal="Split content into clean, searchable chunks.",
                    backstory="You strip boilerplate and produce coherent passages for semantic search.",
                    llm=_llm(), verbose=False, allow_delegation=False)
    task = Task(description=f"{INDEX_INSTRUCTIONS}\n\nCONTENT:\n{content}",
                expected_output="A JSON array of chunk strings.", agent=indexer)
    return str(Crew(agents=[indexer], tasks=[task], process=Process.sequential, verbose=False).kickoff()).strip()


def collect(ctx: dict) -> dict:
    return agentic_stages.collect_flow("crewai", "CrewAI", CREW_MODEL, _collect, ctx)


def index(ctx: dict) -> dict:
    return agentic_stages.index_flow("crewai", "CrewAI", CREW_MODEL, _chunk, ctx)


agentic_stages.register_collect("crewai", collect)
agentic_stages.register_index("crewai", index)
