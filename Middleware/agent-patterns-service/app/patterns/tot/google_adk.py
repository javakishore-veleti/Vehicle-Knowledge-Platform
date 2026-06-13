"""Tree of Thoughts on **Google ADK** — branch (propose 3) → evaluate (score) → select.

Implements the 5 VKP use cases via ctx['useCase']; branch prompts + eval criteria come from
`_base.USE_CASES` (shared with every framework cell). Each step is an LlmAgent run via adk.complete."""
from ... import registry, adk
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, branch_p, eval_crit = _base.spec_for(ctx.get("useCase"), q)
    thoughts = _base.parse_thoughts(adk.complete(branch_p))
    scores = [_base.score_of(adk.complete(_base.eval_prompt(eval_crit, t))) for t in thoughts]
    best = max(range(len(thoughts)), key=lambda i: scores[i])
    return {"answer": thoughts[best], "useCase": uc,
            "steps": [f"thought{i+1}: score {s}" for i, s in enumerate(scores)]}


registry.register("tot", "google_adk", run)
