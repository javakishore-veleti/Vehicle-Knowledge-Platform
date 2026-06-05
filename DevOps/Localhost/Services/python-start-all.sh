#!/usr/bin/env bash
# Start all Python (Flask / FastAPI) microservices found under Middleware/.
# A "service" is any direct child directory of Middleware/ that has a
# requirements.txt or pyproject.toml.
#
# Each service is started by its OWN scripts/run.sh when present — that script is
# authoritative: it picks the service's .venv, its fixed PORT (e.g. explore 8090,
# guardrails 8091), and loads the service's .env (provider keys, VKP_SESSION_SECRET).
# run.sh ends in `exec`, so the pid we capture is the live uvicorn process.
#
# Services without a scripts/run.sh fall back to a generic uvicorn launch (app/main.py
# or main.py) using the service .venv if present; without a declared port these get an
# OS-assigned port (a warning is logged) — add a scripts/run.sh to pin one.
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
    logfile="$RUN_DIR/python-$name.log"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "==> $name already running (pid $(cat "$pidfile"))"; found=1; continue
    fi

    if [[ -f "$svc_dir/scripts/run.sh" ]]; then
      echo "==> Starting Python service: $name (scripts/run.sh)"
      ( cd "$svc_dir" && nohup bash scripts/run.sh > "$logfile" 2>&1 & echo $! > "$pidfile" )
      found=1
      continue
    fi

    # --- generic fallback (no scripts/run.sh) ---
    if [[ -f "$svc_dir/app/main.py" ]]; then
      app="app.main:app"
    elif [[ -f "$svc_dir/main.py" ]]; then
      app="main:app"
    else
      echo "==> $name: no scripts/run.sh and no main.py entrypoint; skipping"; continue
    fi
    py="python"
    [[ -x "$svc_dir/.venv/bin/python" ]] && py="$svc_dir/.venv/bin/python"
    echo "==> Starting Python service: $name (generic uvicorn; no scripts/run.sh -> OS-assigned port)"
    ( cd "$svc_dir" && nohup "$py" -m uvicorn "$app" --host 0.0.0.0 --port 0 \
        > "$logfile" 2>&1 & echo $! > "$pidfile" )
    found=1
  done
fi

if [[ "$found" -eq 0 ]]; then echo "==> No Python services found under Middleware/ yet (nothing to start)."; fi
