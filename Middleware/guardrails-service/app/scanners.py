"""Built-in rules engine — fast, dependency-free guardrails (always available).

Input: length, prompt-injection markers, out-of-scope markers, PII redaction.
Output: citation validity, light groundedness, code/markup leak, PII redaction.
Actions: allow | redact | flag | block (block => not allowed).
"""
import re

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE = re.compile(r"\b(?:\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")

INJECTION_MARKERS = [
    "ignore previous", "ignore all previous", "ignore the above", "ignore your instructions",
    "disregard previous", "disregard the above", "system prompt", "you are now", "act as ",
    "pretend to be", "reveal your instructions", "developer mode", "jailbreak", "do anything now",
]
OUT_OF_SCOPE_MARKERS = [
    "write a python", "write python", "reverse a linked list", "linked list", "def ", "import ",
    "select * from", "sql query", "write me a", "write a poem", "write an essay", "recipe for",
    "javascript", "c++ code", "leetcode",
]

CITATION = re.compile(r"\[(\d+)\]")
CODE_LEAK = re.compile(r"```|def \w+\(|class \w+\(|SELECT .+ FROM|<\w+>.*</\w+>", re.IGNORECASE)


def redact_pii(text: str):
    found = []

    def sub(pattern, label, t):
        if pattern.search(t):
            found.append(label)
            return pattern.sub(f"[REDACTED_{label}]", t)
        return t

    t = sub(EMAIL, "EMAIL", text)
    t = sub(SSN, "SSN", t)
    t = sub(CARD, "CARD", t)
    t = sub(PHONE, "PHONE", t)
    return t, found


def scan_input(text: str, max_chars: int) -> dict:
    reasons = []
    action = "allow"
    low = text.lower()

    if len(text) > max_chars:
        return {"action": "block", "sanitizedText": text[:max_chars],
                "reasons": [{"scanner": "length", "detail": f"query exceeds {max_chars} chars"}]}

    if any(m in low for m in INJECTION_MARKERS):
        reasons.append({"scanner": "prompt_injection", "detail": "possible prompt-injection / jailbreak phrasing"})
        action = "block"
    if any(m in low for m in OUT_OF_SCOPE_MARKERS):
        reasons.append({"scanner": "scope", "detail": "appears out of scope (not a vehicle question)"})
        action = "block"

    sanitized, pii = redact_pii(text)
    if pii:
        reasons.append({"scanner": "pii", "detail": "redacted " + ", ".join(pii)})
        if action == "allow":
            action = "redact"

    return {"action": action, "sanitizedText": sanitized, "reasons": reasons}


def scan_output(answer: str, num_sources: int) -> dict:
    reasons = []
    action = "allow"

    cites = [int(x) for x in CITATION.findall(answer)]
    bad = [c for c in cites if c < 1 or c > max(num_sources, 0)]
    if bad:
        reasons.append({"scanner": "citation", "detail": f"citations out of range: {bad}"})
        action = "flag"
    if num_sources > 0 and not cites:
        reasons.append({"scanner": "groundedness", "detail": "answer cites none of the provided sources"})
        if action == "allow":
            action = "flag"
    if CODE_LEAK.search(answer):
        reasons.append({"scanner": "code_leak", "detail": "answer contains code/markup (off-topic drift)"})
        action = "block"

    sanitized, pii = redact_pii(answer)
    if pii:
        reasons.append({"scanner": "pii", "detail": "redacted " + ", ".join(pii)})
        if action in ("allow", "flag"):
            action = "redact"

    return {"action": action, "sanitizedText": sanitized, "reasons": reasons}
