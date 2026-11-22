# Clean-checkout rehearsal checklist — CloudServe Assistant

Purpose: prove that someone with only the packaged `04_Source_Code/` and the reference datasets pack can reproduce setup, tests, the evaluation harness and the demo commands (acceptance criteria A1, A9, A12).

**Legend:** ✅ verified on this machine on 2026-11-22 · ⬜ not verified (do on the recording or grading machine) · ⚠️ verified with a caveat.

**This machine:** macOS (darwin), Python 3.14.5 with global site-packages (no fresh virtual environment was created), reportlab 5.0.1. The README recommends Python 3.11 (the CloudServe CI version); the suite also passes on 3.14.5 here.

**How the rehearsal was done.** (a) In-repo checks ran from `submission/`. (b) Package-tree checks ran on a copy assembled by `PACKAGE_NO_ZIP=1 PACKAGE_OUT=/tmp/pkg ./scripts/package_submission.sh`, whose `04_Source_Code/` has no `.env` and no `storage/`, so setup had to rebuild everything. No zip was created.

## Summary of what is and is not proven

| Area | Result |
|------|--------|
| Package assembles without `.env`, `storage/` or a zip | ✅ |
| Classifier and index rebuild from an empty `storage/` | ✅ (`indexed_chunks=59`) |
| Route-only harness on the full validation file reproduces the recorded numbers | ✅ (66 auto, 14 escalate, accuracy 0.9875, fairness gap 0.0, 160 decision rows, 0 missing) |
| `pytest` in-repo | ✅ 28 passed |
| `pytest` in the package tree | ⚠️ 28 passed only if the Pack sits at `<bundle>/your 05_Datasets directory`; otherwise 14 passed, 6 failed, 5 skipped, 3 errors |
| Fresh virtual environment and `pip install -r requirements.txt` | ⬜ |
| Live `GENERATE=1` batch | ⬜ (rate-limited earlier; never recorded) |
| Different machine / Python 3.11 / CI run | ⬜ |

## Steps

### 0. Pre-flight

| # | Step | Command | Status |
|---|------|---------|--------|
| 0.1 | Python 3.10+ available (3.11 recommended) | `python3 --version` | ⚠️ 3.14.5 here, not 3.11 |
| 0.2 | reference datasets pack datasets present | `ls $DATASETS_PATH` | ✅ |
| 0.3 | No secrets in the tree to be packaged | `git status` / confirm `.env` is git-ignored | ✅ `.env` is in `.gitignore`; package script refuses to ship it |

### 1. Environment and dependencies

| # | Step | Command | Status |
|---|------|---------|--------|
| 1.1 | Create and activate a virtual environment | `cd submission && python3 -m venv .venv && source .venv/bin/activate` | ⬜ (global Python used) |
| 1.2 | Install requirements | `pip install -r requirements.txt` | ⬜ (dependencies already installed globally) |
| 1.3 | Copy environment file | `cp .env.example .env` | ✅ (in the package-tree copy) |
| 1.4 | Point datasets at the Pack | edit `.env`: `DATASETS_PATH=<path to 05_Datasets>` (default `$DATASETS_PATH`) | ✅ (absolute path used in the package-tree copy) |
| 1.5 | Set `OPENROUTER_API_KEY` only for live generation | edit `.env` | ⬜ (not needed for route-only runs; do not paste the key on camera) |

### 2. Build local artifacts

| # | Step | Command | Status |
|---|------|---------|--------|
| 2.1 | Train classifier and build Chroma index | `./scripts/setup_all.sh` | ✅ in the package-tree copy: classifier written (`train=400 test=100`), `indexed_chunks=59`, about 9 seconds |
| 2.2 | Sanity check | `./scripts/status.sh` | ✅ classifier present, chroma present, kill switch off |
| 2.3 | Chroma count is 59 | `curl -s localhost:8000/health` (see 4.1) or `index_stats()` | ✅ `count: 59` |

Equivalent explicit commands (what `setup_all.sh` runs):

```bash
python -m scripts.train_classifier --input "$DATASETS_PATH/development_tickets.json" --output storage/models/classifier
python -m scripts.build_index --input "$DATASETS_PATH/documentation.json"
```

### 3. Tests (A12)

| # | Step | Command | Status |
|---|------|---------|--------|
| 3.1 | Run the suite in the repository | `./scripts/run_tests.sh` or `python -m pytest tests/ -v` | ✅ **28 passed** (needs network to the model hub for the two real-data tests; in a network-restricted run those two errored and 26 passed) |
| 3.2 | Run the suite in the package tree, Pack missing | `cd 04_Source_Code && python -m pytest tests/ -q` | ⚠️ 14 passed, 6 failed, 5 skipped, 3 errors: tests look for the Pack at `<repo root>/your 05_Datasets directory` |
| 3.3 | Run the suite in the package tree, Pack placed at `<bundle>/cloudserve_guide/...` | same command | ✅ 28 passed |

