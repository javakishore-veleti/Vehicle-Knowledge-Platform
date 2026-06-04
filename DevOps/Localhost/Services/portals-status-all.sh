#!/usr/bin/env bash
# Show status of all Angular portals started by portals-start-all.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="$ROOT/DevOps/Localhost/.run"

shopt -s nullglob
found=0
for pidfile in "$RUN_DIR"/portal-*.pid; do
  name="$(basename "$pidfile" .pid)"; name="${name#portal-}"
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "  UP    $name (pid $pid)"
  else
    echo "  DOWN  $name (stale pidfile)"
  fi
  found=1
done
if [[ "$found" -eq 0 ]]; then
  echo "  (no portals started via portals-start-all.sh)"
fi
exit 0
