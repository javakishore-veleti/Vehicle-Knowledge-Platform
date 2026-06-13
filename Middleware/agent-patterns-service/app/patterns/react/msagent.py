"""ReAct on the **Microsoft Agent Framework** — an Agent + a native @tool (the AF tool loop)."""
from ... import registry, tools as vtools, msa


def run(ctx: dict) -> dict:
    from agent_framework import tool

    @tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return vtools.vehicle_spec(model, field)

    async def _go():
        return await msa.acomplete(ctx["input"], "Use the vehicle_spec tool to answer with exact figures.", tools=[vehicle_spec])

    return {"answer": msa.run_sync(_go())}


registry.register("react", "msagent", run)
