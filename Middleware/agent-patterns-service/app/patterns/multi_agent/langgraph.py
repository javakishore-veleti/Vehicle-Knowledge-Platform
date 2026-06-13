"""Multi-agent on **LangGraph** — supervisor → parallel specialist workers (reducer-merged) → compose.

Implements the 5 VKP use cases via ctx['useCase'] (default = spec-price-safety). Each defines its workers
(label, prompt) + a merge instruction; per-brand-workers spins up one worker per brand found in the query."""
import operator
import re
from typing import Annotated, TypedDict

from ... import llm, registry

_BRANDS = ["Toyota", "Ford", "Tesla", "Honda", "Chevrolet", "GMC", "BMW"]


def _brands_in(q: str) -> list:
    ql = (q or "").lower()
    return [b for b in _BRANDS if b.lower() in ql] or ["Toyota", "Tesla"]


def _spec_price_safety(q):
    return ([("spec", f"Provide only spec facts relevant to: {q}"),
             ("pricing", f"Provide pricing / value facts for: {q}"),
             ("safety", f"Provide safety / reliability facts for: {q}")],
            "As the lead advisor, compose a concise buyer's report from the specialists.")


def _researcher_advisor(q):
    return ([("researcher", f"Gather the key facts relevant to: {q}")],
            "As the advisor, compose the final answer from the researcher's facts.")


def _per_brand(q):
    return ([(b, f"You research only {b}. Provide {b}'s relevant facts for: {q}") for b in _brands_in(q)],
            "Merge the per-brand findings into a clear side-by-side comparison.")


def _onboarding(q):
    return ([("crawler", f"Plan the link discovery / crawl for: {q}"),
             ("extractor", f"Plan content extraction (fetch + clean) for: {q}"),
             ("indexer", f"Plan chunking + embedding into vkp_vectors for: {q}")],
            "Compose the onboarding plan from the crawler, extractor and indexer agents.")


def _review_aggregator(q):
    return ([("owners", f"Summarize likely owner reviews for: {q}"),
             ("experts", f"Summarize likely expert reviews for: {q}"),
             ("safety", f"Summarize safety ratings / recalls for: {q}")],
            "Synthesize a balanced consensus review from the sources.")


_USE_CASES = {"spec-price-safety": _spec_price_safety, "researcher-advisor": _researcher_advisor,
              "per-brand-workers": _per_brand, "onboarding-crew": _onboarding, "review-aggregator": _review_aggregator}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "spec-price-safety"
    workers, merge_instr = _USE_CASES.get(uc, _spec_price_safety)(q)

    class S(TypedDict, total=False):
        notes: Annotated[list, operator.add]
        answer: str

    def mk(label, prompt):
        return lambda _s: {"notes": [(label, llm.complete(prompt))]}

    def merge(s):
        body = "\n\n".join(f"{l}: {t}" for l, t in s["notes"])
        return {"answer": llm.complete(f"{merge_instr}\n\nTASK: {q}\n\nSPECIALIST NOTES:\n{body}")}

    g = StateGraph(S)
    names = []
    for label, prompt in workers:
        nm = "w_" + re.sub(r"\W+", "_", label.lower())
        g.add_node(nm, mk(label, prompt)); names.append(nm)
    g.add_node("merge", merge)
    for nm in names:
        g.add_edge(START, nm); g.add_edge(nm, "merge")
    g.add_edge("merge", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "steps": [l for l, _ in out["notes"]], "useCase": uc}


registry.register("multi-agent", "langgraph", run)
