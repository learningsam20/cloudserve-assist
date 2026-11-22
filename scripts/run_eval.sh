#!/usr/bin/env bash
# Run evaluation harness. Defaults: validation set, no LLM generate.
#
# Usage:
#   ./scripts/run_eval.sh
#   ./scripts/run_eval.sh validation
#   ./scripts/run_eval.sh development
#   ./scripts/run_eval.sh /path/to/tickets.json
#   GENERATE=1 ./scripts/run_eval.sh validation   # calls OpenRouter when auto_respond
#   LIMIT=20 ./scripts/run_eval.sh development
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage
require_pack

SET_NAME="${1:-validation}"
case "$SET_NAME" in
  validation|val)
    INPUT="$PACK_DATA/validation_tickets.json"
    TAG="validation"
    ;;
  development|dev)
    INPUT="$PACK_DATA/development_tickets.json"
    TAG="development"
    ;;
  *)
    INPUT="$SET_NAME"
    TAG="$(basename "$INPUT" .json)"
    ;;
esac

if [[ ! -f "$INPUT" ]]; then
  echo "error: input not found: $INPUT" >&2
  exit 2
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

echo "==> harness input=$INPUT output=$OUT"
"$PYTHON" -m evaluation.harness "${ARGS[@]}"
echo ""
echo "metrics: $OUT/metrics.md"
echo "results: $OUT/results.jsonl"
