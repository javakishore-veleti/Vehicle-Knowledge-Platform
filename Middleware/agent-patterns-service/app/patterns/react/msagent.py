"""ReAct on the **Microsoft Agent Framework** — an Agent + per-use-case native @tool subset (the AF loop).

Implements the 5 VKP ReAct use cases via ctx['useCase']: the toolset + system prompt come from
`_base.USE_CASES` (shared with every framework cell). Each @tool wraps a mock in app/tools.py
(crawl, vehicle_spec, NHTSA, dealer, find_moved). Runs in ONE event loop (AF telemetry)."""
from ... import registry, tools as vtools, msa
from . import _base


def run(ctx: dict) -> dict:
    from agent_framework import tool
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    @tool
    def vehicle_spec(model: str, field: str = "") -> dict:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return vtools.vehicle_spec(model, field)

    @tool
    def crawl_page(url: str) -> dict:
        """Fetch a web page; returns the outbound links found on it."""
        return vtools.crawl_page(url)

    @tool
    def nhtsa_recalls(model: str, year: str = "") -> dict:
        """Look up NHTSA safety recalls for a vehicle model / year."""
        return vtools.nhtsa_recalls(model, year)

    @tool
    def dealer_inventory(model: str, zip_code: str = "") -> dict:
        """Find local dealer inventory / stock for a model near a ZIP code."""
        return vtools.dealer_inventory(model, zip_code)

    @tool
    def find_moved(url: str) -> dict:
        """Given a 404 URL, search the site for the page's likely new location."""
        return vtools.find_moved(url)

    fn_map = {"vehicle_spec": vehicle_spec, "crawl_page": crawl_page, "nhtsa_recalls": nhtsa_recalls,
              "dealer_inventory": dealer_inventory, "find_moved": find_moved}
    toolset = [fn_map[n] for n in tool_names]

    async def _go():
        return await msa.acomplete(q, system, tools=toolset)

    return {"answer": msa.run_sync(_go()), "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "msagent", run)
