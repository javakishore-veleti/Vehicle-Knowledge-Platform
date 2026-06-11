"""RAG on **LangGraph** — a retrieve -> generate StateGraph. Implements the 5 VKP RAG use cases via
ctx['useCase'] (default = single-fact-qa): each scopes retrieval differently and tailors the prompt."""
from typing import TypedDict

from ... import llm, registry, corpus

_BRANDS = {"toyota": "toyota", "lexus": "toyota", "camry": "toyota", "rav4": "toyota",
           "ford": "ford", "lincoln": "ford", "f-150": "ford", "f150": "ford",
           "tesla": "tesla", "model 3": "tesla", "honda": "honda", "civic": "honda"}


def _company(q: str):
    ql = (q or "").lower()
    for k, v in _BRANDS.items():
        if k in ql:
            return v
    return None


def _retrieve_for(uc: str, q: str) -> list:
    if uc == "company-scoped-faq":
        return corpus.retrieve(q, 3, source_prefix=_company(q))
    if uc == "snapshot-grounded":
        return corpus.retrieve(q, 5, source_prefix=_company(q))
    if uc == "brochure-pdf-lookup":
        return corpus.retrieve(q, 3, contains="brochure")
    if uc == "explain-feature":
        return corpus.retrieve(q, 4)
    return corpus.retrieve(q, 3)   # single-fact-qa


_PROMPTS = {
    "single-fact-qa": "Answer using ONLY these sources and cite [n].",
    "company-scoped-faq": "Answer ONLY about this brand, using ONLY these sources; cite [n].",
    "brochure-pdf-lookup": "Answer from these brochure sources; cite [n].",
    "explain-feature": "Explain the feature, drawing across these model sources; cite [n].",
    "snapshot-grounded": "Answer STRICTLY from this snapshot's content only; cite [n].",
}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "single-fact-qa"

    class S(TypedDict, total=False):
        docs: list
        answer: str

    def retrieve(_s): return {"docs": _retrieve_for(uc, q)}

    def generate(s):
        ctxt = "\n".join(f"[{i+1}] {d['text']} (source: {d['source']})" for i, d in enumerate(s["docs"]))
        instr = _PROMPTS.get(uc, _PROMPTS["single-fact-qa"])
        return {"answer": llm.complete(f"{instr}\n\nSOURCES:\n{ctxt}\n\nQUESTION: {q}")}

    g = StateGraph(S)
    g.add_node("retrieve", retrieve); g.add_node("generate", generate)
    g.add_edge(START, "retrieve"); g.add_edge("retrieve", "generate"); g.add_edge("generate", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [d["source"] for d in out["docs"]], "useCase": uc}


registry.register("rag", "langgraph", run)
