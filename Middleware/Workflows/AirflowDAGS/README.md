# Airflow DAGs

All Airflow DAGs for VKP live here, organized **categorically by functionality and
data-management use case** rather than as a flat list. Airflow discovers DAGs recursively,
so sub-folders are fine.

Top-level grouping is by domain, then by data-management concept:

```text
AirflowDAGS/
  Vehicles/
    DataCollection/   # crawl LINKS ONLY from Company Resources; update the
                      # Company Resource (child) graph table. No content extraction.
    Ingestion/        # iterate each discovered link, fetch the ACTUAL content, and
                      # store it (local filesystem, AWS S3, or another blob/file server).
    Indexing/         # (add when needed) chunk + embed + index content into vector stores.
    VectorDbs/        # (add when needed) vector-store routing / maintenance DAGs.
```

Add new categories (e.g. `Refresh/`, `Enrichment/`) as new data-management use cases appear.
Each leaf folder holds the actual `*.py` DAG files for that use case.
