#!/usr/bin/env bash
# Stop all Python microservices started by python-start-all.sh.
# Kills each tracked pid's whole subtree (children first), so any uvicorn worker /
# reloader children can't outlive the tracked parent and orphan onto a port.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="$ROOT/DevOps/Localhost/.run"

# Recursively kill a pid and all its descendants, leaves first.
kill_tree() {
  local pid="$1" kid
  for kid in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$kid"
  done
  kill "$pid" 2>/dev/null || true
}

found=0
for pidfile in "$RUN_DIR"/python-*.pid; do
  [[ -e "$pidfile" ]] || continue
  found=1
  name="$(basename "$pidfile" .pid)"
  pid="$(cat "$pidfile")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "==> Stopping $name (pid $pid + descendants)"
    kill_tree "$pid"
  fi
  rm -f "$pidfile"
done

if [[ "$found" -eq 0 ]]; then echo "==> No running Python services tracked."; fi
