"""RAG on **LangGraph** — a retrieve -> generate StateGraph. Implements the 5 VKP RAG use cases via
ctx['useCase'] (default = single-fact-qa): each scopes retrieval differently and tailors the prompt.

The retrieval-scoping + prompts live in `_base` (shared with every framework cell); this cell shows
ONLY the LangGraph retrieve→generate graph."""
from typing import TypedDict

from ... import llm, registry
from . import _base


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc, instr = _base.spec_for(ctx.get("useCase"))

    class S(TypedDict, total=False):
        docs: list
        answer: str

    def retrieve(_s): return {"docs": _base.retrieve_for(uc, q)}

    def generate(s):
        return {"answer": llm.complete(f"{instr}\n\nSOURCES:\n{_base.format_sources(s['docs'])}\n\nQUESTION: {q}")}

    g = StateGraph(S)
    g.add_node("retrieve", retrieve); g.add_node("generate", generate)
    g.add_edge(START, "retrieve"); g.add_edge("retrieve", "generate"); g.add_edge("generate", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [d["source"] for d in out["docs"]], "useCase": uc}


registry.register("rag", "langgraph", run)
