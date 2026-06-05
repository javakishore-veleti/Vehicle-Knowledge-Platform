"""The 'msagent' framework — Microsoft Agent Framework (https://github.com/microsoft/agent-framework,
the GA successor that merged Semantic Kernel + AutoGen).

Uses its OpenAIChatClient pointed at OpenAI (api_key) or free Groq (api_key + base_url), turned into
an agent via `as_agent(instructions=...)`. `agent.run()` may be sync or awaitable depending on
version, so we handle both.
"""
import asyncio
import inspect

from .. import config, registry
from ._base import INSTRUCTIONS, run_search


def _answer(query: str, context: str) -> str:
    from agent_framework.openai import OpenAIChatClient
    prompt = f"Question: {query}\n\nSOURCES:\n{context}"

    # Build + run inside ONE event-loop context: MAF's run() sets telemetry ContextVars in its sync
    # prelude, so calling it outside asyncio.run() (then awaiting the coroutine in a fresh context)
    # raises "Token ... was created in a different Context".
    async def _run() -> str:
        if config.OPENAI_API_KEY:
            client = OpenAIChatClient(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
        elif config.GROQ_API_KEY:
            client = OpenAIChatClient(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                                      base_url=config.GROQ_BASE_URL)
        else:
            raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")
        agent = client.as_agent(instructions=INSTRUCTIONS, name="vehicle_search")
        result = agent.run(prompt)
        if inspect.isawaitable(result):
            result = await result
        return getattr(result, "text", None) or str(result)

    return asyncio.run(_run())


def search(ctx: dict) -> dict:
    model = config.OPENAI_MODEL if config.OPENAI_API_KEY else config.GROQ_MODEL
    return run_search("msagent", "Microsoft Agent Framework", model, _answer, ctx)


registry.register("msagent", "search", search)
