"""Plan-and-Execute on the **Microsoft Agent Framework** — planner Agent → execute → synthesizer Agent.

Implements the 5 VKP use cases via ctx['useCase']. The plan/execute/synthesize spec comes from
`_base.USE_CASES` (shared with every framework cell): LLM plans decompose via a planner Agent, the execute
step gathers evidence deterministically (corpus retrieval / vehicle_spec tool), and a synthesizer Agent
writes the final answer. All calls run in ONE event loop (AF telemetry)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    async def _go():
        if spec["plan"][0] == "llm":
            n = spec["plan"][1]
            raw = await msa.acomplete(f"Break this into {n} focused sub-queries. Return ONLY a JSON array of strings.\n\n{q}", "You are a planner.")
            steps = _base.parse_steps(raw, q, n)
        else:
            steps = list(spec["plan"][1])
        evidence = spec["exec"](q, steps)        # deterministic execute — no LLM in the loop
        return steps, await msa.acomplete(_base.synth_prompt(spec["instr"], q, evidence))

    steps, ans = msa.run_sync(_go())
    return {"answer": ans, "steps": steps, "useCase": uc}


registry.register("plan-execute", "msagent", run)
