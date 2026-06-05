"""VKP Vehicle Explore Service (FastAPI) — semantic search over indexed vehicle content.

Search is framework-routed: POST /api/vehicle-explore/{frameworkName}/search. Retrieval runs
against the pgVector embeddings produced by the indexing subsystem.
"""
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from . import config, frameworks, guardrails, metrics, session, telemetry

app = FastAPI(title="VKP Vehicle Explore Service", version="0.1.0")
telemetry.setup_tracing(app, "vehicle-explore-service")

# The Vehicle Search Portal calls this directly in dev; a proxy is preferred but CORS keeps it simple.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchReq(BaseModel):
    query: str
    companyId: Optional[str] = None
    topK: int = 5
    store: Optional[str] = None     # pgvector | mongodb (defaults to VKP_VECTOR_STORE)
    mode: Optional[str] = None      # vector | fts | hybrid (defaults to VKP_SEARCH_MODE; fts/hybrid need pgvector)
    useLlm: bool = True             # when false (or no key/quota), returns the extractive answer
    providers: Optional[list[str]] = None   # provider ids to query; None = server default
    sessionId: Optional[str] = None         # fallback when no X-VKP-Session token
    userType: Optional[str] = None          # GUEST | AUTH (fallback)
    userId: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class StageReq(BaseModel):
    seedUrl: Optional[str] = None    # collect stage
    content: Optional[str] = None    # index stage
    sourceUrl: Optional[str] = None  # index provenance
    table: Optional[str] = None      # index target override
    companyId: Optional[str] = None
    # --- platform integration (opt-in) ---
    persist: bool = False                        # collect: persist links to company_resource_graph
    companyResourceId: Optional[str] = None
    parentResourceGraphId: Optional[str] = None
    indexLogId: Optional[str] = None             # index: report to the indexing-service ledger


# Import the agent modules that register collect/index stages (side-effect registration).
from . import agentic_stages  # noqa: E402
for _m in ("haystack_agent", "crewai_agent", "llamaindex_agent", "langgraph_agent"):
    try:
        __import__(f"app.{_m}", fromlist=[_m])
    except Exception as _e:  # noqa: BLE001
        pass


@app.get("/api/vehicle-explore/frameworks")
def list_frameworks():
    return {"known": sorted(frameworks.KNOWN), "implemented": sorted(frameworks.IMPLEMENTED),
            "stages": {"search": sorted(frameworks.IMPLEMENTED),
                       "collect": agentic_stages.collect_frameworks(),
                       "index": agentic_stages.index_frameworks()}}


@app.post("/api/vehicle-explore/{framework_name}/collect")
def collect(framework_name: str, req: StageReq):
    if framework_name not in agentic_stages.collect_frameworks():
        raise HTTPException(501, f"'{framework_name}' has no collect stage. "
                                 f"Implemented: {agentic_stages.collect_frameworks()}")
    if not (req.seedUrl or "").strip():
        raise HTTPException(400, "seedUrl is required for the collect stage")
    try:
        return agentic_stages.dispatch_collect(framework_name, req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"{framework_name}/collect failed: {e}")


@app.post("/api/vehicle-explore/{framework_name}/index")
def index(framework_name: str, req: StageReq):
    if framework_name not in agentic_stages.index_frameworks():
        raise HTTPException(501, f"'{framework_name}' has no index stage. "
                                 f"Implemented: {agentic_stages.index_frameworks()}")
    if not (req.content or "").strip():
        raise HTTPException(400, "content is required for the index stage")
    try:
        return agentic_stages.dispatch_index(framework_name, req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"{framework_name}/index failed: {e}")


@app.get("/api/vehicle-explore/providers")
def list_providers():
    """Providers whose creds are present (for the UI checkboxes). `default`=pre-checked (free)."""
    from . import providers as prov
    return {"providers": prov.available_providers()}


