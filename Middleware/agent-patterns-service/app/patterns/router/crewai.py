"""Router on **CrewAI** — a classifier agent picks a category; Python routes to the matching handler
(a specialist agent for LLM routes, or a fixed routing string for static routes).

Implements the 5 VKP router use cases via ctx['useCase']. The classify prompts + route tables come
from `_base.USE_CASES` (shared with every framework cell); this cell shows ONLY the CrewAI mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    clf = Agent(role="Query Router", goal="Classify the query into exactly one category.",
                backstory="Routes queries to the right specialist.", llm=crew.crew_llm(), verbose=False)
    ct = Task(description=_base.classify_prompt(spec, q), expected_output="One word.", agent=clf)
    raw = str(Crew(agents=[clf], tasks=[ct], process=Process.sequential, verbose=False).kickoff())
    route = _base.pick_route(spec, raw)

    h = spec["routes"][route]
    if h[0] == "llm":
        system, prefix = h[1], h[2]
        specialist = Agent(role=f"{route} specialist", goal=system, backstory=system,
                           llm=crew.crew_llm(), verbose=False)
        at = Task(description=q, expected_output="A strong answer.", agent=specialist)
        ans = prefix + str(Crew(agents=[specialist], tasks=[at], process=Process.sequential, verbose=False).kickoff())
    else:
        ans = _base.render_static(h, q)

    return {"answer": ans, "steps": [f"routed -> {route}"], "useCase": uc}


registry.register("router", "crewai", run)
