"""Plan-and-Execute on the **OpenAI Agents SDK** (`agents`) — a planner Agent emits the sub-queries via
`Runner.run_sync`. Reference implementation — needs `openai-agents` + an OpenAI/Groq key. Mirrors the
run pattern used in agentic-service/app/frameworks/openai_agents.py.
"""
from typing import Callable

from _common import PLAN_PROMPT, merge, parse_steps


def run(query: str, retrieve: Callable[[str], list], synthesize: Callable[[str, list], str],
        model: str = "gpt-4o-mini"):
    from agents import Agent, Runner, set_tracing_disabled
    set_tracing_disabled(True)

    # ---- PLAN ----
    planner = Agent(
        name="Search Planner",
        instructions="Decompose a compound vehicle question into focused sub-queries; reply ONLY with a JSON array.",
        model=model,
    )
    raw = str(Runner.run_sync(planner, PLAN_PROMPT.format(q=query)).final_output)
    steps = parse_steps(raw, query)

    # ---- EXECUTE + SYNTHESIZE ----
    results = merge([retrieve(sq) for sq in steps], cap=12)
    return synthesize(query, results), steps, results
