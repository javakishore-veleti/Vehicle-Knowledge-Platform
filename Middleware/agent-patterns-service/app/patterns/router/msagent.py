"""Router on the **Microsoft Agent Framework** — a classifier Agent routes to a tailored specialist Agent."""
from ... import registry, msa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    instr = {"spec": "Give precise specs.", "compare": "Compare clearly with a verdict.",
             "recommend": "Recommend with reasons.", "other": "Help with the vehicle question."}

    async def _go():
        r = (await msa.acomplete(f"Classify as one word: spec, compare, recommend, other.\n\n{q}", "Reply one word.") or "other").strip().lower()
        route = next((c for c in ("spec", "compare", "recommend") if c in r), "other")
        return route, await msa.acomplete(q, instr[route])

    route, ans = msa.run_sync(_go())
    return {"answer": ans, "steps": [f"routed -> {route}"]}


registry.register("router", "msagent", run)
