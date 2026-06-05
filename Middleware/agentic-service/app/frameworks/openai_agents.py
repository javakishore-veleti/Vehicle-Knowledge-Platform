"""The 'openai-agents' framework — OpenAI Agents SDK (https://openai.github.io/openai-agents-python).

Model = OpenAI if OPENAI_API_KEY is set, else free Groq via the SDK's OpenAI-compatible model.
"""
from .. import config, registry
from ._base import INSTRUCTIONS, run_search


def _answer(query: str, context: str) -> str:
    from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
    set_tracing_disabled(True)   # don't phone home
    if config.OPENAI_API_KEY:
        agent = Agent(name="Vehicle Search Analyst", instructions=INSTRUCTIONS, model=config.OPENAI_MODEL)
    elif config.GROQ_API_KEY:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=config.GROQ_BASE_URL, api_key=config.GROQ_API_KEY)
        agent = Agent(name="Vehicle Search Analyst", instructions=INSTRUCTIONS,
                      model=OpenAIChatCompletionsModel(model=config.GROQ_MODEL, openai_client=client))
    else:
        raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")
    return str(Runner.run_sync(agent, f"Question: {query}\n\nSOURCES:\n{context}").final_output)


def search(ctx: dict) -> dict:
    model = config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL
    return run_search("openai-agents", "OpenAI Agents SDK", model, _answer, ctx)


registry.register("openai-agents", "search", search)
