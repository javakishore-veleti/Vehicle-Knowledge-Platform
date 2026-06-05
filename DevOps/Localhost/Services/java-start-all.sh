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
    # Multi-module convention: the bootable Spring Boot app is the 'api' module.
    # Prefer the already-built fat jar (fast, reliable). Fall back to spring-boot:run
    # scoped to the api module only (NOT -am: that would run the goal on the non-app
    # modules too, which have no main class).
    jar=""
    if [[ -d "$svc_dir/api/target" ]]; then
      jar="$(find "$svc_dir/api/target" -maxdepth 1 -name '*.jar' ! -name '*.original' ! -name '*-plain.jar' 2>/dev/null | head -1)"
    fi
    if [[ -n "$jar" ]]; then
      ( cd "$svc_dir" && nohup java -jar "$jar" > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    elif [[ -f "$svc_dir/api/pom.xml" ]]; then
      echo "    (no jar yet — building/running via Maven; run 'mvn -q install' for faster starts)"
      ( cd "$svc_dir" && nohup $(mvn_cmd) -pl api spring-boot:run > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    else
      ( cd "$svc_dir" && nohup $(mvn_cmd) spring-boot:run > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    fi
    found=1
  done < <(find "$MIDDLEWARE" -maxdepth 2 -name pom.xml 2>/dev/null)
fi

if [[ "$found" -eq 0 ]]; then echo "==> No Java services found under Middleware/ yet (nothing to start)."; fi
