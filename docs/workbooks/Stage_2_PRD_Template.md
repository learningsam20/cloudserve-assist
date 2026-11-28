# Stage 2 — Product Requirements Document: CloudServe Assistant

Source of truth for the full narrative PRD is `docs/plan/prd.md`; this workbook is the delivery stage 2 form of the same requirements. Requirement IDs here use the template's two-digit style (`FR-01`); `docs/plan/prd.md` writes the same requirements as `FR-1` to `FR-13`, and acceptance codes `A1`–`A12` come from the CloudServe Build Specification. "Discovery evidence" cites Stage 1 rows (`§2.8` = section 2, row 8; `§1a` interviews; `§1b` disagreements).

This document is the revised requirements set (version 2.0). The assumptions in section 7 are recorded as they stood at version 1.0; whether each held is recorded in `Stage_5_PRD_Revision_Log`.

## 1 Document control

<!-- docx-table: 1 -->
| Field | Value |
|-------|-------|
| Version | 2.0 (revises 1.0; changes in Stage_5_PRD_Revision_Log) |
| Written by | Sameer J (sameer_j) |
| Date | 2026-11-22 |
| Status | Revised after build; submitted with the cloudserve |
| Approved by | Individual product: self-reviewed, no separate approver |

## 2 The problem in one paragraph

<!-- docx-table: 2 -->
| Problem statement |
|-------------------|
| CloudServe's support team already has most of the answers its customers need. Seven in ten tickets are covered by the 29 articles in the support knowledge base, but the agents cannot find them quickly, so each familiar ticket is rewritten from memory or from a personal file, replies take 8 to 12 hours against a 2-hour promise, and fewer than half of tickets are settled at first contact. Almost half of the tickets passed up to tier two are ones that could have been settled at the first line, and they arrive as a bare forwarded message, so the customer is asked the same questions again. Urgent tickets wait in the same queue as simple ones and do slightly worse. The team does not need something that answers everything: security, billing disputes, data location and unclear requests must always go to a person, and about three in ten tickets have no written answer at all. What the team needs is a way to send a short, honest, sourced first reply on the tickets that documentation already answers, and to pass every other ticket to the right person with a summary, the articles that look relevant and a note of what is uncertain. Success is a first contact resolution of at least 60%, no more than 30% of tickets escalated, replies in minutes, and no wrong answer sent. |
| Copied unchanged from Stage 1 section 6 ("The one paragraph version"). Figures: 71.4% answerable from documentation (§2.8), 43.8% first contact resolution (§2.5), 49.1% of escalations answerable (§2.13), 28.6% unanswerable and 17.4% policy-restricted (§2.8, §2.12). |

## 3 Who this is for

<!-- docx-table: 3 -->
| User group | What they need from this system | What they currently do instead | How you will know it worked for them |
|------------|---------------------------------|--------------------------------|--------------------------------------|
| Customers raising tickets | A fast, honest first reply for answerable questions, labelled as automated, with the source page; "I do not know" in preference to a confident error; urgent problems not stuck behind simple ones (Ravi). | Search the documentation themselves (about half the time successful), then wait for a human reply that is usually the same article. | First reply in minutes (target under 5 minutes mean); citation accuracy at least 95%; hallucination at most 5%; sampled CSAT proxy at least 4.0. |
| Tier one support agents | A draft with the relevant page attached on tickets they would otherwise answer from memory; automatic escalation of security and low-confidence tickets (Sofia). | Search a keyword knowledge base, give up, copy from a private file of past answers, write the reply by hand. | Escalation and first contact outcomes move toward targets; every auto-sent answer carries `doc_id` citations the agent can check. |
| Tier two and specialist agents | Escalations that arrive with a summary, the intent, the articles considered and what the first line was unsure about (Daniel). | Read the whole forwarded thread and re-ask the customer questions already answered. | Every escalation record contains reason, summary and sources whenever any were retrieved (verified in the harness output and decision log). |
| The head of support | First contact resolution up and escalations down without extra headcount; no wrong customer-facing answer; every automated decision explainable for the autumn compliance review (Marcus). | Reports first response time against the 2-hour agreement; manages by headcount and canned responses that agents avoid. | Harness metrics report shows first contact resolution at least 60%, escalation at most 30%, governance checks passing, and the decision log reconciles with tickets processed. |
| Technical writer (knowledge base owner) | To see which article each answer came from, so an error can be fixed in the article or in the system's reading (Ines). | Sees tickets answered with near copies of her articles, reconstructed from memory. | Every logged decision lists `sources_used` as `doc_id` values that resolve to real articles. |
| Operator and compliance reviewer | A way to stop automatic answering at once without a redeploy, and a log that explains each decision (Marcus, Daniel). | No automation exists; nothing to stop. | Kill switch forces escalate on the next routing decision and on any in-flight generation; documented in the governance notes and exercised by a test. |

