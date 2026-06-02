#!/usr/bin/env bash
# Start all Spring Boot (Java) microservices found under Middleware/.
# A "service" is any directory under Middleware/ (excluding Workflows) that has a
# Maven build file (pom.xml). Each is started with Spring Boot and backgrounded;
# its PID is recorded under DevOps/Localhost/.run/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MIDDLEWARE="$ROOT/Middleware"
RUN_DIR="$ROOT/DevOps/Localhost/.run"
mkdir -p "$RUN_DIR"

mvn_cmd() { command -v mvn >/dev/null 2>&1 && echo "mvn" || echo "./mvnw"; }

found=0
if [[ -d "$MIDDLEWARE" ]]; then
  while IFS= read -r pom; do
    svc_dir="$(dirname "$pom")"
    # Skip nested module poms: only treat top-level service dirs (direct children of Middleware).
    case "$svc_dir" in
      "$MIDDLEWARE"/*/) ;;
    esac
    rel="${svc_dir#"$MIDDLEWARE"/}"
    [[ "$rel" == Workflows* ]] && continue
    # Only direct children of Middleware are services.
    [[ "$rel" == */* ]] && continue
    name="$(basename "$svc_dir")"
    pidfile="$RUN_DIR/java-$name.pid"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "==> $name already running (pid $(cat "$pidfile"))"; found=1; continue
    fi
    echo "==> Starting Java service: $name"
    ( cd "$svc_dir" && nohup $(mvn_cmd) spring-boot:run > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    found=1
  done < <(find "$MIDDLEWARE" -maxdepth 2 -name pom.xml 2>/dev/null)
fi

[[ "$found" -eq 0 ]] && echo "==> No Java services found under Middleware/ yet (nothing to start)."
