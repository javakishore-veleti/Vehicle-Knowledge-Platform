"""Router on **LlamaIndex** — its LLM classifies, then routes to a tailored handler."""
from ... import registry, li


def run(ctx: dict) -> dict:
    q = ctx["input"]
    r = (li.complete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}") or "other").strip().lower()
    route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
    sysmap = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
              "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}
    return {"answer": li.complete(f"{sysmap[route]}\n\n{q}"), "steps": [f"routed -> {route}"]}


registry.register("router", "llamaindex", run)
