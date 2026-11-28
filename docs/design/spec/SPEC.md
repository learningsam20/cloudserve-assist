---
id: SPEC-cloudserve-support
companions:
  - acceptance-criteria.md
  - data-schemas.md
  - stack-and-env.md
  - submission-layout.md
sources:
  - ../../planning-artifacts/prds/prd-cloudserve_cloudserve-2026-11-22/prd.md
  - ../../../reference 01_Read_First/README.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale this contract intentionally omits.

# CloudServe Assistant

## Why

**Mandate + pain.** Graded cloudserve requires a clean-checkout, unattended-eval support system (**CloudServe Assistant**) for fictional CloudServe Solutions. The client asked for a chatbot; interview evidence shows the failure is findability and safe first response: answers already live in a small KB, escalations lack context, and confident wrong replies are unacceptable. The system must triage and assist with retrieval, deterministic routing, citations, blocking guardrails, and a full decision audit — then prove it on a path-injected ticket file a grader has never shown you.

## Capabilities

- **CAP-1**
  - **intent:** System can ingest Tickets from email, chat, docs_comment, and forum into one normalised representation that preserves original text and channel.
  - **success:** One Ticket per channel processes without channel-specific failure; empty/malformed fields do not crash the pipeline (A2, A11).

- **CAP-2**
  - **intent:** System can assign Intent and Urgency to every Ticket with a Confidence in `[0, 1]` and record alternatives considered: apply **deterministic rules first**, then a **trained local classifier** (fit on development ticket labels via script; sklearn stack already in CloudServe pins), so classification does not consume remote LLM quota.
  - **success:** Output always includes Intent, Urgency, Confidence; rule hits short-circuit the model where applicable; low model confidence leads to escalate (not LLM-as-classifier); classification stage appears in the decision log; no OpenRouter call required for this stage (A3).

- **CAP-3**
  - **intent:** System can retrieve ranked Passages from the documentation Corpus with scores and resolvable `doc_id`s, returning none when below relevance threshold.
  - **success:** Returned IDs resolve to Corpus articles; irrelevant queries may return empty list (A4).

- **CAP-4**
  - **intent:** System can route each Ticket to auto_respond or escalate using **deterministic code** over local Confidence (and policy flags), a Threshold measured then frozen from development data, with a manager-readable reason; escalations include summary and sources.
  - **success:** Same input twice → same route with no remote LLM in the route decision; reason + sources logged (A5).

- **CAP-5**
  - **intent:** System can generate a structured answer grounded in retrieved Passages with citations tied to those Passages, or state that it does not know, without treating Ticket text as instructions.
  - **success:** Every cited ID appears in the retrieved set (membership check in code); no retrieval or weak retrieval ⇒ no fake citations — escalate/abstain (A6).

- **CAP-6**
  - **intent:** System can run blocking Guardrails on every candidate response (private data, grounding, instruction integrity, tone/scope, confidence floor, fabricated citation IDs).
  - **success:** Engineered trigger produces a block, not a send; result recorded (A7).

- **CAP-7**
  - **intent:** System can persist every automated decision with Governance Framework fields and reconcile log count to Tickets processed.
  - **success:** After a full harness run, decision coverage matches processed Tickets (A8).

- **CAP-8**
  - **intent:** Assessor can run one documented harness command with `--input` and `--output` paths that processes every Ticket unattended and writes the metrics report.
  - **success:** No intervention; metrics file appears with required volume/business/technical/governance sections; no silent drops (A9, A10).

- **CAP-9**
  - **intent:** Operator can start a FastAPI service from documented commands and disable auto-answering via a kill switch without redeploying.
  - **success:** README path brings API up from clean checkout; kill switch prevents auto_respond (A1, FR-8).

- **CAP-10**
  - **intent:** Builder can run discovery/analysis scripts that accept dataset paths and emit Stage-1 aggregate figures without hand-reading Ticket or article bodies for insight.
  - **success:** Documented script(s) produce channel/intent/FCR/fairness-style aggregates from path args only.

