"""VKP Agentic Service (FastAPI) — a pluggable roster of agent-SDK frameworks across the
collect / index / search stages.

  POST /agentic/{stage}/{framework}/run   -> run a stage with a specific framework
  GET  /agentic/frameworks                -> the stage x framework coverage matrix
  GET  /health

Isolated from vehicle-explore-service (modern dependency baseline) so heavy agent SDKs
(openai-agents, google-adk, ...) don't collide with explore's legacy pins.
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import frameworks as _frameworks  # noqa: F401 — import registers all frameworks
from . import registry

app = FastAPI(title="VKP Agentic Service", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class RunReq(BaseModel):
    query: Optional[str] = None          # search stage
    seedUrl: Optional[str] = None        # collect stage (the URL to discover links from)
    content: Optional[str] = None        # index stage (the text to chunk + index)
    sourceUrl: Optional[str] = None      # index stage (provenance of the content)
    table: Optional[str] = None          # index stage (override target table)
    companyId: Optional[str] = None
    topK: int = 5
    useLlm: bool = True
    # --- platform integration (opt-in) ---
    persist: bool = False                # collect: persist links to company_resource_graph
    companyResourceId: Optional[str] = None      # collect persist: the resource being discovered
    parentResourceGraphId: Optional[str] = None  # collect persist: the root graph node
    indexLogId: Optional[str] = None     # index: report to the indexing-service ledger
    params: Optional[dict] = None         # stage-specific extras


@app.get("/health")
def health():
    return {"status": "UP", "frameworks": registry.frameworks()}


@app.get("/agentic/frameworks")
def list_frameworks():
    """The coverage matrix: which frameworks implement each stage."""
    return {"stages": list(registry.STAGES), "matrix": registry.matrix(), "frameworks": registry.frameworks()}


@app.post("/agentic/{stage}/{framework}/run")
def run(stage: str, framework: str, req: RunReq):
    if stage not in registry.STAGES:
        raise HTTPException(404, f"unknown stage '{stage}'. Stages: {list(registry.STAGES)}")
    if framework not in registry.implemented(stage):
        raise HTTPException(501, f"'{framework}' does not implement '{stage}'. "
                                 f"Implemented: {registry.implemented(stage)}")
    ctx = req.model_dump()
    if stage == "search" and not (ctx.get("query") or "").strip():
        raise HTTPException(400, "query is required for the search stage")
    ctx["topK"] = max(1, min(ctx.get("topK", 5), 20))
    try:
        return registry.run(stage, framework, ctx)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"{framework}/{stage} failed: {e}")
