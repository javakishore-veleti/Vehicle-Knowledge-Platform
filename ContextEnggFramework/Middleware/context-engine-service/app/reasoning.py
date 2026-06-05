"""LLM Reasoning Engine — generate the answer from the assembled context. Direct OpenAI/Groq call by
default; when CEF_AGENTIC_URL is set, route to the VKP agent roster so any framework can be the
reasoning engine (reuses the 8-framework agentic-service)."""
import json
import urllib.request

from . import config

SYSTEM = ("You are a vehicle knowledge assistant. Use ONLY the SOURCES in the provided context, "
          "answer concisely, and cite sources as [n]. If the sources don't cover it, say so.")


def reason(context_block: str, framework: str | None = None) -> tuple[str, str]:
    if config.AGENTIC_URL:
        try:
            return _via_agentic(context_block, framework or config.DEFAULT_FRAMEWORK)
        except Exception:  # noqa: BLE001 — fall back to a direct call
            pass
    return _direct(context_block)


def _direct(context_block: str) -> tuple[str, str]:
    from openai import OpenAI
    if config.OPENAI_API_KEY:
        client, model = OpenAI(api_key=config.OPENAI_API_KEY), config.OPENAI_MODEL
    elif config.GROQ_API_KEY:
        client = OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
        model = config.GROQ_MODEL
    else:
        raise RuntimeError("no OPENAI_API_KEY or GROQ_API_KEY set")
    resp = client.chat.completions.create(model=model, temperature=0.2, messages=[
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": context_block}])
    return resp.choices[0].message.content.strip(), model


def _via_agentic(context_block: str, framework: str) -> tuple[str, str]:
    url = config.AGENTIC_URL.rstrip("/") + f"/agentic/search/{framework}/run"
    data = json.dumps({"query": context_block, "topK": 1, "useLlm": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode("utf-8"))
    return d.get("answer", ""), f"agentic:{framework}"
