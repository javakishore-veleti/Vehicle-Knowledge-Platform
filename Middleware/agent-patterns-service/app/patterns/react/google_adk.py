"""ReAct on **Google ADK** — an LlmAgent + a native FunctionTool (the ADK tool-use loop)."""
from ... import registry, tools, adk


def run(ctx: dict) -> dict:
    from google.adk.tools import FunctionTool

    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return tools.vehicle_spec(model, field)

    ans = adk.run_agent("Use the vehicle_spec tool to answer with exact figures.",
                        ctx["input"], tools=[FunctionTool(func=vehicle_spec)])
    return {"answer": ans}


registry.register("react", "google_adk", run)
