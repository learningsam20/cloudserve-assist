# Work log — CloudServe Assistant

Part of the submission package. Updated as each delivery stage / build slice lands. Prefer real reference datasets pack datasets; do not invent ticket bodies unless a criterion forces a fixture.

**How to use:** append under the matching stage when work completes. Keep evidence paths concrete.

**Effort note:** Hours below are **estimated person-hours (phrs)** for planning and submission honesty — reconstructed from the build sequence on 2026-11-22 (and Stage sequencing), not from contemporaneous time tracking. See also `docs/workbooks/Effort_Log.md`.

---

## Stage status snapshot

| delivery stage | Focus | Status |
|----------------|--------|--------|
| 0 — Setup / config | Resolvable deps, env, ops scripts | **Done** |
| 1 — Discovery tooling | Aggregates + classifier train on pack data | **Done** |
| 2 — Requirements / design docs | PRD, SPEC, architecture, findings | **Done** |
| 3 — Prompt library | Versioned prompts + generate contract wiring | **Done** |
| 4 — Sprint / build | Epics 1–6 implementation | **Done** |
| 5 — Eval / PRD revision | Harness, metrics, fairness, recorded runs | **Done** |
| 6 — Submission package | Report, workbooks, video script, package tree | **Mostly done** (video recording + final zip pending) |

### Build slice (Epic) snapshot

| Epic | Status | Notes |
|------|--------|-------|
| 1 Foundation + discovery scripts | Done | Threshold frozen 0.35 |
| 2 Ingest / classify / retrieve | Done | Embedder hardened; Chroma 59 chunks |
| 3 Route / generate / guards | Done | LangGraph; kill mid-flight; USE_EVAL_LABELS |
| 4 Persistence / API / kill / README | Done | `/health` chroma; `/metrics`; grader README |
| 5 Harness / metrics / resilience | Done | FCR honesty; A8 reconcile; scoped export |
| 6 Tests / CI / governance / package | Done | 28 pytest; report/workbooks; video TBD |

---

## Sequential change log with estimated effort (phrs)

Ordered in the sequence the work was done. **Est. phrs** = estimated person-hours for that slice.

