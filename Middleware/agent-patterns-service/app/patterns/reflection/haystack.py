"""Reflection on **Haystack 2.x** — an OpenAIGenerator drives draft -> critique -> revise."""
from ... import config, registry
from . import _base


def _gen():
    from haystack.components.generators import OpenAIGenerator
    from haystack.utils import Secret
    if config.OPENAI_API_KEY:
        return OpenAIGenerator(model=config.OPENAI_MODEL, api_key=Secret.from_token(config.OPENAI_API_KEY))
    return OpenAIGenerator(model=config.GROQ_MODEL, api_key=Secret.from_token(config.GROQ_API_KEY),
                           api_base_url=config.GROQ_BASE_URL)


def _ask(gen, prompt: str) -> str:
    return (gen.run(prompt=prompt).get("replies") or [""])[0]


def run(ctx: dict) -> dict:
    gen = _gen()
    q = ctx["input"]
    draft = _ask(gen, f"{_base.DRAFT_SYS}\n\nQuestion: {q}")
    critique = _ask(gen, _base.CRITIQUE.format(q=q, a=draft))
    answer = _ask(gen, _base.REVISE.format(q=q, a=draft, c=critique))
    return _base.result(draft, critique, answer)


registry.register("reflection", "haystack", run)
