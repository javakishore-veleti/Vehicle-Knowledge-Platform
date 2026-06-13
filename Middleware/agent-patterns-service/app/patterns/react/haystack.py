"""ReAct on **Haystack** — its native agents.Agent + per-use-case tools.Tool subset.

Implements the 5 VKP ReAct use cases via ctx['useCase']: the toolset + system prompt come from
`_base.USE_CASES` (shared with every framework cell). Each Tool wraps a mock in app/tools.py
(crawl, vehicle_spec, NHTSA, dealer, find_moved); this cell uses Haystack's native Agent loop."""
from ... import registry, tools, hay
from . import _base


def run(ctx: dict) -> dict:
    from haystack.components.agents import Agent
    from haystack.tools import Tool
    from haystack.dataclasses import ChatMessage
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    def vehicle_spec(model: str, field: str = "") -> dict:
        return tools.vehicle_spec(model, field)

    def crawl_page(url: str) -> dict:
        return tools.crawl_page(url)

    def nhtsa_recalls(model: str, year: str = "") -> dict:
        return tools.nhtsa_recalls(model, year)

    def dealer_inventory(model: str, zip_code: str = "") -> dict:
        return tools.dealer_inventory(model, zip_code)

    def find_moved(url: str) -> dict:
        return tools.find_moved(url)

    _S = {"type": "string"}
    specs = {
        "vehicle_spec": (vehicle_spec, "Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model.",
                         {"type": "object", "properties": {"model": _S, "field": _S}, "required": ["model"]}),
        "crawl_page": (crawl_page, "Fetch a web page; returns the outbound links found on it.",
                       {"type": "object", "properties": {"url": _S}, "required": ["url"]}),
        "nhtsa_recalls": (nhtsa_recalls, "Look up NHTSA safety recalls for a vehicle model / year.",
                          {"type": "object", "properties": {"model": _S, "year": _S}, "required": ["model"]}),
        "dealer_inventory": (dealer_inventory, "Find local dealer inventory / stock for a model near a ZIP code.",
                             {"type": "object", "properties": {"model": _S, "zip_code": _S}, "required": ["model"]}),
        "find_moved": (find_moved, "Given a 404 URL, search the site for the page's likely new location.",
                       {"type": "object", "properties": {"url": _S}, "required": ["url"]}),
    }
    toolset = [Tool(name=n, description=specs[n][1], parameters=specs[n][2], function=specs[n][0]) for n in tool_names]

    agent = Agent(chat_generator=hay.chat_generator(), tools=toolset, system_prompt=system)
    res = agent.run(messages=[ChatMessage.from_user(q)])
    return {"answer": res["messages"][-1].text, "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "haystack", run)
