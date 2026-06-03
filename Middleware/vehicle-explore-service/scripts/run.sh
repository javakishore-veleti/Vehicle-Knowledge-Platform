#!/usr/bin/env bash
# Run vehicle-explore-service. Loads ./.env (if present) for provider config, then starts uvicorn.
# Copy .env.example -> .env and pick a profile (e.g. Groq LLM, OpenAI embeddings).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a; . ./.env; set +a
fi

PORT="${PORT:-8090}"
echo "vehicle-explore-service on :$PORT  (LLM=${VKP_LLM_MODEL:-gpt-4o-mini}@${VKP_LLM_BASE_URL:-openai}  embed=${VKP_EMBED_PROVIDER:-sentence-transformers}  store=${VKP_VECTOR_STORE:-pgvector})"
exec ./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
