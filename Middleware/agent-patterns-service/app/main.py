"""VKP Agent Patterns Service (FastAPI, :8094).

Every agentic pattern implemented in every framework, side by side, behind a uniform API:
  GET  /agent-patterns/patterns                     -> coverage matrix
  POST /agent-patterns/{pattern}/{framework}/run    -> run one cell ({"input": "..."})
  GET  /health

Cells live in app/patterns/<pattern>/<framework>.py and register themselves; SDKs are imported lazily,
so the service boots without any heavy SDK installed (a missing SDK only fails its own cell)."""
import logging
import time

from fastapi import FastAPI, HTTPException

from . import config, registry
from .models import RunReq, RunResp
from . import patterns  # noqa: F401  — importing triggers cell registration

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent-patterns.main")

app = FastAPI(title="VKP Agent Patterns Service",
              description="Every agentic pattern in every framework — production reference + comparison harness.")


@app.get("/health")
def health():
    return {"status": "UP", "llm": config.has_llm(), "cells": registry.matrix()["count"]}


@app.get("/agent-patterns/patterns")
def patterns_matrix():
    return registry.matrix()


@app.post("/agent-patterns/{pattern}/{framework}/run", response_model=RunResp)
def run_cell(pattern: str, framework: str, req: RunReq):
    if not registry.implemented(pattern, framework):
        raise HTTPException(status_code=404,
                            detail=f"{pattern}/{framework} not implemented yet — see GET /agent-patterns/patterns")
    if not req.input or not req.input.strip():
        raise HTTPException(status_code=400, detail="input is required")
    t0 = time.perf_counter()
    try:
        out = registry.dispatch(pattern, framework, req.model_dump())
    except Exception as e:  # noqa: BLE001 — surface a clean 502 (missing SDK/key, provider error, …)
        log.warning("%s/%s failed: %s", pattern, framework, e)
        raise HTTPException(status_code=502, detail=f"{pattern}/{framework} failed: {e}")
    return RunResp(
        pattern=pattern, framework=framework, input=req.input,
        answer=out.get("answer"), draft=out.get("draft"), critique=out.get("critique"),
        steps=out.get("steps"), iterations=req.maxIterations, model=config.model_name(),
        latencyMs=int((time.perf_counter() - t0) * 1000),
    )
