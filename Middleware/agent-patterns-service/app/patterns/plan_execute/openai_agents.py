"""Plan-and-Execute on the **OpenAI Agents SDK** — planner Agent → execute sub-steps → synthesizer Agent."""
from ... import registry, oa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    plan = oa.complete(f"List 2-4 sub-questions (one per line) needed to answer: {q}", "You are a planner.")
    subs = [s.strip("-* ").strip() for s in plan.splitlines() if s.strip()][:4]
    findings = "\n".join(f"{s} -> {oa.complete('Answer briefly: ' + s)}" for s in subs)
    return {"answer": oa.complete(f"Using these findings, answer: {q}\n\n{findings}"), "steps": subs}


registry.register("plan-execute", "openai_agents", run)
