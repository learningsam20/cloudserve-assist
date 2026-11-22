#!/usr/bin/env bash
# Re-score CONFIDENCE_THRESHOLD candidates on development labels (findings D3).
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage
require_pack

OUT="${1:-$ROOT/storage/reports/threshold_tune.json}"
mkdir -p "$(dirname "$OUT")"
"$PYTHON" -m scripts.tune_threshold \
  --input "$PACK_DATA/development_tickets.json" \
  --output "$OUT"
echo "See docs/plan/threshold-freeze.md before changing a frozen value."
