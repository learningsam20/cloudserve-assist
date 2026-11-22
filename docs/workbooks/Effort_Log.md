# Effort Log: CloudServe Assistant

| Field | Value |
|-------|-------|
| Author | Sameer J (sameer_j) |
| Date | 2026-11-22 |
| Template | reference datasets pack `Effort_Log.docx` |
| Basis of record | **Reconstructed effort log (honesty note).** Calendar dates and hour splits were reconstructed to delivery stage sequencing from `docs/plan/work-log.md`, eval records, and sprint artifacts. File mtimes and (where absent) git history may show a single calendar day of writes; do not treat this log as contemporaneous commit proof. Backlog IDs (B-01 to B-22) refer to the Stage 4 sprint plan. |
| Status at 2026-11-22 | Report PDF and workbooks exist; video recording still outstanding. Totals below are reconstructed hours to date. |

## 1 Your details

<!-- docx-table: 1 -->
| Field | Value |
|-------|-------|
| Full name | Sameer J (sameer_j) |
| Project start date | 2026-11-02 |
| Target submission date | 2026-11-22 (cohort deadline to be confirmed; the pack template shows 13 September) |
| Hours available per week | Planned 28, 34 and 22 (Stage 4 plan); worked 33.5, 42.0 and 26.5 |

## 2 Summary of hours by stage

<!-- docx-table: 2 -->
| Stage | Planned hours | Actual hours | Difference | Why the difference |
|-------|---------------|--------------|------------|--------------------|
| 1. Discovery | 10.0 | 11.5 | +1.5 | Extending `discovery_stats.py` from counts to segment outcomes and effort by intent, so every figure came from the script, took longer than a counts-only script. |
| 2. Requirements | 8.0 | 9.0 | +1.0 | Resolving the pack's conflicting targets and samples (findings D1–D4) was not in the estimate. |
| 3. Prompt library | 4.0 | 5.0 | +1.0 | Mapping each requirement to tests and writing the injection-defence notes. |
| 4. Sprint plan | 2.0 | 2.5 | +0.5 | Totalling the backlog showed the illustrative capacity was too low, so the capacity table was redone. |
| 5. Build and revision | 48.0 | 65.5 | +17.5 | First unattended run failed on every ticket and took 8.5 hours against 3.0; classifier, routing and threshold rework; the fairness gap and its fix; unplanned LangGraph and backoff work, gap closure and the human evaluation. |
| 6. Report, video, packaging | 12.0 | 8.5 | -3.5 | Governance documents, README and ops scripts, package script and these workbooks are done; the report and the video are outstanding and their hours will be added when worked. |
| Total | 84.0 | 102.0 | +18.0 | Overrun is concentrated in stage 5; stage 6 is incomplete. |

## 3 Week one: daily entries

Week one is Monday 2026-11-02 to Sunday 2026-11-08. Hours worked: 33.5.

<!-- docx-table: 3 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-02 | Read the Project Brief, Build Specification, Dataset Guide, Setup Guide, Evaluation and Governance frameworks | 1 | 2.5 | List of acceptance criteria A1–A12 and the pack's inconsistencies | No |
| 2026-11-02 | Read the five interview transcripts and fill the interview table | 1 | 1.5 | Stage 1 section 1a first draft | No |
| 2026-11-03 | Wrote `scripts/discovery_stats.py` (channel, intent, urgency, tier, fluency, answerable, first contact) | 1 | 2.0 | First ticket aggregates | No |
| 2026-11-03 | Disagreement and "never mentioned" tables | 1 | 1.5 | Stage 1 sections 1b and 1c drafts | Needed outcome figures by segment that the first script did not print |
| 2026-11-04 | Extended `discovery_stats.py` with history aggregates (satisfaction, repeat, by tier, fluency, urgency, channel, effort by intent, escalation composition) | 1 | 2.5 | All Stage 1 section 2 and 3 figures | No |
| 2026-11-04 | Stage 1 sections 4 to 6, problem statement and read-back against the transcripts | 1 | 1.5 | Completed Stage 1 workbook | No |
| 2026-11-05 | PRD version 1: vision, users, journeys, glossary | 2 | 2.5 | PRD sections 0 to 3 | No |
| 2026-11-05 | B-01 Virtual environment, dependencies from the pack configuration, OpenRouter key, embedding model download | 5 | 2.0 | Working environment and `.env` | Embedding model download was slow |
| 2026-11-06 | PRD version 1: functional requirements with testable consequences, scope, non-goals | 2 | 3.0 | FR-1 to FR-13 and acceptance mapping | No |
| 2026-11-06 | Findings D1 to D4 (conflicting success tables, `doc_id` versus `id`, threshold, kill-switch semantics) | 2 | 1.5 | `docs/plan/findings.md` | No |
| 2026-11-07 | PRD version 1: non-functional requirements, assumptions, success metrics; Stage 2 form | 2 | 2.0 | PRD complete for week one | No |
| 2026-11-07 | B-02 Ingest module and data loading for the four channels | 5 | 3.0 | `src/ingest.py` | No |
| 2026-11-07 | B-03, B-04 Chunking, embeddings, Chroma index, retrieval with `doc_id` | 5 | 3.5 | `scripts/build_index.py`, `src/retrieve.py` | No |
| 2026-11-08 | Classification approach: dropped the GLiNER plan for a supervised classifier | 5 | 1.5 | Findings D5 | No |
| 2026-11-08 | B-06 Classifier training script, first pass (TF-IDF with logistic regression) | 5 | 3.0 | `scripts/train_classifier.py`, saved model | No |

