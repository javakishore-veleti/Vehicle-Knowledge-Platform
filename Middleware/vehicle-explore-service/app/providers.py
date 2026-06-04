"""Multi-provider LLM answer fan-out.

By default the query is answered by EVERY enabled provider (over the same retrieved sources),
so answers can be compared side by side. Providers are OpenAI-compatible (one SDK, different
base_url/key/model). Selection: VKP_LLM_PROVIDERS (comma list of ids); default below.

A provider is used only if it's selected AND its key env is set; failures (quota, bad key, ...)
are captured per-provider so the UI can show them next to the working ones.
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

# id -> provider. base_url "" means the OpenAI default endpoint.
REGISTRY = [
    {"id": "openai", "label": "OpenAI · gpt-4o-mini", "base_url": "",
     "key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"},
    {"id": "groq-70b", "label": "Groq · Llama-3.3-70B", "base_url": "https://api.groq.com/openai/v1",
     "key_env": "GROQ_API_KEY", "model": "llama-3.3-70b-versatile"},
    {"id": "groq-8b", "label": "Groq · Llama-3.1-8B", "base_url": "https://api.groq.com/openai/v1",
     "key_env": "GROQ_API_KEY", "model": "llama-3.1-8b-instant"},
    # Available once you have valid keys (enable via VKP_LLM_PROVIDERS):
    {"id": "google", "label": "Google · Gemini 2.0 Flash",
     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
     "key_env": "GOOGLE_API_KEY", "model": "gemini-2.0-flash"},
    {"id": "anthropic", "label": "Anthropic · Claude 3.5 Haiku", "base_url": "https://api.anthropic.com/v1/",
     "key_env": "ANTHROPIC_API_KEY", "model": "claude-3-5-haiku-20241022"},
]

DEFAULT_ENABLED = "openai,groq-70b,groq-8b"

PROMPT_SYS = (
    "You are a vehicle research assistant. Answer the user's question using ONLY the provided "
    "sources. Cite sources inline as [n]. Be concise (2-4 sentences). If the sources don't "
    "contain the answer, say so briefly."
)


def enabled_providers() -> list[dict]:
    selected = [s.strip() for s in os.getenv("VKP_LLM_PROVIDERS", DEFAULT_ENABLED).split(",") if s.strip()]
    out = []
    for p in REGISTRY:
        if p["id"] not in selected:
            continue
        key = os.getenv(p["key_env"], "")
        if key:
            out.append({**p, "api_key": key})
    return out


def _friendly_error(exc: Exception) -> str:
    """Map a raw provider exception to a short, user-readable reason."""
    s = str(exc)
    low = s.lower()
    if "insufficient_quota" in low or "exceeded your current quota" in low:
        return "Quota exceeded — this provider's account needs billing/credits."
    if "api key not valid" in low or "invalid api key" in low or "incorrect api key" in low \
            or "401" in low or "authentication" in low:
        return "Invalid or missing API key for this provider."
    if "not_found" in low or "does not exist" in low or "404" in low:
        return "Model not available for this account."
    if "rate limit" in low or "429" in low:
        return "Rate-limited — please try again shortly."
    if "timeout" in low or "timed out" in low:
        return "The provider timed out."
    return (s[:140] + "…") if len(s) > 140 else s


def _answer_one(provider: dict, query: str, context: str) -> dict:
    t0 = time.perf_counter()
    base = {"provider": provider["id"], "label": provider["label"], "model": provider["model"]}
    try:
        kwargs = {"api_key": provider["api_key"], "timeout": 30}
        if provider["base_url"]:
            kwargs["base_url"] = provider["base_url"]
        resp = OpenAI(**kwargs).chat.completions.create(
            model=provider["model"],
            messages=[{"role": "system", "content": PROMPT_SYS},
                      {"role": "user", "content": f"Question: {query}\n\nSources:\n{context}"}],
            temperature=0.2, max_tokens=300)
        usage = getattr(resp, "usage", None)
        finish = resp.choices[0].finish_reason if resp.choices else None
        return {**base, "answer": resp.choices[0].message.content.strip(), "ok": True, "error": None,
                "promptTokens": getattr(usage, "prompt_tokens", None),
                "completionTokens": getattr(usage, "completion_tokens", None),
                "totalTokens": getattr(usage, "total_tokens", None),
                "finishReason": finish,
                "latencyMs": int((time.perf_counter() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001 — per-provider failure is data, not fatal
        return {**base, "answer": None, "ok": False, "error": _friendly_error(e),
                "errorDetail": str(e)[:300], "promptTokens": None, "completionTokens": None,
                "totalTokens": None, "finishReason": None,
                "latencyMs": int((time.perf_counter() - t0) * 1000)}


def generate_all(query: str, results: list[dict]) -> list[dict]:
    """Fan out to all enabled providers in parallel over the same retrieved context."""
    providers = enabled_providers()
    if not providers:
        return []
    context = "\n\n".join(f"[{i + 1}] {r['sourceUrl']}\n{r['snippet']}" for i, r in enumerate(results))
    out: list = [None] * len(providers)
    with ThreadPoolExecutor(max_workers=min(6, len(providers))) as ex:
        futures = {ex.submit(_answer_one, p, query, context): i for i, p in enumerate(providers)}
        for fut in as_completed(futures):
            out[futures[fut]] = fut.result()
    return out
