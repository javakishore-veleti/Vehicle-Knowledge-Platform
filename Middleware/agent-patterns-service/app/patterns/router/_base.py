"""Shared classify prompts + route tables for the Router pattern (reused by every framework cell).

Each use case = a classify prompt + a routes table. A route handler is DATA, not a closure, so each
framework renders it in its own idiom:
  - ("llm", system, prefix)  → run the LLM/agent with `system`, prepend `prefix` to the answer
  - ("static", text)         → a fixed routing string (text may contain {q})
"""
from ... import llm

USE_CASES = {
    "query-type-router": {
        "classify": "Classify this vehicle query as exactly one of: spec, buy, recall, price. Reply with one word only.\n\n{q}",
        "routes": {
            "spec": ("llm", "Give the precise spec.", "[→ vector search] "),
            "buy": ("static", "[→ dealer-locator tool] I'd query local dealer inventory for: {q}"),
            "recall": ("static", "[→ NHTSA safety source] I'd look up open recalls by VIN/model for: {q}"),
            "price": ("llm", "Give pricing / MSRP info.", "[→ pricing index] "),
        },
    },
    "compound-vs-simple": {
        "classify": "Classify as exactly 'compound' (compares multiple brands/facets) or 'simple'. One word.\n\n{q}",
        "routes": {
            "compound": ("static", "[→ plan-execute] Decompose into sub-queries (one per brand×facet) and synthesize: {q}"),
            "simple": ("llm", "Answer concisely.", "[→ langgraph RAG] "),
        },
    },
    "framework-router": {
        "classify": "Which agent framework best fits this task? Reply one of: langgraph, crewai, llamaindex, haystack. One word.\n\n{q}",
        "routes": {
            "langgraph": ("static", "[→ langgraph] graph-structured control flow fits: {q}"),
            "crewai": ("static", "[→ crewai] a multi-agent crew fits: {q}"),
            "llamaindex": ("static", "[→ llamaindex] a retrieval/query-engine fits: {q}"),
            "haystack": ("static", "[→ haystack] a pipeline fits: {q}"),
        },
    },
    "store-router": {
        "classify": "Which vector store fits this task? Reply one of: pgvector, mongodb, company. One word.\n\nTask: {q}",
        "routes": {
            "pgvector": ("static", "[→ pgVector] default SQL + vector store for: {q}"),
            "mongodb": ("static", "[→ MongoDB Atlas Vector] flexible document store for: {q}"),
            "company": ("static", "[→ company-scoped index] one company's index for: {q}"),
        },
    },
    "topic-guardrail-router": {
        "classify": "Classify as exactly one of: vehicle, offtopic, unsafe. Reply with one word.\n\n{q}",
        "routes": {
            "vehicle": ("llm", "Answer the vehicle question.", "[→ pipeline] "),
            "offtopic": ("static", "[→ refuse] I can only help with vehicle questions."),
            "unsafe": ("static", "[→ block] This request was blocked by guardrails."),
        },
    },
}

DEFAULT_UC = "query-type-router"


def spec_for(use_case: str | None) -> tuple:
    uc = use_case or DEFAULT_UC
    return uc, USE_CASES.get(uc, USE_CASES[DEFAULT_UC])


def classify_prompt(spec: dict, q: str) -> str:
    return spec["classify"].format(q=q)


def categories(spec: dict) -> list:
    return list(spec["routes"])


def pick_route(spec: dict, raw: str) -> str:
    cats = categories(spec)
    r = (raw or "").strip().lower()
    return next((c for c in cats if c in r), cats[-1])


def render_static(handler: tuple, q: str) -> str:
    return handler[1].format(q=q)


def answer_for(spec: dict, route: str, q: str) -> str:
    """Programmatic render of a route (used by non-agentic cells like LangGraph)."""
    h = spec["routes"][route]
    if h[0] == "llm":
        return h[2] + llm.complete(q, system=h[1])
    return render_static(h, q)
