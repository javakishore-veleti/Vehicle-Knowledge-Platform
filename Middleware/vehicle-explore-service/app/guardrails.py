"""Thin client for the guardrails-service (input/output checks). Fails OPEN if unreachable."""
import json
import logging
import urllib.request
from typing import Optional

from . import config

log = logging.getLogger("vehicle-explore")


def _post(path: str, payload: dict, timeout: int = 20) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(config.GUARDRAILS_URL.rstrip("/") + path, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _open(extra_reason: Optional[dict] = None, **fields) -> dict:
    base = {"allowed": True, "action": "allow", "reasons": [], "skipped": True}
    base.update(fields)
    if extra_reason:
        base["reasons"] = [extra_reason]
    return base


def input_check(text, session_id, user_type, user_id, query_id=None, framework=None, store=None) -> dict:
    if not config.GUARDRAILS_ENABLED:
        return _open(sanitizedText=text, queryId=query_id or "")
    try:
        return _post("/guardrails/v1/input/check", {
            "text": text, "sessionId": session_id, "queryId": query_id,
            "userType": user_type, "userId": user_id, "framework": framework, "store": store})
    except Exception as e:  # noqa: BLE001
        log.warning("guardrails input check unreachable (%s) — failing open", e)
        return _open({"scanner": "guardrails", "detail": "service unreachable (fail-open)"},
                     sanitizedText=text, queryId=query_id or "")


def output_check(answer, session_id, query_id, user_type, num_sources) -> dict:
    if not config.GUARDRAILS_ENABLED:
        return _open(sanitizedText=answer)
    try:
        return _post("/guardrails/v1/output/check", {
            "answer": answer, "sessionId": session_id, "queryId": query_id,
            "userType": user_type, "numSources": num_sources})
    except Exception as e:  # noqa: BLE001
        log.warning("guardrails output check unreachable (%s) — failing open", e)
        return _open(sanitizedText=answer)
