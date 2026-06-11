"""Reflection on the **Microsoft Agent Framework** (`agent_framework`) — OpenAIChatClient agents."""
import asyncio
import inspect

from ... import config, registry
from . import _base


def _client():
    from agent_framework.openai import OpenAIChatClient
    if config.OPENAI_API_KEY:
        return OpenAIChatClient(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
    return OpenAIChatClient(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)


def _ask(instructions: str, prompt: str) -> str:
    agent = _client().create_agent(name="agent", instructions=instructions)

    async def _run() -> str:
        result = agent.run(prompt)
        if inspect.isawaitable(result):
            result = await result
        return getattr(result, "text", str(result))

    return asyncio.run(_run())


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = _ask(_base.DRAFT_SYS, q)
    critique = _ask(_base.CRITIC_SYS, _base.CRITIQUE.format(q=q, a=draft))
    answer = _ask(_base.DRAFT_SYS, _base.REVISE.format(q=q, a=draft, c=critique))
    return _base.result(draft, critique, answer)


registry.register("reflection", "msagent", run)
