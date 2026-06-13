"""ReAct on the **OpenAI Agents SDK** — a native Agent + @function_tool + Runner (the agent loop)."""
from ... import registry, tools, oa


def run(ctx: dict) -> dict:
    from agents import Agent, Runner, function_tool

    @function_tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return tools.vehicle_spec(model, field)

    oa._ensure_key()
    agent = Agent(name="vkp-react", model="gpt-4o-mini",
                  instructions="Use the vehicle_spec tool to answer vehicle questions with exact figures.",
                  tools=[vehicle_spec])
    return {"answer": Runner.run_sync(agent, ctx["input"]).final_output}


registry.register("react", "openai_agents", run)
