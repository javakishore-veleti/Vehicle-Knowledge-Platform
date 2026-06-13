"""Shared retrieval-scoping + prompts for the RAG pattern (reused by every framework cell).

Each use case scopes retrieval differently (company-only, brochure-only, snapshot, wider) and tailors
the generation prompt — that scoping is the whole point of the RAG use cases, so it lives here and
every cell pulls it (LangGraph retrieves directly; CrewAI wraps it in a use-case-scoped search tool)."""
from ... import corpus

_BRANDS = {"toyota": "toyota", "lexus": "toyota", "camry": "toyota", "rav4": "toyota",
           "ford": "ford", "lincoln": "ford", "f-150": "ford", "f150": "ford",
           "tesla": "tesla", "model 3": "tesla", "honda": "honda", "civic": "honda"}


def company(q: str):
    ql = (q or "").lower()
    for k, v in _BRANDS.items():
        if k in ql:
            return v
    return None


def retrieve_for(uc: str, query: str, scope_q: str = None) -> list:
    """Scope retrieval per use case. `scope_q` (default = query) drives company detection so an agent's
    rephrased tool query still resolves the right brand."""
    scope_q = scope_q if scope_q is not None else query
    if uc == "company-scoped-faq":
        return corpus.retrieve(query, 3, source_prefix=company(scope_q))
    if uc == "snapshot-grounded":
        return corpus.retrieve(query, 5, source_prefix=company(scope_q))
    if uc == "brochure-pdf-lookup":
        return corpus.retrieve(query, 3, contains="brochure")
    if uc == "explain-feature":
        return corpus.retrieve(query, 4)
    return corpus.retrieve(query, 3)   # single-fact-qa


PROMPTS = {
    "single-fact-qa": "Answer using ONLY these sources and cite [n].",
    "company-scoped-faq": "Answer ONLY about this brand, using ONLY these sources; cite [n].",
    "brochure-pdf-lookup": "Answer from these brochure sources; cite [n].",
    "explain-feature": "Explain the feature, drawing across these model sources; cite [n].",
    "snapshot-grounded": "Answer STRICTLY from this snapshot's content only; cite [n].",
}

DEFAULT_UC = "single-fact-qa"


def spec_for(use_case: str | None) -> tuple:
    uc = use_case if use_case in PROMPTS else DEFAULT_UC
    return uc, PROMPTS[uc]


def format_sources(docs: list) -> str:
    return "\n".join(f"[{i+1}] {d['text']} (source: {d['source']})" for i, d in enumerate(docs))
