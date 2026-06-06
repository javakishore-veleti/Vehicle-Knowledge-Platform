#!/usr/bin/env bash
# Show status of all localhost infrastructure containers.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Observability disabled to save memory/disk — add "Observability" back to also show its containers.
STACKS=(MongoDB Postgres Airflow)
# STACKS=(MongoDB Postgres Airflow Observability)

for stack in "${STACKS[@]}"; do
  f="$HERE/$stack/docker-compose.yaml"
  if [[ -f "$f" ]]; then
    echo "==> $stack"
    docker compose -f "$f" ps
    echo
  fi
done
