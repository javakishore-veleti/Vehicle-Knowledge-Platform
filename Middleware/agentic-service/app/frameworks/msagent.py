"""The 'msagent' framework — Microsoft Agent Framework (https://github.com/microsoft/agent-framework,
the GA successor that merged Semantic Kernel + AutoGen).

Uses its OpenAIChatClient pointed at OpenAI (api_key) or free Groq (api_key + base_url), turned into
an agent via `as_agent(instructions=...)`. `agent.run()` may be sync or awaitable depending on
version, so we handle both.
"""
import asyncio
import inspect

from .. import config, registry, tools
from ._base import COLLECT_INSTRUCTIONS, INSTRUCTIONS, run_collect, run_search


def fetch_page(url: str) -> dict:
    """Fetch a web page and return its title, links, and images (a MAF function tool)."""
    return tools.fetch_page(url)


def _client():
    from agent_framework.openai import OpenAIChatClient
    if config.OPENAI_API_KEY:
        return OpenAIChatClient(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
    if config.GROQ_API_KEY:
        return OpenAIChatClient(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                                base_url=config.GROQ_BASE_URL)
    raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")


def _model_name() -> str:
    return config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL


def _run_agent(name: str, instructions: str, prompt: str, tool_list: list | None = None) -> str:
    """Build + run the agent inside ONE event-loop context. MAF's run() sets telemetry ContextVars in
    its sync prelude, so calling it outside asyncio.run() then awaiting in a fresh context raises
    'Token ... was created in a different Context'."""
    async def _run() -> str:
        agent = _client().as_agent(instructions=instructions, name=name, tools=tool_list or [])
        result = agent.run(prompt)
        if inspect.isawaitable(result):
            result = await result
        return getattr(result, "text", None) or str(result)
    return asyncio.run(_run())


def search(ctx: dict) -> dict:
    def _answer(query: str, context: str) -> str:
        return _run_agent("vehicle_search", INSTRUCTIONS, f"Question: {query}\n\nSOURCES:\n{context}")
    return run_search("msagent", "Microsoft Agent Framework", _model_name(), _answer, ctx)


def collect(ctx: dict) -> dict:
    def _collect(seed: str) -> str:
        return _run_agent("vehicle_scout", COLLECT_INSTRUCTIONS,
                          f"Seed URL: {seed}\nDiscover and return the relevant vehicle resource links as JSON.",
                          tool_list=[fetch_page])
    return run_collect("msagent", "Microsoft Agent Framework", _model_name(), _collect, ctx)


registry.register("msagent", "search", search)
registry.register("msagent", "collect", collect)
