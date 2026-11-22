#!/usr/bin/env bash
# Start FastAPI (uvicorn) in background — host/port from .env.
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "API already running (pid $(cat "$PID_FILE")) on port $API_PORT"
  exit 0
fi

nohup "$PYTHON" -m uvicorn src.api:app --host "$API_HOST" --port "$API_PORT" \
  >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

# Cold start can take >10s (torch / sentence-transformers import).
ok=0
for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 0.5
done

if [[ "$ok" -eq 1 ]]; then
  echo "API started pid=$(cat "$PID_FILE")  http://127.0.0.1:$API_PORT"
  echo "  logs: $LOG_FILE"
else
  echo "error: API did not become healthy — see $LOG_FILE" >&2
  if [[ -f "$PID_FILE" ]]; then
    kill "$(cat "$PID_FILE")" 2>/dev/null || true
    rm -f "$PID_FILE"
  fi
  exit 1
fi
