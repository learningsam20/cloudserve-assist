---
title: CloudServe Assistant
status: draft
created: 2026-11-22
updated: 2026-11-22
---

# PRD: CloudServe Assistant

*Capstone Stage-2 workbook still needs a student-filled copy for submission.*

## 0. Document Purpose

This PRD defines what to build for the CloudServe Solutions capstone: a runnable support triage and assist system that meets acceptance criteria A1–A12, produces honest evaluation, and leaves an audit trail. It is for the builder (sameer_j), and for downstream architecture, prompt library, sprint plan, and the graded report. Discovery numbers that depend on ticket data are marked for script output — not invented here. Interview evidence is cited by role. Capstone Pack paths under `capstone_guide/Capstone_Pack/` are the authority when this draft and the pack disagree; resolve and log the change.

## 1. Vision

CloudServe’s support team takes 8–12 hours to first reply against a 2-hour SLA, resolves only 42% of tickets on first contact, and is drowning in volume that agents describe as repetitive. The client asked for a chatbot. Interviews point elsewhere: answers already exist in a 29-article knowledge base that agents cannot find under real wording; escalations arrive with no context; a wrong confident reply is worse than silence.

Support Assist ingests tickets from four channels, classifies them, retrieves real passages from CloudServe’s documentation, and either returns a cited draft answer or escalates with a readable reason, summary, and sources. Guardrails can block unsafe output. Every automated decision is logged. An unattended evaluation harness proves behaviour on a path-injected ticket file so a clean checkout can be graded without hand-holding.

## 2. Target User

### 2.1 Jobs To Be Done

- **Marcus (Head of Support):** raise first-contact resolution and cut waiting without hiring; never ship a wrong answer he cannot explain to compliance.
- **Sofia (Tier 1):** get a draft plus the relevant page so she stops hunting private snippet files; escalate security and low-confidence cases.
- **Daniel (Tier 2):** receive escalations that show what was tried and which docs were considered — “show its working,” not a bare forward.
- **Ines (Technical writer):** see which article was cited so she can fix the article or the reading of it.
- **Ravi (customer):** get a fast, honest first reply labelled as automated, with a page link; prefer “I don’t know” over confident error.
- **Builder / assessor:** clone, configure from `.env.example`, run API, run harness, run tests, reconcile decision log — all from the README.

### 2.2 Non-Users (v1)

- End customers chatting in a polished consumer UI (API + harness first).
- Billing settlement or contractual commitment engines.
- Replacement for human handling of security, account compromise, or data-location disputes.

### 2.3 Key User Journeys

- **UJ-1. Sofia clears a repeat how-to ticket with a cited draft.**
  - **Persona + context:** Tier 1, queue 40–70/day; ticket is a familiar deployment/auth question.
  - **Entry state:** ticket already in the system (email/chat/docs/forum normalised).
  - **Path:** classify → retrieve docs → confidence above threshold → generate cited answer → guardrails pass → auto_respond logged.
  - **Climax:** she sees answer text, doc citations, and confidence; sends or lightly edits.
  - **Resolution:** decision log row for classification, routing, generation, validation; ticket marked auto_respond.
  - **Edge case:** retrieval empty → escalate with reason, no fabricated citations.
- **UJ-2. Daniel gets a useful escalation.**
  - **Persona + context:** Tier 2; ticket was below threshold or blocked.
  - **Path:** route escalate → package summary, alternatives considered, sources, uncertainty.
  - **Climax:** he does not re-ask the customer for basics already in the thread.
  - **Resolution:** action_taken=escalate in log with human-readable reason.
- **UJ-3. Guardrail blocks a dangerous reply.**
  - **Path:** generate → validation detects PII leak, ungrounded claim, injection attempt, out-of-scope commitment, or missing confidence → block.
  - **Climax:** nothing is sent; block recorded; ticket escalated.
  - **Resolution:** A7 demonstrable with an engineered ticket.
- **UJ-4. Assessor runs the gate.**
  - **Path:** clean clone → README → venv → `.env` from example → `python -m evaluation.harness --input <path> --output <dir>` → metrics file + decision log reconcile → `pytest`.
  - **Climax:** full file processed unattended; A9/A10/A12 hold.

## 3. Glossary

