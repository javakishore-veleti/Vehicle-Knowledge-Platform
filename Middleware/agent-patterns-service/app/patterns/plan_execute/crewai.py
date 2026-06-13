"""Plan-and-Execute on **CrewAI** — a planner agent emits the plan (for LLM-planned use cases),
Python executes it deterministically, a synthesizer agent writes the final answer.

Implements the 5 VKP use cases via ctx['useCase']. The plan/execute/synthesize specs come from
`_base.USE_CASES` (shared with every framework cell): execute gathers evidence via corpus retrieval
or the vehicle_spec tool (no LLM in the execute step). This cell shows ONLY the CrewAI mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"), q)

    if spec["plan"][0] == "llm":
        n = spec["plan"][1]
        planner = Agent(role="Planner", goal="Decompose a question into focused sub-queries.",
                        backstory="Breaks complex questions into searchable parts.", llm=crew.crew_llm(), verbose=False)
        pt = Task(description=f"Decompose into {n} sub-queries. Return ONLY a JSON array of strings.\n\n{q}",
                  expected_output="A JSON array of strings.", agent=planner)
        raw = str(Crew(agents=[planner], tasks=[pt], process=Process.sequential, verbose=False).kickoff())
        steps = _base.parse_steps(raw, q, n)
    else:
        steps = list(spec["plan"][1])

    evidence = spec["exec"](q, steps)        # deterministic execute — no LLM in the loop

    synth = Agent(role="Synthesizer", goal="Write the final, grounded answer from the evidence.",
                  backstory="Composes the final answer.", llm=crew.crew_llm(), verbose=False)
    st = Task(description=_base.synth_prompt(spec["instr"], q, evidence), expected_output="Final answer.", agent=synth)
    ans = str(Crew(agents=[synth], tasks=[st], process=Process.sequential, verbose=False).kickoff())
    return {"answer": ans, "steps": steps, "useCase": uc}


registry.register("plan-execute", "crewai", run)
