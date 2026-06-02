"""vkp_process_resources — Vehicles / Ingestion.

Crawls the links that DataCollection discovered and extracts their CONTENT (title + text),
then calls back into ingestion-service to persist it into company_resource_content.

Flow:
  1. fetch discovered LINK nodes from data-collection-service (graph_base_url)
  2. for each (up to `limit`), fetch the page and extract title + clean text + sha256 hash
  3. POST the extracted items back to ingestion-service (callback_base_url)

Triggered (with conf) by ingestion-service via airflow-adapter-service.
Expected conf:
  {
    "company_id": "...", "company_resource_id": "...",
    "graph_base_url": "http://host.docker.internal:8084",
    "callback_base_url": "http://host.docker.internal:8085",
    "limit": 5
  }
Only stdlib is used (urllib + html.parser + hashlib).
"""
from __future__ import annotations

import hashlib
import json
import logging
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

DEFAULT_LIMIT = 5
MAX_TEXT = 20_000
GRAPH_PATH = "/admin/data-collection/service/v1/companies/{company_id}/resource-graph"
CALLBACK_PATH = "/admin/ingestion/service/v1/content/record"


class _ContentExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in ("script", "style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("script", "style", "noscript") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        elif self._skip == 0:
            piece = data.strip()
            if piece:
                self.text_parts.append(piece)


def _get(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "VKP-Ingestion/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read(2_000_000).decode(charset, errors="replace")


def _extract(html: str) -> tuple[str, str]:
    parser = _ContentExtractor()
    parser.feed(html)
    title = " ".join(" ".join(parser.title_parts).split())[:250]
    text = " ".join(" ".join(parser.text_parts).split())[:MAX_TEXT]
    return title, text


def process_resources(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    company_id = conf.get("company_id")
    company_resource_id = conf.get("company_resource_id")
    graph_base_url = conf.get("graph_base_url")
    callback_base_url = conf.get("callback_base_url")
    limit = int(conf.get("limit") or DEFAULT_LIMIT)

    if not (company_id and graph_base_url and callback_base_url):
        log.warning("Missing company_id/graph_base_url/callback_base_url in conf — nothing to do.")
        return {"processed": 0}

    # 1) discovered LINK nodes for this company (+ resource if provided)
    graph_url = graph_base_url.rstrip("/") + GRAPH_PATH.format(company_id=company_id)
    graph = json.loads(_get(graph_url))
    nodes = [
        n for n in graph.get("nodes", [])
        if n.get("resourceType") == "LINK"
        and (not company_resource_id or n.get("companyResourceId") == company_resource_id)
    ][:limit]
    log.info("Ingesting %d of %d discovered link(s)", len(nodes), graph.get("count", 0))

    # 2) crawl + extract content for each
    items = []
    for node in nodes:
        url = node.get("resourceUrl")
        if not url:
            continue
        try:
            title, text = _extract(_get(url))
            items.append({
                "resourceGraphId": node.get("resourceGraphId"),
                "sourceUrl": url,
                "title": title,
                "cleanText": text,
                "contentHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            })
            log.info("Extracted %d chars from %s", len(text), url)
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to crawl %s: %s", url, exc)

    # 3) persist via callback
    callback_url = callback_base_url.rstrip("/") + CALLBACK_PATH
    payload = json.dumps({
        "companyId": company_id,
        "companyResourceId": company_resource_id,
        "items": items,
    }).encode("utf-8")
    req = urllib.request.Request(callback_url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        log.info("Callback %s -> HTTP %s (%d items)", callback_url, resp.status, len(items))

    return {"processed": len(items)}


with DAG(
    dag_id="vkp_process_resources",
    description="Crawl discovered links and extract their content into company_resource_content.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "ingestion"],
) as dag:
    PythonOperator(task_id="process_resources", python_callable=process_resources)
