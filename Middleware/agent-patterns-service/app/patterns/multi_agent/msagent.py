"""Multi-agent on the **Microsoft Agent Framework** — spec/pricing/safety Agents → a lead Agent composes."""
from ... import registry, msa


def run(ctx: dict) -> dict:
    q = ctx["input"]
    roles = [("spec", "Give spec facts."), ("pricing", "Give pricing/value."), ("safety", "Give safety/reliability.")]

    async def _go():
        notes = [(role, await msa.acomplete(q, f"You are the {role} specialist. {sysp}")) for role, sysp in roles]
        body = "\n\n".join(f"{r}: {t}" for r, t in notes)
        return await msa.acomplete(f"Compose a buyer's report from:\n\n{body}", "You are the lead advisor."), [r for r, _ in notes]

    ans, steps = msa.run_sync(_go())
    return {"answer": ans, "steps": steps}


registry.register("multi-agent", "msagent", run)