- **Ticket** — One support request from a Channel, normalised into a single internal representation that preserves original text and channel.
- **Channel** — One of: `email`, `chat`, `docs_comment`, `forum`.
- **Intent** — Classification label for what the Ticket is about (taxonomy discovered from labelled development data via scripts; Dataset Guide states 22 classes).
- **Urgency** — `high` | `medium` | `low`.
- **Corpus** — The 29 articles in `documentation.json` (field `doc_id`), indexed for retrieval.
- **Passage** — A retrieved chunk with a resolvable `doc_id` and score.
- **Route** — `auto_respond` | `escalate` | `block` (block is a validation outcome that prevents send).
- **Confidence** — Numeric score in `[0, 1]` attached to classification (and used by routing); must be calibratable against observed accuracy.
- **Threshold** — Routing cutoff measured from development data; env default is illustrative only.
- **Guardrail** — Runtime check that can **block** a response (warn-only does not satisfy A7).
- **Decision log** — Persistent store of every automated decision with required fields; count must equal tickets processed for covered stages.
- **Harness** — CLI that reads a ticket JSON path, writes results and a metrics report to an output path, unattended.
- **Hidden set** — Grader-held tickets (~100–120; pack inconsistent); same schema; never tuned against; harness must accept arbitrary path.
- **Support Assist** — This product (not a free-form chatbot).

## 4. Features

### 4.1 Ingest and normalise

**Description:** Accept Tickets from all four Channels and map them to one internal schema without channel-specific crashes. Preserve body text and channel; tolerate missing fields, odd characters, empty bodies. Realizes UJ-1, UJ-4. Evidence: Build Spec A2; Dataset Guide channel enum.

**Functional Requirements:**

#### FR-1: Four-channel ingest

System can ingest email, chat, docs_comment, and forum Tickets into one normalised representation. Realizes UJ-1, UJ-4.

**Consequences (testable):**

- One sample per Channel processes without channel-specific exception.
- Normalised object retains original text and Channel.
- Missing/empty fields do not crash the pipeline (degrade or escalate per policy).

### 4.2 Classification

**Description:** Assign Intent and Urgency with Confidence; record alternatives considered; never throw on hard cases — return a defined fallback. Realizes UJ-1. Evidence: A3; Evaluation Framework classification precision ≥85%.

**Functional Requirements:**

#### FR-2: Intent and urgency with confidence

System can classify every Ticket for Intent and Urgency and attach Confidence in `[0, 1]`. Realizes UJ-1.

**Consequences (testable):**

- Output includes Intent, Urgency, Confidence.
- Alternatives considered are recorded in the Decision log for the classification stage.
- Failure path returns defined fallback (e.g. escalate) rather than an unhandled exception.

### 4.3 Retrieval

**Description:** Search the Corpus; return ranked Passages with scores and real `doc_id`s. Below relevance threshold return nothing (no filler hits). Chunking is a justified design choice. Realizes UJ-1. Evidence: A4; Setup Guide chunk experiments.

**Functional Requirements:**

#### FR-3: Corpus retrieval with resolvable sources

System can retrieve ranked Passages from the Corpus with identifiers that resolve to real articles. Realizes UJ-1.

**Consequences (testable):**

- Returned `doc_id`s exist in the Corpus.
- Irrelevant queries can yield an empty Passage list.
- Scores are present and ordered.

### 4.4 Routing

**Description:** Deterministic decision to auto_respond vs escalate using a Threshold measured from data. Reasons readable by a support manager. Escalations carry summary + sources. Realizes UJ-2. Evidence: A5; Brief threshold note; Marcus/Daniel interviews.

**Functional Requirements:**

#### FR-4: Threshold routing

System can route Tickets using a configured Threshold such that the same input yields the same Route. Realizes UJ-2.

**Consequences (testable):**

- Identical Ticket twice → identical Route.
- Escalation payload includes summary and retrieved sources when any exist.
- Reason string is human-readable and logged.
- Tickets with `must_not_auto_respond` never auto_respond. If it is absent, it can be computed based on guardrails and intent classification

### 4.5 Generation

**Description:** Produce answers grounded in Passages with citations tied to retrieved text; say when unknown; separate Ticket content from instructions (injection defence); structured parseable output; disclose automation where customer-facing. Realizes UJ-1. Evidence: A6; Ravi interview; Governance Framework.

**Functional Requirements:**

#### FR-5: Grounded cited generation

System can generate a structured answer grounded in retrieved Passages with citations that resolve to those Passages, or state that it does not know. Realizes UJ-1.

**Consequences (testable):**

- Citations resolve to retrieved Passage/`doc_id` pairs (A6).
- No retrieval → no fabricated citations; prefer escalate/unknown.
- Ticket body cannot override system instructions (injection cases blocked or ignored).

### 4.6 Validation and guardrails

**Description:** Run on every generated response. Minimum: private data, grounding; also tone/scope and instruction integrity per Governance Framework. Must be able to **block**. Realizes UJ-3. Evidence: A7.

**Functional Requirements:**

#### FR-6: Blocking guardrails

System can validate every candidate response and block when a Guardrail fires. Realizes UJ-3.

**Consequences (testable):**

- Engineered trigger Ticket → response blocked, not sent (A7).
- Guardrail results recorded whether pass or fail.
- Private data in outbound text: zero tolerance (governance pass/fail).

