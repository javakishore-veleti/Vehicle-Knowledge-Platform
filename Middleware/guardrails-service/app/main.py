"""VKP Guardrails Service (FastAPI).

Input + output guardrails for the LLM search pipeline, with a Postgres query ledger split into
guest and authenticated-user tables.

  POST /guardrails/v1/input/check    -> scan a user query before retrieval/generation
  POST /guardrails/v1/output/check   -> scan an answer before returning it
  GET  /guardrails/v1/queries/{userType}/{sessionId}
  GET  /health
"""
import logging
import uuid
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db, engine
from .models import FeedbackReq, InputCheckReq, OutputCheckReq

log = logging.getLogger("guardrails")
app = FastAPI(title="VKP Guardrails Service", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def _startup():
    try:
        db.init_db()
        log.info("user_queries tables ready")
    except Exception as e:  # noqa: BLE001 — guardrails still work without the ledger
        log.warning("DB init failed (query ledger disabled): %s", e)


@app.get("/health")
def health():
    return {"status": "UP", "engine": engine.active_engine()}


@app.post("/guardrails/v1/input/check")
def input_check(req: InputCheckReq):
    query_id = req.queryId or ("qry_" + uuid.uuid4().hex)
    res = engine.check_input(req.text)
    try:
        db.log_input(req.userType, query_id, req.sessionId, req.userId, req.text,
                     req.framework, req.store, res["action"], res["reasons"])
    except Exception as e:  # noqa: BLE001
        log.warning("log_input failed: %s", e)
    return {"queryId": query_id, "allowed": res["action"] != "block",
            "engine": engine.active_engine(), **res}


@app.post("/guardrails/v1/output/check")
def output_check(req: OutputCheckReq):
    res = engine.check_output(req.answer, req.numSources)
    try:
        db.log_output(req.userType, req.queryId, res["action"], res["reasons"])
    except Exception as e:  # noqa: BLE001
        log.warning("log_output failed: %s", e)
    return {"queryId": req.queryId, "allowed": res["action"] != "block", **res}


@app.get("/guardrails/v1/queries/{user_type}/{session_id}")
def queries(user_type: str, session_id: str):
    return {"queries": db.list_queries(user_type, session_id)}


@app.get("/guardrails/v1/admin/queries")
def admin_queries(userType: Optional[str] = None, limit: int = 100):
    """Recent queries across sessions, with input/output verdicts (admin query log)."""
    return {"queries": db.recent_queries(userType, max(1, min(limit, 500)))}


@app.post("/guardrails/v1/feedback")
def feedback(req: FeedbackReq):
    """Capture 👍/👎 on an answer (search_feedback table)."""
    rating = 1 if (req.rating or "").lower() in ("up", "1", "+1", "good") else -1
    fid = "fb_" + uuid.uuid4().hex
    try:
        db.save_feedback(fid, req.queryId, req.sessionId, req.userType, req.userId,
                         rating, req.provider, req.comment)
    except Exception as e:  # noqa: BLE001
        log.warning("save_feedback failed: %s", e)
    return {"feedbackId": fid, "rating": rating}


@app.get("/guardrails/v1/admin/feedback/stats")
def feedback_stats():
    """Thumbs up/down totals + positive rate (a core search-quality KPI)."""
    return db.feedback_stats()
