"""Plan-and-Execute on **Haystack** — plan sub-questions → answer each over the doc store → synthesize."""
from ... import registry, hay


def run(ctx: dict) -> dict:
    q = ctx["input"]
    plan = hay.complete(f"List 2-4 sub-questions (one per line) needed to answer: {q}")
    subs = [s.strip("-* ").strip() for s in plan.splitlines() if s.strip()][:4]
    findings = "\n".join(f"{s} -> {hay.complete('Answer briefly: ' + s)}" for s in subs)
    return {"answer": hay.complete(f"Using these findings, answer: {q}\n\n{findings}"), "steps": subs}


registry.register("plan-execute", "haystack", run)
