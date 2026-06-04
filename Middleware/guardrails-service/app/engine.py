"""Guardrail engine dispatch.

The built-in rules engine ALWAYS runs (cheap, dependency-free). On top of it, a model-based layer
can be enabled (defense-in-depth):
  - VKP_GUARDRAILS_ENGINE=groq      -> Meta Llama Guard via Groq (free, no torch)
  - VKP_GUARDRAILS_ENGINE=llmguard  -> protectai/llm-guard scanners (heavier; needs the package)
  - VKP_GUARDRAILS_ENGINE=auto      -> llmguard if importable, else rules
  - VKP_GUARDRAILS_ENGINE=rules     -> rules only
"""
import logging

from . import config, scanners

log = logging.getLogger("guardrails")


def active_engine() -> str:
    e = config.ENGINE
    if e == "auto":
        try:
            import llm_guard  # noqa: F401
            return "llmguard"
        except Exception:
            return "rules"
    return e


_GUARD_SYS = (
    "You are a content-safety classifier for a vehicle-shopping assistant. Decide if the USER "
    "message is UNSAFE — i.e. it requests weapons/explosives, violence, illegal activity, self-harm, "
    "hate, sexual content, malware, or other clearly harmful content. A normal car/vehicle question "
    "is SAFE. Respond with exactly one word: SAFE or UNSAFE."
)


def _groq_safety(text: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1", timeout=25)
    r = client.chat.completions.create(
        model=config.GROQ_GUARD_MODEL,
        messages=[{"role": "system", "content": _GUARD_SYS}, {"role": "user", "content": text}],
        max_tokens=600, temperature=0)
    out = (r.choices[0].message.content or "").strip().lower()
    unsafe = "unsafe" in out
    return {"safe": not unsafe, "raw": out[-80:]}


def _llmguard_augment(text: str, res: dict) -> None:
    from llm_guard.input_scanners import PromptInjection, Toxicity
    from llm_guard.input_scanners.prompt_injection import MatchType
    for scanner, name in ((PromptInjection(threshold=0.85, match_type=MatchType.FULL), "prompt_injection_model"),
                          (Toxicity(threshold=0.7), "toxicity")):
        _, valid, score = scanner.scan(text)
        if not valid:
            res["reasons"].append({"scanner": name, "detail": f"llm-guard flagged (score={score})"})
            res["action"] = "block"


def check_input(text: str) -> dict:
    res = scanners.scan_input(text, config.MAX_QUERY_CHARS)   # rules always
    eng = active_engine()
    try:
        if eng == "groq" and config.GROQ_API_KEY:
            g = _groq_safety(text)
            if not g["safe"]:
                res["reasons"].append({"scanner": "safeguard_model", "detail": "flagged unsafe by content-safety model"})
                res["action"] = "block"
        elif eng == "llmguard":
            _llmguard_augment(text, res)
    except Exception as e:  # noqa: BLE001 — model layer is best-effort; rules already ran
        log.warning("model guardrail layer (%s) failed: %s", eng, e)
    return res


def check_output(answer: str, num_sources: int) -> dict:
    return scanners.scan_output(answer, num_sources)
