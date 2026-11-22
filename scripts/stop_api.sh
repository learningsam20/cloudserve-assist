#!/usr/bin/env bash
# Stop background API started by start_api.sh.
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

if [[ ! -f "$PID_FILE" ]]; then
  echo "API not running (no pid file)"
  exit 0
fi

pid="$(cat "$PID_FILE")"
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid" || true
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" || true
  fi
  echo "API stopped (was pid $pid)"
else
  echo "stale pid file ($pid) — removed"
fi
rm -f "$PID_FILE"