## 4 Functional requirements

Priority scale: Must (not acceptable without it), Should (expected; could be deferred with a stated consequence), Could, Will not. Exclusions (Will not) are recorded in section 6.

<!-- docx-table: 4 -->
| ID | Requirement | Priority | Discovery evidence | Acceptance criteria |
|----|-------------|----------|--------------------|---------------------|
| FR-01 | The system shall ingest tickets from email, chat, docs_comment and forum into one normalised representation that keeps the original text and channel, and shall tolerate missing or empty fields. (`docs/plan/prd.md` FR-1; A2) | Must | §2.2 (four channels, 26.6% from docs comments and forum); §1c (channels never mentioned) | One sample ticket per channel processes without channel-specific failure; the normalised ticket retains original text and channel; empty or missing fields degrade or escalate rather than raise. |
| FR-02 | The system shall classify every ticket for intent and urgency and attach a confidence in [0, 1], applying deterministic rules first and then a locally trained classifier. It shall record alternatives considered and shall escalate, not call a language model, when confidence is too low. (FR-2; A3) | Must | §2.3 (22 intents, none above 5.8%); §2.4 (urgency 29.2% high); §1b.5 (urgency matters); §1a Marcus (does not know what tickets are about) | Output always contains intent, urgency and confidence; alternatives appear in the classification decision-log row; a failure path returns a defined fallback (escalate) instead of an unhandled exception; no remote model call is needed to classify. |
| FR-03 | The system shall retrieve ranked passages from the 29-article corpus, each with a score and a `doc_id` that resolves to a real article, and shall return nothing when relevance is below the measured floor. (FR-3; A4) | Must | §2.8 (71.4% answerable); §1b.3 (findability, not content); §1a Sofia, Ines | Every returned `doc_id` exists in the corpus; an irrelevant query can return an empty list; scores are present and ordered. |
| FR-04 | The system shall route each ticket to auto_respond or escalate by deterministic code over classifier confidence, a threshold measured from development data and frozen before the recorded evaluation, policy flags and the kill switch. Escalations carry a readable reason, a summary and the retrieved sources. Tickets with `must_not_auto_respond` set, or matching label-free text rules when the label is absent, never auto_respond. (FR-4; A5) | Must | §2.12 (17.4% policy-restricted); §2.13 (49.1% of escalations answerable); §1a Daniel (context on escalation), Marcus (explainability) | The same ticket twice yields the same route; threshold in force (frozen at 0.35) is logged on every decision; reason string is human-readable; escalation payload includes summary and sources when any exist; empty retrieval escalates. |
| FR-05 | The system shall generate a structured answer grounded in retrieved passages with citations that resolve to those passages, shall say it does not know when passages are insufficient, shall treat ticket text as untrusted data, and shall label the reply as automated. Generation runs only on auto_respond routes. (FR-5; A6) | Must | §1a Ravi (honest, labelled, sourced), Ines (traceability); §1a Marcus (silence over error) | Every cited `doc_id` is in the retrieved set (checked in code); no retrieval produces no citations and an escalation; an injection-style ticket cannot override instructions; output is parseable JSON with answer and citation ids. |
| FR-06 | The system shall validate every candidate reply with guardrails that can block: non-empty answer, citation ids inside the retrieved set, no citations on empty retrieval, no private-data patterns, instruction integrity, out-of-scope commitments, and a confidence floor. A blocked reply is not sent and the ticket escalates. (FR-6; A7) | Must | §1a Marcus (failure = wrong answer), Daniel (billing, security, data location); §5 risk rows 1–2 | An engineered ticket produces a block that is not sent; every guardrail result, pass or fail, is recorded; private data in outbound text has zero tolerance. |
| FR-07 | The system shall write every automated decision to a persistent decision log with the CloudServe-required fields (decision id, timestamp, ticket id, stage, input summary, model, prediction and confidence, alternatives, sources used, threshold applied, action taken, reason, guardrail results, prompt version, requirement ids). (FR-7; A8) | Must | §1a Marcus (compliance review, "I need to be able to say why") | After a harness run the number of decisions reconciles with tickets processed (reported as missing rows, expected zero); all listed fields present. |
| FR-08 | An operator shall be able to disable automatic answering immediately without a redeployment. While the switch is on the system never auto_responds; a generation already in flight finishes but its draft is not sent as auto and the ticket escalates; a running batch continues under escalate-only. The switch is read live from an environment value or a file. (FR-8; findings D4) | Must | §1a Marcus (wrong answer worse than silence), Sofia (does not want to apologise); §5 risk row 7 | With the switch on, no route is auto_respond; flipping it during a run changes the next decision and discards an in-flight auto send; behaviour is documented and tested. |
| FR-09 | An assessor shall be able to run one documented harness command with `--input` and `--output` paths that processes every ticket unattended and writes a metrics report with volume, business, technical and governance sections. No input path is hardcoded and no ticket is silently dropped. (FR-9; A9, A10) | Must | §1a Marcus (needs numbers); Stage 4 rule that the unattended run is the gate | `python -m evaluation.harness --input <file> --output <dir>` completes without intervention; every ticket yields a sent answer, an escalation or a block; the metrics file appears in the output directory. |
| FR-10 | An assessor shall be able to start the API from the README commands after copying `.env.example` to `.env`, and see health and metrics endpoints. No secrets are in the repository or its history. (FR-10; A1) | Must | Build Specification A1; Stage 1 §5 (provider key handling) | A clean checkout following the README starts the service; `.env.example` contains placeholders only. |
| FR-11 | The system shall continue through retrieval misses, provider timeouts or outages, rate limiting and malformed input without aborting a batch, degrading to escalate or skip-with-log. (FR-11; A11) | Must | §5 risk row 5 (free tier limits) | Induced failures (empty retrieval, timeout, 429, malformed ticket mid-batch) leave the harness running to completion with the failure logged. |
| FR-12 | A developer shall be able to run one documented test command and see a passing suite that covers the behaviour behind A1–A12, and no more. (FR-12; A12) | Must | Build Specification A12; project rule against decorative test suites | `python -m pytest tests/ -v` runs from `submission/` and passes. |
| FR-13 | A builder shall be able to run documented scripts that read a dataset path and print Stage 1 aggregates (channel, intent, urgency, tier and fluency splits; first contact, escalation, repeat, satisfaction and effort by segment) without reading ticket bodies. (FR-13) | Should | Stage 1 sections 2–3 (all figures); project rule on discovery | `python -m scripts.discovery_stats --input <file>` prints aggregates only and is documented. If deferred the consequence is hand-mined figures, which the project rules forbid. |

