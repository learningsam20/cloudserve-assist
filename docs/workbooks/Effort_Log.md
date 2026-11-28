# Effort Log: CloudServe Assistant

| Field | Value |
|-------|-------|
| Author | Sameer J (sameer_j) |
| Date | 2026-11-28 |
| Template | reference datasets pack `Effort_Log.docx` |
| Basis of record | Reconstructed effort log aligned to stage sequencing in `docs/plan/work-log.md`, eval records and sprint artifacts. Stage totals below are authoritative. File mtimes may show a concentrated write window; do not treat this log as contemporaneous commit proof. Backlog IDs (B-01 to B-22) refer to the Stage 4 sprint plan. |
| Status at 2026-11-28 | Report and workbooks exist; video recording still outstanding. Stage 5 (build and revision) actual is **26.0 hours**; project total to date is **62.5 hours**. |

## 1 Your details

<!-- docx-table: 1 -->
| Field | Value |
|-------|-------|
| Full name | Sameer J (sameer_j) |
| Project start date | 2026-11-02 |
| Target submission date | 2026-11-22 (cohort deadline to be confirmed; the pack template shows 13 September) |
| Hours available per week | Planned 28, 34 and 22 (Stage 4 plan); worked approximately 25.5, 21.0 and 16.0 |

## 2 Summary of hours by stage

<!-- docx-table: 2 -->
| Stage | Planned hours | Actual hours | Difference | Why the difference |
|-------|---------------|--------------|------------|--------------------|
| 1. Discovery | 10.0 | 11.5 | +1.5 | Extending `discovery_stats.py` from counts to segment outcomes and effort by intent, so every figure came from the script. |
| 2. Requirements | 8.0 | 9.0 | +1.0 | Resolving the pack's conflicting targets and samples (findings D1–D4). |
| 3. Prompt library | 4.0 | 5.0 | +1.0 | Mapping each requirement to tests and writing the injection-defence notes. |
| 4. Sprint plan | 2.0 | 2.5 | +0.5 | Totalling the backlog showed the illustrative capacity was too low; capacity table redone. |
| 5. Build and revision | 48.0 | 26.0 | -22.0 | Underrun vs plan: AI-assisted implementation and scripted `setup_all` / harness loops. Covered ingest through guardrails, classifier and threshold freeze, fairness fix, LangGraph wrap, gap closure and human evaluation. |
| 6. Report, video, packaging | 12.0 | 8.5 | -3.5 | Governance, README, package script, workbooks and report drafted; video capture pending. |
| Total | 84.0 | 62.5 | -21.5 | Build underrun dominates; stage 6 incomplete pending video. |

## 3 Week one: daily entries

Week one is Monday 2026-11-02 to Sunday 2026-11-08. Hours worked: approximately 25.5.

<!-- docx-table: 3 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-02 | Read Project Brief, Build Spec, Dataset/Setup/Eval/Governance guides | 1 | 2.5 | A1–A12 list and pack inconsistencies | No |
| 2026-11-02 | Read five interview transcripts; interview table | 1 | 1.5 | Stage 1 section 1a draft | No |
| 2026-11-03 | `scripts/discovery_stats.py` (channel, intent, urgency, tier, fluency, answerable, FCR) | 1 | 2.0 | First ticket aggregates | No |
| 2026-11-03 | Disagreement and "never mentioned" tables | 1 | 1.5 | Stage 1 sections 1b and 1c | Needed segment outcomes |
| 2026-11-04 | Extended discovery_stats (satisfaction, repeat, segments, effort by intent) | 1 | 2.5 | Stage 1 sections 2–3 figures | No |
| 2026-11-04 | Stage 1 sections 4–6; problem statement | 1 | 1.5 | Completed Stage 1 workbook | No |
| 2026-11-05 | PRD v1: vision, users, journeys, glossary | 2 | 2.5 | PRD sections 0–3 | No |
| 2026-11-05 | B-01 Environment, deps, OpenRouter/Groq keys, embedding download | 5 | 1.0 | Working `.env` | Embedding download slow |
| 2026-11-06 | PRD v1: FR-1 to FR-13 with testable consequences | 2 | 3.0 | Functional requirements | No |
| 2026-11-06 | Findings D1–D4 | 2 | 1.5 | `docs/plan/findings.md` | No |
| 2026-11-07 | PRD NFR, assumptions, success metrics; Stage 2 form | 2 | 2.0 | PRD week-one complete | No |
| 2026-11-07 | B-02 Ingest; B-03/B-04 chunking, Chroma, retrieval | 5 | 2.5 | `src/ingest.py`, `src/retrieve.py`, `scripts/build_index.py` | No |
| 2026-11-08 | Drop GLiNER (D5); first classifier train | 5 | 1.5 | Findings D5; `scripts/train_classifier.py` | No |

## 4 Week two: daily entries

Week two is Monday 2026-11-09 to Sunday 2026-11-15. Hours worked: approximately 21.0.

