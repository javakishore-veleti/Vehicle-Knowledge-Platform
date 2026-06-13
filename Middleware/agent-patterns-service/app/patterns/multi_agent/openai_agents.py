"""Multi-agent on the **OpenAI Agents SDK** — spec/pricing/safety specialist Agents → a lead Agent composes."""
from ... import registry, oa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    notes = [(role, oa.complete(q, f"You are the {role} specialist. {sysp}"))
             for role, sysp in [("spec", "Give spec facts."), ("pricing", "Give pricing/value."), ("safety", "Give safety/reliability.")]]
    body = "\n\n".join(f"{r}: {t}" for r, t in notes)
    return {"answer": oa.complete(f"Compose a buyer's report from:\n\n{body}", "You are the lead advisor."),
            "steps": [r for r, _ in notes]}


registry.register("multi-agent", "openai_agents", run)
