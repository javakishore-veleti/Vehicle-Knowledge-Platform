"""Evaluator-optimizer on **CrewAI** — an Optimizer agent generates, then refines once if the
score gate is not met.

Implements the 5 VKP use cases via ctx['useCase']. The use-case prompts + eval strategies come from
`_base.USE_CASES` (shared with every framework cell): the CrewAI Agent does the generate/refine
(the optimize side), while the score signal is the use case's own (LLM judge, REAL corpus retrieval
for query-rewriter, or single-pass for embedding selection)."""
from ... import registry, crew
from . import _base


def run(ctx: dict) -> dict:
    from crewai import Agent, Task, Crew, Process
    q = ctx["input"]
    uc, spec = _base.spec_for(ctx.get("useCase"))

    writer = Agent(role="Content Optimizer", goal="Produce and refine high-quality, accurate vehicle content.",
                   backstory="A meticulous automotive content optimizer.", llm=crew.crew_llm(), verbose=False)

    first_prompt, _system = spec["first"](q)
    draft_t = Task(description=first_prompt, expected_output="The generated output.", agent=writer)
    Crew(agents=[writer], tasks=[draft_t], process=Process.sequential, verbose=False).kickoff()
    draft = str(draft_t.output)

    score, feedback = _base.evaluate(spec, q, draft)
    refined = score < 8 and spec.get("refinable")
    if not refined:
        answer = draft
    else:
        revise_t = Task(description=spec["refine"](q, draft, feedback), expected_output="The improved output.", agent=writer)
        Crew(agents=[writer], tasks=[revise_t], process=Process.sequential, verbose=False).kickoff()
        answer = str(revise_t.output)

    return {"answer": answer, "critique": feedback, "useCase": uc,
            "steps": [f"score={score}", f"refined={'yes' if refined else 'no'}"]}


registry.register("evaluator-optimizer", "crewai", run)
