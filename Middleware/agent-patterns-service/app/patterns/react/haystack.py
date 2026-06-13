"""ReAct on **Haystack** — its native agents.Agent + a tools.Tool (chat-generator loop)."""
from ... import registry, tools, hay


def run(ctx: dict) -> dict:
    from haystack.components.agents import Agent
    from haystack.tools import Tool
    from haystack.dataclasses import ChatMessage

    def vehicle_spec(model: str, field: str = "") -> dict:
        return tools.vehicle_spec(model, field)

    tool = Tool(name="vehicle_spec", description="Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model.",
                parameters={"type": "object", "properties": {"model": {"type": "string"}, "field": {"type": "string"}}, "required": ["model"]},
                function=vehicle_spec)
    agent = Agent(chat_generator=hay.chat_generator(), tools=[tool])
    res = agent.run(messages=[ChatMessage.from_user(ctx["input"])])
    return {"answer": res["messages"][-1].text}


registry.register("react", "haystack", run)
