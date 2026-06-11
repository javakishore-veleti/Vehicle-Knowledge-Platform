"""ReWOO on **CrewAI** — a planner agent emits all tool calls blind; Python executes them; a solver answers."""
import json
import re

from ... import registry, tools, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    planner = Agent(role="Planner", goal="Plan the tool calls without executing.",
                    backstory="Plans blind, no observations.", llm=crew.crew_llm(), verbose=False)
    pt = Task(description='Plan the vehicle_spec(model, field) calls needed (no results yet). '
                          'Return ONLY a JSON array of {"model":..,"field":..} objects.\n\n' + q,
              expected_output="A JSON array.", agent=planner)
    raw = str(Crew(agents=[planner], tasks=[pt], process=Process.sequential, verbose=False).kickoff())
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        plan = json.loads(m.group(0)) if m else []
    except Exception:
        plan = []
    evidence = "\n".join(f"{c} -> {tools.vehicle_spec(c.get('model', ''), c.get('field', ''))}" for c in plan[:6])

    solver = Agent(role="Solver", goal="Answer from the evidence.", backstory="Combines evidence into an answer.",
                   llm=crew.crew_llm(), verbose=False)
    st = Task(description=f"Using ONLY this evidence, answer: {q}\n\nEVIDENCE:\n{evidence}",
              expected_output="Final answer.", agent=solver)
    ans = str(Crew(agents=[solver], tasks=[st], process=Process.sequential, verbose=False).kickoff())
    return {"answer": ans, "steps": [str(c) for c in plan]}


registry.register("rewoo", "crewai", run)