**Caveat to carry into the hand-in notes.** The test files locate the Pack through a fixed path two directories above `tests/`; they do not read `DATASETS_PATH`. In the packaged layout that path is the bundle folder, so a grader must place (or symlink) `your 05_Datasets directory` there, or the data-backed tests fail. The harness and the scripts do accept injected paths. Making the tests honour `DATASETS_PATH` is a recorded follow-up, not done in this change.

### 4. Service and kill switch (A1, FR-8)

| # | Step | Command | Status |
|---|------|---------|--------|
| 4.1 | Start the API and check health | `./scripts/start_api.sh && curl -s localhost:8000/health` | ✅ `status: ok`, `kill_switch: false`, `chroma.count: 59` |
| 4.2 | Process one validation ticket (route-only) | `curl -s -X POST localhost:8000/tickets/process -H 'content-type: application/json' -d @ticket.json` with `{"ticket": {...}, "allow_generate": false}` | ✅ first validation ticket routed `auto_respond` (confidence 0.695, 5 passages) |
| 4.3 | Kill switch on, health shows it | `./scripts/kill_on.sh && curl -s localhost:8000/health` | ✅ `kill_switch: true` |
| 4.4 | Kill switch off | `./scripts/kill_off.sh && curl -s localhost:8000/health` | ✅ `kill_switch: false` |
| 4.5 | Stop the API | `./scripts/stop_api.sh` | ✅ |

### 5. Harness (A9, A10)

| # | Step | Command | Status |
|---|------|---------|--------|
| 5.1 | Short unattended slice | `python -m evaluation.harness --input <validation_tickets.json> --output /tmp/demo_run --no-generate --limit 3` | ✅ 3 processed, 0 silent drops, 1 auto and 2 escalate (both policy must-not); isolated database used |
| 5.2 | Full validation file, route-only, from the package tree | `python -m evaluation.harness --input <validation_tickets.json> --output <dir> --no-generate` | ✅ 66 auto_respond, 14 escalate; accuracy 0.9875; tier quality gap 0.0; 160 decision rows for 80 tickets; `tickets_missing_decision_row` empty; `first_contact_resolution_pct` null (claim withheld) |
| 5.3 | Same via ops script | `./scripts/run_eval.sh validation` | ⬜ (5.2 used the module directly) |
| 5.4 | Live generate-on batch | `GENERATE=1 ./scripts/run_eval.sh validation` (or `LIMIT=…`) | ⬜ **not done**: free-tier rate limits; no recorded batch exists |

Note on decision-export scope: `decisions_export.jsonl` dumps the whole decision database. With a fresh database the export for 3 tickets held 6 rows; the packaged export for the recorded validation run holds 850 rows across 180 ticket ids because that database was shared by several runs. Use a fresh `DATABASE_URL` per run when a run-scoped export matters.

### 6. Package (A1 hand-in structure)

| # | Step | Command | Status |
|---|------|---------|--------|
| 6.1 | Build the report PDF | `python docs/report/build_pdf.py` | ✅ 33 pages (28 in sections 1 to 10) |
| 6.2 | Assemble without zipping | `PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh` | ✅ folders `01_Video` (README + script), `02_Report` (PDF + Markdown), `03_Workbooks` (5 stage workbooks and Effort Log as docx + md, human evaluation appendix), `04_Source_Code`; no zip created |
| 6.3 | No `.env`, no `storage/` in `04_Source_Code` | `ls -a 04_Source_Code` | ✅ script aborts if either appears |
| 6.4 | Pattern scan for OpenRouter-style keys in the bundle | `grep -rIl "sk-or-" <bundle>` | ✅ none found |
| 6.5 | Add the recorded video to `01_Video`, then zip | `(cd _package && zip -r CloudServe_Assistant_Release.zip CloudServe_Assistant_Release -x '*.DS_Store')` and rename to `FirstnameLastname_CloudServe_Release.zip` | ⬜ (video not yet recorded; zip is created by the user) |

### 7. Not rehearsed

| # | Item | Why it matters |
|---|------|----------------|
| 7.1 | Install on a machine without cached models (first download of `all-MiniLM-L6-v2`) | The embedding dimension check turns a silent fallback into an error; confirm the hub is reachable |
| 7.2 | GitHub Actions run of `.github/workflows/ci.yml` | CI would need the Pack available to the runner for the data-backed tests |
| 7.3 | Windows activation path (`.venv\Scripts\activate`) | Documented in the README, not run |

## Verified numbers to quote (and nothing else)

- pytest: **28 passed** (in-repo with network; package tree with the Pack placed as above).
- Chroma `cloudserve_docs`: **59** chunks (rebuilt from an empty `storage/`).
- Validation, route-only: **66** auto_respond, **14** escalate, accuracy **0.9875**, fairness gap **0.0** (tier and fluency), **160** decision rows, **0** missing.
- PDF report: **33** pages total, **28** pages in sections 1 to 10.
