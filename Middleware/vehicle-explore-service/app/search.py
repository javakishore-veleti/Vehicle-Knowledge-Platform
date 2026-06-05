"""Retrieval over the pgVector embeddings produced by the indexing subsystem.

Three retrieval modes over the same vec_<model> tables (selected per-request, see frameworks._retrieve):
  - vector : pgvector cosine distance (<=>) over the query embedding (default).
  - fts    : Postgres full-text search (tsvector @@ websearch_to_tsquery), ranked by ts_rank_cd.
  - hybrid : Reciprocal-Rank-Fusion of the vector + fts result lists.

The query is embedded locally with fastembed (same model as the indexed table); no external API
is needed for vector retrieval, and FTS needs no embedding at all. `ensure_fts()` lazily adds the
generated tsvector column + GIN index, so keyword/hybrid search works over already-indexed rows
without re-embedding them.
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


def _safe_table(table: str) -> str:
    if not _TABLE_RE.fullmatch(table):
        raise ValueError(f"unsafe vector table name: {table!r}")
    return table


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


def _rows_to_results(rows) -> list[dict]:
    return [
        {"sourceUrl": r[0], "snippet": (r[1] or "").strip()[:400], "score": round(float(r[2]), 4)}
        for r in rows
    ]


# A cache of tables we've already FTS-prepared this process, to skip the DDL round-trip.
_fts_ready: set[str] = set()


def ensure_fts(table: str) -> None:
    """Idempotently add a generated `content_tsv` tsvector column + GIN index to a vec_<model>
    table, so keyword/hybrid search works over already-indexed rows without re-embedding them.
    Safe to call repeatedly; cached per-process after the first success."""
    table = _safe_table(table)
    if table in _fts_ready:
        return
    conn = _pg()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS content_tsv tsvector "
                f"GENERATED ALWAYS AS (to_tsvector('english', coalesce(chunk_text, ''))) STORED")
            cur.execute(f"CREATE INDEX IF NOT EXISTS {table}_tsv_gin ON {table} USING gin(content_tsv)")
        conn.commit()
        _fts_ready.add(table)
    finally:
        conn.close()


def search_chunks(query: str, company_id: Optional[str] = None, top_k: int = 5) -> list[dict]:
    """vector mode: top-k most similar chunks (optionally scoped to a company). score = cosine similarity."""
    table = _safe_table(config.VECTOR_TABLE)
    vec = _vec_literal(embed_query(query))
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
    return _rows_to_results(rows)


def _or_tsquery(query: str) -> str:
    """Build an OR tsquery string from the query's word tokens (e.g. 'hybrid | suv | drive').

    OR-recall is what a keyword path should contribute alongside vector search; ts_rank_cd then
    ranks by how many terms match and how close they are. Tokens are stripped to [A-Za-z0-9] so
    nothing special ever reaches to_tsquery() (injection-safe); English stopwords are dropped by
    to_tsquery itself. Returns '' when the query has no usable lexemes."""
    return " | ".join(re.findall(r"[A-Za-z0-9]+", query.lower()))


def search_chunks_fts(query: str, company_id: Optional[str] = None, top_k: int = 5) -> list[dict]:
    """fts mode: Postgres full-text search over chunk_text (OR-recall), ranked by ts_rank_cd. No embedding."""
    table = _safe_table(config.VECTOR_TABLE)
    ensure_fts(table)
    tsq = _or_tsquery(query)
    if not tsq:
        return []
    sql = (f"SELECT source_url, chunk_text, ts_rank_cd(content_tsv, q) AS score "
           f"FROM {table}, to_tsquery('english', %s) AS q "
           f"WHERE content_tsv @@ q")
    params: list = [tsq]
    if company_id:
        sql += " AND company_id = %s"
        params.append(company_id)
    sql += " ORDER BY score DESC LIMIT %s"
    params.append(top_k)

    conn = _pg()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()
    return _rows_to_results(rows)


def search_chunks_hybrid(query: str, company_id: Optional[str] = None, top_k: int = 5,
                         k_rrf: int = 60) -> list[dict]:
    """hybrid mode: Reciprocal Rank Fusion of vector + fts. Each list contributes 1/(k_rrf+rank);
    documents found by both rank highest. score = the fused RRF score (not a similarity)."""
    pool = max(top_k * 4, 20)
    vec_hits = search_chunks(query, company_id, pool)
    try:
        fts_hits = search_chunks_fts(query, company_id, pool)
    except Exception:  # noqa: BLE001 — if FTS can't run (e.g. empty tsquery), fall back to vector
        return vec_hits[:top_k]

    fused: dict[tuple, float] = {}
    meta: dict[tuple, dict] = {}
    for hits in (vec_hits, fts_hits):
        for rank, r in enumerate(hits):
            key = (r["sourceUrl"], r["snippet"])
            fused[key] = fused.get(key, 0.0) + 1.0 / (k_rrf + rank + 1)
            meta.setdefault(key, r)
    ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [{**meta[key], "score": round(score, 6)} for key, score in ranked]
