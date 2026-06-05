#!/usr/bin/env bash
# Run the CEF context-engine-service. Loads ./.env if present, starts uvicorn on :8093.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && { set -a; . ./.env; set +a; }
PORT="${PORT:-8093}"
echo "context-engine-service on :$PORT (reasoning=${CEF_AGENTIC_URL:-direct-llm})"
exec ./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
