"""The 'google-adk' framework — Google Agent Development Kit (https://google.github.io/adk-docs).

ADK runs an LlmAgent through a Runner + session, streaming events. We point its model at OpenAI/Groq
via the LiteLlm wrapper (LiteLLM reads OPENAI_API_KEY / GROQ_API_KEY from env), so no Gemini key is
needed. The Runner is async, so the sync search() drives it with asyncio.run().
"""
import asyncio

from .. import config, registry
from ._base import INSTRUCTIONS, run_search

_APP = "vkp"
_USER = "vkp-user"


def _litellm_model() -> str:
    """LiteLLM model id; LiteLLM picks the matching *_API_KEY from the environment."""
    if config.OPENAI_API_KEY:
        return f"openai/{config.OPENAI_MODEL}"
    if config.GROQ_API_KEY:
        return f"groq/{config.GROQ_MODEL}"
    raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")


def _answer(query: str, context: str) -> str:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = LlmAgent(model=LiteLlm(model=_litellm_model()), name="vehicle_search", instruction=INSTRUCTIONS)
    runner = InMemoryRunner(agent=agent, app_name=_APP)
    prompt = f"Question: {query}\n\nSOURCES:\n{context}"

    async def _run() -> str:
        session = await runner.session_service.create_session(app_name=_APP, user_id=_USER)
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        final = ""
        async for event in runner.run_async(user_id=_USER, session_id=session.id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                final = event.content.parts[0].text or final
        return final

    return asyncio.run(_run())


def search(ctx: dict) -> dict:
    model = config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL
    return run_search("google-adk", "Google ADK", model, _answer, ctx)


registry.register("google-adk", "search", search)
