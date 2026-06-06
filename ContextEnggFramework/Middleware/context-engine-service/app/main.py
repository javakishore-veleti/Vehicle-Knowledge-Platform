"""CEF Context Engine Service (FastAPI). The Context Engineering Framework's orchestrator pipeline:
  POST /context-engine/orchestrate  -> Orchestrator -> Retrieval/Memory/Permission -> Assembly(5
                                        strategies) -> LLM reasoning -> Response + memory evolution
  GET  /context-engine/info         -> the framework layers + strategies (for the UI)
  GET  /health
"""
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel

from . import chat_log, memory, orchestrator, telemetry

app = FastAPI(title="VKP Context Engine (CEF)", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
telemetry.setup_tracing(app, "context-engine-service")

ORCHESTRATIONS = Counter("vkp_cef_orchestrations_total", "CEF orchestrate runs", ["role"])


@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class OrchestrateReq(BaseModel):
    query: str
    companyId: Optional[str] = None
    sessionId: Optional[str] = None         # memory continuity across turns
    role: Optional[str] = "USER"            # ADMIN | USER (Permission Layer)
    framework: Optional[str] = None         # reasoning engine when CEF_AGENTIC_URL is set
    topK: int = 8
    includeDiagram: bool = False            # return the flow steps inline for the UI diagram
    origin: Optional[dict] = None           # where the message came from {source, label, ...}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/context-engine/info")
def info():
    return {
        "corePrinciple": ["Right Knowledge", "Right Scope", "Right Role", "Right Time"],
        "layers": ["Context Orchestrator", "Retrieval", "Memory", "Permission",
                   "Context Assembly", "LLM Reasoning", "Context Evolution"],
        "strategies": ["selection", "compression", "ordering", "isolation", "format"],
    }


@app.get("/context-engine/memory/{session_id}")
def memory_view(session_id: str, limit: int = 20):
    """Inspect a session's memory (the Context Evolution loop's persisted turns)."""
    return {"sessionId": session_id, "turns": memory.recent_turns(session_id, limit)}


@app.post("/context-engine/orchestrate")
def orchestrate(req: OrchestrateReq):
    if not req.query.strip():
        raise HTTPException(400, "query is required")
    t0 = time.perf_counter()
    try:
        result = orchestrator.orchestrate(req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"orchestrate failed: {e}")
    ORCHESTRATIONS.labels((req.role or "USER").upper()).inc()

    # --- Telemetry: one richly-detailed cef_chat_request_log row per orchestrate (best-effort) ---
    log_id = "cef_" + uuid.uuid4().hex
    result["logId"] = log_id
    rec = chat_log.build(req={**req.model_dump(), "_logId": log_id}, result=result,
                         origin=req.origin, latency_ms=int((time.perf_counter() - t0) * 1000))
    chat_log.record(rec)
    if req.includeDiagram:
        result["steps"] = rec["steps"]
        result["techStack"] = rec["tech_stack"]
        result["vendors"] = rec["vendors"]
    return result


@app.get("/context-engine/logs")
def list_chat_logs(page: int = 0, size: int = 20, limit: Optional[int] = None,
                   companyId: Optional[str] = None, status: Optional[str] = None):
    """CEF chat telemetry rows. Server-side paging (page&size) or latest-N (limit) for client-side."""
    try:
        return chat_log.list_logs(page=page, size=size, limit=limit, company_id=companyId, status=status)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"log store error: {e}")


@app.get("/context-engine/logs/{log_id}")
def get_chat_log(log_id: str):
    """Full telemetry row (all jsonb) for the detail + dynamic flow-diagram page."""
    row = chat_log.get_log(log_id)
    if not row:
        raise HTTPException(404, f"no log {log_id}")
    return row
