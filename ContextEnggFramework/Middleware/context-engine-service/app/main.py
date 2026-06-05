"""CEF Context Engine Service (FastAPI). The Context Engineering Framework's orchestrator pipeline:
  POST /context-engine/orchestrate  -> Orchestrator -> Retrieval/Memory/Permission -> Assembly(5
                                        strategies) -> LLM reasoning -> Response + memory evolution
  GET  /context-engine/info         -> the framework layers + strategies (for the UI)
  GET  /health
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import orchestrator

app = FastAPI(title="VKP Context Engine (CEF)", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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


@app.post("/context-engine/orchestrate")
def orchestrate(req: OrchestrateReq):
    if not req.query.strip():
        raise HTTPException(400, "query is required")
    try:
        return orchestrator.orchestrate(req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"orchestrate failed: {e}")
