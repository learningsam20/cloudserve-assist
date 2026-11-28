# Submission and repo layout

## Public git repository (this tree)

| Artifact | Filename in git |
|----------|-----------------|
| Demonstration video | `docs/video/demo.mp4` |
| Report PDF | `docs/report/CloudServe_Assistant_Report.pdf` |
| Packaging script | **Not in this repo** (parent Capstone `scripts/`) |

## Graded hand-in archive (assembled outside git)

Archive: `FirstnameLastname_Capstone_Submission.zip` — four folders at zip root:

1. `01_Video` — `SameerJoshi_Capstone_Video.mp4`
2. `02_Report` — `SameerJoshi_Capstone_Report.pdf` (+ Markdown)
3. `03_Workbooks` — Stage 1–5 + Effort Log (**PDF**)
4. `04_Source_Code` — complete repository **including history**, tests, working README

## Required shape inside `04_Source_Code`

```
.git/
README.md
requirements.txt
.env.example
.gitignore
src/ prompts/ tests/ evaluation/ docs/ datasets/
.github/workflows/ci.yml
docs/report/CloudServe_Assistant_Report.pdf
docs/video/demo.mp4   # may be omitted from zip binary copy; README documents it
```

## Rules that catch people out

- Clean-checkout: follow the README on a machine that is not yours.
- No API key in code or git history.
- Hidden evaluation set: run once when injected; state date and run count.
- Attribute AI-assisted work (see report declaration).
