"""Prompt chaining on the **Microsoft Agent Framework** — a deterministic 2-Agent chain (rewrite → answer)."""
from ... import registry, msa


def run(ctx: dict) -> dict:
    async def _go():
        refined = await msa.acomplete(f"Rewrite as a precise vehicle question. Return only the question:\n\n{ctx['input']}", "You rewrite questions.")
        return await msa.acomplete(f"Answer concisely:\n\n{refined}")

    return {"answer": msa.run_sync(_go()), "steps": ["rewrite", "answer"]}


registry.register("chaining", "msagent", run)
