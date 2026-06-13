"""Shared AWS Strands helpers — a Strands Agent over OpenAIModel (synchronous, callable)."""
from . import config


def model():
    from strands.models.openai import OpenAIModel
    return OpenAIModel(client_args={"api_key": config.OPENAI_API_KEY}, model_id=config.OPENAI_MODEL)


def run_agent(system_prompt: str, prompt: str, tools=None) -> str:
    from strands import Agent
    agent = Agent(model=model(), tools=tools or [], system_prompt=system_prompt)
    return str(agent(prompt))


def complete(prompt: str, system_prompt: str = "You are a precise vehicle assistant.") -> str:
    return run_agent(system_prompt, prompt)
