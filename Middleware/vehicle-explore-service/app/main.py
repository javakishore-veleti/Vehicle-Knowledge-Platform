"""VKP Vehicle Explore Service (FastAPI) — semantic search over indexed vehicle content.

Search is framework-routed: POST /api/vehicle-explore/{frameworkName}/search. Retrieval runs
against the pgVector embeddings produced by the indexing subsystem.
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config, frameworks

app = FastAPI(title="VKP Vehicle Explore Service", version="0.1.0")

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
    useLlm: bool = True             # when false (or no key/quota), returns the extractive answer
    providers: Optional[list[str]] = None   # provider ids to query; None = server default


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/api/vehicle-explore/frameworks")
def list_frameworks():
    return {"known": sorted(frameworks.KNOWN), "implemented": sorted(frameworks.IMPLEMENTED)}


@app.get("/api/vehicle-explore/providers")
def list_providers():
    """Providers whose creds are present (for the UI checkboxes). `default`=pre-checked (free)."""
    from . import providers as prov
    return {"providers": prov.available_providers()}


@app.post("/api/vehicle-explore/{framework_name}/search")
def search(framework_name: str, req: SearchReq):
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
    try:
        answer, answer_source, results, answers = frameworks.run(
            framework_name, req.query.strip(), req.companyId, top_k, store, req.useLlm, req.providers)
    except Exception as e:  # noqa: BLE001 — surface a clean 502 (e.g. store unreachable)
        raise HTTPException(status_code=502, detail=f"Search backend error ({store}): {e}")
    return {
        "framework": framework_name,
        "store": store,
        "query": req.query,
        "answer": answer,
        "answerSource": answer_source,
        "answers": answers,        # per-provider answers for side-by-side comparison
        "results": results,
        "count": len(results),
    }
