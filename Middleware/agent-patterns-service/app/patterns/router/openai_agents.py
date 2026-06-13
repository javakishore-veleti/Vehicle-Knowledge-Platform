"""Router on the **OpenAI Agents SDK** — a classifier Agent routes to a tailored specialist Agent."""
from ... import registry, oa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    r = (oa.complete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}", "You are a classifier. Reply one word.") or "other").strip().lower()
    route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
    instr = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
             "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}
    return {"answer": oa.complete(q, instr[route]), "steps": [f"routed -> {route}"]}


registry.register("router", "openai_agents", run)