## 5 Non-functional requirements

<!-- docx-table: 5 -->
| ID | Category | Requirement | How it will be verified |
|----|----------|-------------|-------------------------|
| NFR-01 | Latency | End-to-end p95 under 3 seconds including retrieval under evaluation conditions. | Latency percentiles (mean, median, p95) in the harness metrics report. |
| NFR-02 | Availability | At least 99.5% availability, with documented behaviour when the model provider is down (escalate, never abort). | Provider-failure tests in the suite; `/health` endpoint; availability section of the metrics report. |
| NFR-03 | Accuracy | Intent classification precision at least 85%; citation accuracy at least 95%; hallucination at most 5%. | Labelled accuracy on the validation set in the metrics report; human claim-by-claim review of a sample of auto replies recorded in the human-evaluation appendix. |
| NFR-04 | Privacy | Zero private data in outbound responses. | Blocking pattern guardrail; governance scan of outputs in the metrics report; engineered test. |
| NFR-05 | Auditability | Complete decision auditability: one logged decision per ticket with the required fields. | Reconciliation of decision rows to tickets processed in every harness run (A8). |
| NFR-06 | Fairness | Resolution quality varies by less than 5 percentage points across customer tier and language fluency. | Segment quality gap in the governance section of the metrics report; method in `docs/governance/fairness-method.md`. |
| NFR-07 | Cost | Free-tier model usage only; caching, backoff and few model calls per ticket so the evaluation fits free-tier limits. | Response cache and local classify/route (no model call for them); configuration review. |
| NFR-08 | Transparency | Customer-facing replies are labelled as automated and cite the source article (Ravi, Ines). | Prompt contract and prompt register (PR-GEN-01); wording of the disclosure string is open question 1. |
| NFR-09 | Security | No API keys or secrets in the repository or history; `.env` is ignored. | `.env.example` placeholders only; packaging script excludes `.env`. |
| NFR-10 | Reproducibility | Same ticket and same configuration give the same route; harness takes input and output paths from the command line. | Determinism test; harness run on a different input file. |

