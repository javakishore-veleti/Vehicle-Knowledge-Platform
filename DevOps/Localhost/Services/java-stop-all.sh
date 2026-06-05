#!/usr/bin/env bash
# Stop all Spring Boot (Java) microservices started by java-start-all.sh.
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
    echo "==> Stopping $name (pid $pid)"
    kill "$pid" 2>/dev/null || true
  fi
  rm -f "$pidfile"
done

if [[ "$found" -eq 0 ]]; then echo "==> No running Java services tracked."; fi
