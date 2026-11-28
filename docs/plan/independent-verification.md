# Independent verification — CloudServe Assistant

**Assessor role:** independent (not the builder). **Date:** 2026-11-22.
**Method:** read the reference datasets pack (README, Build Specification A1–A12, Evaluation Framework, Submission Guide) and then followed `submission/README.md` literally against a copy of `_package/CloudServe_Assistant_Release/04_Source_Code/` placed in an empty directory (`/tmp/grader`, no parent `project root` layout, no `.venv`, no `storage/`, no `.env`). Fresh virtual environments were built with `uv` on Python 3.11.14 and `python -m venv` on 3.13.15. No application source was modified.

---

## 0. Remediation status (updated after builder fixes)

| ID | Original blocker | Status now | Residual |
|----|------------------|------------|----------|
| B1/B2 | Unresolvable Pack pins / wrong chromadb | **Resolved** for install | `requirements.txt` ranges + `requirements-pin-log.md`; verified 28 pytest on 3.11 |
| B3 | No video; no AI declaration; Effort Log not PDF | **Partial** | AI declaration in report **done**; **video still unrecorded**; Effort Log still md/docx |
| B4 | Stale zip | **Open (operator)** | Re-run package after video; rename to release name |
| B5 | Gold must_not; FCR claim flags; missing metric fields | **Partial** | `USE_EVAL_LABELS`; label-free rates in `eval-runs.md`; route-auto wording; per-class precision / retrieval hit / guardrail-by-type still thin |
| B6 | Default datasets path | **Mostly resolved** | README requires absolute `DATASETS_PATH` before setup |
| B7 | Effort log vs mtimes / no git | **Mitigated** | Log annotated **reconstructed**; git history still absent |
| B8 | `openrouter/auto`; generate-first README | **Resolved** | Free-tier default model; `--no-generate` first |
| B9 | Python version / bash | **Partial** | 3.11 documented; Windows not rehearsed |

**Current verdict:** **READY WITH GAPS** for code/clean-checkout once a grader sets `DATASETS_PATH` and installs the resolvable requirements. **NOT complete** for release hand-off until **video + release-named zip** exist.

---

## 1. Verdict (as of original assessor pass)

# NOT READY (as packaged on first review day)

Two independent reasons would stop a grader before any marks are awarded:

1. **`pip install -r requirements.txt` cannot succeed.** README step 3 fails with `ResolutionImpossible` on Python 3.11 and with a `pandas==2.0.0` build failure on 3.13. Under the Build Specification this is "it will not start" (48-hour repair window for setup and docs only, visible in commit history; this tree has no commit history, see B7).
2. **The submission is incomplete.** `01_Video` contains only a README and a script (no recording). The Submission Guide says a submission missing any of the four parts is treated as incomplete. In addition, the shipped zip is stale and does not contain the report, workbooks or newest tests.

**Path to READY WITH GAPS** (all achievable without redesign):

1. Replace `requirements.txt` with a version set that installs and runs, ideally with a lock file taken from a verified run (B1 and B2).
2. Rebuild the zip from the 11:39 package tree and add the video (B3 and B4).
3. Report the label-free route numbers and fix the metrics report's missing required measures (B5).
4. Make `DATASETS_PATH` work out of the box for a bundle that does not contain the Pack (B6).

**What does work.** With a working dependency set on a clean 3.11 environment, the code itself is sound. `setup_all.sh` took about 25 s. The suite gave **28 passed**. The route-only validation run reproduced **66 auto_respond and 14 escalate** with 0 silent drops and 160 decision rows for 80 tickets. A 120-ticket file with an arbitrary name was processed (also in wrapper-dict form and with labels removed). The 500-ticket development file took about 9 s. The API `/health` and `/tickets/process` worked.

---

## 2. Gate table A1–A12

Legend: **Pass** = verified by me on a clean copy. **Partial** = works but evidence or behaviour falls short of the criterion. **Fail** = does not work as documented.

