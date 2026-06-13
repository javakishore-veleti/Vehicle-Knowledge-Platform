"""Plan-and-Execute on the **Microsoft Agent Framework** — planner Agent → execute sub-steps → synthesizer Agent."""
from ... import registry, msa


def run(ctx: dict) -> dict:
    q = ctx["input"]

    async def _go():
        plan = await msa.acomplete(f"List 2-4 sub-questions (one per line) needed to answer: {q}", "You are a planner.")
        subs = [s.strip("-* ").strip() for s in plan.splitlines() if s.strip()][:4]
        parts = [f"{s} -> {await msa.acomplete('Answer briefly: ' + s)}" for s in subs]
        ans = await msa.acomplete(f"Using these findings, answer: {q}\n\n" + "\n".join(parts))
        return ans, subs

    ans, subs = msa.run_sync(_go())
    return {"answer": ans, "steps": subs}


registry.register("plan-execute", "msagent", run)
