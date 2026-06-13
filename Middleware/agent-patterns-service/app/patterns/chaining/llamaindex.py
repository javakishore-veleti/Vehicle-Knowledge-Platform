"""Prompt chaining on **LlamaIndex** — a deterministic 2-step LLM chain (rewrite → answer)."""
from ... import registry, li


def run(ctx: dict) -> dict:
    refined = li.complete(f"Rewrite as a precise vehicle question. Return only the question:\n\n{ctx['input']}")
    answer = li.complete(f"Answer concisely:\n\n{refined}")
    return {"answer": answer, "steps": ["rewrite", "answer"]}


registry.register("chaining", "llamaindex", run)
