"""Reflection on **LangGraph** — a draft -> critique -> revise StateGraph.

Implements the 5 VKP Reflection use cases via ctx['useCase'] (default = answer-quality-gate). Each use
case is the same reflect loop with use-case-specific prompts, so you see the pattern realized concretely."""
from typing import TypedDict

from ... import llm, registry

# Each entry: (generate_prompt, critique_prompt{d}, revise_prompt{d,c}) for one use case.
USE_CASES = {
    "answer-quality-gate": lambda q: (
        f"You are a vehicle expert. Answer accurately and concisely: {q}",
        "Critique the DRAFT for grounding, on-topic focus, and unsupported/hallucinated claims; list concrete fixes.\n\nDRAFT:\n{d}",
        "Revise the DRAFT using the CRITIQUE. Return ONLY the improved answer.\n\nDRAFT:\n{d}\n\nCRITIQUE:\n{c}"),
    "chunk-quality-review": lambda q: (
        f"Split this vehicle content into clean, self-contained chunks (one topic each). Return a numbered list.\n\nCONTENT:\n{q}",
        "Critique the CHUNKS: any incoherent, too long, or mixing topics / boilerplate? List which to re-chunk.\n\nCHUNKS:\n{d}",
        "Re-chunk the flagged ones. Return the final clean numbered chunk list.\n\nCHUNKS:\n{d}\n\nCRITIQUE:\n{c}"),
    "citation-verification": lambda q: (
        f"Answer with bracketed [n] citations where a claim needs support: {q}",
        "Check each claim is actually supported; flag any unsupported or uncited claims.\n\nANSWER:\n{d}",
        "Drop or qualify the unsupported claims. Return ONLY the corrected, properly-cited answer.\n\nANSWER:\n{d}\n\nCRITIQUE:\n{c}"),
    "crawl-coverage-self-check": lambda q: (
        f"Given these discovered sections/links from a vehicle site, list the high-value sections likely still MISSING:\n\n{q}",
        "Critique the gap list: which gaps are real and high-value (EV, trucks, recalls, pricing)? Drop the noise.\n\nGAPS:\n{d}",
        "Return the final prioritized list of sections to re-crawl.\n\nGAPS:\n{d}\n\nCRITIQUE:\n{c}"),
    "spec-extraction-accuracy": lambda q: (
        f"Extract the vehicle specs as 'key: value' lines from this text:\n\n{q}",
        "Verify each extracted spec against the source text; flag mismatches or hallucinated values.\n\nEXTRACTED:\n{d}",
        "Correct the mismatches. Return ONLY the final verified spec list.\n\nEXTRACTED:\n{d}\n\nCRITIQUE:\n{c}"),
}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "answer-quality-gate"
    gen_p, crit_p, rev_p = USE_CASES.get(uc, USE_CASES["answer-quality-gate"])(q)

    class S(TypedDict, total=False):
        draft: str
        critique: str
        answer: str

    def generate(_s): return {"draft": llm.complete(gen_p)}
    def critique(s): return {"critique": llm.complete(crit_p.format(d=s["draft"]))}
    def revise(s): return {"answer": llm.complete(rev_p.format(d=s["draft"], c=s["critique"]))}

    g = StateGraph(S)
    g.add_node("generate", generate); g.add_node("critique", critique); g.add_node("revise", revise)
    g.add_edge(START, "generate"); g.add_edge("generate", "critique"); g.add_edge("critique", "revise"); g.add_edge("revise", END)
    out = g.compile().invoke({})
    return {"answer": out["answer"], "draft": out["draft"], "critique": out["critique"], "useCase": uc}


registry.register("reflection", "langgraph", run)
