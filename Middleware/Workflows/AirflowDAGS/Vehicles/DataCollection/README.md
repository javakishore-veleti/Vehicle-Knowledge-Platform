# Vehicles / DataCollection DAGs

**Purpose:** crawl **links only** from Company Resources.

These DAGs discover URLs (page links, sitemap entries, image/document URLs) and update the
Company Resource child/graph table (`company_resource_graph`) with the discovered nodes and
their crawl/discovery status. They do **not** fetch or extract full page content — that is
the job of the `Ingestion` DAGs.

Place link-discovery DAG `.py` files in this folder (e.g. `vkp_discover_resources.py`).
