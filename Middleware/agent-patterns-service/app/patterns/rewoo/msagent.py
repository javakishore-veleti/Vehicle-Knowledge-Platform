"""ReWOO on the **Microsoft Agent Framework** — planner Agent emits blind tool calls → execute (no LLM) → solver Agent."""
import json
import re

from ... import registry, msa, tools


def run(ctx: dict) -> dict:
    q = ctx["input"]

    async def _go():
        raw = await msa.acomplete('Plan the vehicle_spec(model, field) calls needed (no results yet). '
                                  'Return ONLY a JSON array of {"model":..,"field":..}.\n\n' + q, "You are a planner.")
        m = re.search(r"\[.*\]", raw, re.S)
        try:
            plan = json.loads(m.group(0)) if m else []
        except Exception:
            plan = []
        ev = "\n".join(f"{c} -> {tools.vehicle_spec(c.get('model', ''), c.get('field', ''))}" for c in plan[:6])
        return await msa.acomplete(f"Using ONLY this evidence, answer: {q}\n\nEVIDENCE:\n{ev}"), [str(c) for c in plan]

    ans, steps = msa.run_sync(_go())
    return {"answer": ans, "steps": steps}


registry.register("rewoo", "msagent", run)
