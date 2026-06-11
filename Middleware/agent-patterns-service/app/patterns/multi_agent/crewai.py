"""Multi-agent on **CrewAI** — spec/pricing/safety specialists + a lead synthesizer (CrewAI's native strength)."""
from ... import registry, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]

    def sp(role, goal):
        return Agent(role=role, goal=goal, backstory=role, llm=crew.crew_llm(), verbose=False)

    spec = sp("Specs Specialist", "Provide spec facts.")
    price = sp("Pricing Specialist", "Provide pricing/value facts.")
    safety = sp("Safety Specialist", "Provide safety/reliability facts.")
    lead = sp("Lead Advisor", "Compose the final answer from the specialists.")

    t1 = Task(description=f"Spec facts for: {q}", expected_output="Specs.", agent=spec, async_execution=True)
    t2 = Task(description=f"Pricing/value for: {q}", expected_output="Pricing.", agent=price, async_execution=True)
    t3 = Task(description=f"Safety/reliability for: {q}", expected_output="Safety.", agent=safety, async_execution=True)
    final = Task(description=f"Compose a final answer to '{q}' from your specialists.",
                 expected_output="Final answer.", agent=lead, context=[t1, t2, t3])
    out = Crew(agents=[spec, price, safety, lead], tasks=[t1, t2, t3, final], process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(out), "steps": ["spec", "pricing", "safety"]}


registry.register("multi-agent", "crewai", run)
