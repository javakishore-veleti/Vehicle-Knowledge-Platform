"""ReWOO on **CrewAI** — a blind plan is executed with NO LLM in the loop, then a Solver agent answers
from the collected evidence (nightly-price-refresh stays fully LLM-free).

Implements the 5 VKP use cases via ctx['useCase']. The plan, worker, and solver spec come from
`_base.USE_CASES` (shared with every framework cell); this cell shows ONLY the CrewAI mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    plan = spec["plan"]
    evidence = spec["worker"](plan)        # blind execute — NO LLM in the loop
    solver_kind, solver_builder = spec["solver"]

    if solver_kind == "llm":
        solver = Agent(role="Solver", goal="Answer from the blind-collected evidence.",
                       backstory="Combines pre-collected tool evidence into a single answer.",
                       llm=crew.crew_llm(), verbose=False)
        st = Task(description=solver_builder(q, evidence), expected_output="Final answer.", agent=solver)
        ans = str(Crew(agents=[solver], tasks=[st], process=Process.sequential, verbose=False).kickoff())
    else:
        ans = solver_builder(q, evidence)  # LLM-free solver

    return {"answer": ans, "steps": [str(c) for c in plan], "useCase": uc}


registry.register("rewoo", "crewai", run)
