# Gaps — CloudServe Assistant vs reference datasets pack

Review date: **2026-11-22**. Updated after gap-closure implementation, and again after the report, workbooks, human-evaluation and clean-checkout work the same day.

Status legend: **Closed** · **Partial** (evidence incomplete) · **Pending** (needs an action outside the repository, e.g. camera capture).

---

## A. Gate / acceptance criteria (A1–A12)

| ID | Status | Notes |
|----|--------|-------|
| A1 | Closed (deps fixed) | Resolvable `requirements.txt` verified on CPython 3.11.14 (`requirements-pin-log.md`). Set `DATASETS_PATH` before `setup_all` / pytest. See `independent-verification.md`. |
| A2 | Closed | Four-channel ingest; non-string channel coerce → email. |
| A3 | Closed | Intent+urgency+confidence; rules path lists other rule intents as alternatives. |
| A4 | Closed | Chroma retrieve with `doc_id`; `index_stats` + `/health.chroma` prove index wired (count 59). |
| A5 | Closed | Deterministic route; twice-run tests in `tests/test_gaps_closure.py`. |
| A6 | Partial | Citation IDs ⊆ retrieved + nonempty answer. Independent second-pass human review is done (`human-eval-notes.md`: 28 drafts, 119 claims, CSAT proxy 4.68, 119/119 supported) but on passage-grounded **simulated** drafts, so it is indicative only; live-output review is still outstanding. |
| A7 | Closed | Engineered bad generation blocks; BLOCK wired through `run_ticket`. |
| A8 | Closed | Decision log + harness reconcile (`tickets_missing_decision_row`); escalation summary on escalate. Note: `decisions_export.jsonl` dumps the whole database (shared across runs), so the packaged export has 850 rows for 180 tickets; reconcile itself is unaffected. |
| A9 | Partial | Harness path-parameterised and run unattended on route-only inputs (also from the package tree); no recorded live generate-on batch (free-tier rate limits). |
| A10 | Closed | Metrics auto-written; FCR honesty (`fcr_claim_allowed`); human CSAT/citation/hallucination figures recorded in `human-eval-notes.md` with their simulation caveat. |
| A11 | Closed | Timeout + 429 backoff; mock rate-limit test; malformed mid-batch continues. |
| A12 | Closed | `pytest tests/ -v` — 28 tests covering gap matrix above (28 passed on the build machine). |

---

## B–H. Close-list G1–G12

| # | Item | Status |
|---|------|--------|
| 1 | Submission artifacts (report/workbooks/video) | **Report: Closed** (`docs/report/CloudServe_Assistant_Report.md` → `SameerJ_CloudServe_Report.pdf`, 33 pages, 28 in sections 1–10). **Workbooks: Closed** (Stage 1–5 + Effort Log, md + docx, plus `human_eval_appendix.md`). **Video: Pending camera capture** — script and README complete (`docs/video/video-script.md`, `docs/video/README.md`); recording not yet made. |
| 2 | A11 timeout/backoff + induced failure tests | **Closed** |
| 3 | A5/A8/kill/grounded tests | **Closed** |
| 4 | Generate mock + BLOCK through graph | **Closed** |
| 5 | Metrics honesty + human eval notes | **Closed** (human eval done as simulation; live-output review still open, see A6) |
| 6 | Package curated results snapshot | **Closed** (`validation_fairness_fix` metrics) |
| 7 | Kill mid-flight + live env re-read | **Closed** |
| 8 | Grounded override × confidence_floor | **Closed** (`skip_confidence_floor`) |
| 9 | must_not without labels | **Closed** |
| 10 | Ingest/guards/ConfigError | **Closed** |
| 11 | Docs sync LangGraph + risk IDs | **Closed** |
| 12 | Clean-checkout rehearsal | **Closed** (`clean-checkout-rehearsal.md`; verified steps marked, unverified steps listed) |

---

## Known limitations carried into the report (not blocking the gaps above)

1. No live generate-on batch recorded → no customer FCR claim; hidden-set runs = 0.
2. Routing precision debt: 17 of 66 validation auto_respond decisions are on tickets labelled not answerable from docs.
3. Validation file was used during iteration (four validation-file runs on disk), so the recorded snapshot is fitted, not held-out.
4. Decision export is now scoped to the harness run’s ticket_ids (A8).

---

## Still for marks (student hand-in)

1. **Record the video** from `docs/video/video-script.md`.
2. Re-assemble package (`PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh`), add video, zip, rename to release name.
3. Optional: live generate-on sample; export Effort Log to PDF if the guide requires PDF specifically.
4. Rotate any OpenRouter key that lived in local `.env` if the workspace was shared.
