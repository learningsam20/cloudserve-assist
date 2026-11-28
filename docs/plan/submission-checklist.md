# CloudServe Capstone submission checklist

Archive name (exact): `SameerJ_Capstone_Submission.zip`  
(`STUDENT_SLUG=SameerJ` — change if enrolment name differs.)

## Zip top-level (exact folder names; four folders at zip root)

| Folder | Contents | Format |
|--------|----------|--------|
| `01_Video` | Recorded presentation | MP4 1080p+: `SameerJ_Capstone_Video.mp4` (or a text file with a shareable link if too large) |
| `02_Report` | Project report | One PDF, 20–30 pages excluding appendices (`SameerJ_Capstone_Report.pdf`) |
| `03_Workbooks` | Five stage workbooks + effort log | PDF or DOCX (+ md companions shipped) |
| `04_Source_Code` | Complete repository **including git history**, tests, working README | Must run from a clean checkout |

## Assemble

```bash
cd submission
python docs/report/build_pdf.py
# After video revision: replace docs/video/demo.mp4, then:
PACKAGE_OUT=../_package STUDENT_SLUG=SameerJ ./scripts/package_submission.sh
# → ../_package/SameerJ_Capstone_Submission/   (01–04)
# → ../_package/SameerJ_Capstone_Submission.zip
```

The script renames the recording to `SameerJ_Capstone_Video.mp4`, copies the report PDF under the Capstone name, includes `.git` in `04_Source_Code`, and zips the **four folders at the archive root**.

## Source code gate (before zip)

- [ ] `.env` **not** in tree (gitignored); only `.env.example`
- [ ] No API keys/tokens in working tree **or git history** (submissions are scanned)
- [ ] `storage/` not needed in zip (regenerate via `setup_all`)
- [ ] Clone / clean checkout: follow README end-to-end on another machine
- [ ] `python -m pytest tests/ -v` passes
- [ ] README clean-checkout path works
- [ ] Hidden set: **0 runs** stated in the report (run once only when graders inject; record date + count)

## Video

- [x] Current recording — [docs/video/demo.mp4](../video/demo.mp4) (repackage after revision)
- [ ] Packaged name `SameerJ_Capstone_Video.mp4` after `package_submission.sh`

## Operator hand-in (not product next steps)

Use `PACKAGE_OUT=../_package STUDENT_SLUG=SameerJ ./scripts/package_submission.sh` after the video file is final, then upload `SameerJ_Capstone_Submission.zip`. Optional: Effort Log PDF; dual review of live drafts.
