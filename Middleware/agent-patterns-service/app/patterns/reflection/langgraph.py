"""Reflection on **LangGraph** — a draft -> critique -> revise StateGraph.

Implements the 5 VKP Reflection use cases via ctx['useCase'] (default = answer-quality-gate). The
use-case instructions live in `_base.USE_CASES` (shared by every framework cell); LangGraph wires the
draft/critique inline through the graph state, so this cell shows ONLY the framework mechanics."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))
    gen_p = spec["generate"].format(q=q)

    class S(TypedDict, total=False):
        draft: str
        critique: str
        answer: str

    def generate(_s): return {"draft": llm.complete(gen_p)}
    def critique(s): return {"critique": llm.complete(f"{spec['critique']}\n\nDRAFT:\n{s['draft']}")}
    def revise(s): return {"answer": llm.complete(f"{spec['revise']}\n\nDRAFT:\n{s['draft']}\n\nCRITIQUE:\n{s['critique']}")}

    # Node names are prefixed (do_*) so they never collide with state keys
    # (newer LangGraph rejects a node named the same as a state key, e.g. "critique").
    g = StateGraph(S)
    g.add_node("do_generate", generate); g.add_node("do_critique", critique); g.add_node("do_revise", revise)
    g.add_edge(START, "do_generate"); g.add_edge("do_generate", "do_critique"); g.add_edge("do_critique", "do_revise"); g.add_edge("do_revise", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "draft": out["draft"], "critique": out["critique"], "useCase": uc}


registry.register("reflection", "langgraph", run)
