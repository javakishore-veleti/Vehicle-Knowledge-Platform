"""Parallelization on **CrewAI** — pros/cons/alternatives run async on SEPARATE agents (one executor each),
then a lead synthesizes via context."""
from ... import registry, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]

    def analyst(label):   # a distinct agent per parallel branch (CrewAI can't reuse one executor concurrently)
        return Agent(role=f"{label} Analyst", goal=f"Give the {label.lower()} relevant to the question.",
                     backstory="A vehicle analyst.", llm=crew.crew_llm(), verbose=False)

    lead = Agent(role="Lead", goal="Synthesize a balanced answer.", backstory="The lead advisor.",
                 llm=crew.crew_llm(), verbose=False)
    pros = Task(description=f"List the PROS relevant to: {q}", expected_output="Pros.", agent=analyst("Pros"), async_execution=True)
    cons = Task(description=f"List the CONS relevant to: {q}", expected_output="Cons.", agent=analyst("Cons"), async_execution=True)
    alts = Task(description=f"Suggest ALTERNATIVES relevant to: {q}", expected_output="Alternatives.", agent=analyst("Alternatives"), async_execution=True)
    merge = Task(description=f"Synthesize a balanced answer to '{q}' from the pros, cons and alternatives.",
                 expected_output="Final answer.", agent=lead, context=[pros, cons, alts])
    out = Crew(agents=[pros.agent, cons.agent, alts.agent, lead], tasks=[pros, cons, alts, merge],
               process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(out), "steps": ["pros", "cons", "alternatives"]}


registry.register("chaining", "crewai", run)
