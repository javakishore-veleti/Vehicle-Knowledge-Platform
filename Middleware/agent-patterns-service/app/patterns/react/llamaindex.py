"""ReAct on **LlamaIndex** — its native (0.14 workflow) ReActAgent + per-use-case FunctionTools.

Implements the 5 VKP ReAct use cases via ctx['useCase']: the use case's toolset + system prompt come
from `_base.USE_CASES` (shared with every framework cell). Each tool wraps a mock in app/tools.py
(crawl, vehicle_spec, NHTSA, dealer, find_moved); this cell uses LlamaIndex's NATIVE workflow ReActAgent."""
import asyncio

from ... import registry, tools, li
from . import _base


def run(ctx: dict) -> dict:
    from llama_index.core.agent.workflow import ReActAgent
    from llama_index.core.tools import FunctionTool
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
    toolset = [FunctionTool.from_defaults(fn=fn_map[n]) for n in tool_names]

    async def _go():
        agent = ReActAgent(tools=toolset, llm=li.llm(), system_prompt=system)
        return await agent.run(q)

    return {"answer": str(asyncio.run(_go())), "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "llamaindex", run)
