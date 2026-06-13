"""ReAct on **LlamaIndex** — its native (0.14 workflow) ReActAgent + a FunctionTool (reason→act loop)."""
import asyncio

from ... import registry, tools, li


def run(ctx: dict) -> dict:
    from llama_index.core.agent.workflow import ReActAgent
    from llama_index.core.tools import FunctionTool

    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return tools.vehicle_spec(model, field)

    async def _go():
        agent = ReActAgent(tools=[FunctionTool.from_defaults(fn=vehicle_spec)], llm=li.llm())
        return await agent.run(ctx["input"])

    return {"answer": str(asyncio.run(_go()))}


registry.register("react", "llamaindex", run)
