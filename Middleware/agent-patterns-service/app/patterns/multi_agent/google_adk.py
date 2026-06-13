"""Multi-agent on **Google ADK** — spec/pricing/safety LlmAgents → a lead LlmAgent composes."""
from ... import registry, adk


def run(ctx: dict) -> dict:
    q = ctx["input"]
    notes = [(role, adk.complete(q, f"You are the {role} specialist. {sysp}"))
             for role, sysp in [("spec", "Give spec facts."), ("pricing", "Give pricing/value."), ("safety", "Give safety/reliability.")]]
    body = "\n\n".join(f"{r}: {t}" for r, t in notes)
    return {"answer": adk.complete(f"Compose a buyer's report from:\n\n{body}", "You are the lead advisor."),
            "steps": [r for r, _ in notes]}


registry.register("multi-agent", "google_adk", run)
