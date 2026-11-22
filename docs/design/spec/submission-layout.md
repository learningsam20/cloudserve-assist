# Submission and repo layout

## Graded zip (Capstone Submission Guide)

Top-level folders only (names exact):

1. `01_Video`
2. `02_Report`
3. `03_Workbooks`
4. `04_Source_Code`

Archive name: `FirstnameLastname_Capstone_Submission.zip` (enrolment name).

## This repository’s working split

| Path | Role |
|------|------|
| `submission/` | **Only** submit-ready source and docs that will ship as `04_Source_Code` (and optionally staged copies of other zip parts later) |
| `_bmad-output/` | Agent drafts, PRD/SPEC workspaces, memlogs, change log — not in the zip |
| `capstone_guide/` | Untouched Capstone Pack |
| `docs/` (repo root) | Optional non-submission working notes / pointers |

Do not put exploratory tests, half-written prompts, or agent memlogs into `submission/` until they are grader-ready.

## Required shape inside `04_Source_Code` / `submission/` when ready

```
README.md
requirements.txt          # pinned
.env.example
.gitignore                # includes .env, storage/
src/
prompts/
tests/
evaluation/               # harness + results dir
docs/                     # architecture notes for the product
  plan/                   # discovery/sprint artifacts promoted when ready
  design/                 # PRD, prompts overview, diagrams
  governance/             # risk, incident, fairness method
data/                     # small samples only — not full 500-ticket dumps if oversized
.github/workflows/ci.yml
```

Large datasets: keep under `capstone_guide/.../05_Datasets/` or document download/copy steps; harness always takes `--input` path. `data/` holds tiny fixtures for tests/README smoke.

## Promote rule

Draft → review → copy/promote into `submission/`. Change log entry when something is promoted.
