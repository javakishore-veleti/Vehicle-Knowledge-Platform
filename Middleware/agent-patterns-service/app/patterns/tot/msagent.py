"""Tree of Thoughts on the **Microsoft Agent Framework** — branch (propose 3) → evaluate (score) → select.

Implements the 5 VKP use cases via ctx['useCase']; branch prompts + eval criteria come from
`_base.USE_CASES` (shared with every framework cell). All calls run in ONE event loop (AF telemetry)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, branch_p, eval_crit = _base.spec_for(ctx.get("useCase"), q)

    async def _go():
        thoughts = _base.parse_thoughts(await msa.acomplete(branch_p))
        scores = [_base.score_of(await msa.acomplete(_base.eval_prompt(eval_crit, t))) for t in thoughts]
        return thoughts, scores

    thoughts, scores = msa.run_sync(_go())
    best = max(range(len(thoughts)), key=lambda i: scores[i])
    return {"answer": thoughts[best], "useCase": uc,
            "steps": [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]}


registry.register("tot", "msagent", run)
