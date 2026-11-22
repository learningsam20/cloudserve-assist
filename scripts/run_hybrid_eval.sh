#!/usr/bin/env bash
# Run validation (or named set) with RETRIEVAL_MODE=hybrid and export Grafana metrics.
#
# Usage:
#   ./scripts/run_hybrid_eval.sh
#   ./scripts/run_hybrid_eval.sh validation
#   LIMIT=20 ./scripts/run_hybrid_eval.sh validation
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage
require_pack

SET_NAME="${1:-validation}"
case "$SET_NAME" in
  validation|val)
    INPUT="$PACK_DATA/validation_tickets.json"
    TAG="validation_hybrid"
    ;;
  development|dev)
    INPUT="$PACK_DATA/development_tickets.json"
    TAG="development_hybrid"
    ;;
  *)
    INPUT="$SET_NAME"
    TAG="$(basename "$INPUT" .json)_hybrid"
    ;;
esac

if [[ ! -f "$INPUT" ]]; then
  echo "error: input not found: $INPUT" >&2
  exit 2
fi

# Ensure lexical index exists (hybrid needs it)
LEX="${LEXICAL_INDEX_PATH:-./storage/lexical_index.joblib}"
if [[ "$LEX" != /* ]]; then LEX="$ROOT/$LEX"; fi
if [[ ! -f "$LEX" ]]; then
  echo "==> lexical index missing — rebuilding dense+lexical index"
  DOCS="$PACK_DATA/documentation.json"
  "$PYTHON" -m scripts.build_index --input "$DOCS"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/evaluation/results/${TAG}_${STAMP}"
mkdir -p "$OUT"

ARGS=(--input "$INPUT" --output "$OUT")
if [[ "${GENERATE:-0}" != "1" ]]; then
  ARGS+=(--no-generate)
fi
if [[ -n "${LIMIT:-}" ]]; then
  ARGS+=(--limit "$LIMIT")
fi

echo "==> hybrid harness RETRIEVAL_MODE=hybrid input=$INPUT output=$OUT"
RETRIEVAL_MODE=hybrid "$PYTHON" -m evaluation.harness "${ARGS[@]}"
echo "hybrid" > "$OUT/retrieval_mode.txt"

# Also tag dense baseline snapshot for dashboard if fairness_fix exists
BASE="$ROOT/evaluation/results/validation_fairness_fix"
if [[ -f "$BASE/metrics.json" && ! -f "$BASE/retrieval_mode.txt" ]]; then
  echo "dense" > "$BASE/retrieval_mode.txt"
fi

echo "==> exporting Prometheus textfiles for Grafana"
"$PYTHON" -m scripts.export_eval_metrics --results-dir "$OUT" --retrieval-mode hybrid
if [[ -f "$BASE/metrics.json" ]]; then
  "$PYTHON" -m scripts.export_eval_metrics --results-dir "$BASE" --retrieval-mode dense
fi

echo ""
echo "metrics: $OUT/metrics.md"
echo "results: $OUT/results.jsonl"
echo "Grafana: refresh 'CloudServe — Eval dense vs hybrid' after ./scripts/grafana_up.sh"
