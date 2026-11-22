# Stage 3 — Prompt Library: CloudServe Assistant

| Field | Value |
|-------|-------|
| Author | Sameer J (sameer_j) |
| Date | 2026-11-22 |
| Requirements source | `Stage_2_PRD_Template` (FR-01 to FR-13, NFR-01 to NFR-10); narrative in `docs/plan/prd.md` |
| Detailed contract | `docs/design/spec/SPEC.md` (capabilities CAP-1 to CAP-12), `docs/design/spec/acceptance-criteria.md` (A1–A12) |
| Prompt files | `prompts/generate_v1.md` (PR-GEN-01). No other prompt file exists, by design. |

**A note on what is, and is not, a prompt in this system.** CloudServe Assistant calls a language model in exactly one place: drafting a cited answer for tickets already routed to auto_respond. Classification is rules followed by a locally trained scikit-learn classifier (TF-IDF with logistic regression, fitted on the labelled development tickets by `scripts/train_classifier.py`). Routing is deterministic code. Retrieval is an embedding search. Escalation summaries are built by code from structured fields. There are therefore no LLM classification, routing or labelling prompts; a low-confidence classification escalates and does not ask a model to label the ticket (findings D5). The register below records the one build prompt (PR-GEN-01), the explicit absence of a classification prompt (PR-02), and the reviewer rubric used for evaluation (PR-03).

## 1 Section one: from requirement to specification

Components named below are in `submission/`. Test identifiers are pytest node names under `tests/`.

