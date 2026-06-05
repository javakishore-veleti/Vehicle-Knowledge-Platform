#!/usr/bin/env bash
# Stop all Spring Boot (Java) microservices started by java-start-all.sh.
# Kills each tracked pid's whole subtree (children first). The fat-jar path runs the JVM
# directly (tracked pid == JVM), but the `mvn spring-boot:run` fallback forks a child JVM,
# so killing only the tracked mvn pid would orphan that JVM onto its port.
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
for pidfile in "$RUN_DIR"/java-*.pid; do
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

if [[ "$found" -eq 0 ]]; then echo "==> No running Java services tracked."; fi
