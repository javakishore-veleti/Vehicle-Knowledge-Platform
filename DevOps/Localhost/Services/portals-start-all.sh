#!/usr/bin/env bash
# Start all Angular portals under Portals/ (background `npm start`, track pids/logs in .run/).
# Each portal owns its dev-server port in its own package.json "start"
# (admin-portal :4200, vehicle-search-portal :4201). New portals should set their own --port.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ROOTS=("$ROOT/Portals" "$ROOT/ContextEnggFramework/Portals")
RUN_DIR="$ROOT/DevOps/Localhost/.run"
mkdir -p "$RUN_DIR"

found=0
for PORTALS in "${ROOTS[@]}"; do
  [[ -d "$PORTALS" ]] || continue
  for dir in "$PORTALS"/*/; do
    [[ -d "$dir" ]] || continue
    name="$(basename "$dir")"
    [[ -f "$dir/package.json" ]] || continue
    pidfile="$RUN_DIR/portal-$name.pid"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "==> $name already running (pid $(cat "$pidfile"))"; found=1; continue
    fi
    if [[ ! -d "$dir/node_modules" ]]; then
      echo "==> Installing deps for $name (first run)..."
      ( npm --prefix "$dir" install --no-audit --no-fund >"$RUN_DIR/portal-$name-install.log" 2>&1 )
    fi
    echo "==> Starting portal: $name"
    ( nohup npm --prefix "$dir" start >"$RUN_DIR/portal-$name.log" 2>&1 & echo $! >"$pidfile" )
    found=1
  done
done

if [[ "$found" -eq 0 ]]; then echo "==> No portals found."; fi
echo "Portals starting (logs in DevOps/Localhost/.run/portal-*.log):"
echo "    admin-portal           -> http://localhost:4200"
echo "    vehicle-search-portal  -> http://localhost:4201"
echo "    cef-portal (CEF)       -> http://localhost:4202"