<!-- docx-table: 2 -->
| Requirement ID | Specification summary | Inputs | Outputs | Acceptance criteria |
|----------------|-----------------------|--------|---------|---------------------|
| FR-01 | `src/ingest.py` maps a raw ticket dict from any of the four channels to one `Ticket` object, preserving subject, body and channel; non-string channel values are coerced to a defined default; absent fields become empty values. | Raw ticket JSON object (channel, subject, body, ids, customer fields, optional labels). | Normalised `Ticket`. | One ticket per channel ingests; original text and channel retained; empty or malformed fields do not raise (A2, A11). |
| FR-02 | `src/classify.py` applies deterministic rules first (`apply_rules`); otherwise predicts intent and urgency with the saved classifier and returns the model confidence and other candidates as alternatives. `node_classify` in `src/graph.py` turns any classification failure into a defined fallback (`unclear_request`, confidence 0.0) so the ticket escalates. No remote model call. | `Ticket` text; classifier artefact under `CLASSIFIER_DIR`. | `Classification` (intent, urgency, confidence in [0, 1], alternatives). | Always returns intent, urgency, confidence; alternatives recorded in the classify decision row; low confidence leads to escalate (A3). |
| FR-03 | `src/retrieve.py` embeds the query, searches the Chroma index built from `documentation.json` by `scripts/build_index.py` (chunk size and overlap from `.env`), applies the relevance floor and returns the top-k passages with `doc_id`, title, text and score. | Ticket text; `RETRIEVAL_TOP_K`, `RETRIEVAL_MIN_SCORE`. | Ordered list of `Passage`; empty when nothing clears the floor. | Every `doc_id` exists in the corpus; scores present and ordered; irrelevant query may return none (A4). |
| FR-04 | `src/route.py` decides auto_respond or escalate in code: kill switch first, then policy must-not (label, else text rules), then empty retrieval, then confidence against the frozen threshold (0.35), with a grounded override when the best passage score is high and confidence is near the threshold. Each decision carries a readable reason and the threshold applied; escalations get a summary and sources from `src/graph.py`. | `Ticket`, `Classification`, passages; `.env` threshold and override settings. | `RouteDecision` (action, reason, threshold_applied, kill_switch, grounded_override); escalation package. | Same input gives the same route; reason logged; policy tickets never auto_respond; empty retrieval escalates (A5). |
| FR-05 | `src/generate.py` builds the messages from `prompts/generate_v1.md` (PR-GEN-01), calls the model through `src/llm.py` (LiteLLM to OpenRouter, timeout, retries with backoff), caches responses on disk, parses structured output and returns answer and citation ids. Called only when the route is auto_respond and passages exist. | `Ticket` text, passages, `LITELLM_MODEL`, temperature. | `GenerationResult` (answer, citation_doc_ids, model, cached). | Citation ids are checked against the retrieved set by code; no retrieval gives no citations and escalates; ticket text is delimited as untrusted data (A6). |
| FR-06 | `src/guardrails.py` runs checks on every candidate: non-empty answer, citation ids within the retrieved set, no citations with empty retrieval, private-data patterns, injection-like language, out-of-scope commitments, confidence floor (skipped only when the grounded override already applied). Any failure blocks; `src/graph.py` turns a block into an escalation. | `GenerationResult`, passages, classification, threshold. | List of `GuardrailResult` (name, passed, detail) and a blocked flag. | An engineered bad generation is blocked and not sent; every result recorded (A7). |
| FR-07 | `src/logging_store.py` persists one row per pipeline stage decision in SQLite with the Governance Framework fields; `evaluation/harness.py` reconciles rows to tickets processed. | Stage outputs from the graph. | Rows in the decision database; reconciliation field in the metrics report. | Decision rows cover every ticket processed; required fields present (A8). |
| FR-08 | `src/config.py` re-reads `KILL_SWITCH` and the `KILL_SWITCH_FILE` path live. `src/graph.py` checks at route, before generate and after generate; an in-flight draft is discarded from the auto path and the ticket escalates; the harness continues escalate-only (findings D4). | Environment value or flag file. | Forced escalate with a kill-switch reason; `/health` exposes the state. | With the switch on no route is auto_respond; flip takes effect on the next decision with no redeploy (FR-8). |
| FR-09 | `evaluation/harness.py` reads the ticket file named by `--input`, runs every ticket through the same LangGraph pipeline as the API, writes per-ticket results and the metrics report (`evaluation/metrics_report.py`) under `--output`; malformed tickets are logged and skipped without stopping the run. | `--input` ticket JSON path, `--output` directory; optional flags such as generation off. | `results.jsonl`, metrics report with volume, business, technical, governance sections. | One unattended command processes the full file; no silent drops; metrics file written (A9, A10). |
| FR-10 | `src/api.py` (FastAPI) exposes health, ticket processing and Prometheus metrics; `README.md` and `scripts/*.sh` give the setup and start commands; `.env.example` holds placeholders only. | `.env`; ticket JSON over HTTP. | Running service; process result JSON. | Clean checkout following the README reaches a healthy service (A1). |
| FR-11 | Provider calls have a timeout and retry with backoff on 429 (`src/llm.py`); `node_generate` converts any generation or validation exception into an escalation; the harness continues after a bad ticket. | Provider responses and errors; malformed ticket objects. | Escalation with an error note; completed batch. | Induced timeouts, rate limits, empty retrieval and malformed tickets do not abort a run (A11). |
| FR-12 | `tests/` holds the pytest suite for the behaviours above; one documented command runs it. | Repository state. | Pass or fail report. | `python -m pytest tests/ -v` passes (A12). |
| FR-13 | `scripts/discovery_stats.py` reads a ticket JSON path and prints aggregate counts, rates and per-segment means from `labels` and `history` only. | `--input` ticket JSON path. | Printed aggregates (see Stage 1 Appendix A). | Prints aggregates only; documented in the README and Stage 1 (FR-13). |

## 2 Section two: the prompt register

### Prompt PR-01 (register id PR-GEN-01)

