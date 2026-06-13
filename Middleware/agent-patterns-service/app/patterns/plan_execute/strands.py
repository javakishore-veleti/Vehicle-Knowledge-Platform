"""Plan-and-Execute on **AWS Strands** — planner Agent → execute → synthesizer Agent.

Implements the 5 VKP use cases via ctx['useCase']. The plan/execute/synthesize spec comes from
`_base.USE_CASES` (shared with every framework cell): LLM plans decompose via a planner Agent, the execute
step gathers evidence deterministically (corpus retrieval / vehicle_spec tool), and a synthesizer Agent
writes the final answer. This cell shows ONLY the AWS Strands mechanics."""
from ... import registry, sa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    if spec["plan"][0] == "llm":
        n = spec["plan"][1]
        raw = sa.complete(f"Break this into {n} focused sub-queries. Return ONLY a JSON array of strings.\n\n{q}", "You are a planner.")
        steps = _base.parse_steps(raw, q, n)
    else:
        steps = list(spec["plan"][1])

    evidence = spec["exec"](q, steps)        # deterministic execute — no LLM in the loop
    return {"answer": sa.complete(_base.synth_prompt(spec["instr"], q, evidence)), "steps": steps, "useCase": uc}


registry.register("plan-execute", "strands", run)
