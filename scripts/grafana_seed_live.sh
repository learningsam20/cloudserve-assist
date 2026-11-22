#!/usr/bin/env bash
# Seed live /metrics by processing validation tickets through the API (route-only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib.sh"
ensure_storage
require_pack

LIMIT="${LIMIT:-40}"
PORT="${API_PORT:-8000}"
API="http://127.0.0.1:${PORT}"

if ! curl -sf "$API/health" >/dev/null 2>&1; then
  echo "==> starting API"
  "$ROOT/scripts/start_api.sh"
  i=0
  while [[ $i -lt 30 ]]; do
    if curl -sf "$API/health" >/dev/null 2>&1; then
      break
    fi
    sleep 1
    i=$((i + 1))
  done
fi

echo "==> seeding ${LIMIT} validation tickets via /tickets/process (allow_generate=false)"
export CS_SEED_ROOT="$ROOT"
export CS_SEED_API="$API"
export CS_SEED_LIMIT="$LIMIT"
"$PYTHON" - <<'PY'
import json
import os
import urllib.request
from pathlib import Path

root = Path(os.environ["CS_SEED_ROOT"])
api = os.environ["CS_SEED_API"]
limit = int(os.environ["CS_SEED_LIMIT"])
tickets = json.loads((root / "datasets" / "validation_tickets.json").read_text())
if isinstance(tickets, dict):
    tickets = tickets.get("tickets") or tickets.get("data") or []
ok = err = 0
for t in tickets[:limit]:
    body = json.dumps({"ticket": t, "allow_generate": False}).encode()
    req = urllib.request.Request(
        api + "/tickets/process",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp.read()
        ok += 1
    except Exception as exc:  # noqa: BLE001
        err += 1
        if err <= 3:
            print("warn:", exc)
print(f"seeded ok={ok} err={err}")
print("metrics:", api + "/metrics")
PY
