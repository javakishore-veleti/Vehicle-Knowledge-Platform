"""Memory Layer — conversation history (+ workflow/long-term). MongoDB-backed when available, else an
in-process dict so the service runs standalone."""
import time

from . import config

_local: dict[str, list[dict]] = {}


def _coll(name: str):
    from pymongo import MongoClient
    return MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=1500)[config.MONGO_DB][name]


def recent_turns(session_id: str | None, limit: int = 6) -> list[dict]:
    if not session_id:
        return []
    if config.MEMORY_ENABLED:
        try:
            docs = list(_coll("cef_memory").find({"sessionId": session_id}).sort("ts", -1).limit(limit))
            return [{"role": d["role"], "text": d["text"]} for d in reversed(docs)]
        except Exception:  # noqa: BLE001 — degrade to in-process
            pass
    return _local.get(session_id, [])[-limit:]


def append_turn(session_id: str | None, role: str, text: str) -> None:
    if not session_id:
        return
    if config.MEMORY_ENABLED:
        try:
            _coll("cef_memory").insert_one({"sessionId": session_id, "role": role,
                                            "text": text[:4000], "ts": time.time()})
            return
        except Exception:  # noqa: BLE001
            pass
    _local.setdefault(session_id, []).append({"role": role, "text": text[:4000]})
