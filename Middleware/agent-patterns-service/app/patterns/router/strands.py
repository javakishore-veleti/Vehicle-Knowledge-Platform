"""Router on **AWS Strands** — a classifier Agent routes to a tailored specialist Agent."""
from ... import registry, sa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    r = (sa.complete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}", "Reply one word.") or "other").strip().lower()
    route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
    sysmap = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
              "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}
    return {"answer": sa.complete(q, sysmap[route]), "steps": [f"routed -> {route}"]}


registry.register("router", "strands", run)