<!-- docx-table: 4 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-09 | Sprint plan: capacity, backlog, drop list (Stage 4) | 4 | 2.5 | Stage 4 workbook | No |
| 2026-11-09 | B-19 FR specifications and traceability (Stage 3) | 3 | 2.0 | Specification table | No |
| 2026-11-10 | B-19 PR-GEN-01 with injection delimiters | 3 | 1.5 | `prompts/generate_v1.md` | No |
| 2026-11-10 | B-07 Routing and threshold sweep | 5 | 1.5 | `src/route.py`, `scripts/tune_threshold.py` | No |
| 2026-11-11 | B-08 Generation (LiteLLM), cache; B-09 Guardrails | 5 | 2.5 | `src/generate.py`, `src/llm.py`, `src/guardrails.py` | No |
| 2026-11-12 | B-10/B-16 Decision log, FastAPI, kill switch; B-05 harness | 5 | 3.0 | `src/logging_store.py`, `src/api.py`, `evaluation/harness.py` | No |
| 2026-11-13 | B-11 First gate run (empty retrieve); embedding check; confidence = intent-only | 5 | 3.0 | Diagnosis in `eval-runs.md`; validation ~65% auto | Silent embedder fallback |
| 2026-11-14 | Threshold freeze at 0.35; fairness audit | 5 | 2.0 | `threshold-freeze.md`; tier gap flagged | Fairness gap |
| 2026-11-15 | Classifier n-grams; grounded override; quality fairness; validation 82.5% | 5 | 3.0 | Fairness-fix snapshot | No |

## 5 Week three: daily entries

Week three is Monday 2026-11-16 to Sunday 2026-11-22. Hours worked: approximately 16.0 (to date).

<!-- docx-table: 5 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-16 | B-17 Test suite A1–A12 | 5 | 2.0 | `tests/` (28 tests) | No |
| 2026-11-17 | B-20 LangGraph wrap; timeout and rate-limit backoff | 5 | 1.5 | `src/graph.py`, backoff in `src/llm.py` | No |
| 2026-11-18 | B-21 Gap closure; Stage 5 revision log / PRD v2 | 5 | 2.0 | `gaps.md`, Stage 5 workbook | No |
| 2026-11-19 | Governance documents | 6 | 2.5 | `docs/governance/` | No |
| 2026-11-20 | CI workflow and `/metrics`; Groq generate-on validation | 5 | 2.5 | CI; `validation_20261122T131433Z` (FCR 82.5%) | Earlier OpenRouter rate limits |
| 2026-11-21 | Human evaluation appendix; README and ops scripts | 5/6 | 2.5 | `human_eval_appendix.md`, `README.md`, scripts | No |
| 2026-11-22 | Workbooks, this log, DOCX fill; report draft | 6 | 3.0 | `docs/workbooks/`, report | No |

## 6 Estimates against reality

<!-- docx-table: 6 -->
| Item | Estimated hours | Actual hours | Why the difference |
|------|-----------------|--------------|--------------------|
| B-11 First full unattended run (the gate) | 3.0 | 3.0 | Silent embedder fallback diagnosed and fixed within the planned gate window once health checks were added. |
| B-06 Intent and urgency classifier | 4.0 | 3.0 | Supervised path with word/char n-grams; GLiNER abandoned early (D5). |
| B-07 Routing logic and thresholds | 2.5 | 2.0 | Sweep and freeze at 0.35; re-tune after intent-only confidence. |
| B-14 Fairness audit | 2.5 | 2.0 | Quality metric and grounded override closed the tier gap. |
| B-03, B-04 Chunking, vector store and retrieval | 6.0 | 2.0 | Small corpus; `doc_id` used from the start. |
| B-05 Evaluation harness | 4.0 | 2.5 | Path-parameterised harness with metrics auto-write. |
| Stage 5 total (build and revision) | 48.0 | 26.0 | AI-assisted coding and scripted setup/eval loops. |
| B-15 Report, video and submission package | 12.0 | 8.5 (to date) | Report and packaging done; video pending. |

## 7 Where the time went unexpectedly

<!-- docx-table: 7 -->
| Question | Your answer |
|----------|-------------|
| Which task took far longer than you expected, and why? | Diagnosing the first unattended run: every ticket escalated with no raised error because the embedding model had silently fallen back. The fix drove the confidence and threshold rework. |
| Which task was easier than you expected, and why? | Chunking, indexing and retrieval on a 29-article corpus once `doc_id` was enforced (finding D2). |
| What would you allocate differently if you started again on Monday? | Run the harness and threshold sweep earlier in week two; start a generate-on batch earlier; reserve calendar time for the video instead of leaving capture to the end. |
| What did you spend time on that turned out not to matter? | The GLiNER classification plan (abandoned under D5). Grafana was deferred mid-sprint, then restored under `observability/` for API and evaluation boards. |

## 8 Declaration

<!-- docx-table: 8 -->
| Full name | Signature | Date | Total hours recorded |
|-----------|-----------|------|----------------------|
| Sameer J (sameer_j) | Not signed in this file; to be signed on the submitted copy | 2026-11-28 | 62.5 |
