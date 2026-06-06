#!/usr/bin/env bash
# Stop and remove all localhost infrastructure containers.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Reverse order of startup. Observability is kept here (even though up/status skip it) so stop-all
# still tears down any observability containers that are currently running — freeing their memory/disk.
STACKS=(Observability Airflow Postgres MongoDB)

for stack in "${STACKS[@]}"; do
  f="$HERE/$stack/docker-compose.yaml"
  if [[ -f "$f" ]]; then
    echo "==> Stopping $stack"
    docker compose -f "$f" down
  fi
done

echo "==> All stacks stopped."
