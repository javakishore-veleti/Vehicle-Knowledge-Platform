"""The 'strands' framework — AWS Strands Agents SDK (https://strandsagents.com).

Model-driven; we point its OpenAIModel at OpenAI (if OPENAI_API_KEY) or free Groq, so it runs without
AWS credentials.
  search:  retrieve -> answer with [n] citations.
  collect: the agent uses the @tool fetch_page to discover + curate vehicle resource links.
"""
from .. import config, registry, tools
from ._base import COLLECT_INSTRUCTIONS, INSTRUCTIONS, run_collect, run_search


def _model():
    from strands.models.openai import OpenAIModel
    if config.OPENAI_API_KEY:
        return OpenAIModel(client_args={"api_key": config.OPENAI_API_KEY},
                           model_id=config.OPENAI_MODEL, params={"temperature": 0.2})
    if config.GROQ_API_KEY:
        return OpenAIModel(client_args={"api_key": config.GROQ_API_KEY, "base_url": config.GROQ_BASE_URL},
                           model_id=config.GROQ_MODEL, params={"temperature": 0.2})
    raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")


def _model_name() -> str:
    return config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL


# ---- search ----
def _answer(query: str, context: str) -> str:
    from strands import Agent
    agent = Agent(model=_model(), system_prompt=INSTRUCTIONS)
    return str(agent(f"Question: {query}\n\nSOURCES:\n{context}"))


def search(ctx: dict) -> dict:
    return run_search("strands", "AWS Strands Agents SDK", _model_name(), _answer, ctx)


# ---- collect ----
def _collect(seed: str) -> str:
    from strands import Agent, tool

    @tool
    def fetch_page(url: str) -> dict:
        """Fetch a web page; returns {url, title, links:[{url,type}], images:[...]}."""
        return tools.fetch_page(url)

    agent = Agent(model=_model(), system_prompt=COLLECT_INSTRUCTIONS, tools=[fetch_page])
    return str(agent(f"Seed URL: {seed}\nDiscover and return the relevant vehicle resource links as JSON."))


def collect(ctx: dict) -> dict:
    return run_collect("strands", "AWS Strands Agents SDK", _model_name(), _collect, ctx)


registry.register("strands", "search", search)
registry.register("strands", "collect", collect)
