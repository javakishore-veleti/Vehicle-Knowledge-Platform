"""vkp_index_sentence_transformers — Vehicles / Indexing.

The AIRFLOW executor for config-driven embedding + vector-store indexing. Triggered by
indexing-service (control plane) via airflow-adapter-service. It:
  1. reads a company's snapshot pages from data-collection-service,
  2. chunks + embeds the text via a per-formula provider:
       - sentence-transformers (default) -> fastembed (ONNX, no torch)
       - openai                          -> openai SDK (text-embedding-3-*, OPENAI_API_KEY)
  3. writes vectors into a per-model store (selected by conf indexed_to):
       - pgvector (default) -> per-model pgVector table   (vec_<model>)
       - mongodb            -> per-model Mongo collection  (vec_<model>)
  4. reports the chunk count back to the control plane's index-log callback.

Mirrors the SPRING_AI executor (wfs-java): provider via embedding_provider, store via
indexed_to. Each embedding model gets its own table/collection (vector_target), so
dimensions never clash. fastembed + psycopg2 + pgvector + openai + pymongo are all in the
custom Airflow image.

Expected conf (from indexing-service):
  { index_log_id, company_id, company_name, vector_target, embedding_provider, embedding_model,
    indexed_to, mongo_uri, params(JSON str), data_collection_base_url, callback_base_url,
    pg_host, pg_port, pg_db, pg_user, pg_password, openai_api_key(optional) }
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from datetime import datetime
from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

PAGES_PATH = "/admin/data-collection/service/v1/snapshots/{company}/pages"
GRAPH_PATH = "/admin/data-collection/service/v1/companies/{company_id}/resource-graph"
CALLBACK_PATH = "/admin/indexing/service/v1/index-logs/{log_id}/callback"
DEFAULT_DIM = 384
PAGE_LIMIT = 100
DEFAULT_OPENAI_MODEL = "text-embedding-3-small"
DEFAULT_MONGO_URI = "mongodb://host.docker.internal:27017/vkp?directConnection=true"


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "VKP-Indexer/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode(resp.headers.get_content_charset() or "utf-8", "replace")


def _post(url: str, payload: dict, timeout: int = 20) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        log.info("POST %s -> HTTP %s", url, resp.status)


def _fetch_pages(base_url: str, company: str) -> list[dict]:
    from urllib.parse import quote
    pages, offset = [], 0
    while True:
        url = (f"{base_url.rstrip('/')}{PAGES_PATH.format(company=quote(company))}"
               f"?offset={offset}&limit={PAGE_LIMIT}&full=true")
        batch = json.loads(_get(url))
        rows = batch.get("pages", [])
        pages.extend(rows)
        total = batch.get("total", len(pages))
        offset += PAGE_LIMIT
        if offset >= total or not rows:
            break
    return pages


def _allowed_urls(base_url: str, company_id: str, doc_ids: list) -> set | None:
    """Map selected resource_graph PKs -> their URLs. None = index the whole company."""
    if not doc_ids:
        return None
    url = f"{base_url.rstrip('/')}{GRAPH_PATH.format(company_id=company_id)}"
    nodes = json.loads(_get(url)).get("nodes", [])
    wanted = set(doc_ids)
    return {n.get("resourceUrl") for n in nodes if n.get("resourceGraphId") in wanted}


def _chunk(text: str, size: int, overlap: int) -> list[str]:
    if not text:
        return []
    step = max(1, size - overlap)
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def _embed_sentence_transformers(model_name: str, texts: list[str]) -> list[list[float]]:
    """fastembed (ONNX sentence-transformers) — local, no key. Returns lists of floats."""
    from fastembed import TextEmbedding
    model_id = model_name if "/" in model_name else f"sentence-transformers/{model_name}"
    log.info("Embedding %d chunk(s) with fastembed model=%s", len(texts), model_id)
    return [vec.tolist() for vec in TextEmbedding(model_name=model_id).embed(texts)]


def _embed_openai(model_name: str, api_key: str, texts: list[str]) -> list[list[float]]:
    """OpenAI embeddings (text-embedding-3-*) — needs OPENAI_API_KEY. Batches the inputs."""
    from openai import OpenAI
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set; cannot use the OpenAI embedding provider")
    model = model_name or DEFAULT_OPENAI_MODEL
    log.info("Embedding %d chunk(s) with OpenAI model=%s", len(texts), model)
    client = OpenAI(api_key=api_key)
    out: list[list[float]] = []
    batch = 256
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=model, input=texts[i:i + batch])
        out.extend(d.embedding for d in resp.data)
    return out


def _write_pgvector(conf: dict, vector_target: str, dim: int, company_id: str,
                    records: list, vectors: list) -> None:
    """Per-model pgVector table: clean re-index for the company, then insert chunk rows."""
    import psycopg2
    from pgvector.psycopg2 import register_vector

    conn = psycopg2.connect(host=conf.get("pg_host"), port=int(conf.get("pg_port") or 5432),
                            dbname=conf.get("pg_db"), user=conf.get("pg_user"), password=conf.get("pg_password"))
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {vector_target} ("
                f"id TEXT PRIMARY KEY, company_id TEXT, source_url TEXT, chunk_index INT, "
                f"chunk_text TEXT, embedding vector({dim}))"
            )
            # Full-text search support: a generated tsvector column + GIN index, so the
            # vehicle-explore service's fts/hybrid retrieval modes work over these rows without
            # re-embedding. Mirrors the SPRING_AI executor's PgVectorWriter.
            cur.execute(
                f"ALTER TABLE {vector_target} ADD COLUMN IF NOT EXISTS content_tsv tsvector "
                f"GENERATED ALWAYS AS (to_tsvector('english', coalesce(chunk_text, ''))) STORED"
            )
            cur.execute(f"CREATE INDEX IF NOT EXISTS {vector_target}_tsv_gin "
                        f"ON {vector_target} USING gin(content_tsv)")
            register_vector(conn)
            cur.execute(f"DELETE FROM {vector_target} WHERE company_id = %s", (company_id,))
            for (url, ci, text), vec in zip(records, vectors):
                cur.execute(
                    f"INSERT INTO {vector_target} (id, company_id, source_url, chunk_index, chunk_text, embedding) "
                    f"VALUES (%s, %s, %s, %s, %s, %s)",
                    (uuid4().hex, company_id, url, ci, text, list(vec)),
                )
        conn.commit()
    finally:
        conn.close()


def _write_mongodb(mongo_uri: str, vector_target: str, dim: int, company_id: str,
                   records: list, vectors: list) -> None:
    """Per-model Mongo collection: clean re-index for the company, then insert chunk docs.

    Mirrors wfs-java MongoVectorWriter doc shape: _id, companyId, sourceUrl, chunkIndex,
    chunkText, dim, embedding[list].
    """
    from pymongo import MongoClient

    client = MongoClient(mongo_uri)
    try:
        db = client.get_default_database()
        col = db[vector_target]
        col.delete_many({"companyId": company_id})   # clean re-index for this company
        docs = []
        for (url, ci, text), vec in zip(records, vectors):
            docs.append({
                "_id": uuid4().hex,
                "companyId": company_id,
                "sourceUrl": url,
                "chunkIndex": ci,
                "chunkText": text,
                "dim": dim,
                "embedding": [float(x) for x in vec],
            })
        if docs:
            col.insert_many(docs)
        log.info("Wrote %d vector doc(s) into MongoDB collection %s for company %s",
                 len(docs), vector_target, company_id)
    finally:
        client.close()


def index_company(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    log_id = conf.get("index_log_id")
    company_id = conf.get("company_id")
    company_name = conf.get("company_name")
    vector_target = conf.get("vector_target") or "vec_default"
    provider = (conf.get("embedding_provider") or "sentence-transformers").lower()
    model_name = conf.get("embedding_model") or "all-MiniLM-L6-v2"
    indexed_to = (conf.get("indexed_to") or "pgvector").lower()
    mongo_uri = conf.get("mongo_uri") or DEFAULT_MONGO_URI
    openai_api_key = conf.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    callback_base = conf.get("callback_base_url")
    dc_base = conf.get("data_collection_base_url")
    params = json.loads(conf.get("params") or "{}") if isinstance(conf.get("params"), str) else (conf.get("params") or {})
    chunk_size = int(params.get("chunk_size") or 512)
    chunk_overlap = int(params.get("chunk_overlap") or 64)
    dim = int(params.get("dim") or DEFAULT_DIM)

    def callback(status, chunks=None, error=None):
        if callback_base and log_id:
            _post(callback_base.rstrip("/") + CALLBACK_PATH.format(log_id=log_id),
                  {"status": status, "chunks": chunks, "error": error, "runRef": context["run_id"]})

    try:
        log.info("Indexing company '%s' -> %s (provider=%s model=%s store=%s dim=%d)",
                 company_name, vector_target, provider, model_name, indexed_to, dim)

        allowed = _allowed_urls(dc_base, company_id, conf.get("doc_ids") or [])
        pages = _fetch_pages(dc_base, company_name)
        if allowed is not None:
            pages = [p for p in pages if p.get("url") in allowed]
            log.info("Doc selection: %d of the company's pages match %d selected id(s)", len(pages), len(allowed))
        else:
            log.info("Whole-company scope: %d snapshot page(s)", len(pages))

        records = []  # (source_url, chunk_index, chunk_text)
        for p in pages:
            for ci, ch in enumerate(_chunk(p.get("text") or "", chunk_size, chunk_overlap)):
                records.append((p.get("url"), ci, ch))
        if not records:
            log.warning("No text chunks to index for '%s'", company_name)
            callback("INDEXED", chunks=0)
            return {"chunks": 0}

        texts = [r[2] for r in records]
        if provider == "openai":
            vectors = _embed_openai(model_name, openai_api_key, texts)
        else:
            vectors = _embed_sentence_transformers(model_name, texts)

        if indexed_to == "mongodb":
            _write_mongodb(mongo_uri, vector_target, dim, company_id, records, vectors)
        else:
            _write_pgvector(conf, vector_target, dim, company_id, records, vectors)

        log.info("Indexed %d chunk(s) into %s (%s)", len(records), vector_target, indexed_to)
        callback("INDEXED", chunks=len(records))
        return {"chunks": len(records)}
    except Exception as exc:  # noqa: BLE001
        log.exception("Indexing failed for '%s'", company_name)
        callback("FAILED", error=str(exc))
        raise


with DAG(
    dag_id="vkp_index_sentence_transformers",
    description="Chunk + embed a company's snapshot (sentence-transformers|openai) into a per-model pgVector table | MongoDB collection.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "indexing", "sentence-transformers"],
) as dag:
    PythonOperator(task_id="index_company", python_callable=index_company)