## 6 What is deliberately out of scope

<!-- docx-table: 6 -->
| Not building | Why not | What would have to change for this to be reconsidered |
|--------------|---------|--------------------------------------------------------|
| Automated replies on security incidents, account compromise, billing disputes, data location, legal matters, and any refund or contractual commitment | Daniel and Sofia: these always go to a person; a wrong commitment becomes contractual or a compliance problem; 17.4% of tickets are policy-restricted (§2.12). | A reviewed policy from CloudServe naming specific sub-cases that are safe to automate, with its own evaluation. |
| Answers to feature requests, roadmap and timing, and novel incidents | No article exists to retrieve (Ines); a fabricated answer here does the most damage. | New or updated knowledge-base content covering the case. |
| A consumer-style chat interface or multi-turn conversation | The need is triage and a first draft for agents; the interface is an API and a harness. | A product decision to expose a customer-facing front end, with its own safety review. |
| Use of agents' private snippet files as a source or as training data | Unreviewed and partly stale (Daniel, Ines); would scale up mistakes. | Ines consolidates and reviews them into the knowledge base. |
| Tuning against the hidden grader set, hardcoding its path, or paid model capacity | Breaks the evaluation's integrity and the free-tier rule. | Not reconsidered within this cloudserve. |
| Auto-closing tickets in an external ticketing system, fine-tuning a custom model, multi-region high availability | Beyond the cloudserve's acceptance criteria; simulation and logging are enough. | A production deployment plan with budget. |

## 7 Assumptions and their consequences

Recorded as at version 1.0; outcomes are in Stage 5 section 3.

<!-- docx-table: 7 -->
| Assumption | Why you believe it | What happens if it is false | How you will find out |
|------------|--------------------|-----------------------------|-----------------------|
| The pack's `.env.example` threshold (0.80) is a reasonable starting point for routing and can be tuned from there. | It ships with the pack's configuration. | Almost every ticket escalates and first contact resolution collapses. The brief itself calls the value illustrative. | Sweep the threshold on development data with `scripts/tune_threshold.py` and compare first contact and escalation at each value. |
| A rules-plus-zero-shot-entity-model (GLiNER) approach would classify intent adequately without a labelled training step. | The earlier plan (findings D5) judged zero-shot extraction cheaper than a labelled training step. | Weak intent accuracy, extra dependency and a model not suited to a 22-class label set. | Compare against a classifier trained on the 500 labelled development tickets. |
| The development tickets are representative of the grader's hidden set (same schema). | The dataset guide states the same schema and categories. | Threshold and fairness results do not transfer. | Run the validation set (80 tickets) and compare against development behaviour; keep the harness path-driven. |
| Free-tier OpenRouter limits allow a full live-generation evaluation if responses are cached. | Cache plus one call per auto-respond ticket looked sufficient. | The live-generation batch cannot be completed and recorded; evidence for answer quality weakens. | Attempt a generation-enabled run and record rate-limit errors. |
| Fairness can be judged by comparing the raw auto-respond rate across tiers and fluency groups. | It is the simplest segment metric available from the harness. | A structural difference in policy-restricted mix across tiers shows as a gap that is not a quality gap. | Run the segment report on validation and inspect the gap against the policy-restricted share. |
| The embedding model and the vector index are available and consistent at run time. | Setup Guide instructs a model download and index build. | Retrieval silently returns nothing and every ticket escalates. | First unattended validation run; check the escalation reason and index statistics. |
| Success is judged against the success table (first contact at least 60%, reply under 5 minutes, satisfaction at least 4.0, escalation at most 30%), not the stricter client wish-list row. | The success table carries calculation definitions (findings D1). | The report and the PRD would aim at different bars. | Read the Evaluation Framework definitions when writing the metrics report. |

