---
status: draft
stepsCompleted: [inventory, epics, stories]
inputDocuments:
  - ../../specs/spec-cloudserve-support/SPEC.md
  - ../prds/prd-cloudserve_cloudserve-2026-11-22/prd.md
  - ../architecture/architecture-cloudserve_cloudserve-2026-11-22/ARCHITECTURE-SPINE.md
  - ../../../submission/docs/plan/findings.md
  - ../../../reference 01_Read_First/README.md
---

# cloudserve_cloudserve - Epic Breakdown

## Overview

Epics and stories for CloudServe Support Assist, traced to SPEC CAP-1..12, PRD FR-1..13, acceptance A1–A12, and delivery stage work (discovery → build → gate → package). Schedule assumes ~1–2h weekdays / ~4–5h weekend days over 2–3 weeks. Code lands in `submission/` when ready; planning artifacts stay under `_bmad-output/` until promote-before-dev (except `submission/docs/plan/findings.md`).

## Requirements Inventory

### Functional Requirements

FR-1 Ingest four channels · FR-2 Classify+confidence · FR-3 Retrieve · FR-4 Route · FR-5 Generate · FR-6 Guardrails · FR-7 Decision log · FR-8 Kill switch · FR-9 Harness · FR-10 API runnable · FR-11 Graceful failure · FR-12 Tests · FR-13 Discovery scripts

### NonFunctional Requirements

NFR-01 Latency · NFR-02 Availability · NFR-03 Accuracy/citation/hallucination · NFR-04 Privacy · NFR-05 Auditability · NFR-06 Fairness · NFR-07 Free-tier cost

### Additional Requirements

A1–A12 · findings D1–D5 · rules+trained classifier · code route · LiteLLM→OpenRouter generate only · harness `--input`/`--output` · `06_Configuration` baseline

### FR Coverage Map

| FR/CAP/A | Epic |
|----------|------|
| FR-13 / CAP-10 | Epic 1 |
| FR-1 / CAP-1 / A2 | Epic 2 |
| FR-2 / CAP-2 / A3 | Epic 2 |
| FR-3 / CAP-3 / A4 | Epic 2 |
| FR-4 / CAP-4 / A5 | Epic 3 |
| FR-5 / CAP-5 / A6 | Epic 3 |
| FR-6 / CAP-6 / A7 | Epic 3 |
| FR-7 / CAP-7 / A8 | Epic 4 |
| FR-8 / CAP-9 | Epic 4 |
| FR-10 / CAP-9 / A1 | Epic 4 |
| FR-9 / CAP-8 / A9–A10 | Epic 5 |
| FR-11 / CAP-11 / A11 | Epic 5 |
| FR-12 / CAP-12 / A12 | Epic 6 |
| NFR-01..07 / governance packaging | Epic 6 |

## Epic List

1. **Repo foundation and discovery tooling** — Scaffold submission project; scripted Stage-1 aggregates (no hand-mining).
2. **Ingest, classify, retrieve** — Normalise channels; rules+trained classifier; Chroma corpus with `doc_id`.
3. **Route, generate, guardrails** — Deterministic threshold route; cited generation; blocking guards.
4. **Persistence, API, kill switch** — Decision log; FastAPI; clean-checkout README path.
5. **Harness, metrics, resilience** — Path-parameterised unattended eval; failure modes; threshold freeze.
6. **Tests, CI, observability, submission readiness** — A12 suite; GHA; Prometheus; packaging checklist.

---

## Epic 1: Repo foundation and discovery tooling

Stand up the submission skeleton and CAP-10 scripts so discovery numbers come from code, not JSON browsing.

### Story 1.1: Submission scaffold and config

As a builder,
I want a CloudServe-shaped `submission/` tree with pinned requirements, `.env.example`, and `.gitignore`,
So that a clean checkout can be configured without secrets in git.

**Acceptance Criteria:**

**Given** an empty or partial `submission/`
**When** this story is done
**Then** `README.md` stub, `requirements.txt` (from `06_Configuration` pins + `litellm`), `.env.example`, `.gitignore` (`.env`, `storage/`), and package dirs exist
**And** no real API keys are committed

### Story 1.2: Shared config and domain models

As a developer,
I want `src/config.py` and Pydantic `Ticket`/`Passage`/result models,
So that every stage shares one shape (AD-4).

**Acceptance Criteria:**

**Given** the scaffold
**When** models load a minimal fixture ticket
**Then** channel enum and required fields validate
**And** config loads dotenv and exposes threshold/top_k/paths

### Story 1.3: Discovery aggregate script

As a builder,
I want `scripts/discovery_stats.py --input <tickets.json>` emitting Stage-1 tables,
So that interview disagreements can be settled without reading ticket bodies in chat (CAP-10).

**Acceptance Criteria:**

**Given** a path to development or validation tickets
**When** the script runs
**Then** it prints or writes aggregates only (counts/rates by channel, intent, tier, fluency, FCR, answerable_from_docs, etc.)
**And** it does not print full `body`/`content` fields

### Story 1.4: Threshold tuning script skeleton

