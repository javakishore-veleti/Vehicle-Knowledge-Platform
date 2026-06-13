"""Evaluator-optimizer on **LlamaIndex** — generate → judge → revise (one round)."""
from ... import registry, li


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = li.complete(f"Answer accurately: {q}")
    critique = li.complete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}")
    answer = li.complete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "llamaindex", run)
