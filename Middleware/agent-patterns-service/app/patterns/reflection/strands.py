"""Reflection on the **AWS Strands Agents SDK** (`strands`) — an Agent per step."""
from ... import config, registry
from . import _base


def _model():
    from strands.models.openai import OpenAIModel
    if config.OPENAI_API_KEY:
        return OpenAIModel(client_args={"api_key": config.OPENAI_API_KEY}, model_id=config.OPENAI_MODEL)
    return OpenAIModel(client_args={"api_key": config.GROQ_API_KEY, "base_url": config.GROQ_BASE_URL},
                       model_id=config.GROQ_MODEL)


def _ask(system: str, prompt: str) -> str:
    from strands import Agent
    return str(Agent(model=_model(), system_prompt=system)(prompt))


def run(ctx: dict) -> dict:
    q = ctx["input"]
    draft = _ask(_base.DRAFT_SYS, q)
    critique = _ask(_base.CRITIC_SYS, _base.CRITIQUE.format(q=q, a=draft))
    answer = _ask(_base.DRAFT_SYS, _base.REVISE.format(q=q, a=draft, c=critique))
    return _base.result(draft, critique, answer)


registry.register("reflection", "strands", run)
