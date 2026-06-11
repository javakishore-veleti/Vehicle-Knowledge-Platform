"""Plan-and-Execute on the **Microsoft Agent Framework** (`agent_framework`) — an OpenAIChatClient is
turned into a planner agent that emits the sub-queries. Reference implementation — needs `agent-framework`
+ an OpenAI/Groq key. Mirrors agentic-service/app/frameworks/msagent.py (run inside one asyncio context).
"""
import asyncio
import inspect
from typing import Callable, Optional

from _common import PLAN_PROMPT, merge, parse_steps


def _plan_text(prompt: str, model: str, api_key: Optional[str]) -> str:
    from agent_framework.openai import OpenAIChatClient

    client = OpenAIChatClient(model=model, api_key=api_key)
    agent = client.create_agent(
        name="search_planner",
        instructions="Decompose a vehicle question into a JSON array of focused sub-queries.",
    )

    async def _run() -> str:
        result = agent.run(prompt)
        if inspect.isawaitable(result):
            result = await result
        return getattr(result, "text", str(result))

    return asyncio.run(_run())


def run(query: str, retrieve: Callable[[str], list], synthesize: Callable[[str, list], str],
        model: str = "gpt-4o-mini", api_key: Optional[str] = None):
    steps = parse_steps(_plan_text(PLAN_PROMPT.format(q=query), model, api_key), query)
    results = merge([retrieve(sq) for sq in steps], cap=12)
    return synthesize(query, results), steps, results
