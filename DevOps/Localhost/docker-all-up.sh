#!/usr/bin/env bash
# Bring up all localhost infrastructure containers (MongoDB, Postgres+pgVector, Airflow).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Order matters: databases first, then Airflow (which depends on its own metadata DB).
# Observability (Jaeger/Prometheus/Grafana) is DISABLED here to save memory/disk on this laptop —
# add "Observability" back to the list to re-enable it.
STACKS=(MongoDB Postgres Airflow)
# STACKS=(MongoDB Postgres Airflow Observability)   # <- re-enable observability

for stack in "${STACKS[@]}"; do
  f="$HERE/$stack/docker-compose.yaml"
  if [[ -f "$f" ]]; then
    echo "==> Starting $stack"
    docker compose -f "$f" up -d
  else
    echo "==> Skipping $stack (no compose file at $f)"
  fi
done

echo "==> Done. Run 'npm run localhost:containers:status-all' to check."
