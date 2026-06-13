"""ReWOO on the **Microsoft Agent Framework** — blind plan → execute (no LLM in the loop) → solver Agent.

Implements the 5 VKP use cases via ctx['useCase']. The plan/worker/solver spec comes from
`_base.USE_CASES` (shared with every framework cell): the plan is blind + deterministic, the worker runs
the vehicle_spec calls with no LLM, and an Agent does the solve (nightly-price-refresh is LLM-free)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)
    plan = spec["plan"]
    evidence = spec["worker"](plan)        # blind execute — no LLM in the loop
    kind, builder = spec["solver"]

    async def _go():
        return await msa.acomplete(builder(q, evidence)) if kind == "llm" else builder(q, evidence)

    return {"answer": msa.run_sync(_go()), "steps": [str(c) for c in plan], "useCase": uc}


registry.register("rewoo", "msagent", run)