### 4.7 Decision logging and kill switch

**Description:** Persist every automated decision with required fields; coverage reconciles with processed Tickets. Kill switch stops auto-answering without redeploy. Realizes UJ-4. Evidence: A8; Governance Framework schema.

**Functional Requirements:**

#### FR-7: Persistent decision log

System can write each automated decision to a persistent Decision log with the Capstone-required fields. Realizes UJ-4.

**Consequences (testable):**

- After a harness run, logged decisions reconcile with Tickets processed (A8).
- Fields include at least: decision_id, timestamp, ticket_id, stage, input_summary, model, prediction+confidence, alternatives, sources_used, threshold_applied, action_taken, reason, guardrail_results, prompt_version, requirement_ids (per Governance Framework).

#### FR-8: Kill switch

Operator can disable automatic answering immediately without a new deployment.

**Consequences (testable):**

- With kill switch on, Routes do not auto_respond; behaviour documented (in-flight policy stated).

### 4.8 Evaluation harness and metrics

**Description:** Single documented command; `--input` and `--output`; processes every Ticket; writes metrics report automatically; no silent drops. Realizes UJ-4. Evidence: A9, A10; Evaluation Framework tiers.

**Functional Requirements:**

#### FR-9: Unattended path-parameterised harness

Assessor can run the Harness with input and output paths and leave it until completion. Realizes UJ-4.

**Consequences (testable):**

- `python -m evaluation.harness --input <file> --output <dir>` (or documented equivalent) processes all Tickets without intervention (A9).
- Metrics report appears under output with volume, business, technical, and governance sections required by Build Spec (A10).
- Every Ticket yields sent answer, escalation, or block — none silently dropped.

### 4.9 API, observability, CI, tests

**Description:** FastAPI entry for Ticket processing; Prometheus metrics; GitHub Actions runs tests; one-command test suite. Evidence: A1, A11, A12; Setup Guide.

**Functional Requirements:**

#### FR-10: Documented runnable service

Assessor can start the API using the README command after configuring `.env` from `.env.example`. Realizes UJ-4.

**Consequences (testable):**

- Clean checkout + README steps succeed (A1).
- No secrets in repo or history.

#### FR-11: Graceful failure

System can continue under no retrieval hit, provider timeout/outage, rate limiting, and malformed input without crashing the batch. Realizes UJ-4.

**Consequences (testable):**

- Induced failure modes degrade (escalate/skip-with-log) rather than abort the Harness (A11).

#### FR-12: One-command tests

Developer can run the documented test command and see a passing suite. Realizes UJ-4.

**Consequences (testable):**

- Documented command (e.g. `python -m pytest tests/ -v`) executes and passes (A12).
- Suite covers behaviour needed for A1–A12 claims — not padded coverage theater. `[ASSUMPTION: minimal tests = component contracts + one guardrail block + harness dry path with fixtures; no load/perf suite required beyond latency measurement in eval]`

### 4.10 Discovery scripts (builder tooling)

**Description:** Scripts compute Stage-1 workbook figures from ticket JSON (channel/intent splits, FCR baseline, answerable_from_docs rate, fairness segment outcomes, etc.) so humans do not hand-mine files. Evidence: Dataset Guide “verify yourself”; user constraint.

**Functional Requirements:**

#### FR-13: Scripted discovery stats

Builder can run documented scripts that read ticket/corpus paths and emit Stage-1 tables without manually inspecting Ticket bodies for insight.

**Consequences (testable):**

- Script accepts input path; prints or writes aggregate stats only.
- README or `docs/plan/` explains how to regenerate Discovery figures.

## 5. Non-Goals (Explicit)

- Consumer chatbot UI / multi-turn sales bot.
- Paying for model capacity to chase marks (free tier only).
- Tuning against the Hidden set or hardcoding its path.
- Auto-sending billing commitments, security incident resolutions, or legal promises.
- Replacing technical writers’ review process; system cites Corpus, it does not invent policy.
- Extra tests, dashboards, or frameworks beyond Capstone requirements.
- Reading dataset contents during planning to pre-fill “insights” into docs.

## 6. MVP Scope

### 6.1 In Scope

- Pipeline: ingest → classify → retrieve → route → generate → validate → log.
- FastAPI + Harness + pinned deps + `.env.example` + README proven on clean checkout.
- Decision log (SQLite acceptable), blocking Guardrails, kill switch.
- Metrics report from Harness matching Evaluation Framework content requirements.
- Prompt library under `prompts/` with versions and requirement traceability.
- CI workflow running tests; Prometheus metrics endpoint.
- Discovery scripts for Stage-1 aggregates.
- Student workbooks, effort log, report, video (submission packaging) — content produced during the three weeks.

