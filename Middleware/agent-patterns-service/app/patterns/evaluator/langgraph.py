"""Evaluator-optimizer on **LangGraph** — generate ↔ evaluate loop with a score-gated conditional edge.

Implements the 5 VKP use cases via ctx['useCase'] (default = answer-refiner). Each provides its own
(generate, evaluate) pair; query-rewriter uses REAL corpus retrieval as the evaluation signal."""
import re
from typing import TypedDict

from ... import llm, registry, corpus


def _parse_score(r: str):
    m = re.search(r"SCORE:\s*(\d+)", r or "")
    fb = re.search(r"FEEDBACK:\s*(.*)", r or "", re.S)
    return (int(m.group(1)) if m else 7), (fb.group(1).strip()[:200] if fb else "")


def _answer_refiner(q):
    def gen(prev, fb):
        if fb and prev:
            return llm.complete(f"Improve this answer to '{q}' using the feedback: {fb}\n\nPrevious:\n{prev}")
        return llm.complete(q, system="You are a vehicle expert. Answer completely, with citations where possible.")
    def ev(out):
        return _parse_score(llm.complete(
            f"Rate 1-10 for completeness + citations, with one-line feedback. Format exactly "
            f"'SCORE: <n> | FEEDBACK: <text>'.\n\nQ: {q}\nA: {out}"))
    return gen, ev


def _query_rewriter(q):
    def gen(prev, fb):
        if fb and prev:
            return llm.complete(f"Rewrite this vehicle search query to retrieve better results. Feedback: {fb}\n"
                                f"Return ONLY the rewritten query.\n\nQuery: {prev}")
        return llm.complete(f"Rewrite this into a precise vehicle search query. Return ONLY the query.\n\n{q}")
    def ev(out):
        hits = corpus.retrieve(out, 3)
        total = sum(h.get("score", 0) for h in hits)
        score = max(1, min(10, 3 + total))
        fb = (f"retrieved {len(hits)} docs (top: {hits[0]['source']}, overlap {total})" if total
              else "no relevant docs — broaden / use model keywords")
        return score, fb
    return gen, ev


def _summary_tightener(q):
    def gen(prev, fb):
        if fb and prev:
            return llm.complete(f"Improve this summary (accuracy + brevity) using feedback: {fb}\n\nSOURCE:\n{q}\n\nSummary:\n{prev}")
        return llm.complete(f"Summarize this accurately in at most 2 sentences:\n\n{q}")
    def ev(out):
        return _parse_score(llm.complete(
            f"Rate 1-10 the summary for accuracy vs source AND brevity, one-line feedback. "
            f"Format 'SCORE: <n> | FEEDBACK: <text>'.\n\nSOURCE:\n{q}\n\nSUMMARY:\n{out}"))
    return gen, ev


def _chunking_optimizer(q):
    def gen(prev, fb):
        if fb and prev:
            return llm.complete(f"Re-chunk addressing: {fb}. Return a numbered list of self-contained chunks.\n\nCONTENT:\n{q}")
        return llm.complete(f"Chunk this content into self-contained pieces for retrieval. Return a numbered list.\n\nCONTENT:\n{q}")
    def ev(out):
        return _parse_score(llm.complete(
            f"Rate 1-10 these chunks for retrieval quality (self-contained, coherent, no boilerplate), one-line "
            f"feedback. Format 'SCORE: <n> | FEEDBACK: <text>'.\n\nCHUNKS:\n{out}"))
    return gen, ev


_EMB = "all-MiniLM-L6-v2 (384d, fast, local, free); text-embedding-3-small (1536d, OpenAI, paid); bge-large-en-v1.5 (1024d, strong retrieval, local)"


def _embedding_selector(q):
    def gen(prev, fb):
        return llm.complete(f"For this retrieval scenario, score each candidate embedding model 1-10 and pick "
                            f"the best with a one-line rationale.\n\nSCENARIO: {q}\n\nCANDIDATES: {_EMB}")
    def ev(out):
        return 9, "selection made (single-pass evaluation)"
    return gen, ev


_HANDLERS = {
    "answer-refiner": _answer_refiner, "query-rewriter": _query_rewriter,
    "summary-tightener": _summary_tightener, "chunking-optimizer": _chunking_optimizer,
    "embedding-model-selector": _embedding_selector,
}


def run(ctx: dict) -> dict:
    from langgraph.graph import StateGraph, START, END
    q = ctx["input"]
    uc = ctx.get("useCase") or "answer-refiner"
    max_iter = int(ctx.get("maxIterations") or 3)
    gen_fn, eval_fn = _HANDLERS.get(uc, _answer_refiner)(q)

    class S(TypedDict, total=False):
        output: str
        score: int
        feedback: str
        n: int

    def generate(s): return {"output": gen_fn(s.get("output"), s.get("feedback")), "n": s.get("n", 0) + 1}
    def evaluate(s):
        score, fb = eval_fn(s["output"]); return {"score": score, "feedback": fb}
    def route(s): return "done" if s["score"] >= 8 or s["n"] >= max_iter else "generate"

    g = StateGraph(S)
    g.add_node("generate", generate); g.add_node("evaluate", evaluate)
    g.add_edge(START, "generate"); g.add_edge("generate", "evaluate")
    g.add_conditional_edges("evaluate", route, {"generate": "generate", "done": END})
    out = g.compile().invoke({})
    return {"answer": out["output"], "critique": out.get("feedback"), "useCase": uc,
            "steps": [f"iterations={out.get('n')}", f"final_score={out.get('score')}"]}


registry.register("evaluator-optimizer", "langgraph", run)
