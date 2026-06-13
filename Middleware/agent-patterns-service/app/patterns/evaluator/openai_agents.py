"""Evaluator-optimizer on the **OpenAI Agents SDK** — generator Agent → judge Agent → revise (one round)."""
from ... import registry, oa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = oa.complete(f"Answer accurately: {q}")
    critique = oa.complete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}", "You are a strict judge.")
    answer = oa.complete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "openai_agents", run)