### 6.2 Out of Scope for MVP

- Multi-region HA / real Postgres unless justified.
- Fine-tuned custom LLM.
- Agent desktop UI beyond API responses.
- Auto-closing tickets in an external ITSM (simulation/log only).

## 7. Success Metrics

**Primary (business — Brief success table)**

- **SM-1:** FCR ≥60% (closed without escalation ÷ total). Validates FR-4, FR-5.
- **SM-2:** Mean time to first reply <5 minutes (also report median, p95). Validates FR-9, FR-10.
- **SM-3:** Escalation rate ≤30%. Validates FR-4.
- **SM-4:** CSAT proxy ≥4.0 via sampled human rubric (state n). Validates FR-5.

**Secondary (technical)**

- **SM-5:** Intent precision ≥85%; hallucination ≤5%; citation accuracy ≥95%; latency p95 <3s; availability ≥99.5% including provider-down behaviour.

**Governance (pass/fail)**

- **SM-6:** Zero PII in outbound; <5pp quality gap across segments; decision log complete coverage; calibration within 5 points.

**Counter-metrics**

- **SM-C1:** Do not maximise auto_respond rate if it raises hallucination or repeat contacts.
- **SM-C2:** Do not chase classification accuracy by answering ungroundable Tickets.

## 8. Open Questions

1. Exact customer-facing automation disclosure string (Ravi) — prompt + API field.
2. Hidden set size 100 vs 120 — treat as “unknown N, same schema”.
3. Validation set: tune on development; validation for self-check; record run counts (confirm).

Settled 2026-11-22: name **CloudServe Assistant**; generation **LiteLLM → OpenRouter**; classify **rules then trained local classifier** (findings D5); kill-switch **findings D4**. Config baseline: `06_Configuration`.

## 9. Assumptions Index

Settled from builder comments (2026-11-22):

- Capstone Brief stack is the default. **Any conflict or departure: ask before changing** — do not silently diverge. Pack conflicts: `submission/docs/plan/findings.md` (D1–D5). Additive package approved: `litellm` only (classifier uses pack sklearn).
- **Business targets (success table):** FCR ≥60%, reply &lt;5 min, CSAT ≥4.0, escalation ≤30%. Client wish-list row (65% / 2h / 4.2) is report context only — see findings D1.
- `CONFIDENCE_THRESHOLD` may be tuned on development data, then **frozen before the recorded eval run**; no further threshold edits after that freeze without a logged PRD revision — see findings D3. Env `0.80` is boot default only.
- Corpus / citation IDs use **`doc_id`** (not Setup Guide `id`) — see findings D2.
- A12 tests cover **all acceptance behaviours needed for A1–A12** (full required matrix, not a stub suite). No decorative extra suites beyond that.
- Runtime decision store is SQLite; for submission, **export/dump** decisions to a shippable artifact (e.g. `evaluation/results/decisions_export.md` or `.jsonl`) in addition to the DB.
- Discovery interview disagreements are settled by FR-13 scripts, not by hand-reading Ticket bodies. Confirmed.
- Schedule: plan work over **2–3 weeks**, about **1–2 hours on weekdays** and **4–5 hours on weekend days** (pack calendar date treated as template until cohort deadline confirmed).

## 10. Constraints and Guardrails

- Clean-checkout gate before marks (A1/A9).
- No API keys in tree or git history.
- AI-tool use allowed with declaration; do not invent discovery findings.
- Individual work; no sharing of code/prompts/workbooks.
- Local models preferred for classify (and any scores feeding route); remote LLM only where generation/language is required (see SPEC / stack-and-env).
- Docs stay in `_bmad-output/` until promote-just-before-development.

## 11. Cross-Cutting NFRs

| ID | Requirement |
|----|-------------|
| NFR-01 | Latency p95 <3s end-to-end including retrieval under eval conditions |
| NFR-02 | Availability ≥99.5% with documented provider-down behaviour |
| NFR-03 | Classification precision ≥85%; citation accuracy ≥95%; hallucination ≤5% |
| NFR-04 | Zero private data in outbound responses |
| NFR-05 | Complete decision auditability (A8) |
| NFR-06 | Fairness: <5pp quality variation across tier / fluency / complexity segments |
| NFR-07 | Free-tier cost only; backoff, queue, cache as needed |

## 12. Traceability to Capstone acceptance

| Acceptance | Primary FRs |
|------------|-------------|
| A1 | FR-10 |
| A2 | FR-1 |
| A3 | FR-2 |
| A4 | FR-3 |
| A5 | FR-4 |
| A6 | FR-5 |
| A7 | FR-6 |
| A8 | FR-7 |
| A9 | FR-9 |
| A10 | FR-9 |
| A11 | FR-11 |
| A12 | FR-12 |
