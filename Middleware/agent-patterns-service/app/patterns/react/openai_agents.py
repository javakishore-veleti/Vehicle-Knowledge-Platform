"""ReAct on the **OpenAI Agents SDK** — a native Agent + per-use-case @function_tool subset + Runner.

Implements the 5 VKP ReAct use cases via ctx['useCase']: the toolset + system prompt come from
`_base.USE_CASES` (shared with every framework cell). Each tool wraps a mock in app/tools.py
(crawl, vehicle_spec, NHTSA, dealer, find_moved); this cell uses the native Agent loop."""
from ... import registry, tools, oa
from . import _base


def run(ctx: dict) -> dict:
    from agents import Agent, Runner, function_tool
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    @function_tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return tools.vehicle_spec(model, field)

    @function_tool
    def crawl_page(url: str) -> dict:
        """Fetch a web page; returns the outbound links found on it."""
        return tools.crawl_page(url)

    @function_tool
    def nhtsa_recalls(model: str, year: str = "") -> dict:
        """Look up NHTSA safety recalls for a vehicle model / year."""
        return tools.nhtsa_recalls(model, year)

    @function_tool
    def dealer_inventory(model: str, zip_code: str = "") -> dict:
        """Find local dealer inventory / stock for a model near a ZIP code."""
        return tools.dealer_inventory(model, zip_code)

    @function_tool
    def find_moved(url: str) -> dict:
        """Given a 404 URL, search the site for the page's likely new location."""
        return tools.find_moved(url)

    fn_map = {"vehicle_spec": vehicle_spec, "crawl_page": crawl_page, "nhtsa_recalls": nhtsa_recalls,
              "dealer_inventory": dealer_inventory, "find_moved": find_moved}
    toolset = [fn_map[n] for n in tool_names]

    oa._ensure_key()
    agent = Agent(name="vkp-react", model="gpt-4o-mini", instructions=system, tools=toolset)
    ans = Runner.run_sync(agent, q).final_output
    return {"answer": ans, "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "openai_agents", run)
