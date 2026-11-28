# CloudServe submission package checklist

Archive name: `FirstnameLastname_CloudServe_Release.zip`

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
# → ./_package/CloudServe_Assistant_Release/
# Add the recorded video to 01_Video, then zip (omit PACKAGE_NO_ZIP to let the script zip).
```

The script copies: report PDF + Markdown → `02_Report`; Stage workbooks, Effort Log (docx + md) and `human_eval_appendix.md` → `03_Workbooks`; `docs/video/README.md` and [demo.mp4](../video/demo.mp4) → `01_Video`.

## Source code gate (before zip)

- [ ] `.env` **not** in tree (gitignored); only `.env.example`
- [ ] `storage/` not needed in zip (regenerate via `setup_all`)
- [ ] `python -m pytest tests/ -v` passes
- [ ] `python -m evaluation.harness --input <validation> --output <dir> --no-generate` completes
- [ ] README clean-checkout path works
- [ ] Kill switch docs present under `docs/governance/`
- [ ] Threshold freeze noted (`docs/plan/threshold-freeze.md`)
- [ ] Fairness pass on validation (`docs/plan/eval-runs.md`)

## Video

- [x] Demonstration recorded — [docs/video/demo.mp4](../video/demo.mp4)

## Still operator-owned

- [ ] Create the zip (the package script can skip it with `PACKAGE_NO_ZIP=1`) and rename it with the release name (`FirstnameLastname_CloudServe_Release.zip`)
- [ ] In `01_Video/`, rename `demo.mp4` to `FirstnameLastname_CloudServe_Demo.mp4` if the Submission Guide requires that exact filename
- [ ] Confirm Effort Log PDF if the Guide requires `..._Effort_Log.pdf` (currently `.md` / `.docx` under `docs/workbooks/`)
- Optional: dual review of live generate-on drafts (see `docs/plan/gaps.md`)
