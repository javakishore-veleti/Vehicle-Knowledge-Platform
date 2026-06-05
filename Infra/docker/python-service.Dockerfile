# Build for any VKP Python FastAPI service (vehicle-explore-service, guardrails-service).
# Build context = the service root.
#
#   docker build -f Infra/docker/python-service.Dockerfile \
#     -t vkp/vehicle-explore-service:0.1.0 Middleware/vehicle-explore-service
#
# Heavy ML deps (fastembed, crewai, llama-index, haystack) live in requirements.txt; the build
# is large. Set PORT via env (default 8080).
FROM python:3.13-slim AS runtime

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# psycopg2-binary needs no build tools, but some transitive wheels do; keep it lean.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app/ app/

RUN useradd -r -u 1001 vkp && chown -R vkp /app
USER 1001
EXPOSE 8080
# app.main:app is the FastAPI entrypoint for both Python services.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