<!-- docx-table: 3 -->
| Field | Value |
|-------|-------|
| Name and purpose | PR-GEN-01, grounded cited answer drafting. Drafts a short customer-facing reply using only the retrieved passages, cites the passages used by `doc_id`, says it does not know when the passages are insufficient, and labels the reply as automated. |
| Category | Build |
| Serves requirement | FR-05 (A6). Its output is the input to FR-06 guardrails. Supports NFR-08 (transparency). |
| Version | 1.0 (file `prompts/generate_v1.md`; configured as `PROMPT_VERSION=PR-GEN-01-v1.0`) |
| Model used | Hosted model through LiteLLM to OpenRouter, selected by `LITELLM_MODEL` in `.env` (default `openrouter/openrouter/free` so the API receives `openrouter/free`; `LITELLM_API_BASE=https://openrouter.ai/api/v1`); temperature `LLM_TEMPERATURE` (0.1); timeout `LLM_TIMEOUT_SECONDS` (30); retries and backoff from `.env`. Free router only. |
| Inputs it expects | Ticket text (subject and body) between `TICKET_BEGIN` and `TICKET_END`; retrieved passages, each with `doc_id`, title and text, between `PASSAGES_BEGIN` and `PASSAGES_END`. Only called when the route is auto_respond and at least one passage exists. |
| Output format required | Intended contract: JSON only, with `answer` (customer-facing draft), `citation_doc_ids` (list of ids from the passages) and `automated_disclosure` (true). `src/generate.py` parses JSON (falling back to the first `{...}` block) and stores the prompt version with cached results. |
| How you know it worked | Code, not model honesty: every cited id must be in the retrieved set and the answer must be non-empty (`citation_ids` and `nonempty_answer` guardrails). Tests: `test_generate_mocked_through_run_ticket`, `test_guardrail_blocks_fabricated_citation`, `test_guardrail_block_through_run_ticket`, `test_positive_citation_pass`. Quality: human claim-by-claim review of 28 auto replies on the validation set found 119 of 119 claims supported, but those drafts were written by the reviewer from the retrieved passages because the live generation batch was rate-limited and not recorded (`human_eval_appendix.md`). |
| Known weaknesses | 1. The JSON-output instruction (the "Respond with JSON only" block in the user template) is in the prompt file but `src/generate.py` currently builds the user message from the delimiters alone and sends only the System section as the system message, so the model is not told the output format; a prose reply fails parsing and the ticket escalates (safe, but it would suppress auto replies on a live run). To be resolved before a live-generation evaluation.<br>2. `automated_disclosure` is requested but not read or enforced by code; the disclosure wording is open question 1 in Stage 2.<br>3. Guardrails verify citation ids and patterns, not that each claim is supported by the cited text; an unsupported claim with a valid id would pass.<br>4. Injection defence is delimiters plus an instruction plus regex checks on the output; it is not a guarantee.<br>5. Live-generation evidence is incomplete (free-tier limits). |
| Change history | 1.0 (2026-11-22): first version; no text changes since. Any change to the text bumps the version and the cache key. |

Prompt text:

<!-- docx-prompt-text: 4 -->
```text
SYSTEM MESSAGE (the "## System" section of prompts/generate_v1.md, sent as the system role):
You are CloudServe Assistant, an automated support draft helper. Answer ONLY from the provided passages. If the passages are insufficient, say you do not know and recommend escalation. Cite supporting passages using their doc_id values. Do not invent doc_ids. Do not make refunds, legal, or security-incident commitments. Label the reply as automated.

USER MESSAGE (built in src/generate.py, sent as the user role):
TICKET_BEGIN
{ticket_text}
TICKET_END

PASSAGES_BEGIN
[1] doc_id={doc_id} title={title}
{passage_text}

[2] doc_id=... (up to RETRIEVAL_TOP_K passages)
PASSAGES_END

TEMPLATE LINES IN THE PROMPT FILE THAT ARE NOT CURRENTLY SENT (see known weakness 1):
Respond with JSON only:
{
  "answer": "<customer-facing draft>",
  "citation_doc_ids": ["DOC-..."],
  "automated_disclosure": true
}
```

### Prompt PR-02 (register id PR-CLS-00: no prompt, by design)

<!-- docx-table: 5 -->
| Field | Value |
|-------|-------|
| Name and purpose | PR-CLS-00, classification has no prompt. Intent and urgency are assigned by deterministic rules and a locally trained classifier, so no ticket text is sent to a language model for labelling. This entry exists so the register states the absence explicitly. |
| Category | Build (not an LLM prompt) |
| Serves requirement | FR-02 (A3); FR-04 depends on its confidence score |
| Version | Not applicable. Classifier artefact: `storage/models/classifier/classifier.joblib`, produced by `python -m scripts.train_classifier --input <tickets.json> --output storage/models/classifier` |
| Model used | None (local). Rules in `src/classify.py`, then TF-IDF (word and character n-grams) with logistic regression from scikit-learn, trained on labelled development tickets. |
| Inputs it expects | Ticket subject and body text. |
| Output format required | Intent, urgency and a confidence in [0, 1], with alternatives, as a `Classification` object. |
| How you know it worked | Labelled accuracy on the validation set reported by the harness (recorded runs in `docs/plan/eval-runs.md`); the threshold sweep in `docs/plan/threshold-freeze.md` ties confidence to routing outcomes. |
| Known weaknesses | Confidence is not calibrated like a probability of correctness, which is why the threshold was measured and frozen (0.35) rather than taken from the pack's illustrative 0.80. Only 22 known intents; novel topics should score low and escalate. |
| Change history | Earlier plan: rules plus GLiNER zero-shot labelling. Replaced by the supervised classifier in the version 2.0 revision (findings D5; Stage 5, change C-01). |

