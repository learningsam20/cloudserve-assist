#!/usr/bin/env bash
# Build Stage 1–5 + Effort_Log PDFs from Markdown (reportlab via docs/report/build_pdf.py).
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

WB="$ROOT/docs/workbooks"
for md in "$WB"/Stage_*.md "$WB"/Effort_Log.md; do
  [[ -f "$md" ]] || continue
  base="$(basename "$md" .md)"
  echo "Building ${base}.pdf ..."
  "$PYTHON" "$ROOT/docs/report/build_pdf.py" --input "$md" --output "$WB/${base}.pdf"
done
echo "Workbook PDFs ready under $WB"
