"""The 'openai-agents' framework — OpenAI Agents SDK (https://openai.github.io/openai-agents-python).

search: retrieve indexed chunks -> agent answers with [n] citations.
collect: agent uses the fetch_page tool to discover + curate vehicle resource links.
Model = OpenAI if OPENAI_API_KEY is set, else free Groq via the SDK's OpenAI-compatible model.
"""
from .. import config, registry, tools
from ._base import (COLLECT_INSTRUCTIONS, INDEX_INSTRUCTIONS, INSTRUCTIONS,
                    run_collect, run_index, run_search)


def _model():
    """The `model=` arg for an Agent: a model-name string (OpenAI) or a Groq-backed model object."""
    from agents import OpenAIChatCompletionsModel, set_tracing_disabled
    set_tracing_disabled(True)   # don't phone home
    if config.OPENAI_API_KEY:
        return config.OPENAI_MODEL
    if config.GROQ_API_KEY:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=config.GROQ_BASE_URL, api_key=config.GROQ_API_KEY)
        return OpenAIChatCompletionsModel(model=config.GROQ_MODEL, openai_client=client)
    raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")


def _model_name() -> str:
    return config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL


# ---- search ----
def _answer(query: str, context: str) -> str:
    from agents import Agent, Runner
    agent = Agent(name="Vehicle Search Analyst", instructions=INSTRUCTIONS, model=_model())
    return str(Runner.run_sync(agent, f"Question: {query}\n\nSOURCES:\n{context}").final_output)


def search(ctx: dict) -> dict:
    return run_search("openai-agents", "OpenAI Agents SDK", _model_name(), _answer, ctx)


# ---- collect ----
def _collect(seed: str) -> str:
    from agents import Agent, Runner, function_tool

    @function_tool
    def fetch_page(url: str) -> dict:
        """Fetch a web page; returns {url, title, links:[{url,type}], images:[...]}."""
        return tools.fetch_page(url)

    agent = Agent(name="Vehicle Resource Scout", instructions=COLLECT_INSTRUCTIONS,
                  tools=[fetch_page], model=_model())
    out = Runner.run_sync(agent, f"Seed URL: {seed}\nDiscover and return the relevant vehicle resource links as JSON.")
    return str(out.final_output)


def collect(ctx: dict) -> dict:
    return run_collect("openai-agents", "OpenAI Agents SDK", _model_name(), _collect, ctx)


# ---- index ----
def _chunk(content: str) -> str:
    from agents import Agent, Runner
    agent = Agent(name="Vehicle Content Indexer", instructions=INDEX_INSTRUCTIONS, model=_model())
    out = Runner.run_sync(agent, f"CONTENT:\n{content}\n\nReturn the chunks as a JSON array of strings.")
    return str(out.final_output)


def index(ctx: dict) -> dict:
    return run_index("openai-agents", "OpenAI Agents SDK", _model_name(), _chunk, ctx)


registry.register("openai-agents", "search", search)
registry.register("openai-agents", "collect", collect)
registry.register("openai-agents", "index", index)
