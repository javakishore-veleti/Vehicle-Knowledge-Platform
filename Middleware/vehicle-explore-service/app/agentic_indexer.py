"""Write side for the classic frameworks' index stage — embed agent-curated chunks into the search
table (vec_<model>) so they're immediately searchable. Reuses search.embed_query + search._pg."""
from uuid import uuid4

from . import config, search


def index_chunks(table: str, company_id: str, source_url: str, chunks: list[str]) -> int:
    table = search._safe_table(table)
    chunks = [c.strip() for c in chunks if c and c.strip()]
    if not chunks:
        return 0
    vectors = [search.embed_query(c) for c in chunks]
    dim = len(vectors[0])

    conn = search._pg()
    try:
        with conn.cursor() as cur:
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
