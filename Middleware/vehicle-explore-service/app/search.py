"""Vector retrieval over the pgVector embeddings produced by the indexing subsystem.

The query is embedded locally with fastembed (same model as the indexed table) and matched
with pgvector cosine distance (<=>). No external API needed for retrieval.
"""
from functools import lru_cache
from typing import Optional

import psycopg2

from . import config


@lru_cache(maxsize=1)
def _st_model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=config.EMBED_MODEL)


def embed_query(text: str) -> list[float]:
    """Embed the query with the configured provider — MUST match the indexed table's model.

    OpenAI embeddings (1536d) require an OpenAI key/quota; Groq has no embeddings API, so the
    query-side provider is sentence-transformers (local) or openai — never Groq.
    """
    if config.EMBED_PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        return client.embeddings.create(model=config.EMBED_MODEL, input=[text]).data[0].embedding
    return list(_st_model().embed([text]))[0].tolist()


def _vec_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vec) + "]"


def search_chunks(query: str, company_id: Optional[str] = None, top_k: int = 5) -> list[dict]:
    """Top-k most similar chunks (optionally scoped to a company). score = cosine similarity."""
    vec = _vec_literal(embed_query(query))
    sql = (f"SELECT source_url, chunk_text, 1 - (embedding <=> %s::vector) AS score "
           f"FROM {config.VECTOR_TABLE}")
    params: list = [vec]
    if company_id:
        sql += " WHERE company_id = %s"
        params.append(company_id)
    sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
    params += [vec, top_k]

    conn = psycopg2.connect(host=config.PG_HOST, port=config.PG_PORT, dbname=config.PG_DB,
                            user=config.PG_USER, password=config.PG_PASSWORD)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {"sourceUrl": r[0], "snippet": (r[1] or "").strip()[:400], "score": round(float(r[2]), 4)}
        for r in rows
    ]
