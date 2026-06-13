"""Multi-agent on **LlamaIndex** — spec/pricing/safety LLM specialists → a lead composes."""
from ... import registry, li


def run(ctx: dict) -> dict:
    q = ctx["input"]
    notes = [(role, li.complete(f"You are the {role} specialist. {sysp}\n\n{q}"))
             for role, sysp in [("spec", "Give spec facts."), ("pricing", "Give pricing/value."), ("safety", "Give safety/reliability.")]]
    body = "\n\n".join(f"{r}: {t}" for r, t in notes)
    return {"answer": li.complete(f"As the lead advisor, compose a buyer's report from:\n\n{body}"),
            "steps": [r for r, _ in notes]}


registry.register("multi-agent", "llamaindex", run)
