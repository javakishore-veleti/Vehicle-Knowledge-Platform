"""Shared prompts + helpers for the Reflection pattern, reused by every framework cell so the cells
differ ONLY in framework mechanics (the point of the comparison)."""

DRAFT_SYS = ("You are a precise automotive expert. Answer the user's vehicle question concisely and "
             "factually. Avoid hallucinated specs or prices.")

CRITIC_SYS = ("You are a meticulous fact critic for automotive answers. Find inaccuracies, missing "
              "context, and unsupported claims.")

CRITIQUE = ("Critique the ANSWER to the QUESTION for factual accuracy, completeness, and any unsupported "
            "claims. Reply with a short bullet list of concrete fixes, or 'No changes needed.'\n\n"
            "QUESTION: {q}\nANSWER: {a}")

REVISE = ("Revise the ANSWER using the CRITIQUE. Return ONLY the improved answer — no preamble.\n\n"
          "QUESTION: {q}\nANSWER: {a}\nCRITIQUE: {c}")


# --- The 5 concrete VKP Reflection use cases (framework-agnostic) ---
# Each use case is the SAME generate -> critique -> revise loop with use-case-specific
# instructions. Cells wire {draft}/{critique} through their own mechanic (LangGraph: inline
# string; CrewAI: Task context), so this catalog is the single source of the use-case intent.
USE_CASES = {
    "answer-quality-gate": {
        "generate": "You are a vehicle expert. Answer accurately and concisely: {q}",
        "critique": "Critique the DRAFT for grounding, on-topic focus, and unsupported/hallucinated claims; list concrete fixes.",
        "revise": "Revise the DRAFT using the CRITIQUE. Return ONLY the improved answer.",
    },
    "chunk-quality-review": {
        "generate": "Split this vehicle content into clean, self-contained chunks (one topic each). Return a numbered list.\n\nCONTENT:\n{q}",
        "critique": "Critique the CHUNKS: any incoherent, too long, or mixing topics / boilerplate? List which to re-chunk.",
        "revise": "Re-chunk the flagged ones. Return the final clean numbered chunk list.",
    },
    "citation-verification": {
        "generate": "Answer with bracketed [n] citations where a claim needs support: {q}",
        "critique": "Check each claim is actually supported; flag any unsupported or uncited claims.",
        "revise": "Drop or qualify the unsupported claims. Return ONLY the corrected, properly-cited answer.",
    },
    "crawl-coverage-self-check": {
        "generate": "Given these discovered sections/links from a vehicle site, list the high-value sections likely still MISSING:\n\n{q}",
        "critique": "Critique the gap list: which gaps are real and high-value (EV, trucks, recalls, pricing)? Drop the noise.",
        "revise": "Return the final prioritized list of sections to re-crawl.",
    },
    "spec-extraction-accuracy": {
        "generate": "Extract the vehicle specs as 'key: value' lines from this text:\n\n{q}",
        "critique": "Verify each extracted spec against the source text; flag mismatches or hallucinated values.",
        "revise": "Correct the mismatches. Return ONLY the final verified spec list.",
    },
}

DEFAULT_UC = "answer-quality-gate"


def spec_for(use_case: str | None) -> tuple:
    """(useCase, spec) for a request — falls back to the default use case."""
    uc = use_case or DEFAULT_UC
    return uc, USE_CASES.get(uc, USE_CASES[DEFAULT_UC])


def result(draft: str, critique: str, answer: str) -> dict:
    """Uniform return shape for every reflection cell."""
    return {"draft": draft, "critique": critique, "answer": answer}
