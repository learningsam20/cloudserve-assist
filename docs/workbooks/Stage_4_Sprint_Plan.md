# Stage 4 — Sprint Plan: CloudServe Assistant

| Field | Value |
|-------|-------|
| Owner | Sameer J (sameer_j), individual cloudserve |
| Date | 2026-11-22 |
| Calendar | Week one Mon 2026-11-02 to Sun 2026-11-08; week two Mon 2026-11-09 to Sun 2026-11-15; week three Mon 2026-11-16 to Sun 2026-11-22 (submission window closes 2026-11-22; the cohort deadline is to be confirmed, the pack template shows 13 September) |
| Plan written | Week two, day one (Monday 2026-11-09), after Stage 1 and Stage 2 were complete |
| Related | `docs/plan/sprint-plan.md` (epic-level plan, illustrative capacity of about 46 hours), `docs/plan/epics.md`, `Effort_Log` for planned versus actual hours |

**Capacity note.** `docs/plan/sprint-plan.md` carries an earlier illustrative capacity of about 46 hours (1–2 hours on weekdays, 4–5 hours at weekends). Totalling the backlog below (64 hours of remaining work plus 20 hours already planned for stages one, two and four) gave 84 hours, so this workbook plans against 84 hours: 28, 34 and 22 hours across the three weeks.

**Dependency rule used throughout.** The retrieval layer (B-04) and the evaluation harness (B-05) come early. The first full unattended run (B-11, the gate) is on the Friday of week two. The hidden evaluation set is held by the assessor and is not in the pack, so the gate is run on the 80-ticket validation file with the same harness command; the harness takes `--input` and `--output` and hardcodes no dataset path.

## 1 Section one: your capacity

<!-- docx-table: 1 -->
| Week | Hours realistically available | Other commitments that week | Days you cannot work |
|------|-------------------------------|-----------------------------|----------------------|
| Week one | 28 (weekdays about 3 hours, weekend days about 6.5) | None recorded; hours are net of other obligations, which are not itemised | None planned |
| Week two | 34 (weekdays about 4.5 hours, weekend days about 5.75) | None recorded | None planned; Friday is the gate day and is kept clear |
| Week three | 22 (weekdays about 3 hours, weekend days about 3.5) | None recorded; reduced capacity assumes the build is finished and only revision, governance and packaging remain | None planned |

**Rule for blockers.** Anything blocking for more than an hour is written in the daily check-in record (section 6), then either worked around or escalated to a decision in `docs/plan/findings.md` the same day.

## 2 Section two: the backlog

<!-- docx-table: 3 -->
| ID | Item | Est. hours | Priority | Depends on | Definition of done |
|----|------|------------|----------|------------|--------------------|
| B-01 | Environment and dependency setup | 2.0 | Must | — | Virtual environment created; `requirements.txt` and `.env.example` based on the pack's `06_Configuration` (additive pin: `litellm`); embedding model downloaded; `.env` kept out of the repository. Done in week one. |
| B-02 | Data loading and normalisation | 2.0 | Must | B-01 | `src/ingest.py` maps all four channels to one ticket object; pack datasets load by configured path; empty or odd fields do not crash. Done in week one. |
| B-03 | Document chunking and embedding | 2.5 | Must | B-02 | `documentation.json` (29 articles, field `doc_id`) chunked from `.env` settings and embedded; chunk size justified in the design notes. Done in week one. |
| B-04 | Vector store and retrieval | 3.5 | Must | B-03 | Chroma index built by `scripts/build_index.py`; `retrieve` returns ordered passages with `doc_id` and score, or none below the floor. Done in week one. |
| B-05 | Evaluation harness | 4.0 | Must | B-02 | `python -m evaluation.harness --input <path> --output <dir>` processes every ticket unattended, never drops a ticket silently, and writes a metrics report with volume, business, technical and governance sections. |
| B-06 | Intent and urgency classifier | 4.0 | Must | B-02 | Rules first, then a classifier trained from the labelled development tickets by `scripts/train_classifier.py`; returns intent, urgency, confidence and alternatives; no model call; labelled accuracy reported on validation. |
| B-07 | Routing logic and thresholds | 2.5 | Must | B-06 | Deterministic `route`; threshold measured by `scripts/tune_threshold.py` on development data and frozen before the recorded run; reason strings readable; policy tickets never auto_respond. |
| B-08 | Answer generation with citations | 4.0 | Must | B-04 | LiteLLM to OpenRouter call with timeout, retries and a disk cache; prompt PR-GEN-01; structured answer and citation ids; only for auto_respond. |
| B-09 | Guardrails and validation | 3.5 | Must | B-08 | Blocking checks for citations in the retrieved set, empty answer, private-data patterns, injection language, out-of-scope commitments and confidence floor; an engineered ticket is blocked and not sent. |
| B-10 | Decision logging | 2.0 | Must | B-07 | SQLite decision log with the Governance Framework fields; harness reconciles decision rows with tickets processed. |
| B-11 | First full unattended run over the hidden evaluation set (THE GATE) | 3.0 | Must | B-05, B-09 | Full validation file processed in one unattended command with metrics written and no ticket dropped; failures diagnosed and the run recorded in `docs/plan/eval-runs.md`. The assessor's hidden file runs through the same command. |
| B-12 | Monitoring and dashboards | 2.0 | Should | B-10 | Prometheus `/metrics` endpoint live; dashboard files are optional (first on the drop list). |
| B-13 | Continuous integration pipeline | 1.5 | Should | B-11 | Workflow runs the documented test command on every push. |
| B-14 | Fairness audit | 2.5 | Must | B-11 | Segment quality gap by tier and fluency computed by the harness and reported; method written in `docs/governance/fairness-method.md`; gap under 5 percentage points or explained. |
| B-15 | Report, video and submission package | 12.0 | Must | all | Report written from the scaffold; video recorded from the outline; package assembled without secrets or draft files; zip named per the Submission Guide. |
| B-16 | FastAPI service and kill switch | 3.0 | Must | B-10 | `/health` and ticket-processing endpoints; kill switch read live from environment or file; behaviour per findings D4 documented. |
| B-17 | Test suite for the A1–A12 behaviour matrix | 4.0 | Must | B-11 | One documented command, `python -m pytest tests/ -v`, passes; no tests beyond what the acceptance criteria need. |
| B-18 | Requirements revision (PRD version 2.0 and Stage 5 log) | 2.0 | Must | B-11 | PRD updated for everything the build contradicted; each change recorded with its trigger in Stage 5. |
| B-19 | Specifications and prompt library (Stage 3) | 4.0 | Must | B-02 | Each FR has a specification; PR-GEN-01 registered with injection defence; traceability table complete. |

