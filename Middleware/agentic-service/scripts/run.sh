#!/usr/bin/env bash
# Run the agentic-service. Loads ./.env (if present), then starts uvicorn on :8092.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && { set -a; . ./.env; set +a; }
PORT="${PORT:-8092}"
echo "agentic-service on :$PORT (frameworks load on import)"
exec ./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
