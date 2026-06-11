"""Multi-provider LLM answer fan-out.

By default the query is answered by EVERY enabled provider (over the same retrieved sources),
so answers can be compared side by side on quality, tokens, latency and cost.

Most providers are OpenAI-compatible (one SDK, different base_url/key/model). AWS Bedrock is not,
so it has its own boto3 path (kind="bedrock"). Selection: VKP_LLM_PROVIDERS (comma list of ids).

A provider runs only if it's selected AND its credentials are present; failures (quota, bad key,
no model access, ...) are captured per-provider so the UI can show them next to the working ones.
"""
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

log = logging.getLogger("vehicle-explore.providers")

# Pricing is USD per 1M tokens (in/out), best-effort for a rough cost estimate; None = unknown.
REGISTRY = [
    {"id": "openai", "label": "OpenAI · gpt-4o-mini", "kind": "openai", "base_url": "",
     "key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini", "priceIn": 0.15, "priceOut": 0.60},
    {"id": "groq-70b", "label": "Groq · Llama-3.3-70B", "kind": "openai", "free": True,
     "base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY",
     "model": "llama-3.3-70b-versatile", "priceIn": 0.59, "priceOut": 0.79},
    {"id": "groq-8b", "label": "Groq · Llama-3.1-8B", "kind": "openai", "free": True,
     "base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY",
     "model": "llama-3.1-8b-instant", "priceIn": 0.05, "priceOut": 0.08},
    {"id": "hf", "label": "Hugging Face · Llama-3.1-8B", "kind": "openai",
     "base_url": "https://router.huggingface.co/v1", "key_env": "HUGGINGFACEHUB_API_TOKEN",
     "model": "meta-llama/Llama-3.1-8B-Instruct", "priceIn": None, "priceOut": None},
    # OpenAI-compatible, enable via VKP_LLM_PROVIDERS once you have valid keys:
    {"id": "google", "label": "Google · Gemini 2.0 Flash", "kind": "openai",
     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GOOGLE_API_KEY",
     "model": "gemini-2.0-flash", "priceIn": 0.10, "priceOut": 0.40},
    {"id": "anthropic", "label": "Anthropic · Claude 3.5 Haiku", "kind": "openai",
     "base_url": "https://api.anthropic.com/v1/", "key_env": "ANTHROPIC_API_KEY",
     "model": "claude-3-5-haiku-20241022", "priceIn": 0.80, "priceOut": 4.00},
    # AWS Bedrock (boto3, not OpenAI-compatible). Needs AWS creds + the model enabled in the account.
    {"id": "bedrock", "label": "AWS Bedrock", "kind": "bedrock", "base_url": "", "key_env": "",
     "model": os.getenv("VKP_BEDROCK_MODEL", "amazon.titan-text-express-v1"),
     "priceIn": None, "priceOut": None},
]

DEFAULT_ENABLED = "openai,groq-70b,groq-8b,hf"
LLM_CONTEXT_K = int(os.getenv("VKP_LLM_CONTEXT_K", "6"))   # # of top chunks fed to the LLM

PROMPT_SYS = (
    "You are a vehicle research assistant. Answer the user's question using ONLY the provided "
    "sources. Cite sources inline as [n]. Be concise (2-4 sentences). If the sources don't "
    "contain the answer, say so briefly."
)


def _aws_creds() -> tuple[str | None, str | None, str]:
    ak = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("MY_AWS_ACCESS_KEY")
    sk = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("MY_AWS_SECRET_KEY")
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    return ak, sk, region


def _has_creds(p: dict) -> bool:
    if p.get("kind") == "bedrock":
        ak, sk, _ = _aws_creds()
        return bool(ak and sk)
    return bool(os.getenv(p.get("key_env", ""), ""))


def available_providers() -> list[dict]:
    """Registry providers whose creds are present — what the UI offers as checkboxes.

    `default` marks the ones pre-checked (free providers, so no cost/errors unless opted in).
    """
    return [{"id": p["id"], "label": p["label"], "model": p["model"],
             "free": bool(p.get("free")), "default": bool(p.get("free"))}
            for p in REGISTRY if _has_creds(p)]


def enabled_providers(selected_ids: list[str] | None = None) -> list[dict]:
    if selected_ids is None:
        selected = [s.strip() for s in os.getenv("VKP_LLM_PROVIDERS", DEFAULT_ENABLED).split(",") if s.strip()]
    else:
        selected = [s for s in selected_ids if s]
    out = []
    for p in REGISTRY:
        if p["id"] not in selected or not _has_creds(p):
            continue
        out.append(dict(p) if p.get("kind") == "bedrock" else {**p, "api_key": os.getenv(p["key_env"], "")})
    return out


