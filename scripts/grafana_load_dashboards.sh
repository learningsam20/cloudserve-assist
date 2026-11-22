#!/usr/bin/env bash
# Ensure dashboards are present and Grafana has reloaded provisioning.
# Dashboards are file-provisioned; this script re-syncs + optionally hits the API.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OBS="$ROOT/observability"
DASH_SRC="$OBS/grafana/dashboards"

if [[ ! -d "$DASH_SRC" ]]; then
  echo "error: missing $DASH_SRC" >&2
  exit 2
fi

echo "==> dashboards on disk:"
ls -1 "$DASH_SRC"/*.json

# Export any existing eval metrics so Eval dashboard has data
if [[ -d "$ROOT/evaluation/results" ]]; then
  echo "==> exporting eval metrics to prometheus textfile"
  PY="${PYTHON:-python3}"
  if command -v "$PY" >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
    PY="$(command -v "$PY" 2>/dev/null || command -v python3)"
    (cd "$ROOT" && "$PY" -m scripts.export_eval_metrics \
      --results-dir evaluation/results/validation_fairness_fix --retrieval-mode dense) || true
    HYBRID_LATEST="$(ls -1d "$ROOT"/evaluation/results/validation_hybrid_* 2>/dev/null | sort | tail -1 || true)"
    if [[ -n "${HYBRID_LATEST:-}" ]]; then
      (cd "$ROOT" && "$PY" -m scripts.export_eval_metrics \
        --results-dir "$HYBRID_LATEST" --retrieval-mode hybrid) || true
    fi
  else
    echo "warn: python3 not found — skip eval metrics export" >&2
  fi
fi

# Restart grafana so file provider re-reads (idempotent)
if docker ps --format '{{.Names}}' | grep -qx cloudserve-grafana; then
  echo "==> restarting grafana to pick up dashboards"
  docker restart cloudserve-grafana >/dev/null
  sleep 5
else
  echo "Grafana not running — start with ./scripts/grafana_up.sh"
  exit 0
fi

# Optional API ping (anonymous or admin)
if command -v curl >/dev/null 2>&1; then
  if curl -sf -u admin:cloudserve "http://127.0.0.1:3000/api/search?query=CloudServe" >/tmp/cs_grafana_search.json 2>/dev/null; then
    echo "==> Grafana search:"
    python3 -c "import json; d=json.load(open('/tmp/cs_grafana_search.json')); print('\n'.join(f\"  - {x.get('title')} ({x.get('uid')})\" for x in d) or '  (empty — wait ~30s for provisioner)')"
  else
    echo "Grafana API not ready yet; open http://127.0.0.1:3000 → Dashboards → CloudServe"
  fi
fi

echo "Done. Open http://127.0.0.1:3000 (folder: CloudServe)"
