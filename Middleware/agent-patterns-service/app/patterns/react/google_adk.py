"""ReAct on **Google ADK** — an LlmAgent + per-use-case native FunctionTool subset (the ADK tool loop).

Implements the 5 VKP ReAct use cases via ctx['useCase']: the toolset + system prompt come from
`_base.USE_CASES` (shared with every framework cell). Each FunctionTool wraps a mock in app/tools.py
(crawl, vehicle_spec, NHTSA, dealer, find_moved); this cell uses the native ADK tool-use loop."""
from ... import registry, tools, adk
from . import _base


def run(ctx: dict) -> dict:
    from google.adk.tools import FunctionTool
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return tools.vehicle_spec(model, field)

    def crawl_page(url: str) -> dict:
        """Fetch a web page; returns the outbound links found on it."""
        return tools.crawl_page(url)

    def nhtsa_recalls(model: str, year: str = "") -> dict:
        """Look up NHTSA safety recalls for a vehicle model / year."""
        return tools.nhtsa_recalls(model, year)

    def dealer_inventory(model: str, zip_code: str = "") -> dict:
        """Find local dealer inventory / stock for a model near a ZIP code."""
        return tools.dealer_inventory(model, zip_code)

    def find_moved(url: str) -> dict:
        """Given a 404 URL, search the site for the page's likely new location."""
        return tools.find_moved(url)

    fn_map = {"vehicle_spec": vehicle_spec, "crawl_page": crawl_page, "nhtsa_recalls": nhtsa_recalls,
              "dealer_inventory": dealer_inventory, "find_moved": find_moved}
    toolset = [FunctionTool(func=fn_map[n]) for n in tool_names]

    ans = adk.run_agent(system, q, tools=toolset)
    return {"answer": ans, "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "google_adk", run)