## 8 Success measures

<!-- docx-table: 8 -->
| Measure | Baseline | Target | Measured how | Reported by |
|---------|----------|--------|--------------|-------------|
| First contact resolution | 42% (Marcus); 43.8% in development history | At least 60% | Tickets closed without escalation divided by tickets processed, from the harness metrics report on the validation file | Sameer J, harness metrics report |
| Time to first reply | 8 to 12 hours (Marcus; not in ticket data) | Under 5 minutes mean; median and p95 also reported | Per-ticket system reply latency (not queue wait) from the harness report; runs without generation do not claim a business result | Sameer J, harness metrics report |
| Customer satisfaction | 3.2 / 5 (Brief baseline); 2.97 mean in development history | At least 4.0 | Mean of a human rubric (clarity, correctness, tone, citation usefulness) over a sample of auto replies, with the sample size stated | Sameer J, human-evaluation appendix |
| Escalation rate | 56.2% in development history | At most 30% | Escalated tickets divided by tickets processed, harness report | Sameer J, harness metrics report |
| Intent classification precision | Not measured | At least 85% | Predicted versus labelled intent on the validation set | Sameer J, harness metrics report |
| Hallucination and citation accuracy | Not measured | Hallucination at most 5%; citation accuracy at least 95% | Claim-by-claim review of cited passages for a sample of auto replies; code check that cited ids are retrieved | Sameer J, human-evaluation appendix |
| Private data in replies | Not measured | Zero | Pattern guardrail plus governance scan of outputs | Sameer J, harness governance section |
| Quality gap across tier and fluency | Not measured | Under 5 percentage points | Segment quality gap in the harness governance section | Sameer J, harness governance section |
| Latency p95 | Not measured | Under 3 seconds | Harness latency percentiles | Sameer J, harness metrics report |

## 9 Open questions

<!-- docx-table: 9 -->
| Question | Why it matters | Owner | Resolve by |
|----------|----------------|-------|------------|
| What exact wording marks a customer-facing reply as automated? | Ravi will calibrate trust on it; the prompt requests a disclosure flag but the wording is not fixed or enforced in code. | Sameer J, with CloudServe's head of support | 2026-11-22 (state as open in the report if not settled) |
| What is the hidden set size (the pack says both 100 and 120)? | Sample size for the final metrics; the design assumes an arbitrary number of tickets with the same schema. | Sameer J | Not blocking; harness accepts any N |
| How was first-response time measured to give "8 to 12 hours"? | The baseline for the time-to-first-reply target is not in the data. | Marcus (CloudServe) | Before any production claim; the cloudserve uses the interview figure |
| Can a live generation-enabled batch run be recorded within free-tier limits? | Closed: generate-on batch recorded (`validation_20261122T131433Z`, LiteLLM → Groq, FCR 82.5%); human review scores in `human_eval_appendix.md`. | Sameer J | 2026-11-22 |
| Does region (north_america, europe, asia_pacific, latin_america) change outcomes? | Not analysed in Stage 1; a possible fairness segment. | Sameer J | Next evaluation run if tier or fluency gaps appear |
