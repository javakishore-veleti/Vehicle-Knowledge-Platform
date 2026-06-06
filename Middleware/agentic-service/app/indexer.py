"""Write side of the index stage: embed agent-curated chunks and upsert them into pgvector — the
SAME vec_<model> table the search stage reads, so anything the index agent writes is immediately
searchable (scope by company_id). Embedding matches the indexed model (fastembed minilm, 384d).
"""
import re
from uuid import uuid4

from . import config, retrieval

_TABLE_RE = re.compile(r"[a-z0-9_]{1,63}")


def index_chunks(table: str, company_id: str, source_url: str, chunks: list[str]) -> int:
    """Clean-reindex (company_id, source_url): embed each chunk and insert. Returns rows written."""
    if not _TABLE_RE.fullmatch(table):
        raise ValueError(f"unsafe vector table: {table!r}")
    chunks = [c.strip() for c in chunks if c and c.strip()]
    if not chunks:
        return 0

    vectors = [retrieval._embed(c) for c in chunks]
    dim = len(vectors[0])

    conn = retrieval._pg()
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {config.VECTOR_SCHEMA}")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ("
                        f"id TEXT PRIMARY KEY, company_id TEXT, source_url TEXT, chunk_index INT, "
                        f"chunk_text TEXT, embedding vector({dim}))")
            cur.execute(f"DELETE FROM {table} WHERE company_id = %s AND source_url = %s",
                        (company_id, source_url))
            for i, (text, vec) in enumerate(zip(chunks, vectors)):
                lit = "[" + ",".join(str(x) for x in vec) + "]"
                cur.execute(
                    f"INSERT INTO {table} (id, company_id, source_url, chunk_index, chunk_text, embedding) "
                    f"VALUES (%s, %s, %s, %s, %s, %s::vector)",
                    (uuid4().hex, company_id, source_url, i, text[:4000], lit))
        conn.commit()
    finally:
        conn.close()
    return len(chunks)
