"""Router on **Haystack** — its generator classifies, then routes to a tailored prompt."""
from ... import registry, hay


def run(ctx: dict) -> dict:
    q = ctx["input"]
    r = (hay.complete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}") or "other").strip().lower()
    route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
    sysmap = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
              "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}
    return {"answer": hay.complete(f"{sysmap[route]}\n\n{q}"), "steps": [f"routed -> {route}"]}


registry.register("router", "haystack", run)
