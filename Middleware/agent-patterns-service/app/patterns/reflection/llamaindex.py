"""Reflection on **LlamaIndex** — its `LLM` abstraction drives draft -> critique -> revise."""
from ... import config, registry
from . import _base


def _llm():
    from llama_index.llms.openai import OpenAI as LIOpenAI
    if config.OPENAI_API_KEY:
        return LIOpenAI(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
    return LIOpenAI(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY, api_base=config.GROQ_BASE_URL)


def run(ctx: dict) -> dict:
    li = _llm()
    q = ctx["input"]
    draft = str(li.complete(f"{_base.DRAFT_SYS}\n\nQuestion: {q}"))
    critique = str(li.complete(_base.CRITIQUE.format(q=q, a=draft)))
    answer = str(li.complete(_base.REVISE.format(q=q, a=draft, c=critique)))
    return _base.result(draft, critique, answer)


registry.register("reflection", "llamaindex", run)
