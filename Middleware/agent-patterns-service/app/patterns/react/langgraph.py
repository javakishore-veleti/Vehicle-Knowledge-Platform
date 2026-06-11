"""ReAct on **LangGraph** — `create_react_agent` + a vehicle_spec tool: reason -> act(tool) -> observe -> answer."""
from ... import registry, tools, config


def _model():
    from langchain_openai import ChatOpenAI
    if config.OPENAI_API_KEY:
        return ChatOpenAI(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY, temperature=0.2)
    return ChatOpenAI(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                      base_url=config.GROQ_BASE_URL, temperature=0.2)


def run(ctx: dict) -> dict:
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool as lc_tool

    @lc_tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, electric_range_mi, mpg, towing_lb, base_price_usd, seats) for a known model."""
        return tools.vehicle_spec(model, field)

    agent = create_react_agent(_model(), [vehicle_spec])
    out = agent.invoke({"messages": [
        ("system", "You are a vehicle expert. Use the vehicle_spec tool for any spec/price/range/towing fact."),
        ("user", ctx["input"])]})
    msgs = out["messages"]
    steps = [f"tool: vehicle_spec({c.get('args')})"
             for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
    return {"answer": msgs[-1].content, "steps": steps}


registry.register("react", "langgraph", run)
