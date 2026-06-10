# Airflow + Playwright (Chromium) for JS-rendered crawling.
# Built locally and referenced by docker-compose as image vkp-airflow:2.10.0-playwright.
FROM apache/airflow:2.10.0-python3.12

ARG PLAYWRIGHT_VERSION=1.48.0

# Chromium OS dependencies (installed as root; the Airflow image forbids pip-as-root,
# so the browser/python package are installed below as the airflow user).
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 \
      libcups2 libdrm2 libgbm1 libglib2.0-0 libpango-1.0-0 libcairo2 libasound2 \
      libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
      libxkbcommon0 libxshmfence1 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright + Chromium as the airflow user (browser cache lives in the user home).
# Also install embedding providers (fastembed = ONNX sentence-transformers, no torch; openai)
# + vector-store deps (pgVector via psycopg2; pymongo) for the config-driven indexing DAG,
# + cloud object-storage SDKs for the crawl-snapshot storage_backend toggle (s3 / azure / gcs).
USER airflow
RUN pip install --no-cache-dir \
      "playwright==${PLAYWRIGHT_VERSION}" \
      "fastembed>=0.3,<0.6" \
      "psycopg2-binary>=2.9" \
      "pgvector>=0.3" \
      "openai>=1.30" \
      "pymongo>=4.6" \
      "boto3>=1.34" \
      "azure-storage-blob>=12.19" "azure-identity>=1.16" \
      "google-cloud-storage>=2.16" \
    && playwright install chromium
