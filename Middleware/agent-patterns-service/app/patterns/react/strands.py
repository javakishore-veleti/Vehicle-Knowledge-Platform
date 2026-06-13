"""ReAct on **AWS Strands** — a Strands Agent + a native @tool (the Strands agent loop)."""
from ... import registry, tools as vtools, sa


def run(ctx: dict) -> dict:
    from strands import tool

    @tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return vtools.vehicle_spec(model, field)

    ans = sa.run_agent("Use the vehicle_spec tool to answer with exact figures.", ctx["input"], tools=[vehicle_spec])
    return {"answer": ans}


registry.register("react", "strands", run)
