#!/usr/bin/env bash
# Assemble release zip layout (01_Video … 04_Source_Code) under ./_package/
# Does NOT include .env, storage/, or venv.
#
# Contents of each folder:
#   01_Video         docs/video/README.md + video-script.md (+ any recorded .mp4/.mov/.webm/.m4v in docs/video/)
#   02_Report        report PDF (docs/report/SameerJ_CloudServe_Report.pdf) + Markdown source
#   03_Workbooks     Stage 1–5 workbooks (.docx + .md), Effort_Log (.docx + .md), human_eval_appendix.md
#   04_Source_Code   this tree (minus secrets, storage, caches) + curated A10 metrics snapshot
#
# Environment:
#   PACKAGE_OUT=/path     output root (default: <repo>/_package)
#   PACKAGE_NO_ZIP=1      assemble the folder tree only; do not create the .zip
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

OUT_ROOT="${PACKAGE_OUT:-$ROOT/_package}"
BUNDLE="$OUT_ROOT/CloudServe_Assistant_Release"
SRC="$BUNDLE/04_Source_Code"

REPORT_PDF="$ROOT/docs/report/SameerJ_CloudServe_Report.pdf"
REPORT_MD="$ROOT/docs/report/CloudServe_Assistant_Report.md"
WORKBOOKS_DIR="$ROOT/docs/workbooks"
VIDEO_DIR="$ROOT/docs/video"

die() { echo "error: $*" >&2; exit 1; }

# ---- preflight: the artifacts the three non-code folders depend on ----------
if [[ ! -f "$REPORT_PDF" ]]; then
  echo "Report PDF missing; building it with docs/report/build_pdf.py ..."
  "$PYTHON" "$ROOT/docs/report/build_pdf.py" || die "could not build report PDF"
fi
[[ -f "$REPORT_PDF" ]] || die "report PDF not found: $REPORT_PDF"
[[ -f "$REPORT_MD" ]] || die "report Markdown not found: $REPORT_MD"

for f in Effort_Log.docx Effort_Log.md human_eval_appendix.md; do
  [[ -f "$WORKBOOKS_DIR/$f" ]] || die "workbook artifact missing: $WORKBOOKS_DIR/$f"
done
shopt -s nullglob
stage_docx=("$WORKBOOKS_DIR"/Stage_*.docx)
stage_md=("$WORKBOOKS_DIR"/Stage_*.md)
shopt -u nullglob
[[ ${#stage_docx[@]} -ge 5 ]] || die "expected 5 Stage_*.docx workbooks in $WORKBOOKS_DIR (found ${#stage_docx[@]})"
[[ ${#stage_md[@]} -ge 5 ]] || die "expected 5 Stage_*.md workbooks in $WORKBOOKS_DIR (found ${#stage_md[@]})"

for f in README.md video-script.md; do
  [[ -f "$VIDEO_DIR/$f" ]] || die "video artifact missing: $VIDEO_DIR/$f"
done

# ---- assemble ---------------------------------------------------------------
rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/01_Video" "$BUNDLE/02_Report" "$BUNDLE/03_Workbooks" "$SRC"

# 01_Video: README + script always; recording only if one exists (it is not recorded yet).
cp "$VIDEO_DIR/README.md" "$VIDEO_DIR/video-script.md" "$BUNDLE/01_Video/"
shopt -s nullglob nocaseglob
recordings=("$VIDEO_DIR"/*.mp4 "$VIDEO_DIR"/*.mov "$VIDEO_DIR"/*.webm "$VIDEO_DIR"/*.m4v)
shopt -u nullglob nocaseglob
if [[ ${#recordings[@]} -gt 0 ]]; then
  cp "${recordings[@]}" "$BUNDLE/01_Video/"
  echo "01_Video: included ${#recordings[@]} recording file(s)."
else
  echo "01_Video: NO recording found in docs/video/ — README + script only (record before final hand-in)."
fi

# 02_Report: PDF + Markdown source.
cp "$REPORT_PDF" "$REPORT_MD" "$BUNDLE/02_Report/"

# 03_Workbooks: Stage workbooks (docx + md), effort log (docx + md), human evaluation appendix.
cp "${stage_docx[@]}" "${stage_md[@]}" "$BUNDLE/03_Workbooks/"
cp "$WORKBOOKS_DIR/Effort_Log.docx" "$WORKBOOKS_DIR/Effort_Log.md" "$WORKBOOKS_DIR/human_eval_appendix.md" "$BUNDLE/03_Workbooks/"

# 04_Source_Code
rsync -a \
  --exclude '.env' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.deepeval' \
  --exclude 'storage/' \
  --exclude 'evaluation/results/*' \
  --exclude 'docs/video/*.mp4' \
  --exclude 'docs/video/*.mov' \
  --exclude 'docs/video/*.webm' \
  --exclude 'docs/video/*.m4v' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  "$ROOT/" "$SRC/"

mkdir -p "$SRC/evaluation/results"
touch "$SRC/evaluation/results/.gitkeep"

# Ship curated A10 evidence snapshots (route-only) — not live secrets/cache.
package_curated_metrics() {
  local src_dir="$1"
  local name
  name="$(basename "$src_dir")"
  if [[ -d "$src_dir" ]]; then
    mkdir -p "$SRC/evaluation/results/$name"
    rsync -a \
      --include 'metrics.json' \
      --include 'metrics.md' \
      --include 'run_summary.json' \
      --include 'retrieval_mode.txt' \
      --exclude '*' \
      "$src_dir/" "$SRC/evaluation/results/$name/"
    echo "Packaged curated metrics from $name (route-only; see fcr_claim_allowed)."
  fi
}
package_curated_metrics "$ROOT/evaluation/results/validation_fairness_fix"
# Prefer the latest hybrid validation folder if present
HYBRID_LATEST="$(ls -1d "$ROOT"/evaluation/results/validation_hybrid_* 2>/dev/null | sort | tail -1 || true)"
if [[ -n "${HYBRID_LATEST:-}" ]]; then
  package_curated_metrics "$HYBRID_LATEST"
fi

# ---- safety checks ----------------------------------------------------------
if [[ ! -f "$SRC/.env.example" ]]; then
  echo "error: .env.example missing from package" >&2
  exit 1
fi
if [[ -f "$SRC/.env" ]]; then
  echo "error: .env leaked into package" >&2
  exit 1
fi
if [[ -d "$SRC/storage" ]]; then
  echo "error: storage/ leaked into package" >&2
  exit 1
fi

# ---- zip (skippable) --------------------------------------------------------
if [[ "${PACKAGE_NO_ZIP:-0}" == "1" ]]; then
  echo "PACKAGE_NO_ZIP=1: folder tree assembled; zip NOT created."
  echo "Packaged:"
  echo "  $BUNDLE"
  echo "To zip later:  (cd \"$OUT_ROOT\" && zip -r CloudServe_Assistant_Release.zip CloudServe_Assistant_Release -x '*.DS_Store')"
else
  (
    cd "$OUT_ROOT"
    zip -r "CloudServe_Assistant_Release.zip" "CloudServe_Assistant_Release" \
      -x "*.DS_Store" >/dev/null
  )
  echo "Packaged:"
  echo "  $BUNDLE"
  echo "  $OUT_ROOT/CloudServe_Assistant_Release.zip"
  echo "Optional: rename zip for your release naming convention."
fi
echo "Optional: add a recorded demo video under 01_Video (script + README are included)."
