"""Router on **LangGraph** — classify → conditional edges → the matching handler node.

Implements the 5 VKP router use cases via ctx['useCase'] (default = query-type-router). The classify
prompts + route tables live in `_base.USE_CASES` (shared with every framework cell); the graph is built
dynamically with real `add_conditional_edges`. This cell shows ONLY the LangGraph routing mechanics."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    cats = _base.categories(spec)

    class S(TypedDict, total=False):
        route: str
        answer: str

    def classify(_s):
        raw = llm.complete(_base.classify_prompt(spec, q))
        return {"route": _base.pick_route(spec, raw)}

    g = StateGraph(S)
    g.add_node("classify", classify)
    for c in cats:
        g.add_node(c, (lambda cc: (lambda _s: {"answer": _base.answer_for(spec, cc, q)}))(c))
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", lambda s: s["route"], {c: c for c in cats})
    for c in cats:
        g.add_edge(c, END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [f"routed -> {out['route']}"], "useCase": uc}


registry.register("router", "langgraph", run)