Totals: backlog 64.0 hours. Together with Stage 1 (10), Stage 2 (8) and this plan (2) the planned total is 84 hours.

## 3 Section three: the week two plan in detail

<!-- docx-table: 4 -->
| Day | What will be finished by the end of the day | Hours | Risk to this |
|-----|---------------------------------------------|-------|--------------|
| Monday 2026-11-09 | Sprint plan (this document); FR specifications and traceability skeleton (B-19); week-one classifier first pass reviewed against validation labels. | 5.0 | Underestimating the backlog; mitigated by hour estimates and the drop list. |
| Tuesday 2026-11-10 | PR-GEN-01 written with injection delimiters (B-19); routing logic and the threshold sweep script (B-07). | 5.0 | The measured threshold may land far from the pack's 0.80; plan time to explain, not to force it. |
| Wednesday 2026-11-11 | Generation via LiteLLM with caching (B-08); blocking guardrails (B-09). | 5.0 | Free-tier rate limits when exercising the real provider; use mocks in tests and the cache for runs. |
| Thursday 2026-11-12 | Decision log, API and kill switch (B-10, B-16); evaluation harness and metrics report (B-05). | 5.0 | Harness scope creep; keep to the sections the Evaluation Framework requires. |
| Friday 2026-11-13 | THE GATE: first full unattended run on the validation file (B-11), failures diagnosed. | 5.0 | A systematic failure (for example retrieval) can make every ticket escalate and consume the day; leave Saturday as buffer. |
| Saturday 2026-11-14 | Threshold frozen and runs recorded (B-07, B-11); fairness audit (B-14). | 5.0 | Fairness gap larger than the 5-point limit; time held on Sunday to respond. |
| Sunday 2026-11-15 | Response to the fairness result (B-14); buffer for gate fixes. | 4.0 | Unknown unknowns; this is the only unallocated day in week two. |

## 4 Section four: the week three plan in detail

<!-- docx-table: 5 -->
| Day | What will be finished by the end of the day | Hours | Risk to this |
|-----|---------------------------------------------|-------|--------------|
| Monday 2026-11-16 | Full test suite for the A1–A12 matrix (B-17). | 4.0 | Tests exposing gaps that need code changes. |
| Tuesday 2026-11-17 | PRD version 2.0 and the Stage 5 revision log (B-18); update findings. | 4.0 | Forgetting a change; use the evaluation records as the source list. |
| Wednesday 2026-11-18 | Monitoring and CI (B-12, B-13); resilience review against A11. | 4.0 | CI environment differs from local (model download). |
| Thursday 2026-11-19 | Governance documents: risk register, fairness method, kill-switch and incident notes (part of B-15). | 3.0 | Documents drifting from the code; cite files and settings. |
| Friday 2026-11-20 | Fresh-clone README rehearsal and package dry-run. Final presentation and submission | 3.0 | Missing steps in the README only appear on a clean machine. |
| Saturday 2026-11-21 | Report written from the scaffold (B-15). | 2.0 | Report time squeezed by earlier overruns; the drop list protects it. |
| Sunday 2026-11-22 | Video recorded and submission assembled (B-15). | 2.0 | No time left to re-record; keep the outline short. |

