"""Multi-agent on **Haystack** — parallel generator specialists → a lead composes.

Implements the 5 VKP use cases via ctx['useCase']; the worker rosters + merge instructions come from
`_base.USE_CASES` (shared with every framework cell). per-brand-workers spins one specialist per brand
in the query. This cell uses Haystack's generator for each specialist + the lead."""
from ... import registry, hay
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, workers, merge_instr = _base.spec_for(ctx.get("useCase"), q)
    notes = [(label, hay.complete(prompt)) for label, prompt in workers]
    body = "\n\n".join(f"{l}: {t}" for l, t in notes)
    return {"answer": hay.complete(_base.merge_prompt(merge_instr, q, body)), "useCase": uc,
            "steps": [l for l, _ in workers]}


registry.register("multi-agent", "haystack", run)
