"""Reflection on **CrewAI** — a Writer agent drafts, a Critic agent critiques, the Writer revises
(sequential crew; each task feeds the next via `context`).

Implements the 5 VKP Reflection use cases via ctx['useCase']. The use-case instructions come from
`_base.USE_CASES` (shared with every framework cell); CrewAI wires the draft/critique through Task
`context`, so this cell shows ONLY the crew mechanics."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    writer = Agent(role="Automotive Writer", goal="Produce accurate, concise vehicle content.",
                   backstory="A precise automotive expert.", llm=crew.crew_llm(), verbose=False)
    critic = Agent(role="Fact Critic", goal="Find inaccuracies and gaps in automotive content.",
                   backstory="A meticulous reviewer of vehicle claims.", llm=crew.crew_llm(), verbose=False)
    draft_t = Task(description=spec["generate"].format(q=q),
                   expected_output="The drafted output.", agent=writer)
    critique_t = Task(description=spec["critique"] + " (Review the previous task's output.)",
                      expected_output="A short bullet list of concrete fixes.", agent=critic, context=[draft_t])
    revise_t = Task(description=spec["revise"] + " (Apply the critique to the draft.)",
                    expected_output="The final improved output.", agent=writer, context=[draft_t, critique_t])
    final = Crew(agents=[writer, critic], tasks=[draft_t, critique_t, revise_t],
                 process=Process.sequential, verbose=False).kickoff()
    return {**_base.result(str(draft_t.output), str(critique_t.output), str(revise_t.output or final)), "useCase": uc}


registry.register("reflection", "crewai", run)
