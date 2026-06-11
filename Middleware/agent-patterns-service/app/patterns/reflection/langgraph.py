"""Reflection on **LangGraph** — a StateGraph: draft -> critique -> revise (add a loop edge for N rounds)."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        draft: str
        critique: str
        answer: str

    def draft(_s: S) -> dict:
        return {"draft": llm.complete(q, system=_base.DRAFT_SYS)}

    def critique(s: S) -> dict:
        return {"critique": llm.complete(_base.CRITIQUE.format(q=q, a=s["draft"]), system=_base.CRITIC_SYS)}

    def revise(s: S) -> dict:
        return {"answer": llm.complete(_base.REVISE.format(q=q, a=s["draft"], c=s["critique"]))}

    g = StateGraph(S)
    g.add_node("draft", draft)
    g.add_node("critique", critique)
    g.add_node("revise", revise)
    g.add_edge(START, "draft")
    g.add_edge("draft", "critique")
    g.add_edge("critique", "revise")
    g.add_edge("revise", END)
    out = g.compile().invoke({})
    return _base.result(out["draft"], out["critique"], out["answer"])


registry.register("reflection", "langgraph", run)
