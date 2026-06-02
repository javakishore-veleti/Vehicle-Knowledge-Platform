#!/usr/bin/env bash
# Show status of all localhost infrastructure containers.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STACKS=(MongoDB Postgres Airflow)

for stack in "${STACKS[@]}"; do
  f="$HERE/$stack/docker-compose.yaml"
  if [[ -f "$f" ]]; then
    echo "==> $stack"
    docker compose -f "$f" ps
    echo
  fi
done
