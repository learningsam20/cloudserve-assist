#!/usr/bin/env bash
# Stop optional Grafana + Prometheus stack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
docker compose -f "$ROOT/observability/docker-compose.yml" down
echo "Grafana stack stopped."