## 5 Section five: what you will drop if you run out of time

<!-- docx-table: 6 -->
| Item | Cut order | Consequence of cutting it | What you will say about it in the report |
|------|-----------|---------------------------|------------------------------------------|
| Grafana dashboard files (part of B-12) | 1st to go | No visual dashboard; the raw `/metrics` endpoint remains. | Metrics are exposed in Prometheus format; dashboards were descoped to protect the gate. |
| Hybrid retrieval and reranking | 2nd to go | Pure embedding search only; some wording may miss. | Retrieval quality is reported as measured; hybrid search is future work. |
| Model-written escalation prose | 3rd to go | Escalation summaries are built from structured fields by code. | Escalations are templated and deterministic, which also keeps them auditable. |
| Extra fairness visualisations beyond the required table | 4th to go | Numbers only, no charts. | The required segment table is present; charts were not needed to meet the criterion. |
| Prompt variants beyond one generation prompt | 5th to go | One prompt, no A/B comparison. | A single prompt version is recorded; variants were not part of the acceptance criteria. |
| Never cut: harness with input and output paths, blocking guardrail, decision log reconciliation, clean README | Not cut | The gate and A1, A7, A8, A9 would fail. | Not applicable. |

## 6 Section six: the daily check-in record

Completed from the start of week two (the plan was written on Monday 2026-11-09). Hours and tasks match the Effort Log.

<!-- docx-table: 7 -->
| Date | Finished since yesterday | Doing today | Blocked by |
|------|--------------------------|-------------|------------|
| Mon 2026-11-09 | Week one: discovery workbook, PRD version 1, ingest, index and retrieval, classifier first pass, decision to drop GLiNER (findings D5). | Sprint plan; FR specifications and traceability skeleton. | Nothing. |
| Tue 2026-11-10 | Sprint plan and FR specifications. | PR-GEN-01 and injection defence; routing logic and threshold sweep script. | Nothing. |
| Wed 2026-11-11 | PR-GEN-01; routing and the sweep script. | Generation with cache (LiteLLM to OpenRouter); guardrails. | Nothing. Free-tier rate limits were anticipated, so tests use mocks. |
| Thu 2026-11-12 | Generation and guardrails. | Decision log, API, kill switch; evaluation harness. | Nothing. |
| Fri 2026-11-13 | Decision log, API, kill switch, harness. | The gate: first unattended validation run. | All 80 tickets escalated: retrieval returned nothing because the embedding model fell back to an untrained one; written up and fixed the same day. |
| Sat 2026-11-14 | Embedding check added; route confidence changed to intent only; validation re-run recorded (FCR 65%, escalation 35%). | Threshold re-tune and freeze at 0.35; fairness audit. | Tier gap of about 35 percentage points in auto-respond rate. |
| Sun 2026-11-15 | Threshold frozen; gap diagnosed as partly structural. | Fairness response: word and character n-grams in the classifier, grounded override, quality-based fairness metric. | Nothing. |
| Mon 2026-11-16 | Fairness fix; validation re-run (FCR 82.5%, gap 0.0 points). | Test suite for the A1–A12 matrix. | Nothing. |
| Tue 2026-11-17 | Test suite. | LangGraph wrap of the pipeline; provider timeout and backoff. | Nothing. |
| Wed 2026-11-18 | LangGraph wrap and backoff. | Gap closure (kill switch mid-flight, label-free policy rules, metrics honesty); Stage 5 revision log and PRD version 2.0. | Nothing. |
| Thu 2026-11-19 | Gap closure; revision log. | Governance documents. | Nothing. |
| Fri 2026-11-20 | Governance documents. | CI workflow and Prometheus metrics endpoint. | Fresh-clone rehearsal not yet done. |
| Sat 2026-11-21 | CI workflow and metrics endpoint. | Human evaluation second pass on 28 auto replies; README, ops scripts and package script. | Live generation batch rate-limited; replies written from the retrieved passages instead. |
| Sun 2026-11-22 | Human evaluation appendix, README, package script. | Stage 1–5 workbooks, effort log and the DOCX fill script. | Report and video still to do; fresh-clone rehearsal outstanding. |
