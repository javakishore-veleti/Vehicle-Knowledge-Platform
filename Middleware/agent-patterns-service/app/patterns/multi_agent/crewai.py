"""Multi-agent on **CrewAI** — parallel specialist agents + a lead synthesizer (CrewAI's native strength).

Implements the 5 VKP use cases via ctx['useCase']: each use case's worker roster (from `_base.USE_CASES`,
shared with every framework cell) becomes one agent + async Task per specialist; a lead agent composes
the final answer via Task context. per-brand-workers spins one agent per brand in the query."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, workers, merge_instr = _base.spec_for(ctx.get("useCase"), q)

    agents, tasks = [], []
    for label, prompt in workers:
        a = Agent(role=f"{label} specialist", goal=f"Provide the {label} findings.",
                  backstory=f"A {label} specialist.", llm=crew.crew_llm(), verbose=False)
        agents.append(a)
        tasks.append(Task(description=prompt, expected_output=f"{label} findings.", agent=a, async_execution=True))

    lead = Agent(role="Lead Advisor", goal="Compose the final answer from the specialists.",
                 backstory="The lead advisor.", llm=crew.crew_llm(), verbose=False)
    final = Task(description=f"{merge_instr}\n\nTASK: {q}", expected_output="The final answer.", agent=lead, context=tasks)
    out = Crew(agents=agents + [lead], tasks=tasks + [final], process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(out), "steps": [l for l, _ in workers], "useCase": uc}


registry.register("multi-agent", "crewai", run)
