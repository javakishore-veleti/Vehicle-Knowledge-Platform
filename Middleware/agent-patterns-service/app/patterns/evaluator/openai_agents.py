"""Evaluator-optimizer on the **OpenAI Agents SDK** — generate → evaluate → refine once if the gate is unmet.

Implements the 5 VKP use cases via ctx['useCase']. The generate/refine prompts + eval strategy come
from `_base.USE_CASES` (shared with every framework cell): an Agent does generate/refine + the LLM judge,
while retrieval / single-pass eval reuse `_base` (query-rewriter scores via REAL corpus retrieval)."""
from ... import registry, oa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    prompt, system = spec["first"](q)
    draft = oa.complete(prompt, system) if system else oa.complete(prompt)

    if spec["eval"] in ("retrieval", "single"):
        score, feedback = _base.evaluate(spec, q, draft)
    else:
        score, feedback = _base._parse_score(oa.complete(spec["judge"](q, draft)))

    refined = score < 8 and spec.get("refinable")
    answer = oa.complete(spec["refine"](q, draft, feedback)) if refined else draft
    return {"answer": answer, "critique": feedback, "useCase": uc,
            "steps": [f"score={score}", f"refined={'yes' if refined else 'no'}"]}


registry.register("evaluator-optimizer", "openai_agents", run)
