"""ReAct on **CrewAI** — an agent equipped with the use case's tool(s) reasons + calls them (CrewAI's
agent loop).

Implements the 5 VKP ReAct use cases via ctx['useCase']. The toolset/system config comes from
`_base.USE_CASES` (shared with every framework cell): each use case gets a different subset of the
mock tools (crawl, vehicle_spec, NHTSA, dealer, find_moved) + a tailored system prompt. This cell shows
ONLY the CrewAI mechanics."""
from ... import registry, tools, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    q = ctx["input"]
    uc, tool_names, system = _base.spec_for(ctx.get("useCase"))

    @tool("vehicle_spec")
    def vehicle_spec(model: str, field: str = "") -> str:
        """Look up specs (type, range, mpg, towing, price, seats) for a known vehicle model."""
        return str(tools.vehicle_spec(model, field))

    @tool("crawl_page")
    def crawl_page(url: str) -> str:
        """Fetch a web page; returns the outbound links found on it."""
        return str(tools.crawl_page(url))

    @tool("nhtsa_recalls")
    def nhtsa_recalls(model: str, year: str = "") -> str:
        """Look up NHTSA safety recalls for a vehicle model / year."""
        return str(tools.nhtsa_recalls(model, year))

    @tool("dealer_inventory")
    def dealer_inventory(model: str, zip_code: str = "") -> str:
        """Find local dealer inventory / stock for a model near a ZIP code."""
        return str(tools.dealer_inventory(model, zip_code))

    @tool("find_moved")
    def find_moved(url: str) -> str:
        """Given a 404 URL, search the site for the page's likely new location."""
        return str(tools.find_moved(url))

    tool_map = {"vehicle_spec": vehicle_spec, "crawl_page": crawl_page, "nhtsa_recalls": nhtsa_recalls,
                "dealer_inventory": dealer_inventory, "find_moved": find_moved}
    toolset = [tool_map[n] for n in tool_names]

    agent = Agent(role="Vehicle ReAct Agent", goal=system, backstory=system,
                  tools=toolset, llm=crew.crew_llm(), verbose=False)
    task = Task(description=q, expected_output="A grounded answer from the tool results.", agent=agent)
    out = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(out), "steps": [f"toolset: {', '.join(tool_names)}"], "useCase": uc}


registry.register("react", "crewai", run)
