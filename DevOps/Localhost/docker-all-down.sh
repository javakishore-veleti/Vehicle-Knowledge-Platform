#!/usr/bin/env bash
# Stop and remove all localhost infrastructure containers.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Reverse order of startup.
STACKS=(Observability Airflow Postgres MongoDB)

for stack in "${STACKS[@]}"; do
  f="$HERE/$stack/docker-compose.yaml"
  if [[ -f "$f" ]]; then
    echo "==> Stopping $stack"
    docker compose -f "$f" down
  fi
done

echo "==> All stacks stopped."
