"""Multi-agent on **AWS Strands** — parallel specialist Agents → a lead Agent composes.

Implements the 5 VKP use cases via ctx['useCase']; the worker rosters + merge instructions come from
`_base.USE_CASES` (shared with every framework cell). per-brand-workers spins one specialist per brand
in the query. Each specialist + the lead is a Strands Agent run via sa.complete."""
from ... import registry, sa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, workers, merge_instr = _base.spec_for(ctx.get("useCase"), q)
    notes = [(label, sa.complete(prompt)) for label, prompt in workers]
    body = "\n\n".join(f"{l}: {t}" for l, t in notes)
    return {"answer": sa.complete(_base.merge_prompt(merge_instr, q, body)), "useCase": uc,
            "steps": [l for l, _ in workers]}


registry.register("multi-agent", "strands", run)