Prompt text:

<!-- docx-prompt-text: 6 -->
```text
None. There is no classification prompt. Classification is local: deterministic rules first, then the trained scikit-learn classifier. Low confidence escalates; no language model is asked to label a ticket (findings D5).
```

### Prompt PR-03 (register id PR-EVAL-01: reviewer rubric, not sent to a model)

<!-- docx-table: 7 -->
| Field | Value |
|-------|-------|
| Name and purpose | PR-EVAL-01, human evaluation rubric. Instructions a reviewer follows to score auto replies for satisfaction proxy, citation support and hallucination. Written as a prompt-style instruction so the scoring is repeatable and versioned; no model executes it. |
| Category | Evaluation |
| Serves requirement | NFR-03 (accuracy: hallucination, citation accuracy); success measure "Customer satisfaction" (Stage 2 section 8) |
| Version | 1.0 |
| Model used | None. Applied by a human reviewer to harness output (`human_eval_appendix.md`, `docs/plan/human-eval-notes.md`). |
| Inputs it expects | For each sampled ticket: the ticket, the retrieved passages and the reply to be judged. |
| Output format required | Per-ticket scores for clarity (C), correctness (K), tone (T) and citation usefulness (U), each 1–5; list of factual claims each marked supported or unsupported by the cited chunk. |
| How you know it worked | The appendix reports mean CSAT proxy, claim support rate and hallucination rate from the same scored table, and lists drafts scoring under 4.0 rather than removing them. |
| Known weaknesses | The recorded sample used passage-grounded simulated drafts, so the numbers are indicative and are not evidence about live model output. A single reviewer, no inter-rater check. |
| Change history | 1.0 (2026-11-22): first version. |

Prompt text:

<!-- docx-prompt-text: 8 -->
```text
Review each sampled auto reply using only the ticket, the retrieved passages for that ticket and the reply.
1. Score clarity (C), correctness (K), tone (T) and citation usefulness (U) from 1 (poor) to 5 (excellent). CSAT proxy for the reply is the mean of the four scores.
2. List every factual claim in the reply. For each claim, find the cited chunk and mark it supported or unsupported. A claim with no citation, or whose citation does not contain the claim, is unsupported.
3. Check that every cited doc_id is among the retrieved doc_ids for that ticket.
4. Hallucination rate = unsupported claims divided by all factual claims. Citation support rate = supported claim-citation pairs divided by cited claims.
5. Report replies scoring under 4.0 and do not remove them from the results.
```

## 3 Section three: what makes a prompt worth keeping

Applied to PR-GEN-01, the only build prompt that reaches a model.

<!-- docx-table: 9 -->
| Check | What you are looking for |
|-------|--------------------------|
| Does it state the role and the task separately? | A prompt that mixes who the model is with what it should do tends to produce inconsistent output. Result: partly. The role ("CloudServe Assistant, an automated support draft helper") and the rules (answer only from passages, cite, do not commit) share one system paragraph; the task data (ticket and passages) arrives separately in the user message. |
| Are the inputs clearly delimited? | Ticket text and instructions must be distinguishable, or a customer can accidentally instruct your system. Result: yes. Ticket text sits between `TICKET_BEGIN` and `TICKET_END`, passages between `PASSAGES_BEGIN` and `PASSAGES_END`, and the system message is fixed text. |
| Is the output format specified exactly? | If you are parsing the response, the format is part of the contract and must be stated. Result: no, at present. The format is defined in the prompt file but not sent in the messages (known weakness 1); the code parser tolerates extra text but cannot repair a prose reply. |
| Does it say what to do when the answer is not known? | Without this instruction the model will invent something, because inventing something is what it does. Result: yes. "If the passages are insufficient, say you do not know and recommend escalation." Code also never calls generation when no passages exist. |
| Are the examples representative? | Examples drawn only from easy cases teach the model that every case is easy. Result: not applicable, the prompt has no examples (zero-shot); this avoids teaching only easy cases but gives no format exemplar. |
| Does it forbid what must never happen? | Constraints stated positively are followed more reliably than constraints implied by omission. Result: yes. It forbids inventing `doc_id` values and refund, legal or security-incident commitments, and requires an automated label. The guardrails enforce citation membership and out-of-scope phrases in code. |

