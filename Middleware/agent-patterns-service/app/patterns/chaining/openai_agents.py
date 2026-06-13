"""Prompt chaining on the **OpenAI Agents SDK** — a deterministic 2-Agent chain (rewrite → answer)."""
from ... import registry, oa


def run(ctx: dict) -> dict:
    refined = oa.complete(f"Rewrite as a precise vehicle question. Return only the question:\n\n{ctx['input']}", "You rewrite questions.")
    answer = oa.complete(f"Answer concisely:\n\n{refined}")
    return {"answer": answer, "steps": ["rewrite", "answer"]}


registry.register("chaining", "openai_agents", run)
