"""Shared LLM access for the framework cells.

Most cells call `complete()` (a plain OpenAI-compatible chat completion). Cells whose framework needs a
model OBJECT (the agent SDKs) build it from `config` themselves. Everything resolves to OpenAI (key) or
free Groq (key + base_url), so the whole service works with either."""
from . import config


def _client():
    from openai import OpenAI
    if config.OPENAI_API_KEY:
        return OpenAI(api_key=config.OPENAI_API_KEY), config.OPENAI_MODEL
    if config.GROQ_API_KEY:
        return OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL), config.GROQ_MODEL
    raise RuntimeError("No OPENAI_API_KEY or GROQ_API_KEY set — set one to run a cell.")


def complete(prompt: str, system: str | None = None, max_tokens: int = 600, temperature: float = 0.3) -> str:
    """One-shot OpenAI-compatible chat completion."""
    client, model = _client()
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=model, messages=messages,
                                          max_tokens=max_tokens, temperature=temperature)
    return (resp.choices[0].message.content or "").strip()
