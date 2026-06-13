"""Evaluator-optimizer on the **Microsoft Agent Framework** — generate → evaluate → refine once.

Implements the 5 VKP use cases via ctx['useCase']. The generate/refine prompts + eval strategy come
from `_base.USE_CASES` (shared with every framework cell): an Agent does generate/refine + the LLM judge,
while retrieval / single-pass eval reuse `_base` (query-rewriter scores via REAL retrieval). All calls
run in ONE event loop (AF telemetry)."""
from ... import registry, msa
from . import _base


def run(ctx: dict) -> dict:
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    async def _go():
        prompt, system = spec["first"](q)
        draft = await msa.acomplete(prompt, system) if system else await msa.acomplete(prompt)
        if spec["eval"] in ("retrieval", "single"):
            score, feedback = _base.evaluate(spec, q, draft)
        else:
            score, feedback = _base._parse_score(await msa.acomplete(spec["judge"](q, draft)))
        refined = score < 8 and spec.get("refinable")
        answer = await msa.acomplete(spec["refine"](q, draft, feedback)) if refined else draft
        return answer, feedback, score, refined

    answer, feedback, score, refined = msa.run_sync(_go())
    return {"answer": answer, "critique": feedback, "useCase": uc,
            "steps": [f"score={score}", f"refined={'yes' if refined else 'no'}"]}


registry.register("evaluator-optimizer", "msagent", run)
