"""Reflection on **Google ADK** (`google.adk`) — LlmAgents driven through the async InMemoryRunner."""
import asyncio

from ... import config, registry
from . import _base

_APP, _USER = "vkp-patterns", "u"


def _litellm_model() -> str:
    return f"openai/{config.OPENAI_MODEL}" if config.OPENAI_API_KEY else f"groq/{config.GROQ_MODEL}"


def _run_agent(name: str, instruction: str, prompt: str) -> str:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = LlmAgent(model=LiteLlm(model=_litellm_model()), name=name, instruction=instruction)
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


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = _run_agent("writer", _base.DRAFT_SYS, q)
    critique = _run_agent("critic", _base.CRITIC_SYS, _base.CRITIQUE.format(q=q, a=draft))
    answer = _run_agent("writer", _base.DRAFT_SYS, _base.REVISE.format(q=q, a=draft, c=critique))
    return _base.result(draft, critique, answer)


registry.register("reflection", "google-adk", run)