- **CAP-11**
  - **intent:** System can degrade under retrieval miss, provider timeout/outage, rate limiting, and malformed input without aborting a batch run.
  - **success:** Induced failures yield escalate/log behaviour; harness completes (A11).

- **CAP-12**
  - **intent:** Developer can run one documented test command that exercises CloudServe-required behaviour and passes.
  - **success:** Documented pytest (or equivalent) command passes; no tests beyond what acceptance needs (A12).

## Constraints

- Only submit-ready artifacts enter this repository; drafts, memlogs, and agent scratch stay outside it.
- Dataset JSON **content** is not used as planning intelligence; schema/guide only. Figures and insights come from CAP-10 scripts and interview transcripts.
- Harness must not hardcode dataset filenames; input/output are CLI paths.
- No secrets in the tree or git history; `.env` gitignored; `.env.example` placeholders only.
- Free-tier model access only (marks do not favour paid capacity). OpenRouter `:free` is typically ~20 req/min and ~50 req/UTC day; honor `Retry-After`, exponential backoff, response cache, and **minimize** remote LLM calls (classify + route are local/code).
- Classification: **rules first**, then a **trained local classifier**. Low confidence → escalate. Do **not** fall back to LLM for labelling. Routing is code over Confidence/Threshold/policy/kill switch.
- Remote generation goes through the **LiteLLM** SDK with **OpenRouter** as the configured provider (swappable via env model/api_base without rewriting call sites). API and harness invoke the same graph.
- **Kill switch (settled):** checked at **route** for every Ticket. If on: never `auto_respond`. A generate already in flight may finish compute, but the send path is forced to **escalate** (draft attached for humans, not sent as auto). Harness continues remaining tickets under escalate-only. Flip takes effect on the **next** route decision (no redeploy).
- Ask before any stack departure from product brief + these local-model decisions.
- Threshold tunable until freeze; frozen before the recorded eval run.
- Weak retrieval (best Passage below relevance threshold) escalates or abstains — do not draft.
- Routing Threshold is measured from development data; pack `0.80` is illustrative.
- Guardrails must be able to **block** in production path, not warn-only.
- Stack starts from product brief (see `stack-and-env.md`); any departure needs a written reason in architecture notes.
- Individual academic integrity rules in CloudServe Project Instructions apply (no sharing submissions; declare AI use; do not invent discovery).
- Hidden evaluation set size may be 100 or 120 — design for arbitrary N, same schema.

## Non-goals

- Building a consumer chatbot UI as the primary deliverable.
- Tuning against or peeking at the hidden set.
- Extra test suites, frameworks, or polish not required by A1–A12 / CloudServe docs.
- Auto-resolving security, billing disputes, or contractual commitments.
- Paying for capacity to improve marks.

## Success signal

From a clean machine: follow the README, configure from `.env.example`, start the API, process one Ticket per channel, trigger one Guardrail block, run `python -m evaluation.harness --input <any_tickets.json> --output <dir>` to completion, open a metrics report and a decision log that reconcile, and run the documented tests successfully. Demo and report can then defend business metrics and governance without hand-waving.

## Assumptions

- Product display name: **CloudServe Assistant**.
- Business targets locked to success table: FCR ≥60%, reply &lt;5 min, CSAT ≥4.0, escalation ≤30% (findings D1).
- Classify: rules then trained local classifier; code for Route; **LiteLLM → OpenRouter** only for answer drafting when route is auto_respond (optional escalation prose).
- Corpus / citation field is `doc_id` (findings D2). Threshold: env 0.80 boot default → measure → freeze pre-eval (findings D3).
- Kill-switch in-flight policy settled (see Constraints).
- A12 tests cover the full A1–A12 behaviour matrix; no padding beyond that.
- SQLite for runtime decisions; export dump shipped with evaluation results for submission.
- Schedule assumes 2–3 weeks at ~1–2h weekdays / ~4–5h weekend days until cohort deadline confirmed.
- Pack deviations catalogue: `submission/docs/plan/findings.md`.

## Open Questions

- Exact customer-facing automation disclosure string (Ravi: label replies as automated).
