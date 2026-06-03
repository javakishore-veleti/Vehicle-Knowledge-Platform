# Vehicles / Crawl DAGs

**`vkp_crawl_company_snapshot`** — a real (Playwright/Chromium) headless-browser recursive
crawl that stores everything as a **filesystem snapshot**, so dropping Postgres never forces
a re-crawl.

## Why a snapshot (not Postgres)
Crawling is expensive and the automaker sites are JavaScript-rendered. The crawl output is
the durable source of truth on disk; the relational DBs hold only operational metadata.

## Layout (per company)
Under `VKP_CRAWL_SNAPSHOT_DIR` (host-mounted to
`~/runtime_data/ai_projects/Vehicle-Knowledge-Platform/Crawling-Snapshot`):

```text
<Company Name>/
  crawl-00001.json        # a JSON array of up to 250 page elements
  crawl-00002.json
  images/<uuid>.<ext>     # every downloaded image, named by UUID
  __COMPLETED__/manifest.json   # marker — its presence makes the DAG SKIP re-crawling
```

Each element:
```json
{ "url": "...", "depth": 0, "title": "...", "text": "...",
  "images": [ { "image_id": "<uuid>", "src": "https://…", "file": "images/<uuid>.jpg" } ],
  "links_count": 42, "fetched_at": "2026-…Z" }
```

## Inputs (DAG run conf)
- `company_id` (required) — roots are pulled from company-service (`/companies/{id}/resources`).
- `company_base_url` (default `http://host.docker.internal:8081`).
- `max_pages` (25), `max_depth` (1), `max_images_per_page` (8) — crawl bounds.
- `storage_backend` (`local` | `s3` | `azure` | `gcs`), `storage_location`.

## Storage toggle (local now, cloud later)
`local` writes to the mounted host folder. `s3` / `azure` / `gcs` are stubs — when the DAG
runs in AWS/Azure/GCP, enable the matching backend (add the SDK + creds and implement
`write_text`/`write_bytes`/`exists`) and pass `storage_location` (bucket/container). The DAG
logic is storage-agnostic.

## Idempotency
If `<Company>/__COMPLETED__` exists, the run is skipped. Delete that folder to force a re-crawl.

## Image / browser
Requires the custom Airflow image (`DevOps/Localhost/Airflow/Dockerfile`: Airflow + Playwright
+ Chromium). Build: `docker compose -f DevOps/Localhost/Airflow/docker-compose.yaml build`.
