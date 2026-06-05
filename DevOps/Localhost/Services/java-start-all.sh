#!/usr/bin/env bash
# Start all Spring Boot (Java) microservices found under Middleware/ and ContextEnggFramework/Middleware/.
# A "service" is any direct-child directory (excluding Workflows) with a pom.xml. Each is started and
# backgrounded; its PID is recorded under DevOps/Localhost/.run/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="$ROOT/DevOps/Localhost/.run"
mkdir -p "$RUN_DIR"

ROOTS=("$ROOT/Middleware" "$ROOT/ContextEnggFramework/Middleware")

mvn_cmd() { command -v mvn >/dev/null 2>&1 && echo "mvn" || echo "./mvnw"; }

found=0
for MIDDLEWARE in "${ROOTS[@]}"; do
  [[ -d "$MIDDLEWARE" ]] || continue
  for svc_dir in "$MIDDLEWARE"/*/; do
    svc_dir="${svc_dir%/}"
    name="$(basename "$svc_dir")"
    [[ "$name" == "Workflows" ]] && continue
    [[ -f "$svc_dir/pom.xml" ]] || continue
    # Only BOOTABLE Spring services — skip the shared libraries (vkp-jwt-rbac, vkp-session-security):
    # a service has an `api/` module OR the spring-boot-maven-plugin in its own pom.
    [[ -d "$svc_dir/api" ]] || grep -q "spring-boot-maven-plugin" "$svc_dir/pom.xml" || continue

    pidfile="$RUN_DIR/java-$name.pid"
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "==> $name already running (pid $(cat "$pidfile"))"; found=1; continue
    fi
    echo "==> Starting Java service: $name"
    # Prefer an already-built fat jar — multi-module (api/target) or single-module (target).
    jar=""
    for tdir in "$svc_dir/api/target" "$svc_dir/target"; do
      [[ -d "$tdir" ]] || continue
      jar="$(find "$tdir" -maxdepth 1 -name '*.jar' ! -name '*.original' ! -name '*-plain.jar' 2>/dev/null | head -1)"
      [[ -n "$jar" ]] && break
    done
    if [[ -n "$jar" ]]; then
      ( cd "$svc_dir" && nohup java -jar "$jar" > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    elif [[ -f "$svc_dir/api/pom.xml" ]]; then
      echo "    (no jar yet — building via Maven api module; run 'mvn -q install' for faster starts)"
      ( cd "$svc_dir" && nohup $(mvn_cmd) -pl api spring-boot:run > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    else
      echo "    (no jar yet — building via Maven; run 'mvn -q package' for faster starts)"
      ( cd "$svc_dir" && nohup $(mvn_cmd) spring-boot:run > "$RUN_DIR/java-$name.log" 2>&1 & echo $! > "$pidfile" )
    fi
    found=1
  done
done

if [[ "$found" -eq 0 ]]; then echo "==> No Java services found yet (nothing to start)."; fi