@app.post("/api/vehicle-explore/{framework_name}/search")
def search(framework_name: str, req: SearchReq,
           x_vkp_session: Optional[str] = Header(default=None)):
    if framework_name not in frameworks.IMPLEMENTED:
        raise HTTPException(
            status_code=501,
            detail=f"Framework '{framework_name}' is not implemented yet. Implemented: {sorted(frameworks.IMPLEMENTED)}",
        )
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query is required")
    top_k = max(1, min(req.topK, 20))
    store = (req.store or config.DEFAULT_STORE).lower()
    if store not in ("pgvector", "mongodb"):
        raise HTTPException(status_code=400, detail="store must be 'pgvector' or 'mongodb'")
    mode = (req.mode or config.DEFAULT_SEARCH_MODE).lower()
    if mode not in ("vector", "fts", "hybrid"):
        raise HTTPException(status_code=400, detail="mode must be 'vector', 'fts', or 'hybrid'")
    if store == "mongodb" and mode != "vector":
        raise HTTPException(status_code=400,
                            detail="mode 'fts'/'hybrid' uses Postgres full-text search; requires store='pgvector'")
    t0 = time.perf_counter()

    # Resolve the session: decrypt the shared token if present, else fall back, else a fresh guest.
    ctx = session.decrypt_session(x_vkp_session) or {}
    session_id = ctx.get("sessionId") or req.sessionId or ("ses_" + uuid.uuid4().hex)
    user_type = ctx.get("userType") or req.userType or "GUEST"
    user_id = ctx.get("userId") or req.userId
    query_id = "qry_" + uuid.uuid4().hex

    # Input guardrail — block off-scope/injection/unsafe before any retrieval or LLM spend.
    gin = guardrails.input_check(req.query.strip(), session_id, user_type, user_id,
                                 query_id, framework_name, store)
    query_id = gin.get("queryId") or query_id
    base = {"framework": framework_name, "store": store, "mode": mode, "query": req.query,
            "queryId": query_id, "sessionId": session_id, "userType": user_type}
    if not gin.get("allowed", True):
        metrics.SEARCHES.labels(framework_name, store, "blocked").inc()
        metrics.GUARDRAIL_BLOCKS.labels("input").inc()
        return {**base, "answer": "This request was blocked by input guardrails — I can only help "
                "with vehicle questions.", "answerSource": "blocked", "answers": [], "results": [],
                "count": 0, "guardrails": {"input": gin, "output": None}}

    safe_query = gin.get("sanitizedText") or req.query.strip()
    try:
        answer, answer_source, results, answers = frameworks.run(
            framework_name, safe_query, req.companyId, top_k, store, req.useLlm, req.providers, mode)
    except Exception as e:  # noqa: BLE001 — surface a clean 502 (e.g. store unreachable)
        metrics.SEARCHES.labels(framework_name, store, "error").inc()
        raise HTTPException(status_code=502, detail=f"Search backend error ({store}): {e}")

    # Output guardrail — check EVERY provider answer (and the extractive fallback).
    if answers:
        for a in answers:
            if a.get("ok") and a.get("answer"):
                go = guardrails.output_check(a["answer"], session_id, query_id, user_type, len(results))
                a["outputAction"] = go.get("action", "allow")
                if not go.get("allowed", True):
                    a["answer"], a["ok"], a["error"] = None, False, "withheld by output guardrails"
                elif go.get("action") == "redact" and go.get("sanitizedText"):
                    a["answer"] = go["sanitizedText"]
        surviving = [a for a in answers if a.get("ok") and a.get("answer")]
        if answer_source == "llm":
            answer = surviving[0]["answer"] if surviving else "All answers were withheld by output guardrails."
            if not surviving:
                answer_source = "blocked"
        gout = {"perProvider": True, "checked": len(answers),
                "blocked": sum(1 for a in answers if a.get("outputAction") == "block")}
    else:
        gout = guardrails.output_check(answer or "", session_id, query_id, user_type, len(results))
        if not gout.get("allowed", True):
            answer, answer_source = "The answer was withheld by output guardrails.", "blocked"
        elif gout.get("action") == "redact" and gout.get("sanitizedText"):
            answer = gout["sanitizedText"]

    metrics.SEARCH_LATENCY.labels(framework_name, store).observe(time.perf_counter() - t0)
    metrics.SEARCHES.labels(framework_name, store, "ok").inc()
    for a in answers:
        metrics.PROVIDER_ANSWERS.labels(a.get("provider", "?"), str(bool(a.get("ok"))).lower()).inc()
    if answer_source == "blocked":
        metrics.GUARDRAIL_BLOCKS.labels("output").inc()

    return {**base, "answer": answer, "answerSource": answer_source, "answers": answers,
            "results": results, "count": len(results),
            "guardrails": {"input": gin, "output": gout}}
