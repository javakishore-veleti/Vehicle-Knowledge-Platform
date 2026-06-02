"""vkp_discover_resources — Vehicles / DataCollection.

Discovers links ONLY from a company resource (page links, sitemap entries, image/document
URLs) and is intended to update the company_resource_graph child table. It does NOT fetch or
extract page content — that is the Ingestion DAGs' job.

Triggered (with conf) by data-collection-service via airflow-adapter-service.
Expected conf: {"company_id": "...", "company_resource_id": "...", "seed_url": "https://..."}

v1 simulates discovery (logs the would-be links). Real crawling + persistence to
company_resource_graph is a follow-up.
"""
from __future__ import annotations

import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)


def discover_links(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    company_id = conf.get("company_id")
    company_resource_id = conf.get("company_resource_id")
    seed_url = conf.get("seed_url")
    log.info(
        "Discovering links: company_id=%s company_resource_id=%s seed_url=%s",
        company_id, company_resource_id, seed_url,
    )
    # v1: simulate discovery. Replace with a real crawler that writes to company_resource_graph.
    discovered = [f"{seed_url.rstrip('/')}/page-{i}" for i in range(1, 4)] if seed_url else []
    log.info("Discovered %d link(s): %s", len(discovered), discovered)
    return {"discovered_count": len(discovered), "links": discovered}


with DAG(
    dag_id="vkp_discover_resources",
    description="Discover links only from a company resource; update the resource graph.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "data-collection"],
) as dag:
    PythonOperator(task_id="discover_links", python_callable=discover_links)
