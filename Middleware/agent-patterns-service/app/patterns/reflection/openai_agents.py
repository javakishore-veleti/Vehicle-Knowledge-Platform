"""Reflection on the **OpenAI Agents SDK** (`agents`) — a Writer agent and a Critic agent;
draft -> critique -> revise via `Runner.run_sync`."""
from ... import config, registry
from . import _base


def _model():
    from agents import OpenAIChatCompletionsModel, set_tracing_disabled
    set_tracing_disabled(True)
    if config.OPENAI_API_KEY:
        return config.OPENAI_MODEL
    from openai import AsyncOpenAI
    client = AsyncOpenAI(base_url=config.GROQ_BASE_URL, api_key=config.GROQ_API_KEY)
    return OpenAIChatCompletionsModel(model=config.GROQ_MODEL, openai_client=client)


def run(ctx: dict) -> dict:
    from agents import Agent, Runner
    q = ctx["input"]
    m = _model()
    writer = Agent(name="Automotive Writer", instructions=_base.DRAFT_SYS, model=m)
    critic = Agent(name="Fact Critic", instructions=_base.CRITIC_SYS, model=m)
    draft = str(Runner.run_sync(writer, q).final_output)
    critique = str(Runner.run_sync(critic, _base.CRITIQUE.format(q=q, a=draft)).final_output)
    answer = str(Runner.run_sync(writer, _base.REVISE.format(q=q, a=draft, c=critique)).final_output)
    return _base.result(draft, critique, answer)


registry.register("reflection", "openai-agents", run)
