"""Plan-and-Execute on **Google ADK** (`google.adk`) — a planner LlmAgent is driven through the async
InMemoryRunner to emit the sub-queries. Reference implementation — needs `google-adk` + a key (model via
LiteLlm, e.g. openai/gpt-4o-mini). Mirrors agentic-service/app/frameworks/google_adk.py.
"""
import asyncio
from typing import Callable

from _common import PLAN_PROMPT, merge, parse_steps

_APP, _USER = "vkp-plan-execute", "u"


def _plan_text(prompt: str, model: str) -> str:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = LlmAgent(model=LiteLlm(model=model), name="search_planner",
                     instruction="Decompose a vehicle question into a JSON array of focused sub-queries.")
    runner = InMemoryRunner(agent=agent, app_name=_APP)

    async def _run() -> str:
        session = await runner.session_service.create_session(app_name=_APP, user_id=_USER)
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        final = ""
        async for event in runner.run_async(user_id=_USER, session_id=session.id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                final = event.content.parts[0].text or final
        return final

    return asyncio.run(_run())


def run(query: str, retrieve: Callable[[str], list], synthesize: Callable[[str, list], str],
        model: str = "openai/gpt-4o-mini"):
    steps = parse_steps(_plan_text(PLAN_PROMPT.format(q=query), model), query)
    results = merge([retrieve(sq) for sq in steps], cap=12)
    return synthesize(query, results), steps, results
