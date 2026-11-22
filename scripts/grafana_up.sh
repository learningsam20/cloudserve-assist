#!/usr/bin/env bash
# Start optional Grafana + Prometheus stack (demo only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OBS="$ROOT/observability"
mkdir -p "$OBS/prometheus/textfile"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker not found — install Docker Desktop to use optional Grafana" >&2
  exit 2
fi

# Seed textfiles so exporter has something to serve
if [[ ! -f "$OBS/prometheus/textfile/placeholder.prom" ]]; then
  echo '# cloudserve eval placeholder' > "$OBS/prometheus/textfile/placeholder.prom"
fi

echo "==> starting Grafana stack (ports 3000 / 9090 / 9101)"
docker compose -f "$OBS/docker-compose.yml" up -d
echo ""
echo "Grafana:    http://127.0.0.1:3000  (admin / cloudserve)"
echo "Prometheus: http://127.0.0.1:9090"
echo "Eval metrics exporter: http://127.0.0.1:9101/metrics"
echo ""
echo "Next: ./scripts/start_api.sh  # so Pipeline/Classification/Retrieval panels fill"
echo "      ./scripts/grafana_load_dashboards.sh"
echo "      ./scripts/export_eval_metrics.py --all"
