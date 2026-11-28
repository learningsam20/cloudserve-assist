# Submission and repo layout

## Graded zip (Capstone Submission Guide)

Top-level folders only (names exact; at **zip root**):

1. `01_Video` — `FirstnameLastname_Capstone_Video.mp4` (1080p+)
2. `02_Report` — one PDF, 20–30 pages excluding appendices
3. `03_Workbooks` — five stage workbooks + effort log (PDF or DOCX)
4. `04_Source_Code` — complete repository **including history**, tests, working README

Archive name: `FirstnameLastname_Capstone_Submission.zip`  
(Default in this tree: `SameerJ_Capstone_Submission.zip`.)

## This workspace’s working split

| Path | Role |
|------|------|
| `submission/` | Submit-ready source (ships as `04_Source_Code`, with `.git`) |
| `_package/` | Assembled hand-in (outside git) |
| `_bmad-output/` / `capstone_guide/` | Builder tooling / Pack — not in the zip |

## Required shape inside `04_Source_Code`

```
.git/                     # history required
README.md
requirements.txt
.env.example              # never ship .env
.gitignore
src/
prompts/
tests/
evaluation/
docs/
datasets/
.github/workflows/ci.yml
```

Datasets ship in-tree at `datasets/` (`DATASETS_PATH=./datasets`).

## Rules that catch people out

- Clean-checkout: follow the README on a machine that is not yours before packaging.
- No API key, token or password in code **or git history**.
- Hidden evaluation set: run once when injected; state date and run count in the report.
- Attribute anything not written by you, including AI-assisted code (see report declaration).