As a builder,
I want `scripts/tune_threshold.py` that scores routing cutoffs on development labels,
So that we can freeze a measured threshold (findings D3) before recorded eval.

**Acceptance Criteria:**

**Given** tickets with `labels.expected_route` and model confidences (or a stub confidence column for dry-run)
**When** the script runs
**Then** it reports candidate thresholds with precision/recall or cost of auto vs escalate errors
**And** documents that the chosen value must be frozen in env before recorded eval

---

## Epic 2: Ingest, classify, retrieve

Deliver CloudServe week-two days 1–2 behaviours: four-channel normalise, local classification, retrieval with real `doc_id`s.

### Story 2.1: Four-channel ingest

As the system,
I want ingest to normalise email/chat/docs_comment/forum into one Ticket,
So that A2 holds and empty/malformed fields do not crash (CAP-1, FR-1).

**Acceptance Criteria:**

**Given** one fixture per channel
**When** ingest runs
**Then** each yields a Ticket preserving text and channel
**And** missing/empty fields produce a defined soft outcome (not an unhandled exception)

### Story 2.2: Train and run local classifier

As the system,
I want Intent, Urgency, and Confidence from rules plus a classifier trained on development labels,
So that A3 holds without burning remote LLM quota (CAP-2, FR-2, AD-3, findings D5).

**Acceptance Criteria:**

**Given** `scripts/train_classifier.py --input <development_tickets.json> --output <CLASSIFIER_DIR>`
**When** training completes
**Then** a joblib artifact is written and loadable by `classify.py`
**And** classify on a Ticket returns Intent, Urgency, Confidence in `[0,1]` with alternatives from `predict_proba`
**And** no OpenRouter call is made during classify
**And** measured intent precision on a held-out slice is reported by the train script

### Story 2.3: Index documentation corpus

As the system,
I want Chroma indexed from `documentation.json` using `doc_id` metadata,
So that retrieval IDs resolve to real articles (CAP-3, AD-8, findings D2).

**Acceptance Criteria:**

**Given** a path to documentation JSON
**When** index/build runs
**Then** each chunk stores `doc_id` (not `id`)
**And** index persists under `CHROMA_PATH`

### Story 2.4: Retrieve ranked passages

As the system,
I want ranked Passages with scores and empty results below relevance,
So that A4 holds and weak retrieval can escalate later (CAP-3, FR-3).

**Acceptance Criteria:**

**Given** an indexed corpus and a Ticket
**When** retrieve runs
**Then** passages include resolvable `doc_id` and score
**And** queries with no relevant hit may return `[]`

---

## Epic 3: Route, generate, guardrails

Deterministic policy, cited answers, and at least one blocking guardrail (A5–A7).

### Story 3.1: Deterministic code routing

As a support manager,
I want auto_respond vs escalate decided by code over Confidence + frozen threshold + policy flags,
So that the same input always yields the same route (CAP-4, FR-4, A5).

**Acceptance Criteria:**

**Given** identical classification+retrieval state twice
**When** route runs
**Then** `action` and reason are identical
**And** `must_not_auto_respond`-style policy never auto_responds
**And** weak/empty retrieval forces escalate
**And** `threshold_applied` is recorded

### Story 3.2: Graph wiring through route

As a developer,
I want LangGraph nodes for ingest→classify→retrieve→route,
So that API and harness share one path (AD-1).

**Acceptance Criteria:**

**Given** a Ticket
**When** `graph.run_ticket` executes through route
**Then** state carries classification, passages, and route decision
**And** escalate path does not call generate

### Story 3.3: Grounded generation with cache

As a customer/agent,
I want a structured cited answer from retrieved passages via remote LLM,
So that A6 can pass and free-tier use stays bounded (CAP-5, FR-5, AD-6).

**Acceptance Criteria:**

**Given** route=auto_respond and non-empty passages
**When** generate runs
**Then** output is structured with citation IDs
**And** results are cached by `(model, prompt_hash)`
**And** 429 handling uses backoff / Retry-After without crashing the caller

### Story 3.4: Blocking guardrails

As compliance,
I want validation that can block unsafe or ungrounded answers,
So that A7 is demonstrable (CAP-6, FR-6).

**Acceptance Criteria:**

**Given** a crafted response with PII and/or citation ID not in retrieved set
**When** guardrails run
**Then** action becomes block (not send)
**And** guardrail results are recorded whether pass or fail
**And** at least one automated test triggers a block

### Story 3.5: Prompt library v1

As a builder,
I want versioned prompts under `prompts/` traced to FRs,
So that delivery stage 3 artefacts exist and injection boundaries are explicit.

**Acceptance Criteria:**

**Given** generate/classify needs
**When** prompts are loaded
**Then** ticket text is delimited as untrusted data
**And** each prompt file records version + requirement ids

---

## Epic 4: Persistence, API, kill switch

Audit trail and clean-checkout service surface (A1, A8).

### Story 4.1: Decision logging store

As an auditor,
I want every automated decision persisted with Governance fields,
So that log count reconciles with processed tickets (CAP-7, FR-7, A8).

**Acceptance Criteria:**

