#!/usr/bin/env bash
# Stop all Angular portals started by portals-start-all.sh (kills the npm + ng serve tree).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="$ROOT/DevOps/Localhost/.run"

# Recursively kill a process and its children (npm spawns ng serve).
kill_tree() {
  local p="$1"
  for c in $(pgrep -P "$p" 2>/dev/null || true); do kill_tree "$c"; done
  kill "$p" 2>/dev/null || true
}

shopt -s nullglob
found=0
for pidfile in "$RUN_DIR"/portal-*.pid; do
  name="$(basename "$pidfile" .pid)"; name="${name#portal-}"
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "==> Stopping $name (pid $pid)"; kill_tree "$pid"
  else
    echo "==> $name not running"
  fi
  rm -f "$pidfile"
  found=1
done
if [[ "$found" -eq 0 ]]; then
  echo "==> No portal pidfiles found (nothing to stop)."
fi
exit 0
