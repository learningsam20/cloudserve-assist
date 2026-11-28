# CloudServe Capstone submission checklist

Public git repo (`cloudserve-assist` / this tree) keeps neutral names:

- Video: `docs/video/demo.mp4`
- Report PDF: `docs/report/CloudServe_Assistant_Report.pdf`

Hand-in names (assembled **outside** this repo):

| Artifact | Name |
|----------|------|
| Archive | `SameerJoshi_Capstone_Report.zip` |
| Video inside `01_Video/` | `SameerJoshi_Capstone_Video.mp4` |
| Report inside `02_Report/` | `SameerJoshi_Capstone_Report.pdf` |

## Zip top-level (four folders at zip root)

| Folder | Contents |
|--------|----------|
| `01_Video` | `SameerJoshi_Capstone_Video.mp4` (+ README) |
| `02_Report` | `SameerJoshi_Capstone_Report.pdf` (+ Markdown source) |
| `03_Workbooks` | Stage 1–5 + Effort Log as **PDF** (+ md) |
| `04_Source_Code` | This repo including `.git` (no `.env`, no packaging script) |

## Assemble (parent Capstone workspace)

```bash
# from IIT_Capstone/ (parent of submission/)
cd submission && python docs/report/build_pdf.py && ./scripts/build_workbook_pdfs.sh && cd ..
./scripts/package_capstone_submission.sh
# → _package/SameerJoshi_Capstone_Submission/
# → _package/SameerJoshi_Capstone_Report.zip
```

## Source code gate

- [ ] `.env` not in tree; only `.env.example`
- [ ] No API keys in working tree or git history
- [ ] No packaging script under `scripts/` in this repo
- [ ] Report in git is `CloudServe_Assistant_Report.pdf` (not enrolment-named)
- [ ] Video in git is `demo.mp4`
- [ ] README clean-checkout path works
- [x] Hidden set provenance in report §8.7: **0 runs**, date N/A (assessor file not issued)
- [ ] When assessor issues the file: run **once**, update §8.7 date/count — no tuning
