"""Shared Microsoft Agent Framework helpers — an OpenAIChatClient agent.

NOTE: agent_framework's telemetry uses a ContextVar token that breaks if `asyncio.run`
is called more than once per thread. So each cell runs ALL its `acomplete` calls inside a
single `run_sync(_go())` event loop (sequential awaits share one context — stable).
"""
import asyncio

from . import config


def client():
    from agent_framework.openai import OpenAIChatClient
    return OpenAIChatClient(api_key=config.OPENAI_API_KEY, model=config.OPENAI_MODEL)


async def acomplete(prompt: str, instructions: str = "You are a precise vehicle assistant.", tools=None) -> str:
    agent = client().as_agent(instructions=instructions, tools=tools or None)
    return (await agent.run(prompt)).text


def run_sync(coro):
    return asyncio.run(coro)
