"""Prompt chaining on **AWS Strands** — a deterministic 2-Agent chain (rewrite → answer)."""
from ... import registry, sa


def run(ctx: dict) -> dict:
    refined = sa.complete(f"Rewrite as a precise vehicle question. Return only the question:\n\n{ctx['input']}", "You rewrite questions.")
    answer = sa.complete(f"Answer concisely:\n\n{refined}")
    return {"answer": answer, "steps": ["rewrite", "answer"]}


registry.register("chaining", "strands", run)
