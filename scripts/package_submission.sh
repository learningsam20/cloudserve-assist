#!/usr/bin/env bash
# Assemble Capstone Submission Guide layout (01_Video … 04_Source_Code).
# Does NOT include .env, storage/, or venv. DOES include .git (history required).
#
# Contents of each folder:
#   01_Video         README + FirstnameLastname_Capstone_Video.mp4
#   02_Report        report PDF + Markdown source
#   03_Workbooks     Stage 1–5 workbooks (.docx + .md), Effort_Log (.docx + .md),
#                    human_eval_appendix.md
#   04_Source_Code   this tree (incl. .git; minus secrets/storage/caches) + curated metrics
#
# Environment:
#   PACKAGE_OUT=/path       output root (default: <repo>/_package)
#   STUDENT_SLUG=SameerJ    FirstnameLastname used in archive + video filenames
#   PACKAGE_NO_ZIP=1        assemble the four folders only; do not create the .zip
#
# Archive (Submission Guide): FirstnameLastname_Capstone_Submission.zip
# Zip root contains the four folders directly (no wrapper directory).
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

STUDENT_SLUG="${STUDENT_SLUG:-SameerJ}"
OUT_ROOT="${PACKAGE_OUT:-$ROOT/_package}"
BUNDLE="$OUT_ROOT/${STUDENT_SLUG}_Capstone_Submission"
SRC="$BUNDLE/04_Source_Code"
ZIP_NAME="${STUDENT_SLUG}_Capstone_Submission.zip"
VIDEO_NAME="${STUDENT_SLUG}_Capstone_Video.mp4"
REPORT_PDF_NAME="${STUDENT_SLUG}_Capstone_Report.pdf"

REPORT_PDF_SRC="$ROOT/docs/report/SameerJ_Capstone_Report.pdf"
# Prefer Capstone name; fall back to earlier CloudServe filename if present.
if [[ ! -f "$REPORT_PDF_SRC" && -f "$ROOT/docs/report/SameerJ_CloudServe_Report.pdf" ]]; then
  REPORT_PDF_SRC="$ROOT/docs/report/SameerJ_CloudServe_Report.pdf"
fi
REPORT_MD="$ROOT/docs/report/CloudServe_Assistant_Report.md"
WORKBOOKS_DIR="$ROOT/docs/workbooks"
VIDEO_DIR="$ROOT/docs/video"

die() { echo "error: $*" >&2; exit 1; }

# ---- preflight --------------------------------------------------------------
if [[ ! -f "$REPORT_PDF_SRC" ]]; then
  echo "Report PDF missing; building it with docs/report/build_pdf.py ..."
  "$PYTHON" "$ROOT/docs/report/build_pdf.py" || die "could not build report PDF"
  REPORT_PDF_SRC="$ROOT/docs/report/SameerJ_Capstone_Report.pdf"
fi
[[ -f "$REPORT_PDF_SRC" ]] || die "report PDF not found (expected SameerJ_Capstone_Report.pdf)"
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

