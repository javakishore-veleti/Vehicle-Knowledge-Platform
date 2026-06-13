"""Evaluator-optimizer on **AWS Strands** — generator Agent → judge Agent → revise (one round)."""
from ... import registry, sa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = sa.complete(f"Answer accurately: {q}")
    critique = sa.complete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}", "You are a strict judge.")
    answer = sa.complete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "strands", run)
