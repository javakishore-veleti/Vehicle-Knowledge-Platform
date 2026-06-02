#!/usr/bin/env bash
# Start all Python (Flask / FastAPI) microservices found under Middleware/.
# A "service" is any direct child directory of Middleware/ that has a
# requirements.txt or pyproject.toml AND an app entrypoint (app/main.py or main.py).
# Each is started with uvicorn (FastAPI) if available, else `python main.py`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MIDDLEWARE="$ROOT/Middleware"
RUN_DIR="$ROOT/DevOps/Localhost/.run"
mkdir -p "$RUN_DIR"

found=0
if [[ -d "$MIDDLEWARE" ]]; then
  for svc_dir in "$MIDDLEWARE"/*/; do
    [[ -d "$svc_dir" ]] || continue
    name="$(basename "$svc_dir")"
    [[ "$name" == "Workflows" ]] && continue
    # Must look like a Python project.
    if [[ ! -f "$svc_dir/requirements.txt" && ! -f "$svc_dir/pyproject.toml" ]]; then
      continue
    fi
    pidfile="$RUN_DIR/python-$name.pid"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "==> $name already running (pid $(cat "$pidfile"))"; found=1; continue
    fi
    echo "==> Starting Python service: $name"
    if [[ -f "$svc_dir/app/main.py" ]]; then
      app="app.main:app"
    elif [[ -f "$svc_dir/main.py" ]]; then
      app="main:app"
    else
      echo "    (no main.py entrypoint found; skipping)"; continue
    fi
    ( cd "$svc_dir" && nohup python -m uvicorn "$app" --host 0.0.0.0 --port 0 \
        > "$RUN_DIR/python-$name.log" 2>&1 & echo $! > "$pidfile" )
    found=1
  done
fi

[[ "$found" -eq 0 ]] && echo "==> No Python services found under Middleware/ yet (nothing to start)."
