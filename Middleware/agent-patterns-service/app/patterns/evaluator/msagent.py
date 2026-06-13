"""Evaluator-optimizer on the **Microsoft Agent Framework** — generator Agent → judge Agent → revise (one round)."""
from ... import registry, msa


def run(ctx: dict) -> dict:
    q = ctx["input"]

    async def _go():
        draft = await msa.acomplete(f"Answer accurately: {q}")
        critique = await msa.acomplete(f"Rate 1-10 for accuracy/completeness and give one-line feedback.\n\nQ:{q}\nA:{draft}", "You are a strict judge.")
        answer = await msa.acomplete(f"Improve the answer using the feedback. Return only the answer.\n\nQ:{q}\nA:{draft}\nFEEDBACK:{critique}")
        return answer, critique

    answer, critique = msa.run_sync(_go())
    return {"answer": answer, "critique": critique}


registry.register("evaluator-optimizer", "msagent", run)
