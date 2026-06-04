#!/usr/bin/env bash
# Run the guardrails service on :8091. VKP_GUARDRAILS_ENGINE = rules | groq | llmguard | auto.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && { set -a; . ./.env; set +a; }
PORT="${PORT:-8091}"
echo "guardrails-service on :$PORT (engine=${VKP_GUARDRAILS_ENGINE:-auto})"
exec ./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
