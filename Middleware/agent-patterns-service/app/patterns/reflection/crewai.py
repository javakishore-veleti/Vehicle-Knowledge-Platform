"""Reflection on **CrewAI** — a Writer agent drafts, a Critic agent critiques, the Writer revises
(sequential crew; each task feeds the next via `context`)."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    writer = Agent(role="Automotive Writer", goal="Answer vehicle questions accurately and concisely.",
                   backstory="A precise automotive expert.", llm=crew.crew_llm(), verbose=False)
    critic = Agent(role="Fact Critic", goal="Find inaccuracies and gaps in automotive answers.",
                   backstory="A meticulous reviewer of vehicle claims.", llm=crew.crew_llm(), verbose=False)
    draft_t = Task(description=f"Answer this vehicle question concisely and factually: {q}",
                   expected_output="A concise, factual answer.", agent=writer)
    critique_t = Task(description="Critique the answer for accuracy/completeness; list concrete fixes.",
                      expected_output="A short bullet list of fixes.", agent=critic, context=[draft_t])
    revise_t = Task(description="Revise the answer using the critique. Return only the improved answer.",
                    expected_output="The improved answer.", agent=writer, context=[draft_t, critique_t])
    final = Crew(agents=[writer, critic], tasks=[draft_t, critique_t, revise_t],
                 process=Process.sequential, verbose=False).kickoff()
    return _base.result(str(draft_t.output), str(critique_t.output), str(revise_t.output or final))


registry.register("reflection", "crewai", run)
