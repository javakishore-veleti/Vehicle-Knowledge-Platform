#!/usr/bin/env bash
# Serve the two static CEF portals.
set -euo pipefail
cd "$(dirname "$0")"
( cd cef-search-portal && exec python3 -m http.server 5173 ) &
( cd cef-admin-portal && exec python3 -m http.server 5174 ) &
echo "cef-search-portal -> http://localhost:5173 | cef-admin-portal -> http://localhost:5174 (Ctrl-C to stop)"
wait
