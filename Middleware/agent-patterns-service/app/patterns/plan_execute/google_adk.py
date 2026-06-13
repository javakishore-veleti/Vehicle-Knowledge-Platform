"""Plan-and-Execute on **Google ADK** — planner LlmAgent → execute sub-steps → synthesizer LlmAgent."""
from ... import registry, adk


def run(ctx: dict) -> dict:
    q = ctx["input"]
    plan = adk.complete(f"List 2-4 sub-questions (one per line) needed to answer: {q}", "You are a planner.")
    subs = [s.strip("-* ").strip() for s in plan.splitlines() if s.strip()][:4]
    findings = "\n".join(f"{s} -> {adk.complete('Answer briefly: ' + s)}" for s in subs)
    return {"answer": adk.complete(f"Using these findings, answer: {q}\n\n{findings}"), "steps": subs}


registry.register("plan-execute", "google_adk", run)
