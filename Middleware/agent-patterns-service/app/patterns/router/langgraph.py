"""Router on **LangGraph** — classify the query, then a conditional edge picks the specialist node."""
from typing import TypedDict

from ... import registry, llm


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        route: str
        answer: str

    def classify(_s):
        r = llm.complete(f"Classify as exactly one of: spec, compare, recommend, other. Reply with only the word.\n\n{q}")
        r = (r or "other").strip().lower().split()[0] if r else "other"
        return {"route": r if r in ("spec", "compare", "recommend") else "other"}

    def make(role, sysp):
        def _n(_s): return {"answer": llm.complete(q, system=sysp)}
        return _n

    g = StateGraph(S)
    g.add_node("classify", classify)
    g.add_node("spec", make("spec", "You are a vehicle SPEC expert. Give precise specs."))
    g.add_node("compare", make("compare", "You are a vehicle COMPARISON expert. Compare clearly with a verdict."))
    g.add_node("recommend", make("recommend", "You are a vehicle BUYING ADVISOR. Recommend with reasons."))
    g.add_node("other", make("other", "You are a helpful vehicle assistant."))
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", lambda s: s["route"],
                            {"spec": "spec", "compare": "compare", "recommend": "recommend", "other": "other"})
    for n in ("spec", "compare", "recommend", "other"):
        g.add_edge(n, END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [f"routed -> {out['route']}"]}


registry.register("router", "langgraph", run)
