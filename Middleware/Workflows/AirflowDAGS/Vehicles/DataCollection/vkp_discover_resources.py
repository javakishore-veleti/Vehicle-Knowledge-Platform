"""vkp_discover_resources — Vehicles / DataCollection.

Discovers links ONLY from a company resource: fetches the seed URL, extracts <a href>
links, and calls back into data-collection-service to persist them as children of the
seed node in company_resource_graph. It does NOT fetch/extract page *content* — that is
the Ingestion DAGs' job.

Triggered (with conf) by data-collection-service via airflow-adapter-service.
Expected conf:
  {
    "company_id": "...", "company_resource_id": "...",
    "seed_url": "https://...", "resource_graph_id": "<root node id>",
    "callback_base_url": "http://host.docker.internal:8084"
  }
Only stdlib is used (urllib + html.parser) so no extra Airflow image deps are required.
"""
from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

MAX_LINKS = 25000
CALLBACK_PATH = "/admin/data-collection/service/v1/graph/record"


class _LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href" and value:
                    self.hrefs.append(value)


def _fetch_links(seed_url: str) -> list[str]:
    req = urllib.request.Request(seed_url, headers={"User-Agent": "VKP-Discovery/0.1"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        html = resp.read(1_000_000).decode(charset, errors="replace")
    parser = _LinkExtractor()
    parser.feed(html)
    seen: set[str] = set()
    links: list[str] = []
    for href in parser.hrefs:
        absolute = urljoin(seed_url, href)
        if urlparse(absolute).scheme in ("http", "https") and absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
            if len(links) >= MAX_LINKS:
                break
    return links


def _callback(base_url: str, payload: dict) -> None:
    url = base_url.rstrip("/") + CALLBACK_PATH
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        log.info("Callback %s -> HTTP %s", url, resp.status)


def discover_links(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    company_id = conf.get("company_id")
    company_resource_id = conf.get("company_resource_id")
    seed_url = conf.get("seed_url")
    parent_id = conf.get("resource_graph_id")
    callback_base_url = conf.get("callback_base_url")

    log.info("Discovering: company=%s resource=%s seed=%s root=%s",
             company_id, company_resource_id, seed_url, parent_id)

    status = "DISCOVERED"
    links: list[str] = []
    if seed_url:
        try:
            links = _fetch_links(seed_url)
            log.info("Discovered %d link(s): %s", len(links), links)
        except Exception as exc:  # noqa: BLE001 - report failure back to the service
            status = "FAILED"
            log.warning("Crawl failed for %s: %s", seed_url, exc)

    if callback_base_url and parent_id:
        _callback(callback_base_url, {
            "companyId": company_id,
            "companyResourceId": company_resource_id,
            "parentResourceGraphId": parent_id,
            "status": status,
            "links": links,
        })
    else:
        log.info("No callback_base_url/resource_graph_id in conf — skipping persistence.")

    return {"discovered_count": len(links), "status": status}


with DAG(
    dag_id="vkp_discover_resources",
    description="Discover links only from a company resource; update the resource graph.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "data-collection"],
) as dag:
    PythonOperator(task_id="discover_links", python_callable=discover_links)
