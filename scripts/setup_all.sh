#!/usr/bin/env bash
# Train classifier + build Chroma index (one-time / refresh).
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage
require_pack

echo "==> train classifier"
"$PYTHON" -m scripts.train_classifier \
  --input "$PACK_DATA/development_tickets.json" \
  --output "$ROOT/storage/models/classifier"

echo "==> build retrieval index"
"$PYTHON" -m scripts.build_index \
  --input "$PACK_DATA/documentation.json"

echo "setup complete."