| ID | Result | Evidence | Independent notes |
|----|--------|----------|-------------------|
| A1 | **Fail as documented; Pass only after replacing the dependency pins** | `/tmp/grader/pip311.log`: `langchain-openai 0.0.7 depends on openai>=1.10.0,<2.0.0` vs `openai==1.0.0`. pip on 3.11: `ResolutionImpossible`. pip on 3.13: `Failed to build 'pandas'`. | See B1 and B2. The claim "28 passed on 3.14.5, global site-packages" in `clean-checkout-rehearsal.md` never exercised `pip install -r requirements.txt`; it is marked ⬜ there. |
| A2 | **Pass** | `tests/test_ingest_and_route.py`, `test_gaps_closure.py` (28/28 green in clean venv). | Four channels, malformed-channel coercion. |
| A3 | **Pass (confidence is not calibrated)** | `evaluation/results/validation_fairness_fix/metrics.json`: class, urgency, confidence and alternatives present. | Calibration bands 0.2–0.8 are off by 0.31–0.68 (under-confident). The report says this plainly (§8.4). Only the top band meets the Evaluation Framework's 5-point tolerance. |
| A4 | **Pass** | `setup_all.sh` → `indexed_chunks=59`; `/health` → `chroma.count: 59`; `test_pipeline_real_data.py`. | `doc_id` resolves to the Pack corpus. First run needs hub access for `all-MiniLM-L6-v2`. |
| A5 | **Pass** | Re-ran the validation set in two environments: identical 66/14. Twice-run tests. | Deterministic. See B5 for what feeds the router. |
| A6 | **Partial** | `human-eval-notes.md`; report §8.6; `gaps.md` A6. | Citation-ID membership is automated. Support was reviewed only on 28 passage-grounded drafts written by the reviewer. Live generation was never exercised, so hallucination and citation figures do not describe a real model. Report §8.6 is titled "independent second reviewer" yet says the same person wrote and scored the drafts. Below the 50-response, two-assessor standard. |
| A7 | **Pass (mocked path only)** | `tests/test_guardrails_and_log.py`, `test_gaps_closure.py` (forged citation, PII pattern, block through graph). | Never demonstrated against live model output. The video (which would show it) does not exist. |
| A8 | **Pass** | Harness reconcile (`tickets_missing_decision_row` empty); 160 rows for 80 tickets in a fresh DB. | `decisions_export.jsonl` in the packaged snapshot has 850 rows for 80 tickets (shared DB), a documented caveat. Use a fresh `DATABASE_URL` per run. |
| A9 | **Partial** | Fresh-copy runs: validation 80, development 500, 120-ticket renamed file, wrapper-dict form, no-labels form. All 0 silent drops. | Route-only (`--no-generate`) only. The README's first harness example has no `--no-generate`, so a grader with no or placeholder key gets every auto candidate escalated with `Generation/validation failed: OPENROUTER_API_KEY is still the placeholder`. This is graceful (A11) but produces a near-zero automated rate. No live generate-on batch exists. Hidden-set runs: 0. |
| A10 | **Partial** | `metrics.json` keys inspected (§5). | Present: volume, FCR proxy, escalation rate, accuracy, per-class **recall**, latency p95, PII, decision coverage, fairness, calibration. **Missing versus the Build Specification metrics list:** per-class **precision** (the field named `precision_overall` is accuracy), **retrieval hit rate**, **guardrail activations by type**, a separate "blocked by guardrails" count. The "reply time" figures are compute wall-clock (0.0009 min mean) and yet drive `meets_reply_target: True`. |
| A11 | **Pass** | Placeholder key with generate-on: 8/8 tickets escalated, no crash. Mocked 429/timeout tests. Malformed mid-batch continues. | Real provider disconnect not induced against a live endpoint (no authorised key used by me). |
| A12 | **Pass with conditions** | Clean 3.11 venv, Pack datasets via `DATASETS_PATH`: **28 passed, 5 warnings, 13.6 s**. | (a) Run before `setup_all.sh`: 20 passed, **8 skipped** (silently vacuous). (b) With the default `.env` path and no Pack beside the bundle: **6 failed, 3 errors, 5 skipped, 14 passed**. `conftest.py` does honour `DATASETS_PATH` now, but the default value cannot resolve in the packaged layout. See B6. |

