"""Prompt chaining on **Google ADK** — a deterministic 2-LlmAgent chain (rewrite → answer)."""
from ... import registry, adk


def run(ctx: dict) -> dict:
    refined = adk.complete(f"Rewrite as a precise vehicle question. Return only the question:\n\n{ctx['input']}", "You rewrite questions.")
    answer = adk.complete(f"Answer concisely:\n\n{refined}")
    return {"answer": answer, "steps": ["rewrite", "answer"]}


registry.register("chaining", "google_adk", run)