[[ -f "$VIDEO_DIR/README.md" ]] || die "video artifact missing: $VIDEO_DIR/README.md"
shopt -s nullglob nocaseglob
recordings=("$VIDEO_DIR"/*.mp4 "$VIDEO_DIR"/*.mov "$VIDEO_DIR"/*.webm "$VIDEO_DIR"/*.m4v)
shopt -u nullglob nocaseglob
[[ ${#recordings[@]} -gt 0 ]] || die "no recording in $VIDEO_DIR (expected demo.mp4; replace after video revision)"
# Prefer a file already named correctly; else first recording (usually demo.mp4).
VIDEO_SRC=""
for f in "${recordings[@]}"; do
  if [[ "$(basename "$f")" == "$VIDEO_NAME" ]]; then
    VIDEO_SRC="$f"
    break
  fi
done
if [[ -z "$VIDEO_SRC" ]]; then
  VIDEO_SRC="${recordings[0]}"
fi

[[ -d "$ROOT/.git" ]] || die "04_Source_Code must include git history; .git missing in $ROOT"

# ---- assemble ---------------------------------------------------------------
rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/01_Video" "$BUNDLE/02_Report" "$BUNDLE/03_Workbooks" "$SRC"

# 01_Video: README + enrolment-named recording only.
cp "$VIDEO_DIR/README.md" "$BUNDLE/01_Video/"
cp "$VIDEO_SRC" "$BUNDLE/01_Video/$VIDEO_NAME"
echo "01_Video: $(basename "$VIDEO_SRC") → $VIDEO_NAME"

# 02_Report: PDF (enrolment name) + Markdown source.
cp "$REPORT_PDF_SRC" "$BUNDLE/02_Report/$REPORT_PDF_NAME"
cp "$REPORT_MD" "$BUNDLE/02_Report/"

# 03_Workbooks: Stage workbooks (docx + md), effort log, human evaluation appendix.
cp "${stage_docx[@]}" "${stage_md[@]}" "$BUNDLE/03_Workbooks/"
cp "$WORKBOOKS_DIR/Effort_Log.docx" "$WORKBOOKS_DIR/Effort_Log.md" "$WORKBOOKS_DIR/human_eval_appendix.md" "$BUNDLE/03_Workbooks/"

# 04_Source_Code — include .git (Submission Guide: complete repository + history).
rsync -a \
  --exclude '.env' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.deepeval' \
  --exclude 'storage/' \
  --exclude '_package/' \
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

# Ship curated A10 evidence snapshots — not live secrets/cache.
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
    echo "Packaged curated metrics from $name."
  fi
}
package_curated_metrics "$ROOT/evaluation/results/validation_fairness_fix"
HYBRID_LATEST="$(ls -1d "$ROOT"/evaluation/results/validation_hybrid_* 2>/dev/null | sort | tail -1 || true)"
if [[ -n "${HYBRID_LATEST:-}" ]]; then
  package_curated_metrics "$HYBRID_LATEST"
fi
GEN_ON="$(ls -1d "$ROOT"/evaluation/results/validation_20261122T131433Z 2>/dev/null | head -1 || true)"
if [[ -n "${GEN_ON:-}" ]]; then
  package_curated_metrics "$GEN_ON"
fi

# ---- safety checks ----------------------------------------------------------
[[ -f "$SRC/.env.example" ]] || die ".env.example missing from package"
[[ ! -f "$SRC/.env" ]] || die ".env leaked into package"
[[ ! -d "$SRC/storage" ]] || die "storage/ leaked into package"
[[ -d "$SRC/.git" ]] || die ".git missing from 04_Source_Code (history required)"
[[ -f "$BUNDLE/01_Video/$VIDEO_NAME" ]] || die "video missing: $BUNDLE/01_Video/$VIDEO_NAME"
[[ -f "$BUNDLE/02_Report/$REPORT_PDF_NAME" ]] || die "report PDF missing: $BUNDLE/02_Report/$REPORT_PDF_NAME"

# ---- zip (skippable) — four folders at zip root ------------------------------
if [[ "${PACKAGE_NO_ZIP:-0}" == "1" ]]; then
  echo "PACKAGE_NO_ZIP=1: folder tree assembled; zip NOT created."
  echo "Packaged:"
  echo "  $BUNDLE"
  echo "To zip later:"
  echo "  (cd \"$BUNDLE\" && zip -r \"../$ZIP_NAME\" 01_Video 02_Report 03_Workbooks 04_Source_Code -x '*.DS_Store')"
else
  rm -f "$OUT_ROOT/$ZIP_NAME"
  (
    cd "$BUNDLE"
    zip -r "$OUT_ROOT/$ZIP_NAME" 01_Video 02_Report 03_Workbooks 04_Source_Code \
      -x "*.DS_Store" >/dev/null
  )
  echo "Packaged:"
  echo "  $BUNDLE"
  echo "  $OUT_ROOT/$ZIP_NAME"
fi
echo "Submission Guide names: $ZIP_NAME · $VIDEO_NAME · $REPORT_PDF_NAME"
echo "Replace docs/video/demo.mp4 after video revision, then re-run this script."