**Count:** Pass 7 (A2, A3, A4, A5, A7, A8, A11), Pass-with-conditions 1 (A12), Partial 3 (A6, A9, A10), Fail 1 (A1).

---

## 3. Submission parts 01–04 checklist

Checked against `Submission_Guide.docx` and the packaged tree `_package/CloudServe_Assistant_Release/`.

| Item | Required | Found | Status |
|------|----------|-------|--------|
| Archive name | `FirstnameLastname_CloudServe_Release.zip` | `CloudServe_Assistant_Release.zip` (rename pending) | ⬜ |
| Zip is current | contains 01–04 | **Stale zip (Nov 22 08:31)**: `02_Report`, `03_Workbooks` hold only a placeholder README each; `04_Source_Code` lacks `conftest.py`, `test_gaps_closure.py`, `.env.example` updates, rehearsal/gap docs; includes an empty `.deepeval/` | ❌ |
| **01_Video** | MP4, 1080p, ~20 min, `FirstnameLastname_CloudServe_Demo.mp4`, on-camera, ≥7 min live demo | No recording. `README.md` says "NOT YET RECORDED"; `video-script.md` only | ❌ **blocks "complete"** |
| **02_Report** | single PDF, 20–30 pp excl. appendices, prescribed section order, `FirstnameLastname_CloudServe_Report.pdf`, AI-use declaration | `SameerJ_CloudServe_Report.pdf` (33 pp incl. appendices; ~28 body). Section order differs from the guide (no standalone Implementation or Requirements-revision sections; revision sits in §3.5). **No declaration of AI tool use found** (searched for declaration / AI / Cursor / Claude / BMad). Filename may not match release name format | ⚠️ |
| **03_Workbooks** | 5 stage workbooks + effort log; log named `..._Effort_Log.pdf` | Five workbooks and Effort Log as `.docx` + `.md`, plus `human_eval_appendix.md`. **Effort log is not a PDF.** Effort log content vs file evidence: see B7 | ⚠️ |
| **04_Source_Code** | README, pinned `requirements.txt`, `.env.example`, `src/`, `prompts/`, `tests/`, `evaluation/`, `docs/`, `data/`, `.github/workflows/` | All present. `requirements.txt` is pinned but unresolvable (B1). `data/` is empty (acceptable: Pack datasets are external). `evaluation/results/` ships one curated snapshot | ⚠️ |
| Hidden set used once and date reported | required | 0 runs; report says so | ⚠️ honest |
| Commit history | reviewed by graders | Workspace is **not a git repository**; package has no `.git` | ❌ (B7) |

---

## 4. Secrets scan

| Check | Result |
|-------|--------|
| `.env` in `_package/…/04_Source_Code/` | Absent. |
| `.env` inside `_package/CloudServe_Assistant_Release.zip` | Absent (stale zip, 93 files). |
| `sk-or-` / `sk-…` patterns in package tree, zip contents, `.docx` XML, PDF strings | None in the package or zip. The only `sk-abcdefghijklmnopqrstuvwxyz123456` matches are deliberate fake values in `tests/test_guardrails_and_log.py` and `tests/test_gaps_closure.py` (PII-guardrail fixtures). |
| `submission/.env` (working tree, git-ignored, **not packaged**) | **Contains what looks like a real OpenRouter key (`sk-or-v1-…`, value redacted here).** It is correctly ignored and excluded by `package_submission.sh`. Because it appeared in plain text in a workspace search, **rotate it before sharing the workspace or recording the screen.** Never `zip` the `submission/` directory directly; only use the package script. |
| `submission/storage/gen_cache/*.json` | Only fake-key test fixtures. `storage/` is git-ignored and absent from the package. |

---

## 5. `.env.example` vs `src/config.py`

Programmatic comparison (every `_require`, `_int_require`, `_float_require`, `_bool_required`, `_path_from_env` key against `.env.example` keys):