**Given** a completed pipeline run for a ticket
**When** stages finish
**Then** SQLite rows exist for required stages with prediction, confidence, sources, action, reason, threshold, prompt_version, requirement_ids
**And** an export path can dump decisions for submission

### Story 4.2: FastAPI ticket endpoint

As an assessor,
I want a documented API to submit a ticket and receive PipelineResult,
So that README smoke tests pass (CAP-9, FR-10, A1).

**Acceptance Criteria:**

**Given** `.env` configured from `.env.example`
**When** `python -m src.api` (or documented uvicorn command) starts
**Then** a ticket POST/GET flow returns classification, route, and answer or escalation
**And** Prometheus metrics endpoint is reachable

### Story 4.3: Kill switch

As Head of Support,
I want to disable auto-answering without redeploying,
So that FR-8 / AD-7 hold.

**Acceptance Criteria:**

**Given** kill switch enabled via documented mechanism
**When** a ticket that would otherwise auto_respond is processed
**Then** action is escalate (or documented safe mode)
**And** README states in-flight behaviour

### Story 4.4: README clean-checkout path

As an assessor,
I want literal README steps from empty clone to running API,
So that A1 passes on a foreign machine.

**Acceptance Criteria:**

**Given** a fresh checkout of `submission/`
**When** README steps are followed in order
**Then** venv, install, `.env`, and API start succeed
**And** commands match what actually works (rehearsed)

---

## Epic 5: Harness, metrics, resilience

The gate: unattended path-parameterised eval (A9–A11).

### Story 5.1: Evaluation harness CLI

As an assessor,
I want `python -m evaluation.harness --input <path> --output <dir>`,
So that hidden-set injection works (CAP-8, FR-9, A9).

**Acceptance Criteria:**

**Given** any tickets JSON of length N
**When** harness runs unattended
**Then** every ticket yields answer, escalate, or block — none silently dropped
**And** no dataset filename is hardcoded

### Story 5.2: Automatic metrics report

As Head of Support,
I want a metrics file with volume, business, technical, and governance sections,
So that A10 and Evaluation Framework content requirements hold (CAP-8).

**Acceptance Criteria:**

**Given** a completed harness run
**When** output dir is inspected
**Then** a metrics report exists covering required sections
**And** business metrics use success-table targets (findings D1)
**And** figures are computed by code

### Story 5.3: Failure-mode resilience

As an assessor,
I want provider timeout/outage, rate limit, empty retrieval, and malformed input handled,
So that A11 / CAP-11 hold without aborting the batch.

**Acceptance Criteria:**

**Given** induced provider failure or malformed ticket mid-run
**When** harness continues
**Then** the process does not crash
**And** affected tickets are escalated/logged

### Story 5.4: Freeze threshold and recorded validation run

As a builder,
I want the measured threshold frozen and a validation run recorded,
So that findings D3 and eval discipline hold before packaging.

**Acceptance Criteria:**

**Given** `tune_threshold.py` results
**When** threshold is written to `.env` / config
**Then** change-log notes freeze date and value
**And** a validation harness run date and count are recorded for the report

---

## Epic 6: Tests, CI, observability, submission readiness

Close CloudServe packaging and A12.

### Story 6.1: A1–A12 behaviour test suite

As a developer,
I want one documented pytest command covering required acceptance behaviours,
So that A12 passes without decorative padding (CAP-12, FR-12).

**Acceptance Criteria:**

**Given** `python -m pytest tests/ -v` (or README equivalent)
**When** tests run
**Then** suite passes
**And** tests cover ingest channels, route determinism, at least one guardrail block, and harness dry-run with fixtures

### Story 6.2: GitHub Actions CI

As a builder,
I want CI to run pytest on push/PR without secrets,
So that CloudServe Setup Guide automation requirement is met.

**Acceptance Criteria:**

**Given** `.github/workflows/ci.yml`
**When** workflow runs
**Then** it installs requirements and runs the documented test command
**And** no API keys are required for CI (mocks/fixtures)

### Story 6.3: Prometheus metrics wiring

As an operator,
I want ticket counters and latency histograms,
So that NFR observability and demo dashboards are possible.

**Acceptance Criteria:**

**Given** API or harness processing tickets
**When** `/metrics` (or documented port) is scraped
**Then** counters include outcomes and guardrail blocks
**And** latency histogram is present

### Story 6.4: Governance artefacts checklist

As a builder,
I want risk register, fairness method note, incident procedure stub, and decision-export verified,
So that CloudServe governance marks have real artefacts (not last-afternoon fiction).

**Acceptance Criteria:**

**Given** docs under `submission/docs/governance/` (when promoted) or staging drafts
**When** checklist is reviewed
**Then** risk register, fairness segment method, incident steps, and kill-switch answers exist
**And** decision export reconciles with a sample harness run

### Story 6.5: Submission package dry-run

As a builder,
I want a pre-submit checklist matching CloudServe Submission Guide,
So that zip layout and gate rehearsal are not left to the final hour.

**Acceptance Criteria:**

**Given** working software
**When** dry-run checklist is executed
**Then** fresh-clone README path, harness on validation path, tests, and secret scan are checked off
**And** change-log notes the rehearsal date
