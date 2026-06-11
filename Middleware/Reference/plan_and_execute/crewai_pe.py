"""Plan-and-Execute on **CrewAI** — a planner agent emits the sub-queries, then (after fan-out
retrieval) a synthesizer agent writes the comparison. Reference implementation — needs `crewai` + an LLM.

CrewAI models work as agents + tasks. Here the planning and synthesis are agent tasks; the deterministic
fan-out retrieval happens between them in plain Python (CrewAI is great at the reasoning steps, not at
issuing N identical DB queries).
"""
from typing import Callable

from _common import PLAN_PROMPT, merge, parse_steps


def run(query: str, retrieve: Callable[[str], list], synthesize: Callable[[str, list], str], llm=None):
    from crewai import Agent, Task, Crew, Process

    # ---- PLAN: a planner agent decomposes the question into sub-queries ----
    planner = Agent(
        role="Search Planner",
        goal="Decompose a compound vehicle question into focused sub-queries.",
        backstory="You break complex comparison questions into atomic, searchable parts.",
        llm=llm, verbose=False,
    )
    plan_task = Task(
        description=PLAN_PROMPT.format(q=query),
        expected_output="A JSON array of 2-6 sub-query strings.",
        agent=planner,
    )
    raw = str(Crew(agents=[planner], tasks=[plan_task], process=Process.sequential, verbose=False).kickoff())
    steps = parse_steps(raw, query)

    # ---- EXECUTE: fan out one retrieval per sub-query, merge + dedup ----
    results = merge([retrieve(sq) for sq in steps], cap=12)

    # ---- SYNTHESIZE: hand the merged sources to a synthesizer (reuse the shared synthesize) ----
    answer = synthesize(query, results)
    return answer, steps, results
