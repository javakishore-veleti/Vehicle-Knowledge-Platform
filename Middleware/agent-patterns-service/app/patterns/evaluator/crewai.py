"""Evaluator-optimizer on **CrewAI** — writer drafts, judge scores+critiques, writer revises (one round)."""
from ... import registry, crew


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    writer = Agent(role="Writer", goal="Answer accurately.", backstory="A vehicle expert.", llm=crew.crew_llm(), verbose=False)
    judge = Agent(role="Judge", goal="Score and critique answers.", backstory="A strict evaluator.", llm=crew.crew_llm(), verbose=False)
    d = Task(description=f"Answer: {q}", expected_output="An answer.", agent=writer)
    j = Task(description="Rate the answer 1-10 and give one-line feedback on accuracy/completeness.",
             expected_output="Score + feedback.", agent=judge, context=[d])
    r = Task(description="Revise the answer using the judge's feedback. Return only the improved answer.",
             expected_output="Improved answer.", agent=writer, context=[d, j])
    out = Crew(agents=[writer, judge], tasks=[d, j, r], process=Process.sequential, verbose=False).kickoff()
    return {"answer": str(r.output or out), "critique": str(j.output)}


registry.register("evaluator-optimizer", "crewai", run)
