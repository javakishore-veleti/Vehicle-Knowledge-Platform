"""vkp_index_sentence_transformers — Vehicles / Indexing.

The AIRFLOW executor for "sentence-transformers -> pgVector". Triggered by indexing-service
(control plane) via airflow-adapter-service. It:
  1. reads a company's snapshot pages from data-collection-service,
  2. chunks + embeds the text with fastembed (ONNX sentence-transformers, no torch),
  3. writes vectors into a per-model pgVector table (vec_<model>),
  4. reports the chunk count back to the control plane's index-log callback.

Each embedding model gets its own table (vector_target), so dimensions never clash.
Only fastembed + psycopg2 + pgvector are used (all in the custom Airflow image).

Expected conf (from indexing-service):
  { index_log_id, company_id, company_name, vector_target, embedding_model, params(JSON str),
    data_collection_base_url, callback_base_url, pg_host, pg_port, pg_db, pg_user, pg_password }
"""
from __future__ import annotations

import json
import logging
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
        url = f"{base_url.rstrip('/')}{PAGES_PATH.format(company=quote(company))}?offset={offset}&limit={PAGE_LIMIT}"
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


def index_company(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    log_id = conf.get("index_log_id")
    company_id = conf.get("company_id")
    company_name = conf.get("company_name")
    vector_target = conf.get("vector_target") or "vec_default"
    model_name = conf.get("embedding_model") or "all-MiniLM-L6-v2"
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
        from fastembed import TextEmbedding
        import psycopg2
        from pgvector.psycopg2 import register_vector

        model_id = model_name if "/" in model_name else f"sentence-transformers/{model_name}"
        log.info("Indexing company '%s' -> %s (model=%s dim=%d)", company_name, vector_target, model_id, dim)

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

        model = TextEmbedding(model_name=model_id)
        vectors = list(model.embed([r[2] for r in records]))

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
                register_vector(conn)
                cur.execute(f"DELETE FROM {vector_target} WHERE company_id = %s", (company_id,))
                for (url, ci, text), vec in zip(records, vectors):
                    cur.execute(
                        f"INSERT INTO {vector_target} (id, company_id, source_url, chunk_index, chunk_text, embedding) "
                        f"VALUES (%s, %s, %s, %s, %s, %s)",
                        (uuid4().hex, company_id, url, ci, text, vec.tolist()),
                    )
            conn.commit()
        finally:
            conn.close()

        log.info("Indexed %d chunk(s) into %s", len(records), vector_target)
        callback("INDEXED", chunks=len(records))
        return {"chunks": len(records)}
    except Exception as exc:  # noqa: BLE001
        log.exception("Indexing failed for '%s'", company_name)
        callback("FAILED", error=str(exc))
        raise


with DAG(
    dag_id="vkp_index_sentence_transformers",
    description="Chunk + embed a company's snapshot (fastembed) into a per-model pgVector table.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "indexing", "sentence-transformers"],
) as dag:
    PythonOperator(task_id="index_company", python_callable=index_company)
