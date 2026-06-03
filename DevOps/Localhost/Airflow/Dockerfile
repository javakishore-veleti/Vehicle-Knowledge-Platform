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
# Also install lightweight embedding (fastembed = ONNX, no torch) + pgVector deps for the
# indexing DAGs.
USER airflow
RUN pip install --no-cache-dir \
      "playwright==${PLAYWRIGHT_VERSION}" \
      "fastembed>=0.3,<0.6" \
      "psycopg2-binary>=2.9" \
      "pgvector>=0.3" \
    && playwright install chromium
