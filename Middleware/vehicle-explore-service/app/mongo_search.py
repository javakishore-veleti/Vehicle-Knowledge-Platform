"""MongoDB Atlas Vector Search retrieval ($vectorSearch) — the alternative store path.

Requires a vectorSearch index on `embedding` (created by scripts/create_mongo_index.py). The
query is embedded with the same fastembed model as the pgVector path, so results are comparable.
"""
from functools import lru_cache
from typing import Optional

from pymongo import MongoClient

from . import config
from .search import embed_query


@lru_cache(maxsize=1)
def _client() -> MongoClient:
    return MongoClient(config.MONGO_URI)


def search_chunks_mongo(query: str, company_id: Optional[str] = None, top_k: int = 5) -> list[dict]:
    vec = embed_query(query)
    coll = _client()[config.MONGO_DB][config.VECTOR_TABLE]
    vs: dict = {
        "index": config.MONGO_VECTOR_INDEX,
        "path": "embedding",
        "queryVector": vec,
        "numCandidates": max(100, top_k * 20),
        "limit": top_k,
    }
    if company_id:
        vs["filter"] = {"companyId": company_id}
    pipeline = [
        {"$vectorSearch": vs},
        {"$project": {"_id": 0, "sourceUrl": 1, "chunkText": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]
    rows = list(coll.aggregate(pipeline))
    return [
        {"sourceUrl": r.get("sourceUrl"), "snippet": (r.get("chunkText") or "").strip()[:400],
         "score": round(float(r.get("score", 0.0)), 4)}
        for r in rows
    ]
