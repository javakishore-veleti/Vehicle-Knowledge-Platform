"""ReAct on **LangGraph** — create_react_agent + tools (reason → act → observe loop).

Implements the 5 VKP ReAct use cases via ctx['useCase'] (default = single-model-deep-dive): each gives the
agent the relevant tool(s) + a use-case system prompt. The toolset/system config lives in `_base.USE_CASES`
(shared with every framework cell); tool implementations are mocks in app/tools.py (crawl, NHTSA, dealer)."""
from ... import registry, tools, config
from . import _base


def _model():
    from langchain_openai import ChatOpenAI
    if config.OPENAI_API_KEY:
        return ChatOpenAI(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY, temperature=0.2)
    return ChatOpenAI(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                      base_url=config.GROQ_BASE_URL, temperature=0.2)


def run(ctx: dict) -> dict:
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool as lc_tool
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    @lc_tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, electric_range_mi, mpg, towing_lb, base_price_usd, seats) for a known model."""
        return tools.vehicle_spec(model, field)

    @lc_tool
    def crawl_page(url: str) -> dict:
        """Fetch a web page; returns the outbound links found on it."""
        return tools.crawl_page(url)

    @lc_tool
    def nhtsa_recalls(model: str, year: str = "") -> dict:
        """Look up NHTSA safety recalls for a vehicle model / year."""
        return tools.nhtsa_recalls(model, year)

    @lc_tool
    def dealer_inventory(model: str, zip_code: str = "") -> dict:
        """Find local dealer inventory / stock for a model near a ZIP code."""
        return tools.dealer_inventory(model, zip_code)

    @lc_tool
    def find_moved(url: str) -> dict:
        """Given a 404 URL, search the site for the page's likely new location."""
        return tools.find_moved(url)

    tool_map = {"vehicle_spec": vehicle_spec, "crawl_page": crawl_page, "nhtsa_recalls": nhtsa_recalls,
                "dealer_inventory": dealer_inventory, "find_moved": find_moved}
    toolset = [tool_map[n] for n in tool_names]
    agent = create_react_agent(_model(), toolset)
    out = agent.invoke({"messages": [("system", system), ("user", q)]})
    msgs = out["messages"]
    steps = [f"tool: {c.get('name')}({c.get('args')})"
             for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
    return {"answer": msgs[-1].content, "steps": steps, "useCase": uc}


registry.register("react", "langgraph", run)