def complete(prompt: str, max_tokens: int = 300, temperature: float = 0.2) -> str | None:
    """Single-shot completion via the first enabled OpenAI-compatible provider (used by the
    plan-execute planner). Returns None if no provider/credentials are available, or on error."""
    for p in enabled_providers():
        if p.get("kind") == "bedrock":
            continue  # the planner uses an OpenAI-compatible chat model
        try:
            kwargs = {"api_key": p["api_key"], "timeout": 30}
            if p.get("base_url"):
                kwargs["base_url"] = p["base_url"]
            resp = OpenAI(**kwargs).chat.completions.create(
                model=p["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature, max_tokens=max_tokens)
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:  # noqa: BLE001
            log.warning("complete() via %s failed: %s", p.get("id"), e)
            continue
    return None


def _cost(provider: dict, p_in, p_out) -> float | None:
    if provider.get("priceIn") is None or provider.get("priceOut") is None or p_in is None or p_out is None:
        return None
    return round((p_in / 1e6) * provider["priceIn"] + (p_out / 1e6) * provider["priceOut"], 6)


def _friendly_error(exc: Exception) -> str:
    """Map a raw provider exception to a short, user-readable reason."""
    s = str(exc)
    low = s.lower()
    if "insufficient_quota" in low or "exceeded your current quota" in low:
        return "Quota exceeded — this provider's account needs billing/credits."
    if "api key not valid" in low or "invalid api key" in low or "incorrect api key" in low \
            or "401" in low or "authentication" in low:
        return "Invalid or missing API key for this provider."
    if "accessdenied" in low or "don't have access" in low or "is not authorized" in low:
        return "Access denied — enable this model for your account/region."
    if "not_found" in low or "does not exist" in low or "could not be found" in low or "404" in low:
        return "Model not available for this account."
    if "rate limit" in low or "429" in low:
        return "Rate-limited — please try again shortly."
    if "timeout" in low or "timed out" in low:
        return "The provider timed out."
    return (s[:140] + "…") if len(s) > 140 else s


def _answer_openai(provider: dict, query: str, context: str) -> tuple[str, dict]:
    kwargs = {"api_key": provider["api_key"], "timeout": 30}
    if provider["base_url"]:
        kwargs["base_url"] = provider["base_url"]
    resp = OpenAI(**kwargs).chat.completions.create(
        model=provider["model"],
        messages=[{"role": "system", "content": PROMPT_SYS},
                  {"role": "user", "content": f"Question: {query}\n\nSources:\n{context}"}],
        temperature=0.2, max_tokens=300)
    u = getattr(resp, "usage", None)
    meta = {"promptTokens": getattr(u, "prompt_tokens", None),
            "completionTokens": getattr(u, "completion_tokens", None),
            "totalTokens": getattr(u, "total_tokens", None),
            "finishReason": resp.choices[0].finish_reason if resp.choices else None}
    return resp.choices[0].message.content.strip(), meta


def _answer_bedrock(provider: dict, query: str, context: str) -> tuple[str, dict]:
    import boto3  # lazy: only needed when Bedrock is enabled
    ak, sk, region = _aws_creds()
    client = boto3.client("bedrock-runtime", region_name=region,
                          aws_access_key_id=ak, aws_secret_access_key=sk)
    resp = client.converse(
        modelId=provider["model"],
        system=[{"text": PROMPT_SYS}],
        messages=[{"role": "user", "content": [{"text": f"Question: {query}\n\nSources:\n{context}"}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.2})
    text = resp["output"]["message"]["content"][0]["text"].strip()
    u = resp.get("usage", {})
    meta = {"promptTokens": u.get("inputTokens"), "completionTokens": u.get("outputTokens"),
            "totalTokens": u.get("totalTokens"), "finishReason": resp.get("stopReason")}
    return text, meta


def _answer_one(provider: dict, query: str, context: str) -> dict:
    t0 = time.perf_counter()
    base = {"provider": provider["id"], "label": provider["label"], "model": provider["model"]}
    try:
        if provider.get("kind") == "bedrock":
            answer, meta = _answer_bedrock(provider, query, context)
        else:
            answer, meta = _answer_openai(provider, query, context)
        return {**base, "answer": answer, "ok": True, "error": None, "errorDetail": None,
                **meta, "costUsd": _cost(provider, meta.get("promptTokens"), meta.get("completionTokens")),
                "latencyMs": int((time.perf_counter() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001 — per-provider failure is data, not fatal
        return {**base, "answer": None, "ok": False, "error": _friendly_error(e),
                "errorDetail": str(e)[:300], "promptTokens": None, "completionTokens": None,
                "totalTokens": None, "finishReason": None, "costUsd": None,
                "latencyMs": int((time.perf_counter() - t0) * 1000)}


def generate_all(query: str, results: list[dict], provider_ids: list[str] | None = None) -> list[dict]:
    """Fan out to the selected providers in parallel over the same (top-K) retrieved context."""
    providers = enabled_providers(provider_ids)
    if not providers:
        return []
    context = "\n\n".join(f"[{i + 1}] {r['sourceUrl']}\n{r['snippet']}"
                          for i, r in enumerate(results[:LLM_CONTEXT_K]))
    out: list = [None] * len(providers)
    with ThreadPoolExecutor(max_workers=min(8, len(providers))) as ex:
        futures = {ex.submit(_answer_one, p, query, context): i for i, p in enumerate(providers)}
        for fut in as_completed(futures):
            out[futures[fut]] = fut.result()
    return out
