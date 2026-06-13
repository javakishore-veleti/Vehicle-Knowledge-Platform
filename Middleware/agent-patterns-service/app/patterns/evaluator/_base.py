"""Shared use-case catalog + eval helpers for the Evaluator-optimizer pattern.

Reused by every framework cell so the cells differ ONLY in framework mechanics (the generate↔evaluate
loop). Each use case provides a first-pass prompt, a refine prompt, and an EVAL STRATEGY:
  - "judge"     → an LLM scores 1-10 + one-line feedback (answer/summary/chunk quality)
  - "retrieval" → REAL corpus retrieval is the signal (query-rewriter: did the rewrite retrieve better?)
  - "single"    → single-pass, no refine loop (embedding-model selection)
"""
import re

from ... import llm, corpus

_EMB = ("all-MiniLM-L6-v2 (384d, fast, local, free); text-embedding-3-small (1536d, OpenAI, paid); "
        "bge-large-en-v1.5 (1024d, strong retrieval, local)")


def _parse_score(r: str):
    m = re.search(r"SCORE:\s*(\d+)", r or "")
    fb = re.search(r"FEEDBACK:\s*(.*)", r or "", re.S)
    return (int(m.group(1)) if m else 7), (fb.group(1).strip()[:200] if fb else "")


USE_CASES = {
    "answer-refiner": {
        "first": lambda q: (q, "You are a vehicle expert. Answer completely, with citations where possible."),
        "refine": lambda q, prev, fb: f"Improve this answer to '{q}' using the feedback: {fb}\n\nPrevious:\n{prev}",
        "eval": "judge",
        "judge": lambda q, out: ("Rate 1-10 for completeness + citations, with one-line feedback. Format exactly "
                                 f"'SCORE: <n> | FEEDBACK: <text>'.\n\nQ: {q}\nA: {out}"),
        "refinable": True,
    },
    "chunking-optimizer": {
        "first": lambda q: (f"Chunk this content into self-contained pieces for retrieval. Return a numbered list.\n\nCONTENT:\n{q}", None),
        "refine": lambda q, prev, fb: f"Re-chunk addressing: {fb}. Return a numbered list of self-contained chunks.\n\nCONTENT:\n{q}",
        "eval": "judge",
        "judge": lambda q, out: ("Rate 1-10 these chunks for retrieval quality (self-contained, coherent, no boilerplate), "
                                 f"one-line feedback. Format 'SCORE: <n> | FEEDBACK: <text>'.\n\nCHUNKS:\n{out}"),
        "refinable": True,
    },
    "query-rewriter": {
        "first": lambda q: (f"Rewrite this into a precise vehicle search query. Return ONLY the query.\n\n{q}", None),
        "refine": lambda q, prev, fb: ("Rewrite this vehicle search query to retrieve better results. Feedback: "
                                       f"{fb}\nReturn ONLY the rewritten query.\n\nQuery: {prev}"),
        "eval": "retrieval",
        "refinable": True,
    },
    "summary-tightener": {
        "first": lambda q: (f"Summarize this accurately in at most 2 sentences:\n\n{q}", None),
        "refine": lambda q, prev, fb: f"Improve this summary (accuracy + brevity) using feedback: {fb}\n\nSOURCE:\n{q}\n\nSummary:\n{prev}",
        "eval": "judge",
        "judge": lambda q, out: ("Rate 1-10 the summary for accuracy vs source AND brevity, one-line feedback. Format "
                                 f"'SCORE: <n> | FEEDBACK: <text>'.\n\nSOURCE:\n{q}\n\nSUMMARY:\n{out}"),
        "refinable": True,
    },
    "embedding-model-selector": {
        "first": lambda q: (f"For this retrieval scenario, score each candidate embedding model 1-10 and pick the best "
                            f"with a one-line rationale.\n\nSCENARIO: {q}\n\nCANDIDATES: {_EMB}", None),
        "refine": None,
        "eval": "single",
        "refinable": False,
    },
}

DEFAULT_UC = "answer-refiner"


def spec_for(use_case: str | None) -> tuple:
    uc = use_case or DEFAULT_UC
    return uc, USE_CASES.get(uc, USE_CASES[DEFAULT_UC])


def generate(spec: dict, q: str, prev: str = None, fb: str = None) -> str:
    """First-pass or refinement generation (framework-agnostic)."""
    if prev and fb and spec.get("refine"):
        return llm.complete(spec["refine"](q, prev, fb))
    prompt, system = spec["first"](q)
    return llm.complete(prompt, system=system) if system else llm.complete(prompt)


def evaluate(spec: dict, q: str, out: str) -> tuple:
    """Return (score, feedback) using the use case's eval strategy."""
    kind = spec["eval"]
    if kind == "retrieval":
        hits = corpus.retrieve(out, 3)
        total = sum(h.get("score", 0) for h in hits)
        score = max(1, min(10, 3 + total))
        fb = (f"retrieved {len(hits)} docs (top: {hits[0]['source']}, overlap {total})" if total
              else "no relevant docs — broaden / use model keywords")
        return score, fb
    if kind == "single":
        return 9, "selection made (single-pass evaluation)"
    return _parse_score(llm.complete(spec["judge"](q, out)))