| # | Sequence (approx. order) | Change / deliverable | Est. phrs | Evidence |
|---|--------------------------|----------------------|-----------|----------|
| 1 | Setup | Baseline config from Pack `06_Configuration` + additive `litellm` / kill / classifier keys | 1.5 | `requirements.txt` (later revised), `.env.example` |
| 2 | Setup | Local `.env`, README, ops scripts (start/stop/eval/setup/status/kill) | 2.0 | `README.md`, `scripts/*.sh` |
| 3 | Discovery | `discovery_stats.py` aggregates (no ticket-body planning) | 1.5 | `scripts/discovery_stats.py` |
| 4 | Discovery | Train TF-IDF + LogisticRegression; drop GLiNER (D5) | 2.5 | `scripts/train_classifier.py`, `storage/models/classifier/` |
| 5 | Discovery | Threshold tune + freeze **0.35** (D3) | 2.0 | `scripts/tune_threshold.py`, `docs/plan/threshold-freeze.md` |
| 6 | Design | Findings D1–D5; PRD / SPEC / architecture / epics promoted | 4.0 | `docs/plan/`, `docs/design/` |
| 7 | Prompts | Generate prompt PR-GEN-01 v1.0 | 0.5 | `prompts/generate_v1.md` |
| 8 | Build | Domain models, ingest, rules+sklearn classify, route | 4.0 | `src/models.py`, `ingest.py`, `classify.py`, `route.py` |
| 9 | Build | Chroma index + retrieve (`doc_id`); build_index script | 3.0 | `src/retrieve.py`, `scripts/build_index.py` |
| 10 | Build | Generate / disk cache / guardrails / SQLite decision log | 3.5 | `src/generate.py`, `guardrails.py`, `logging_store.py`, `cache.py` |
| 11 | Build | FastAPI `/health`, `/tickets/process`, Prometheus `/metrics` | 2.0 | `src/api.py`, `observability.py` |
| 12 | Eval | Harness `--input`/`--output` + metrics report (A9–A11) | 3.5 | `evaluation/harness.py`, `metrics_report.py` |
| 13 | Eval | Broken val (0% auto) → harden embedder; intent-only confidence | 2.5 | `eval-runs.md`, `retrieve.py`, `classify.py` |
| 14 | Eval | Recorded val 65% / dev sample 77%; retune still 0.35 | 1.5 | `evaluation/results/validation_20261122T024619Z/` |
| 15 | Eval | Fairness: char TF-IDF + grounded override + quality metric | 3.0 | `train_classifier.py`, `route.py`, `metrics_report.py` |
| 16 | Eval | Validation fairness fix: route auto **82.5%**, fairness **0pp** | 1.0 | `evaluation/results/validation_fairness_fix/` |
| 17 | Config | `.env`-only Settings (no code product defaults); CI workflows | 2.0 | `src/config.py`, `.github/workflows/ci.yml` |
| 18 | Governance | Risk / fairness / kill / incident stubs; package script scaffold | 2.0 | `docs/governance/`, `scripts/package_submission.sh` |
| 19 | Gaps | LangGraph `StateGraph`; LLM timeout + 429 backoff | 3.0 | `src/graph.py`, `src/llm.py` |
| 20 | Gaps | Kill mid-flight + live env re-read (D4); grounded×confidence_floor | 1.5 | `config.py`, `graph.py`, `guardrails.py` |
| 21 | Gaps | Label-free / intent must_not; escalation summary; A8 reconcile | 2.0 | `route.py`, `harness.py`, `logging_store.py` |
| 22 | Gaps | Metrics honesty (`fcr_claim_allowed`); Chroma `index_stats` + health | 1.5 | `metrics_report.py`, `retrieve.py`, `api.py` |
| 23 | Gaps | Gap-closure tests (A5/A8/A11/kill/grounded/generate/chroma) → **28 pytest** | 3.0 | `tests/test_gaps_closure.py` |
| 24 | Gaps | Risk IDs R-01…R-08; curated package metrics snapshot | 1.0 | `risk-register.md`, `package_submission.sh` |
| 25 | Human eval | Independent second-pass CSAT/citation simulation (n=28) | 3.5 | `docs/plan/human-eval-notes.md`, `human_eval_appendix.md` |
| 26 | Workbooks | Stage 1–5 + Effort Log (md); `fill_workbook_docx.py` → docx | 5.0 | `docs/workbooks/`, `scripts/fill_workbook_docx.py` |
| 27 | Workbooks | Extend `discovery_stats` for Stage 1 segment/effort tables | 1.0 | `scripts/discovery_stats.py` |
| 28 | Report | Expand CloudServe report + `build_pdf.py` → 33-page PDF | 6.0 | `docs/report/SameerJ_CloudServe_Report.pdf` |
| 29 | Video | Video outline/script + README (recording not made) | 2.0 | `docs/video/video-script.md` |
| 30 | Rehearsal | Clean-checkout rehearsal; package copies 01–03; `PACKAGE_NO_ZIP` | 2.5 | `clean-checkout-rehearsal.md`, `package_submission.sh` |
| 31 | Fix | Wire JSON output contract into generate messages | 0.5 | `src/generate.py` |
| 32 | Fix | Tests resolve datasets via `DATASETS_PATH` (`conftest.py`) | 0.5 | `tests/conftest.py` |
| 33 | Fix | Scope `decisions_export` to harness run ticket_ids | 0.5 | `logging_store.py`, `harness.py` |
| 34 | Verify | Independent assessor clean-checkout review → NOT READY (deps) | 2.0 | `docs/plan/independent-verification.md` |
| 35 | Fix | Resolvable `requirements.txt` + pin log (Pack pins unsatisfiable) | 2.0 | `requirements.txt`, `requirements-pin-log.md` |
| 36 | Fix | README grader path; free-tier model; `USE_EVAL_LABELS`; AI declaration | 1.5 | `README.md`, `.env.example`, report § declaration |
| 37 | Verify | Re-verify install + **28 pytest** on CPython 3.11.14 | 1.0 | pin log; independent-verification §12 |
| | | **Subtotal (recorded slices above)** | **~81.5** | |
| — | Pending | Record demo video (~20 min + prep/edit) | ~4.0 | `docs/video/` |
| — | Pending | Final package re-assemble + release-named zip | ~0.5 | `package_submission.sh` |
| | | **Estimated total incl. pending** | **~86** | Aligns with Effort Log ~102 reconstructed (includes discovery reading / iteration overhead not itemised above) |

