"""Integration with the platform's Java services, so the agentic stages become real pipeline steps:
  - collect persists discovered links to data-collection-service's company_resource_graph
    (POST .../graph/record — mirrors the vkp_discover_resources DAG callback)
  - index reports to indexing-service's resource_graph_index_log ledger
    (POST .../index-logs/{id}/callback)
Both endpoints are permit-listed (no JWT). Both integrations are OPT-IN (need the platform ids) and
best-effort — a failure is reported in the response, never fatal.
"""
import json
import os
import urllib.request

DATA_COLLECTION_URL = os.getenv("VKP_DATA_COLLECTION_URL", "http://localhost:8084")
INDEXING_URL = os.getenv("VKP_INDEXING_URL", "http://localhost:8086")
GRAPH_RECORD = "/admin/data-collection/service/v1/graph/record"
INDEX_CALLBACK = "/admin/indexing/service/v1/index-logs/{id}/callback"


def _post(url: str, payload: dict, timeout: int = 15) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8") or "{}")


def record_graph(company_id: str, company_resource_id: str, parent_resource_graph_id: str,
                 links: list[str], status: str = "DISCOVERED") -> dict:
    """Persist discovered link URLs into company_resource_graph (returns {added, parentResourceGraphId})."""
    return _post(DATA_COLLECTION_URL.rstrip("/") + GRAPH_RECORD, {
        "companyId": company_id, "companyResourceId": company_resource_id,
        "parentResourceGraphId": parent_resource_graph_id, "status": status, "links": links})


def index_callback(index_log_id: str, status: str, chunks: int | None = None,
                   error: str | None = None, run_ref: str | None = None) -> dict:
    """Update an indexing-service ledger row (status IN_PROGRESS | INDEXED | FAILED)."""
    return _post(INDEXING_URL.rstrip("/") + INDEX_CALLBACK.format(id=index_log_id),
                 {"status": status, "chunks": chunks, "error": error, "runRef": run_ref})