- **Required keys missing from `.env.example`: none.** `LITELLM_API_BASE` is optional and is present commented-out.
- **Extra key in `.env.example` not read by `config.py`: `TARGET_CLASSIFICATION_PRECISION`** (read by `evaluation/metrics_report.py` through settings; fine, informational).
- Placeholder `OPENROUTER_API_KEY=your_key_here` passes `Settings()` and is rejected only at generation time with a clear message.
- **Deviations from the Pack's `06_Configuration/.env.example`** (approved additive keys are fine; these are behavioural):
  - `MODEL_NAME` / `LITELLM_MODEL = openrouter/auto` versus the Pack's `meta-llama/llama-3.1-8b-instruct`. **`openrouter/auto` routes to whichever model OpenRouter picks and can select a paid model**, which conflicts with the Pack's "free tier only" cost principle. See B8.
  - `CONFIDENCE_THRESHOLD=0.35` versus the Pack's illustrative 0.80 (documented in findings D3 and `threshold-freeze.md`).
  - `DATASETS_PATH=$DATASETS_PATH` default does not resolve in the packaged layout (B6).

---

## 6. Clean-checkout blockers, ordered by severity

| # | Severity | Blocker | Evidence | Minimal fix |
|---|----------|---------|----------|-------------|
| **B1** | **Critical (gate: will not start)** | `requirements.txt` is unresolvable. `openai==1.0.0` vs `langchain-openai==0.0.7` (needs `openai>=1.10`); `pydantic==2.0.0` vs `fastapi==0.104.0` (fastapi excludes 2.0.0); `langchain==0.1.0` vs `langchain-openai==0.0.7` (conflicting `langsmith` ranges). `litellm>=1.40.0` adds further tension. The Pack's own `06_Configuration/requirements.txt` has the same defects, but the grader follows the submission README, not the Pack. | pip 3.11: `ResolutionImpossible`; uv: "requirements are unsatisfiable"; pip 3.13: pandas 2.0.0 sdist build failure (`pkg_resources`). | Ship a resolvable set. Needs an approved, logged pin change (AGENTS.md: log any pin change). |
| **B2** | **Critical** | The pins that *would* install (`chromadb==0.3.21`, `langgraph==0.0.20`) are not what the code runs on. `src/retrieve.py` uses `chromadb.PersistentClient` (added after 0.3.x), and `chromadb 0.3.21` imports `pydantic.BaseSettings`, which fails on pydantic 2 (`PydanticImportError`, verified after relaxing three conflicts). The recorded results were produced on Python 3.14.5 with unpinned latest libraries (builder env: chromadb 1.5.9, langgraph 1.0.1, litellm 1.83.7, numpy 2.4.6, pandas 3.0.5, fastapi 0.139.2). No lock file exists. | Install log; `pip list` on the builder interpreter. | Record a lock from a verified run. Verified working on a clean **Python 3.11.14** venv: `chromadb 1.5.9`, `langgraph 1.2.24`, `sentence-transformers 6.3.0`, `scikit-learn 1.9.1`, `fastapi 0.165.0`, `pydantic 2.14.4`, `litellm 1.110.2`, `numpy 2.4.6`, `torch 2.15.0`, `SQLAlchemy 2.1.9`, `pytest 9.2.0` (28 passed). Minimal unpinned install list that worked: `langgraph chromadb sentence-transformers scikit-learn fastapi uvicorn pydantic litellm python-dotenv SQLAlchemy prometheus-client joblib pytest numpy pandas PyYAML httpx`. Note: `joblib` and `httpx` are imported directly but are not listed in `requirements.txt`. |
| **B3** | **High (completeness)** | No demonstration video; Effort Log is not a PDF; filenames do not follow the guide; no AI-use declaration in the report. | `01_Video/` listing; checklist §5 of the Submission Guide. | Record video, export Effort Log to PDF, add declaration, rename files to release name. |
| **B4** | **High** | The shipped zip is stale and incomplete. It predates the 11:39 package assembly. | `unzip -l`: `02_Report` and `03_Workbooks` hold a README only; 4 test files vs 6 in the package tree. | Re-run `PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh`, add the video, then zip, rename, and re-check the listing. |
| **B5** | **High (metric definition)** | The router reads the **gold label** `labels.must_not_auto_respond` (`src/route.py` `policy_must_not`). On validation, all 14 escalations are `policy_must_not`. With labels (and history) stripped from the same 80 tickets, the same code gives **74 auto_respond / 6 escalate (92.5% / 7.5%)**, not 66/14. A set without that label would therefore behave very differently from the recorded 82.5% / 17.5% snapshot. Report §6.4 and §8.7 mention label-free text rules but never publish the label-free split. Also: the packaged snapshot's `first_contact_resolution_pct = 82.5` is **not reproduced** by the current harness (it returns `null` because `fcr_claim_allowed=false` on route-only runs), yet `README.md`, the results table and `gaps.md` still quote 82.5%. The tier-fairness "0.0 pp" result depends on a metric that was redefined after a 35-pp raw gap appeared (raw tier spread is still 19.5 pp). | `/tmp/grader/out_vnl/metrics.json`; `/tmp/grader/out_val/metrics.json`; `evaluation/results/validation_fairness_fix/metrics.json`. | Publish label-free numbers beside labelled ones; regenerate the snapshot with the current harness; describe 82.5% as a label-assisted route rate; add per-class precision, retrieval hit rate, guardrail activations by type and a blocked count. |
| **B6** | **Medium** | Out-of-the-box dataset path fails in the bundle: README and `.env.example` default `DATASETS_PATH=$DATASETS_PATH`, which resolves to a sibling of `04_Source_Code/` that the submission does not ship. `setup_all.sh` exits 2 with a clear message (error message is good, but README never says to edit it). Tests: 6 failed / 3 errors / 5 skipped with the default. `clean-checkout-rehearsal.md` (step 3.2) and report §8.8 / Table 25 still say tests ignore `DATASETS_PATH`; `tests/conftest.py` already honours it, so those statements are stale. Test order matters: before `setup_all.sh`, 8 tests skip and the run still looks green. | `setup_all.sh` output; pytest summary in `/tmp/grader`. | README: state "set `DATASETS_PATH` to the Pack's `05_Datasets` directory before step 5", and "run `setup_all.sh` before pytest". Optionally fail rather than skip. |
| **B7** | **Medium (integrity risk, needs the student's explanation)** | **Effort log vs file evidence.** The Effort Log claims about 62.5 hours across 2026-11-02 to 2026-11-22 (stage 5 build 26.0 h; weeks approximately 25.5 / 21.0 / 16.0 h). Every file in `submission/` was created on 2026-11-22 (121 of 121 files, source 07:38–08:31), `work-log.md` has only 2026-11-22 entries, `AGENTS.md` carries the same date, and **there is no git repository at all**. The Submission Guide asks for steady-work commit history and warns that a log "written from memory in the final week is obvious". I cannot prove how the log was compiled, but a grader looking at mtimes or history would see this. | `find submission … stat`; `Effort_Log.md`; no `.git`. | Initialise history honestly if work really spanned weeks (it cannot be reconstructed after the fact). At minimum, annotate the log as reconstructed. |
| **B8** | **Medium** | Live generation has never been exercised and the default model is `openrouter/auto`. The first harness example in the README has no `--no-generate`. With a real key a grader would pay for or get routed to an arbitrary model; with none, every auto candidate is escalated. A6/A7/A9 live evidence therefore does not exist. | `gaps.md`, report Table 25; placeholder-key run in `/tmp/grader/out_gen`. | Default to a free model slug with the `openrouter/` prefix (for example the Pack's `meta-llama/llama-3.1-8b-instruct`), and show a route-only example first in the README. |
| **B9** | Low | `README.md` says Python 3.10+, but the tested set is now 3.11 (this review) and 3.14 (builder); 3.10 and 3.12 are untested. Scripts are bash-only although the README gives a Windows activate line. `lib.sh` silently prefers `./.venv` over an already-activated environment. `package_submission.sh` and `.github/workflows/ci.yml` run the same `pip install -r requirements.txt` and would fail the same way. CI also skips training when the Pack is absent. | files named. | Document supported versions; note bash requirement. |

---

## 7. Python and pin risk

| Item | Documented | Reality |
|------|-----------|---------|
| Python | "3.10+ (3.11 recommended)" | Builder ran 3.14.5. This review: 3.11.14 works once dependencies are resolvable; 3.13 fails to install pinned `pandas==2.0.0`. |
| `langgraph` | `==0.0.20` | Builder: 1.0.1. This review: 1.2.24 (works). `0.0.20` could not be exercised because of the chromadb conflict. |
| `chromadb` | `==0.3.21` | Code needs `PersistentClient` (≥0.4); builder 1.5.9, review 1.5.9. |
| `langchain`, `langchain-community`, `langchain-openai`, `openai` | pinned | **Not imported anywhere in `src/`.** Only `langgraph` is used from that family. Removing them removes two of the three conflicts. |
| `pydantic` | `==2.0.0` | Excluded by `fastapi==0.104.0`; runtime resolves to 2.14.x. |
| `numpy`, `pandas`, `scikit-learn`, `torch` | `1.24.0`, `2.0.0`, `1.3.0`, n/a | Builder: numpy 2.4.6, pandas 3.0.5. Trained `classifier.joblib` is tied to the scikit-learn version, so it must be rebuilt, which `setup_all.sh` does. |
| Not in `requirements.txt` | n/a | `joblib`, `httpx` (TestClient), `python-docx` and `reportlab` (documentation tooling only). |

---

## 8. Exact commands a grader must run

These are the commands that worked in my clean 3.11 run. Step 3 differs from the README (B1/B2 workaround); steps marked * are not in the README today.

```bash
# 0. Unpack the archive; Pack datasets must exist somewhere (path below is an example)
cd 04_Source_Code
python3.11 -m venv .venv && source .venv/bin/activate

# 1. Dependencies  (README says: pip install -r requirements.txt  -> FAILS)
pip install langgraph chromadb sentence-transformers scikit-learn fastapi uvicorn \
    pydantic litellm python-dotenv SQLAlchemy prometheus-client joblib pytest \
    numpy pandas PyYAML httpx                                    # *

# 2. Environment
cp .env.example .env
# edit .env:
#   DATASETS_PATH=/abs/path/to/your 05_Datasets directory   # *
#   OPENROUTER_API_KEY=<real key>   (only for generate-on; optional for route-only)

# 3. Build local artifacts (needs network the first time for all-MiniLM-L6-v2)
./scripts/setup_all.sh        # ~25 s; classifier trained, indexed_chunks=59
./scripts/status.sh

# 4. Tests (run after setup_all.sh, otherwise 8 tests skip)
python -m pytest tests/ -v    # 28 passed (13.6 s)

# 5. Unattended run, route-only (reproduced 66 auto / 14 escalate, 0 drops, 160 rows)
python -m evaluation.harness --input "$DATASETS_PATH/validation_tickets.json" \
    --output /tmp/out_val --no-generate

# 6. Hidden-set style run (any path; use a fresh DB per run for a run-scoped export)
DATABASE_URL=sqlite:///./storage/run2.db \
python -m evaluation.harness --input /path/to/unseen.json --output /tmp/out_hidden
#   without --no-generate this calls the configured model for auto_respond tickets

# 7. API / kill switch
./scripts/start_api.sh && curl -s localhost:8000/health
./scripts/kill_on.sh && curl -s localhost:8000/health   # kill_switch: true
./scripts/kill_off.sh && ./scripts/stop_api.sh
```

Verified timings on an Apple-silicon laptop: setup 25 s, tests 14 s, 80-ticket harness 6 s, 500-ticket harness 9 s.

---

## 9. What happens if a grader follows the README literally on a clean machine

| README step | Literal outcome |
|-------------|-----------------|
| `python3 -m venv .venv` (3.11) | OK. |
| `pip install -r requirements.txt` | **Stops: `ResolutionImpossible` (3.11); `Failed to build 'pandas'` (3.13).** Nothing after this works. |
| (if the grader improvises an install) `cp .env.example .env` | OK. |
| `./scripts/setup_all.sh` | **`error: CloudServe datasets not found at <bundle>/$DATASETS_PATH`**, exit 2. The README mentions the override only under "Ops scripts", after setup. The earlier failing venv I created in the copy was silently picked up by `lib.sh` (it prefers `./.venv`), which also produced a misleading `No module named 'joblib'` error. |
| `./scripts/status.sh` | Reports classifier and Chroma `MISSING` until setup succeeds. |
| `./scripts/run_tests.sh` / pytest, Pack not beside the bundle | 6 failed, 3 errors, 5 skipped, 14 passed. |
| `python -m evaluation.harness --input … --output …` (no `--no-generate`) with the `.env.example` key | Runs to completion, no crash; every ticket that would be auto_respond is escalated with a "placeholder key" reason. With a real key it calls `openrouter/auto` (cost and model not controlled). |
| Parent `project root` layout absent | The repo-root `.github/workflows/ci.yml` and `scripts/fill_workbook_docx.py` (`--pack-dir` default) assume the sibling layout; the submission CI mirror skips training if the Pack is missing. Everything else runs from `04_Source_Code/` alone once paths are injected. No hardcoded `/Users/…` paths were found in code or in `04_Source_Code/` (author name `sameer_j` appears in workbook text). |

---

## 10. Evidence checklist

| Claim | Verdict |
|-------|---------|
| FCR 82.5% | Route-level rate on the packaged route-only snapshot; customer FCR is claimed on generate-on (`validation_20261122T131433Z`). Harness withholds FCR on `--no-generate` (B5). |
| Validation as held-out | Report notes it is fitted (multiple validation-file runs; iteration after seeing validation). |
| Hidden set | 0 runs, stated in the report. |
| Human evaluation | Passage-grounded review, single reviewer, 28 drafts; documented in report §8.6. |
| Fairness 0.0 pp | Holds for resolution quality on expected-auto tickets (small n: enterprise 6, non-fluent 8). Raw tier spread 19.5 pp is also reported. |
| 28 tests | Confirmed (with Pack and network). Generation, guardrail block, and backoff paths use mocks. |
| Calibration | Reported as unmet outside the top confidence band. |
| Gaps noted | Label-free routing split (74/6); reply-time proxy is harness wall-clock; per-class precision, retrieval hit rate, and guardrail activations by type are thin in the metrics report. |

---

## 11. Top five blockers (summary)

1. **B1/B2: `requirements.txt` is unresolvable and does not describe what runs**; `pip install -r requirements.txt` fails on 3.11 and 3.13. Pins `chromadb==0.3.21`/`langgraph==0.0.20` are incompatible with the code (`PersistentClient`, pydantic 2).
2. **B3: No video, Effort Log not a PDF, no AI-use declaration**: the submission is incomplete under the Guide.
3. **B4: The packaged zip is stale** (no report, workbooks or newest tests) and not named for the release name.
4. **B5: Routing consumes the gold `must_not_auto_respond` label**; label-free validation gives 74/6 rather than 66/14, the packaged FCR 82.5% is not reproducible by the current harness, and the metrics report omits per-class precision, retrieval hit rate and guardrail activations by type.
5. **B6/B7: Default dataset path breaks the packaged layout** (tests 6 failed / 3 errors, setup exits 2) and the **effort log (three weeks) contradicts file evidence (one day, no git history)**.


## 12. Remediation applied after this review (builder)

After the NOT READY verdict, the builder applied: resolvable `requirements.txt` + `requirements-pin-log.md`; README clean-checkout order and `DATASETS_PATH` emphasis; free-tier default model; `USE_EVAL_LABELS` for labelled vs label-free routing; AI-use declaration in the report; effort-log reconstructed caveat. Re-verified: `uv pip install -r requirements.txt` on CPython 3.11.14 and `pytest` → **28 passed**. Video recording and release-named zip remain operator-owned. Re-assess readiness as **READY WITH GAPS** once the video exists and the package tree is re-assembled.
