"""pgvector retrieval over the indexed chunks — shared by every search-stage framework.

Same tables the indexing subsystem fills and the explore service reads (vec_<model>); the query is
embedded locally with fastembed (matching the indexed model), so no external API is needed to retrieve.
"""
import re
from functools import lru_cache
from typing import Optional

import psycopg2

from . import config

_TABLE_RE = re.compile(r"[a-z0-9_]{1,63}")


def _pg():
    return psycopg2.connect(host=config.PG_HOST, port=config.PG_PORT, dbname=config.PG_DB,
                            user=config.PG_USER, password=config.PG_PASSWORD)


@lru_cache(maxsize=1)
def _st_model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=config.EMBED_MODEL)


def _embed(text: str) -> list[float]:
    if config.EMBED_PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=config.OPENAI_API_KEY).embeddings.create(
            model=config.EMBED_MODEL, input=[text]).data[0].embedding
    return list(_st_model().embed([text]))[0].tolist()


def retrieve(query: str, company_id: Optional[str] = None, top_k: int = 5) -> list[dict]:
    """Top-k most similar indexed chunks. Returns [{sourceUrl, snippet, score}]."""
    table = config.VECTOR_TABLE
    if not _TABLE_RE.fullmatch(table):
        raise ValueError(f"unsafe vector table: {table!r}")
    vec = "[" + ",".join(str(x) for x in _embed(query)) + "]"
    sql = f"SELECT source_url, chunk_text, 1 - (embedding <=> %s::vector) AS score FROM {table}"
    params: list = [vec]
    if company_id:
        sql += " WHERE company_id = %s"
        params.append(company_id)
    sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
    params += [vec, top_k]

    conn = _pg()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()
    return [{"sourceUrl": r[0], "snippet": (r[1] or "").strip()[:400], "score": round(float(r[2]), 4)}
            for r in rows]


def context_block(results: list[dict]) -> str:
    """Render retrieved chunks as a numbered, citable SOURCES block for an agent prompt."""
    return "\n".join(f"[{i + 1}] {r['sourceUrl']}\n{r['snippet']}" for i, r in enumerate(results[:6]))
