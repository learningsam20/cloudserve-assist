# CloudServe Capstone submission checklist

Public git repo (`cloudserve-assist` / this tree) keeps neutral names:

- Video: `docs/video/demo.mp4`
- Report PDF: `docs/report/CloudServe_Assistant_Report.pdf`

Hand-in names (assembled **outside** this repo; enrolment slug from packager default):

| Artifact | Name |
|----------|------|
| Archive | `FirstnameLastname_Capstone_Report.zip` |
| Video inside `01_Video/` | `FirstnameLastname_Capstone_Video.mp4` |
| Report inside `02_Report/` | `FirstnameLastname_Capstone_Report.pdf` |

## Zip top-level (four folders at zip root)

| Folder | Contents |
|--------|----------|
| `01_Video` | Enrolment-named video (+ README) |
| `02_Report` | Enrolment-named report PDF (+ Markdown source) |
| `03_Workbooks` | Stage 1–5 + Effort Log as **PDF** (+ md) |
| `04_Source_Code` | This repo including `.git` (no `.env`, no packaging script) |

## Assemble (parent Capstone workspace)

```bash
# from IIT_Capstone/ (parent of submission/)
cd submission && python docs/report/build_pdf.py && ./scripts/build_workbook_pdfs.sh && cd ..
./scripts/package_capstone_submission.sh
```

## Source code gate (validated 2026-11-28 — fresh GitHub clone)

- [x] `.env` not in tree; only `.env.example`
- [x] No API keys in working tree or git history
- [x] No packaging script under `scripts/` in this repo
- [x] Report in git is `CloudServe_Assistant_Report.pdf` (not enrolment-named)
- [x] Video in git is `demo.mp4` (renamed to enrolment video name only in `01_Video/` at package time)
- [x] README clean-checkout path works (`setup_all` → **28** pytest passed → validation **66/14**, API `/health` ok)
- [x] Hidden set provenance in report §8.7: **0 runs**, date N/A (assessor file not issued)
- [ ] When assessor issues the file: run **once**, update §8.7 date/count — no tuning
