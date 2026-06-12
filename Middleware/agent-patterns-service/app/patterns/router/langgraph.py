"""Router on **LangGraph** — classify → conditional edges → the matching handler node.

Implements the 5 VKP router use cases via ctx['useCase'] (default = query-type-router). Each use case
defines its own categories + handlers; the graph is built dynamically with real `add_conditional_edges`."""
from typing import TypedDict

from ... import llm, registry


def _query_type(q):
    cp = f"Classify this vehicle query as exactly one of: spec, buy, recall, price. Reply with one word only.\n\n{q}"
    return cp, {
        "spec": lambda: "[→ vector search] " + llm.complete(q, system="Give the precise spec."),
        "buy": lambda: f"[→ dealer-locator tool] I'd query local dealer inventory for: {q}",
        "recall": lambda: f"[→ NHTSA safety source] I'd look up open recalls by VIN/model for: {q}",
        "price": lambda: "[→ pricing index] " + llm.complete(q, system="Give pricing / MSRP info."),
    }


def _compound(q):
    cp = f"Classify as exactly 'compound' (compares multiple brands/facets) or 'simple'. One word.\n\n{q}"
    return cp, {
        "compound": lambda: f"[→ plan-execute] Decompose into sub-queries (one per brand×facet) and synthesize: {q}",
        "simple": lambda: "[→ langgraph RAG] " + llm.complete(q, system="Answer concisely."),
    }


def _framework(q):
    cp = f"Which agent framework best fits this task? Reply one of: langgraph, crewai, llamaindex, haystack. One word.\n\n{q}"
    return cp, {
        "langgraph": lambda: f"[→ langgraph] graph-structured control flow fits: {q}",
        "crewai": lambda: f"[→ crewai] a multi-agent crew fits: {q}",
        "llamaindex": lambda: f"[→ llamaindex] a retrieval/query-engine fits: {q}",
        "haystack": lambda: f"[→ haystack] a pipeline fits: {q}",
    }


def _store(q):
    cp = f"Which vector store fits this task? Reply one of: pgvector, mongodb, company. One word.\n\nTask: {q}"
    return cp, {
        "pgvector": lambda: f"[→ pgVector] default SQL + vector store for: {q}",
        "mongodb": lambda: f"[→ MongoDB Atlas Vector] flexible document store for: {q}",
        "company": lambda: f"[→ company-scoped index] one company's index for: {q}",
    }


def _topic(q):
    cp = f"Classify as exactly one of: vehicle, offtopic, unsafe. Reply with one word.\n\n{q}"
    return cp, {
        "vehicle": lambda: "[→ pipeline] " + llm.complete(q, system="Answer the vehicle question."),
        "offtopic": lambda: "[→ refuse] I can only help with vehicle questions.",
        "unsafe": lambda: "[→ block] This request was blocked by guardrails.",
    }


_USE_CASES = {
    "compound-vs-simple": _compound, "framework-router": _framework, "query-type-router": _query_type,
    "store-router": _store, "topic-guardrail-router": _topic,
}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "query-type-router"
    classify_prompt, handlers = _USE_CASES.get(uc, _query_type)(q)
    cats = list(handlers)

    class S(TypedDict, total=False):
        route: str
        answer: str

    def classify(_s):
        r = (llm.complete(classify_prompt) or "").strip().lower()
        return {"route": next((c for c in cats if c in r), cats[-1])}

    g = StateGraph(S)
    g.add_node("classify", classify)
    for c in cats:
        g.add_node(c, (lambda cc: (lambda _s: {"answer": handlers[cc]()}))(c))
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", lambda s: s["route"], {c: c for c in cats})
    for c in cats:
        g.add_edge(c, END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [f"routed -> {out['route']}"], "useCase": uc}


registry.register("router", "langgraph", run)
