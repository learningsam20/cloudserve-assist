# Capstone submission package checklist

Archive name: `FirstnameLastname_Capstone_Submission.zip`

## Zip top-level (exact names)

| Folder | Contents |
|--------|----------|
| `01_Video` | Demo video (mp4 or link note) |
| `02_Report` | Graded report PDF/MD |
| `03_Workbooks` | Stage workbooks |
| `04_Source_Code` | This `submission/` tree (no `.env`, no secrets) |

## Assemble

```bash
cd submission
python docs/report/build_pdf.py                 # regenerate the report PDF
PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh   # assemble 01–04 folders, no zip
# → ../_package/CloudServe_Capstone_Submission/
# Add the recorded video to 01_Video, then zip (omit PACKAGE_NO_ZIP to let the script zip).
```

The script copies: report PDF + Markdown → `02_Report`; Stage workbooks, Effort Log (docx + md) and `human_eval_appendix.md` → `03_Workbooks`; `docs/video/README.md`, `video-script.md` and any recording → `01_Video`.

## Source code gate (before zip)

- [ ] `.env` **not** in tree (gitignored); only `.env.example`
- [ ] `storage/` not needed in zip (regenerate via `setup_all`)
- [ ] `python -m pytest tests/ -v` passes
- [ ] `python -m evaluation.harness --input <validation> --output <dir> --no-generate` completes
- [ ] README clean-checkout path works
- [ ] Kill switch docs present under `docs/governance/`
- [ ] Threshold freeze noted (`docs/plan/threshold-freeze.md`)
- [ ] Fairness pass on validation (`docs/plan/eval-runs.md`)

## Still student-owned

- Record the video (`docs/video/video-script.md`) and place it in `docs/video/` — **not yet recorded**
- Create the zip (the package script can skip it with `PACKAGE_NO_ZIP=1`) and rename it with the enrolment name
- Optional: live generate-on sample and dual review of live drafts (see `docs/plan/gaps.md`)
