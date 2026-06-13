"""Shared worker rosters + merge instructions for the Multi-agent pattern (every framework cell).

Each use case returns (workers, merge_instr): a list of (label, prompt) specialists to run in parallel,
and the instruction for the lead/merge step. per-brand-workers builds one worker per brand in the query.
Framework-agnostic, so every cell shares the roster and differs only in how it fans out + merges."""

_BRANDS = ["Toyota", "Ford", "Tesla", "Honda", "Chevrolet", "GMC", "BMW"]


def brands_in(q: str) -> list:
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
    return ([(b, f"You research only {b}. Provide {b}'s relevant facts for: {q}") for b in brands_in(q)],
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


USE_CASES = {"spec-price-safety": _spec_price_safety, "researcher-advisor": _researcher_advisor,
             "per-brand-workers": _per_brand, "onboarding-crew": _onboarding, "review-aggregator": _review_aggregator}

DEFAULT_UC = "spec-price-safety"


def spec_for(use_case: str | None, q: str) -> tuple:
    uc = use_case if use_case in USE_CASES else DEFAULT_UC
    workers, merge_instr = USE_CASES[uc](q)
    return uc, workers, merge_instr


def merge_prompt(merge_instr: str, q: str, body: str) -> str:
    return f"{merge_instr}\n\nTASK: {q}\n\nSPECIALIST NOTES:\n{body}"