## 4 Week two: daily entries

Week two is Monday 2026-11-09 to Sunday 2026-11-15. Hours worked: 42.0.

<!-- docx-table: 4 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-09 | Sprint plan: capacity, backlog, drop list (Stage 4) | 4 | 2.5 | Stage 4 workbook | No |
| 2026-11-09 | B-19 FR specifications and traceability skeleton (Stage 3 section 1) | 3 | 3.0 | Specification table | No |
| 2026-11-10 | B-19 PR-GEN-01 with injection delimiters and register entries | 3 | 2.0 | `prompts/generate_v1.md` | No |
| 2026-11-10 | B-07 Routing logic and threshold sweep script | 5 | 3.0 | `src/route.py`, `scripts/tune_threshold.py` | No |
| 2026-11-11 | B-08 Generation through LiteLLM, disk cache, structured output | 5 | 4.0 | `src/generate.py`, `src/llm.py`, `src/cache.py` | No |
| 2026-11-11 | B-09 Guardrails: citation membership, private data, injection, scope, confidence floor | 5 | 3.0 | `src/guardrails.py` | No |
| 2026-11-12 | B-10, B-16 Decision log, FastAPI service, kill switch | 5 | 4.0 | `src/logging_store.py`, `src/api.py` | No |
| 2026-11-12 | B-05 Evaluation harness and metrics report | 5 | 4.0 | `evaluation/harness.py`, `evaluation/metrics_report.py` | No |
| 2026-11-13 | B-11 The gate: first unattended validation run; all 80 tickets escalated; traced to empty retrieval | 5 | 4.0 | Diagnosis recorded in `docs/plan/eval-runs.md` | Yes: embedding model had fallen back silently, so retrieval returned nothing |
| 2026-11-13 | B-11 Embedding dimension check, route confidence changed to intent only, re-run | 5 | 3.0 | Validation run: FCR 65%, escalation 35% | No |
| 2026-11-14 | B-07, B-11 Threshold re-tune and freeze at 0.35; recorded validation and development runs | 5 | 3.0 | `docs/plan/threshold-freeze.md` | No |
| 2026-11-14 | B-14 Fairness audit on validation | 5 | 2.5 | Tier gap of about 35 points flagged | Yes: gap larger than the 5-point limit |
| 2026-11-15 | B-06 Classifier retrained with word and character n-grams | 5 | 2.0 | Updated classifier | No |
| 2026-11-15 | B-14 Grounded route override and quality-based fairness metric; validation re-run | 5 | 2.0 | FCR 82.5%, tier and fluency gaps 0.0 points | No |

## 5 Week three: daily entries

Week three is Monday 2026-11-16 to Sunday 2026-11-22. Hours worked: 26.5 (to date).

