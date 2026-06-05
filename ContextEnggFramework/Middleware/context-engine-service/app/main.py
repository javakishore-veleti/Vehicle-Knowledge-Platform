"""CEF Context Engine Service (FastAPI). The Context Engineering Framework's orchestrator pipeline:
  POST /context-engine/orchestrate  -> Orchestrator -> Retrieval/Memory/Permission -> Assembly(5
                                        strategies) -> LLM reasoning -> Response + memory evolution
  GET  /context-engine/info         -> the framework layers + strategies (for the UI)
  GET  /health
"""
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel

from . import memory, orchestrator, telemetry

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
    try:
        result = orchestrator.orchestrate(req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"orchestrate failed: {e}")
    ORCHESTRATIONS.labels((req.role or "USER").upper()).inc()
    return result
