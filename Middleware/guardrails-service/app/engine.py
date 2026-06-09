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

log = logging.getLogger("guardrails.engine")


def active_engine() -> str:
    e = config.ENGINE
    if e == "auto":
        # Prefer the free Groq safeguard model when a key is present (no torch); else llm-guard; else rules.
        if config.GROQ_API_KEY:
            return "groq"
        try:
            import llm_guard  # noqa: F401
            return "llmguard"
        except Exception:
            return "rules"
    return e


_GUARD_SYS = (
    "You are a safety + topic classifier for a VEHICLE-SHOPPING assistant. Classify the USER message "
    "as exactly one word:\n"
    "SAFE — a genuine question about cars/trucks/SUVs/EVs/vehicles: features, specs, pricing, brands, "
    "fuel economy, buying/leasing, comparisons.\n"
    "OFFTOPIC — harmless but NOT about vehicles (e.g. cooking, geography, sports, coding, chit-chat).\n"
    "UNSAFE — sexual content, hate, harassment, violence, weapons, illegal activity, drugs, self-harm, "
    "or malware/hacking.\n"
    "Answer with ONLY one word: SAFE, OFFTOPIC, or UNSAFE."
)


def _groq_safety(text: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1", timeout=25)
    r = client.chat.completions.create(
        model=config.GROQ_GUARD_MODEL,
        messages=[{"role": "system", "content": _GUARD_SYS}, {"role": "user", "content": text}],
        max_tokens=600, temperature=0)
    out = (r.choices[0].message.content or "").strip().lower()
    label = ("unsafe" if "unsafe" in out
             else "offtopic" if ("offtopic" in out or "off-topic" in out or "off topic" in out)
             else "safe")
    return {"label": label, "raw": out[-80:]}


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
            if g["label"] == "unsafe":
                res["reasons"].append({"scanner": "safeguard_model", "detail": "flagged UNSAFE by content-safety model"})
                res["action"] = "block"
            elif g["label"] == "offtopic":
                res["reasons"].append({"scanner": "topic_model", "detail": "not a vehicle-related question (off-topic)"})
                res["action"] = "block"
        elif eng == "llmguard":
            _llmguard_augment(text, res)
    except Exception as e:  # noqa: BLE001 — model layer is best-effort; rules already ran
        log.warning("model guardrail layer (%s) failed: %s", eng, e)
    return res


def check_output(answer: str, num_sources: int) -> dict:
    return scanners.scan_output(answer, num_sources)