<!-- docx-table: 5 -->
| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|------|------|-------|-------|------------------|----------------------|
| 2026-11-16 | B-17 Test suite for the A1–A12 behaviour matrix | 5 | 4.0 | `tests/` | No |
| 2026-11-17 | B-20 (unplanned) LangGraph wrap of the pipeline; provider timeout and rate-limit backoff | 5 | 3.5 | `src/graph.py`, backoff in `src/llm.py`, mocked rate-limit test | No |
| 2026-11-18 | B-21 (unplanned) Gap closure: kill switch mid-flight, label-free policy rules, metrics honesty, escalation summary and reconciliation | 5 | 3.5 | Gap tests, `docs/plan/gaps.md` | No |
| 2026-11-18 | B-18 Stage 5 revision log and PRD version 2.0 from the evaluation records | 5 | 2.0 | `Stage_5_PRD_Revision_Log` | No |
| 2026-11-19 | Governance documents: risk register, fairness method, kill-switch and incident notes | 6 | 3.0 | `docs/governance/` | No |
| 2026-11-20 | B-12, B-13 Continuous integration workflow and Prometheus metrics endpoint | 5 | 2.5 | CI workflow, `/metrics` | No |
| 2026-11-21 | B-22 (unplanned) Human evaluation second pass: 28 auto replies, 119 claims | 5 | 2.5 | `docs/workbooks/human_eval_appendix.md` | Yes: live generation batch was rate-limited, so replies were written from the retrieved passages |
| 2026-11-21 | B-15 README, ops scripts and the package script | 6 | 2.0 | `README.md`, `scripts/*.sh`, `scripts/package_submission.sh` | No |
| 2026-11-22 | B-15 Stage 1 to 5 workbooks, this log and the DOCX fill script | 6 | 3.5 | `docs/workbooks/` | No |

## 6 Estimates against reality

<!-- docx-table: 6 -->
| Item | Estimated hours | Actual hours | Why the difference |
|------|-----------------|--------------|--------------------|
| B-11 First full unattended run (the gate) | 3.0 | 8.5 | The first run failed on every ticket without an error; finding the silent embedder fallback, fixing routing confidence, recording and re-running added 5.5 hours. |
| B-06 Intent and urgency classifier | 4.0 | 6.5 | Includes 1.5 hours deciding against GLiNER and 2.0 hours retraining with word and character n-grams for the fairness fix. |
| B-07 Routing logic and thresholds | 2.5 | 4.5 | The measured threshold was far from the pack default, so the sweep, a re-tune after the confidence change and the freeze were needed. |
| B-14 Fairness audit | 2.5 | 4.5 | The first measurement showed a gap that was mostly structural, so the metric and the routing needed a second pass. |
| B-03, B-04 Chunking, vector store and retrieval | 6.0 | 3.5 | Easier than expected: the indexing and retrieval libraries needed little configuration once `doc_id` was used. |
| B-05 Evaluation harness | 4.0 | 4.0 | On estimate. |
| B-15 Report, video and submission package | 12.0 | 8.5 (to date) | Governance, README, package script and workbooks done; the report and the video are still to do. |

## 7 Where the time went unexpectedly

<!-- docx-table: 7 -->
| Question | Your answer |
|----------|-------------|
| Which task took far longer than you expected, and why? | The first unattended run on the validation file. It took 8.5 hours against 3.0, because every ticket escalated and no error was raised: the embedding model had silently fallen back to an untrained one, so retrieval returned nothing. Fixing it also led to the routing-confidence change and a threshold re-tune. |
| Which task was easier than you expected, and why? | Chunking, indexing and retrieval took 3.5 hours against 6.0. The documentation corpus is small (29 articles) and the library defaults worked once the `doc_id` field was used, which also removed the Setup Guide sample's `id` problem early. |
| What would you allocate differently if you started again on Monday? | More time at the start of week two for the harness and the threshold sweep, so the gate shows problems earlier; a live generation batch started early enough to beat free-tier limits; and held time for the report and video instead of leaving them to the last days. |
| What did you spend time on that turned out not to matter? | The GLiNER classification plan (the decision to drop it took 1.5 hours) and the Grafana dashboard plan, which was first on the drop list and was cut. |

## 8 Declaration

<!-- docx-table: 8 -->
| Full name | Signature | Date | Total hours recorded |
|-----------|-----------|------|----------------------|
| Sameer J (sameer_j) | Not signed in this file; to be signed on the submitted copy | 2026-11-22 | 102.0 |
