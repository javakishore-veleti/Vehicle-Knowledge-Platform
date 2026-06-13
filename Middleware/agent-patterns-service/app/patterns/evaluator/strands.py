"""Evaluator-optimizer on **AWS Strands** — generate → evaluate → refine once if the gate is unmet.

Implements the 5 VKP use cases via ctx['useCase']. The generate/refine prompts + eval strategy come
from `_base.USE_CASES` (shared with every framework cell): an Agent does generate/refine + the LLM judge,
while retrieval / single-pass eval reuse `_base` (query-rewriter scores via REAL corpus retrieval)."""
from ... import registry, sa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    prompt, system = spec["first"](q)
    draft = sa.complete(prompt, system) if system else sa.complete(prompt)

    if spec["eval"] in ("retrieval", "single"):
        score, feedback = _base.evaluate(spec, q, draft)
    else:
        score, feedback = _base._parse_score(sa.complete(spec["judge"](q, draft)))

    refined = score < 8 and spec.get("refinable")
    answer = sa.complete(spec["refine"](q, draft, feedback)) if refined else draft
    return {"answer": answer, "critique": feedback, "useCase": uc,
            "steps": [f"score={score}", f"refined={'yes' if refined else 'no'}"]}


registry.register("evaluator-optimizer", "strands", run)
