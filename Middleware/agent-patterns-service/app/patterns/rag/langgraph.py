"""RAG on **LangGraph** — a retrieve -> generate StateGraph over the in-memory corpus."""
from typing import TypedDict

from ... import registry, llm, corpus


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]

    class S(TypedDict, total=False):
        docs: list
        answer: str

    def retrieve(_s): return {"docs": corpus.retrieve(q, k=3)}

    def generate(s):
        ctxt = "\n".join(f"[{i+1}] {d['text']} (source: {d['source']})" for i, d in enumerate(s["docs"]))
        return {"answer": llm.complete(f"Answer using ONLY these sources and cite [n].\n\nSOURCES:\n{ctxt}\n\nQUESTION: {q}")}

    g = StateGraph(S)
    g.add_node("retrieve", retrieve); g.add_node("generate", generate)
    g.add_edge(START, "retrieve"); g.add_edge("retrieve", "generate"); g.add_edge("generate", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [d["source"] for d in out["docs"]]}


registry.register("rag", "langgraph", run)