Injection defence recorded for the register: ticket text is untrusted data. It is placed only in the delimited user section and never in the system message; the system message tells the model to answer only from passages; the output is then checked by guardrails for fabricated citation ids and injection-like phrasing, and anything blocked is escalated, not sent. The classification and routing stages never pass ticket text to a model, so injection cannot influence them.

## 4 Section four: traceability check

<!-- docx-table: 11 -->
| Requirement ID | Specification written? | Prompts covering it | Test case identifier | Gaps |
|----------------|------------------------|---------------------|----------------------|------|
| FR-01 | Yes (section 1) | None (no model) | `test_ingest_and_route.py::test_ingest_four_channels_from_pack`; `test_gaps_closure.py::test_ingest_coerces_non_string_channel`; `test_pipeline_real_data.py::test_ingest_preserves_channel_from_real_ticket` | None known. |
| FR-02 | Yes | PR-02 (explicitly no prompt) | `test_pipeline_real_data.py::test_run_ticket_on_real_sample` (classification runs inside the pipeline) | No isolated classifier unit test; accuracy is measured by the harness on the validation set. |
| FR-03 | Yes | None (embedding search) | `test_pipeline_real_data.py::test_retrieve_returns_doc_ids_from_real_corpus`; `test_gaps_closure.py::test_chroma_index_in_use`; `test_gaps_closure.py::test_empty_passages_escalate` | The real-data retrieval tests need the embedding model to be downloadable; they error where the model hub is unreachable. |
| FR-04 | Yes | None (code) | `test_ingest_and_route.py::test_route_escalates_on_low_confidence`; `::test_route_auto_respond_when_confident`; `test_gaps_closure.py::test_route_determinism_a5`; `::test_run_ticket_twice_same_route`; `::test_grounded_override_below_threshold`; `::test_must_not_from_text_without_labels` | None known. |
| FR-05 | Yes | PR-GEN-01 | `test_gaps_closure.py::test_generate_mocked_through_run_ticket`; `::test_positive_citation_pass`; `test_guardrails_and_log.py::test_guardrail_blocks_fabricated_citation` | Live generation not recorded; output-format instruction not sent (Stage 3 section 2, weakness 1). |
| FR-06 | Yes | PR-GEN-01 (its output is what is checked) | `test_guardrails_and_log.py::test_guardrail_blocks_pii_pattern`; `::test_guardrail_blocks_fabricated_citation`; `test_gaps_closure.py::test_guardrail_block_through_run_ticket`; `::test_nonempty_answer_guard`; `::test_confidence_floor_skipped_on_grounded_override` | Guardrails check citation ids and patterns, not claim-level support. |
| FR-07 | Yes | None | `test_guardrails_and_log.py::test_decision_log_writes_rows`; `test_gaps_closure.py::test_harness_a8_reconcile` | None known. |
| FR-08 | Yes | None | `test_gaps_closure.py::test_kill_switch_env_live_reread` | No dedicated named test for the in-flight forced-escalate path or the file-based flag; the logic is in `src/graph.py`. |
| FR-09 | Yes | None | `test_harness.py::test_harness_dry_run_no_silent_drops`; `test_gaps_closure.py::test_harness_a8_reconcile` | A live-generation unattended run is not recorded. |
| FR-10 | Yes | None | None (verified by following `README.md`) | Clean-checkout rehearsal still outstanding. |
| FR-11 | Yes | None | `test_gaps_closure.py::test_llm_backoff_on_rate_limit`; `test_harness.py::test_harness_continues_on_malformed_ticket`; `test_gaps_closure.py::test_config_error_on_bad_numeric` | None known. |
| FR-12 | Yes | None | The command itself: `python -m pytest tests/ -v` | See FR-03 note on tests that need the model download. |
| FR-13 | Yes | None | None (script verified by running it; output in Stage 1 Appendix A) | No automated test, by the project rule against decorative suites. |
| NFR-06 | Yes (`docs/governance/fairness-method.md`) | None | `test_gaps_closure.py::test_fairness_quality_gap_structure` | Measured on the validation set only. |
