"""ReWOO on the **OpenAI Agents SDK** — planner Agent emits blind tool calls → execute (no LLM) → solver Agent."""
import json
import re

from ... import registry, oa, tools


def run(ctx: dict) -> dict:
    q = ctx["input"]
    raw = oa.complete('Plan the vehicle_spec(model, field) calls needed (no results yet). '
                      'Return ONLY a JSON array of {"model":..,"field":..}.\n\n' + q, "You are a planner.")
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        plan = json.loads(m.group(0)) if m else []
    except Exception:
        plan = []
    ev = "\n".join(f"{c} -> {tools.vehicle_spec(c.get('model', ''), c.get('field', ''))}" for c in plan[:6])
    return {"answer": oa.complete(f"Using ONLY this evidence, answer: {q}\n\nEVIDENCE:\n{ev}"),
            "steps": [str(c) for c in plan]}


registry.register("rewoo", "openai_agents", run)
