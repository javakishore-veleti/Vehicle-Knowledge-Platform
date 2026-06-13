"""Shared Google ADK helpers — an LlmAgent (via LiteLLM→OpenAI) run through InMemoryRunner."""
import asyncio

from . import config


def run_agent(instruction: str, prompt: str, tools=None) -> str:
    from google.adk.agents import LlmAgent
    from google.adk.runners import InMemoryRunner
    from google.adk.models.lite_llm import LiteLlm
    from google.genai import types

    agent = LlmAgent(name="vkp", model=LiteLlm(model="openai/" + config.OPENAI_MODEL),
                     instruction=instruction, tools=tools or [])
    runner = InMemoryRunner(agent=agent, app_name="vkp")

    async def go():
        s = await runner.session_service.create_session(app_name="vkp", user_id="u1")
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        final = ""
        async for ev in runner.run_async(user_id="u1", session_id=s.id, new_message=msg):
            if ev.is_final_response() and ev.content and ev.content.parts:
                final = ev.content.parts[0].text
        return final

    return asyncio.run(go())


def complete(prompt: str, instruction: str = "You are a precise vehicle assistant.") -> str:
    return run_agent(instruction, prompt)
