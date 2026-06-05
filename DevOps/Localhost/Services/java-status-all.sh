#!/usr/bin/env bash
# Show status of Spring Boot (Java) microservices started by java-start-all.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="$ROOT/DevOps/Localhost/.run"

found=0
for pidfile in "$RUN_DIR"/java-*.pid; do
  [[ -e "$pidfile" ]] || continue
  found=1
  name="$(basename "$pidfile" .pid)"
  pid="$(cat "$pidfile")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "UP    $name (pid $pid)"
  else
    echo "DOWN  $name (stale pid $pid)"
  fi
done

if [[ "$found" -eq 0 ]]; then echo "==> No Java services tracked."; fi
