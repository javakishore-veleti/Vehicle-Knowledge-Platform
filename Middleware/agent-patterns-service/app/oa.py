"""Shared OpenAI Agents SDK helpers — a default Agent + Runner over gpt-4o-mini."""
from . import config


def _ensure_key():
    if config.OPENAI_API_KEY:
        from agents import set_default_openai_key
        set_default_openai_key(config.OPENAI_API_KEY)


def run_agent(instructions: str, prompt: str, tools=None) -> str:
    from agents import Agent, Runner
    _ensure_key()
    a = Agent(name="vkp", instructions=instructions, model=config.OPENAI_MODEL, tools=tools or [])
    return Runner.run_sync(a, prompt).final_output


def complete(prompt: str, instructions: str = "You are a precise vehicle assistant.") -> str:
    return run_agent(instructions, prompt)