---

## Chronological entries (detail)

### Stage 0 — Setup

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Baseline then **resolvable** deps (Pack pins logged as broken) | `requirements.txt`, `docs/plan/requirements-pin-log.md` |
| 2026-11-22 | Local `.env` with frozen threshold + LiteLLM/classifier/kill keys | `.env` (gitignored) |
| 2026-11-22 | README (grader path) + ops scripts | `README.md`, `scripts/*.sh` |

### Stage 1 — Discovery tooling

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Discovery aggregates (+ later segment/effort extensions) | `scripts/discovery_stats.py` |
| 2026-11-22 | Train TF-IDF + **LogisticRegression** intent/urgency | `scripts/train_classifier.py` → `storage/models/classifier/` |
| 2026-11-22 | No GLiNER; no LLM labelling (D5) | `docs/plan/findings.md` |
| 2026-11-22 | Threshold tune + freeze **0.35** | `scripts/tune_threshold.py`; `docs/plan/threshold-freeze.md` |

### Stage 2 — Requirements / design

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Findings D1–D5; PRD/SPEC/architecture/epics promoted | `docs/plan/`, `docs/design/` |

### Stage 3 — Prompt library

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Generate prompt PR-GEN-01 v1.0 | `prompts/generate_v1.md` |
| 2026-11-22 | JSON contract wired into system + user messages | `src/generate.py` |

### Stage 4 — Build

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Pipeline modules + API `/health` + `/tickets/process` | `src/` |
| 2026-11-22 | LangGraph StateGraph orchestration | `src/graph.py` |
| 2026-11-22 | Index + retrieve (`doc_id`); Chroma health | `scripts/build_index.py`, `src/retrieve.py`, `api.py` |
| 2026-11-22 | Generate / cache / guards / decision log | `src/generate.py`, `guardrails.py`, `logging_store.py` |
| 2026-11-22 | Prometheus `/metrics` | `src/observability.py`, `src/api.py` |
| 2026-11-22 | Ops scripts start/stop/eval/setup/status/kill | `scripts/*.sh` |

### Stage 5 — Evaluation / revision

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Harness + metrics (A9–A11); FCR honesty; scoped export | `evaluation/` |
| 2026-11-22 | Broken val → fix → fairness 0pp snapshot | `docs/plan/eval-runs.md`, `validation_fairness_fix/` |
| 2026-11-22 | Regression | `pytest tests/` — **28 passed** (incl. gap suite) |

### Stage 6 — Packaging / governance / verification

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Governance; CI; package assembler; checklist | `docs/governance/`, `package_submission.sh` |
| 2026-11-22 | Gap closure G2–G11 | `docs/plan/gaps.md` |
| 2026-11-22 | Human eval (independent second pass) | `docs/plan/human-eval-notes.md` |
| 2026-11-22 | Workbooks Stage 1–5 + Effort Log | `docs/workbooks/` |
| 2026-11-22 | Report PDF 33 pp; video script; clean-checkout rehearsal | `docs/report/`, `docs/video/`, `clean-checkout-rehearsal.md` |
| 2026-11-22 | Independent verification NOT READY → dep/README remediation | `independent-verification.md` §12 |

---

### Optional observability / hybrid (demo)

| Date | Item | Evidence |
|------|------|----------|
| 2026-11-22 | Hybrid retrieve (`dense`/`hybrid`/`auto` + lexical TF-IDF RRF); auto only falls back when dense &lt; floor | `src/retrieve.py`, `.env.example` |
| 2026-11-22 | Prometheus retrieval + classification metrics | `src/observability.py` |
| 2026-11-22 | Optional Grafana+Prometheus compose + 4 dashboards + load/export scripts | `observability/`, `scripts/grafana_*.sh`, `scripts/export_eval_metrics.py` |
| 2026-11-22 | Hybrid validation eval (66/14, 82.5% route-auto; matches dense) | `evaluation/results/validation_hybrid_20261122T101209Z/`, `eval-runs.md` |

---

## Next up

1. Record video from `docs/video/video-script.md` (~4 phrs estimated) — include Grafana folder if Docker is up  
2. `PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh`, add video, zip, rename to release name (~0.5 phrs)  
3. Optional: live generate-on sample + dual review of live drafts  
4. Rotate any OpenRouter key that lived in local `.env` if the workspace was shared  
