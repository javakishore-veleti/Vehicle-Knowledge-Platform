"""Evaluator-optimizer on **Google ADK** — generator LlmAgent → judge LlmAgent → revise (one round)."""
from ... import registry, adk


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = adk.complete(f"Answer accurately: {q}")
    critique = adk.complete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}", "You are a strict judge.")
    answer = adk.complete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "google_adk", run)
