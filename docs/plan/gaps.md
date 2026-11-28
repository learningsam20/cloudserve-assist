# Gaps — CloudServe Assistant vs reference datasets pack

Review date: **2026-11-22**. Updated after Groq generate-on validation (`validation_20261122T131433Z`).

Status legend: **Closed** · **Partial** (evidence incomplete) · **Pending** (needs an action outside the repository).

---

## A. Gate / acceptance criteria (A1–A12)

| ID | Status | Notes |
|----|--------|-------|
| A1 | Closed (deps fixed) | Resolvable `requirements.txt` verified on CPython 3.11.14 (`requirements-pin-log.md`). Set `DATASETS_PATH` before `setup_all` / pytest. See `independent-verification.md`. |
| A2 | Closed | Four-channel ingest; non-string channel coerce → email. |
| A3 | Closed | Intent+urgency+confidence; rules path lists other rule intents as alternatives. |
| A4 | Closed | Chroma retrieve with `doc_id`; `index_stats` + `/health.chroma` prove index wired (count 59). |
| A5 | Closed | Deterministic route; twice-run tests in `tests/test_gaps_closure.py`. |
| A6 | Partial | Citation IDs ⊆ retrieved + nonempty answer; live generate-on batch recorded (Groq). Independent second-pass human review in `human-eval-notes.md` remains on **simulated** drafts (indicative). Optional: sample live drafts for dual review. |
| A7 | Closed | Engineered bad generation blocks; BLOCK wired through `run_ticket`. |
| A8 | Closed | Decision log + harness reconcile; run-scoped export. |
| A9 | Closed | Harness path-parameterised; route-only and **generate-on** batches recorded (`validation_fairness_fix`, `validation_20261122T131433Z`). |
| A10 | Closed | Metrics auto-written; `fcr_claim_allowed` gates customer FCR; generate-on FCR **82.5%**; human CSAT/citation notes in `human-eval-notes.md`. |
| A11 | Closed | Timeout + 429 backoff; throttle; daily-quota fail-fast; mock rate-limit test. |
| A12 | Closed | `pytest tests/ -v` — 28 tests. |

---

## B–H. Close-list G1–G12

| # | Item | Status |
|---|------|--------|
| 1 | Submission artifacts (report/workbooks) | **Closed**. Report PDF + Stage 1–5 / Effort Log as PDF (+ md). |
| 2–12 | Gap-closure items | **Closed** (see prior revision + `independent-verification.md`) |

---

## Known limitations (honest, not blocking)

1. Hidden-set runs = 0 (pack constraint / access).
2. Routing precision debt: some auto_respond on tickets labelled not answerable from docs.
3. Validation file was used during iteration (fitted snapshot risk).
4. Dual human review of **live** LLM drafts is still optional (A6 partial).

---

## Still for marks (outside product backlog)

1. Rotate any API keys that lived in shared `.env` / chat logs; ensure none appear in git history.
2. Optional: dual review of live generate-on drafts (A6).
3. Hidden set: **0 runs** as of 2026-11-28 (file not issued). When issued, run once only; update report §8.7 + `eval-runs.md`.
