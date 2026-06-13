"""Evaluator-optimizer on **Haystack** — generate → judge → revise (one round)."""
from ... import registry, hay


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = hay.complete(f"Answer accurately: {q}")
    critique = hay.complete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}")
    answer = hay.complete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "haystack", run)
