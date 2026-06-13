"""Multi-agent on the **Microsoft Agent Framework** — parallel specialist Agents → a lead Agent composes.

Implements the 5 VKP use cases via ctx['useCase']; the worker rosters + merge instructions come from
`_base.USE_CASES` (shared with every framework cell). per-brand-workers spins one specialist per brand
in the query. All calls run in ONE event loop (AF telemetry)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, workers, merge_instr = _base.spec_for(ctx.get("useCase"), q)

    async def _go():
        notes = [(label, await msa.acomplete(prompt)) for label, prompt in workers]
        body = "\n\n".join(f"{l}: {t}" for l, t in notes)
        return await msa.acomplete(_base.merge_prompt(merge_instr, q, body))

    return {"answer": msa.run_sync(_go()), "useCase": uc, "steps": [l for l, _ in workers]}


registry.register("multi-agent", "msagent", run)
