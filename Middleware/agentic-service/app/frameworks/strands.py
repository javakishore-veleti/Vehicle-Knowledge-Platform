"""The 'strands' framework — AWS Strands Agents SDK (https://strandsagents.com).

Strands is model-driven; instead of its default Bedrock provider we point its OpenAIModel at OpenAI
(if OPENAI_API_KEY) or free Groq (OpenAI-compatible endpoint) so it runs without AWS credentials.
"""
from .. import config, registry
from ._base import INSTRUCTIONS, run_search


def _answer(query: str, context: str) -> str:
    from strands import Agent
    from strands.models.openai import OpenAIModel
    if config.OPENAI_API_KEY:
        model = OpenAIModel(client_args={"api_key": config.OPENAI_API_KEY},
                            model_id=config.OPENAI_MODEL, params={"temperature": 0.2})
    elif config.GROQ_API_KEY:
        model = OpenAIModel(client_args={"api_key": config.GROQ_API_KEY, "base_url": config.GROQ_BASE_URL},
                            model_id=config.GROQ_MODEL, params={"temperature": 0.2})
    else:
        raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")
    agent = Agent(model=model, system_prompt=INSTRUCTIONS)
    return str(agent(f"Question: {query}\n\nSOURCES:\n{context}"))


def search(ctx: dict) -> dict:
    model = config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL
    return run_search("strands", "AWS Strands Agents SDK", model, _answer, ctx)


registry.register("strands", "search", search)
