"""Router on **Google ADK** — a classifier LlmAgent routes to a tailored specialist LlmAgent."""
from ... import registry, adk


def run(ctx: dict) -> dict:
    q = ctx["input"]
    r = (adk.complete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}", "Reply one word.") or "other").strip().lower()
    route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
    instr = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
             "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}
    return {"answer": adk.complete(q, instr[route]), "steps": [f"routed -> {route}"]}


registry.register("router", "google_adk", run)
