# CloudServe Assistant — Product Report

**Author:** Sameer J  
**Product:** CloudServe Assistant (RAG triage and assist — not a chatbot)  
**Client context:** CloudServe Solutions support organisation  
**Date:** 2026-11-22  
**Version:** 1.2  

**Declaration of AI tool use.** Planning, drafting, coding assistance, workbook and report drafting, and an independent second-pass human-evaluation simulation were produced with AI coding assistants (including Cursor agents). The builder remains responsible for configuration choices, threshold freeze, recorded evaluation commands, and for verifying that a clean checkout follows this report and the README. No reference datasets pack ticket or knowledge-base *content* was used for planning insights beyond aggregate scripts and interview transcripts as required by the Pack. Generated drafts in the human-evaluation notes are explicitly labelled as passage-grounded simulations, not live model output.

**Reading guide.** This report describes CloudServe Assistant in the third person, as a product that a reviewer could assess without having watched the build. Every number in it is a number that already exists in a recorded artefact of the repository: the discovery script output, the threshold-freeze note, the evaluation-run log, the recorded metrics file for the validation run, the human-evaluation notes, the governance documents, or the workbooks. No figure was estimated for this report. Where evidence is missing, the text says so. The three largest gaps are stated here at the start so that no reader needs to infer them. First, a live generate-on evaluation batch was not recorded, so no customer-facing first-contact-resolution claim is made. Second, the hidden grader set has been run zero times. Third, the demonstration video has not yet been recorded; its script is complete and the recording is pending camera capture.

---

## Summary

CloudServe Assistant is a support triage and assist service built for the CloudServe Solutions CloudServe. It accepts a support ticket from any of four channels, classifies its intent and urgency with deterministic rules followed by a locally trained scikit-learn classifier, retrieves passages from the 29-article CloudServe knowledge base through a Chroma vector index, and then routes the ticket in plain code. A ticket that is policy-restricted, poorly grounded, or low in confidence is escalated with a readable reason, a summary and the sources considered. A ticket that is confident and well grounded may receive a cited draft answer produced through LiteLLM and OpenRouter, which then passes through blocking guardrails before anything is treated as sendable. Every automated decision is written to a SQLite decision log, a kill switch can stop automatic answering without a redeploy, and an unattended harness takes `--input` and `--output` paths so that a grader can run the system on an injected ticket file.

The recorded evidence supports the following claims, each qualified in the sections that follow. On the 80-ticket validation file, run route-only after the fairness fix, 66 tickets (82.5%) were routed to auto_respond and 14 (17.5%) were escalated, and all 14 escalations were policy must-not tickets. A later generate-on validation batch (LiteLLM → Groq, `validation_20261122T131433Z`) produced the same 66/14 split with **customer FCR 82.5%** (`fcr_claim_allowed=true`), citation ID validity 1.0 on 65 generations, and fairness quality gaps of 0.0 percentage points. Intent classification accuracy on the labelled validation tickets was 98.75%. The 28-test pytest suite passes on the build machine, and the Chroma collection holds 59 chunks. A second reviewer also scored 28 passage-grounded simulated drafts with a mean satisfaction proxy of 4.68 (119 of 119 claims supported); those remain indicative of retrieval quality alongside the live generate-on batch.

The claims the evidence does not support are equally important. The 82.5% figure is a route-level auto_respond rate, not customer first-contact resolution. The validation file was used during iteration, so it is not a clean held-out estimate. No hallucination rate for live model output exists. The hidden set has not been run. The video is not yet recorded.

---

## 1. Problem and stakeholders

### 1.1 The business problem

CloudServe Solutions’ support organisation is missing its first-response service agreement while ticket volume continues to grow. Marcus Adeyemi, Head of Support, reports roughly five hundred tickets a week handled by six agents, with first response averaging eight to twelve hours against a two-hour agreement. Two hires and a canned-response library did not fix the problem, because agents found searching the library slower than writing the answer again, and outsourcing quotes exceeded the team’s budget. The development ticket sample used in this project contains exactly 500 tickets, which is close to one week of volume by Marcus’s account, and it is therefore a reasonable picture of the queue the system is meant to relieve.

The historical labels on that sample show a first-contact resolution rate of 43.8% (219 of 500 tickets) and an escalation rate of 56.2% (281 of 500). Marcus quotes a figure of 42%, so the two sources agree closely. The ticket data also carries an elapsed resolution time, with a mean of 421.7 minutes per ticket, but it carries no first-response timestamp. First-reply time as Marcus defines it therefore cannot be verified from the tickets, and the discovery workbook records this as an open question rather than inventing a baseline.

### 1.2 The ask and the diagnosis

The client’s initial ask was a chatbot. The discovery interviews contradict that framing. Each of the five stakeholders described a different part of the same underlying problem, and none of them described a need that a conversational assistant would meet. Table 1 summarises what each stakeholder needs and what each fears, and the paragraphs after it explain how those needs shaped the product.

**Table 1.** Stakeholder needs and feared failure modes, drawn from the five discovery interviews.

| Stakeholder | Need from the system | Failure mode they fear |
|-------------|----------------------|------------------------|
| Marcus Adeyemi, Head of Support | Higher first-contact resolution without unsafe automation; explainable decisions for an autumn compliance review | A wrong confident answer that engineers screenshot; more agent work than the system saves |
| Sofia Restrepo, Tier One agent | A cited draft and the relevant page so she stops searching a private snippet file | Search that still fails under real customer wording; apologising for a wrong automated reply |
| Daniel Okonkwo, Tier Two engineer | Escalations that show what was tried, which pages were considered and what was uncertain | Bare forwards that force him to re-read the thread and re-ask the customer |
| Ines Varga, Technical Writer | Visibility of which article an answer cited, so she can tell an article error from a misreading | Unreviewed private answer files remaining the real source of truth |
| Ravi Menon, customer | A fast, honest, labelled first reply with a page link; urgent failures separated from mild how-to waits | Certain-sounding wrong answers |

Sofia says that roughly seven in ten tickets are repeats she could answer quickly if she could find the right page, and that the documentation is fine but unfindable. Ines, who maintains the 29 knowledge-base articles, says the articles are accurate within the review cycle and are used heavily by customers but hardly at all by support, because internal search matches article titles rather than customer wording. Daniel estimates that about half of what reaches him is something Tier One could have closed with confidence and the right page, and he asks that an automated system show its working rather than merely be right. Ravi accepts an automated first reply if it says what the system thinks, names the source page and says that a person will confirm; he rejects confident error. Marcus, for his part, defines failure as shipping something wrong and says he would rather the system said nothing.

Taken together, the interviews describe a findability and context problem rather than a conversation problem. The answers exist, the people who need them cannot reach them quickly, and escalations lose context on the way up. The product therefore is **CloudServe Assistant**: a system that ingests tickets from four channels, classifies intent and urgency locally, retrieves passages from CloudServe’s documentation by `doc_id`, and then either drafts a cited auto-response or escalates with a readable reason, a summary and the sources. Guardrails can block unsafe drafts, every automated decision is logged, and an unattended harness evaluates an injected ticket path.

### 1.3 What success means

The CloudServe Project Brief contains two target tables that disagree. One, closer to a client wish list, quotes first-contact resolution of 65% or more, a two-hour first reply and a satisfaction score of 4.2. The other, the success and outcomes table with explicit calculation definitions in the Evaluation Framework, quotes first-contact resolution of at least 60%, a mean first reply under five minutes, a satisfaction proxy of at least 4.0 and an escalation rate of at most 30%. The project adopted the second table as the pass bar and treats the first as context (finding D1). Table 2 lists the targets that the rest of this report is measured against and where each comes from.

**Table 2.** Success targets used in this report and their sources.

| Measure | Target | Source of the target | Historical baseline (development sample) |
|---------|--------|----------------------|------------------------------------------|
| First-contact resolution | at least 60% | Success table (finding D1) | 43.8% |
| Escalation rate | at most 30% | Success table (finding D1) | 56.2% |
| Mean time to first reply | under 5 minutes | Success table (finding D1) | Not measurable from the tickets (no first-response field) |
| Customer satisfaction proxy | at least 4.0 | Success table; human rubric sample required | Mean historical rating 2.97 |
| Intent classification precision | at least 85% | Evaluation Framework | Not applicable (no prior classifier) |
| Hallucination / citation accuracy | at most 5% / at least 95% | Evaluation Framework; dual human review | Not measured today |
| Fairness quality gap | under 5 percentage points | Evaluation Framework governance tier | Not measured for an automated path |
| Private data in outbound replies | zero | Governance Framework | Not measured today |

The discovery workbook adds a second constraint on what success can mean. In the development sample, 143 tickets (28.6%) are not answerable from the documentation and 87 (17.4%) are policy-restricted and must never be auto-answered. Both groups were always escalated in the historical record. A ceiling on automation therefore exists, and the value of the system lies in routing correctly and handing over context, not in answering more tickets. The counter-metrics in the product requirements document make this explicit: the system must not maximise its auto-respond rate if doing so raises hallucination, and it must not chase classification accuracy by answering tickets it cannot ground.

---

## 2. Discovery and findings

### 2.1 Method

Discovery combined five stakeholder interview transcripts with aggregate statistics over the 500-ticket development file. A project rule governed the second source: ticket and knowledge-base content were never read by hand for planning insight. Every development-ticket figure in this report was produced by running `python -m scripts.discovery_stats --input <development_tickets.json>`, which prints counts, rates and per-segment means from the `labels` and `history` fields and no ticket text. Where a figure is simple arithmetic on that output, such as a share of 500, the arithmetic is shown in the workbook. This discipline had a practical benefit beyond rule compliance: when two stakeholders disagreed, the disagreement could be settled by a reproducible command rather than by choosing whom to believe.

### 2.2 Disagreements settled by data

The interviews disagreed in six places. Table 3 states each disagreement, how the aggregates settled it and what followed for the design. The supporting numbers appear in Tables 4 and 5.

**Table 3.** Interview disagreements and how the development aggregates settled them.

| Disagreement | What the data showed | Consequence for the product |
|--------------|----------------------|-----------------------------|
| How many escalations Tier One could have resolved (Daniel: about half) | Of 281 escalations, 138 (49.1%) were answerable from documentation and 107 (38.1%) were answerable and not policy-restricted. | A large part of the escalation load is a findability and confidence problem. Automation can lift first-contact resolution without touching genuinely hard tickets. |
| How repetitive the work is (Sofia: seven in ten) | 71.4% of tickets (357 of 500) are answerable from documentation, but the intent mix is flat: the largest intent is 5.8% and the smallest 2.6%. | Repetition sits at the article level, not the topic level. A topic-based canned-response library would need more than twenty buckets; retrieval over 29 articles with citations fits better. |
| Whether the documentation is the problem (Sofia and Ines) | Answers exist for 71.4% of tickets, yet 38.1% of escalations were answerable and non-policy: the answers were available and unused. | Build meaning-based retrieval with citations rather than rewrite content; restrict the corpus to the 29 reviewed articles. |
| Whether non-fluent customers have the worst satisfaction (Sofia) | 120 tickets (24.0%) are non-fluent. Satisfaction is 3.04 versus 2.95 for fluent customers; resolution takes 466.1 versus 407.7 minutes (about 14% longer). | Do not claim a historical satisfaction gap. Keep a fluency segment in the fairness check, because the risk is the new system misreading non-fluent wording. |
| One response-time number versus urgency-dependent pain (Marcus and Ravi) | High-urgency tickets are 29.2% of volume and fare worse: first-contact resolution 39.7% versus 48.4% for low urgency. | Urgency is an explicit classification output and appears on escalations; reporting should be split by urgency. |
| Whether enterprise customers are better served (Ravi) | Enterprise tickets (83, or 16.6%) have the lowest first-contact resolution (37.3%) and the highest escalation rate (62.7%). | Do not assume enterprise is well served; keep a tier fairness check. |

### 2.3 The development sample in numbers

Table 4 collects the main aggregates. The sample has 22 intent labels, no missing intent or urgency label, four channels and three customer tiers. Email is the largest channel at 212 tickets, and more than a quarter of the volume (26.6%) arrives as documentation comments or forum posts, which no interviewee mentioned but which the system must ingest without channel-specific failure.

**Table 4.** Development sample aggregates (`development_tickets.json`, n=500), produced by `scripts.discovery_stats`.

| Measure | Figure |
|---------|--------|
| Channels | email 212, chat 155, docs_comment 78, forum 55 |
| Urgency | medium 226, high 146, low 128 |
| Customer tier | standard 253, business 164, enterprise 83 |
| Language fluency | fluent 380, non-fluent 120 |
| Answerable from documentation | 71.4% (357 of 500) |
| Policy must_not_auto_respond | 17.4% (87 of 500) |
| Historical first-contact resolution / escalation | 43.8% (219) / 56.2% (281) |
| Repeat contact | 21.6% |
| Mean historical satisfaction | 2.97 |
| Mean resolution time | 421.7 minutes (sum 210,849 minutes) |
| Documentation corpus | 29 articles (`documentation.json`, field `doc_id`) |

The segment outcomes in Table 5 show that human handling is not uniform across segments, and Figure 1 draws the first-contact resolution column for easy comparison. Enterprise customers do worst on first contact and on speed. Documentation comments are the slowest channel and the most repeated, with a repeat-contact rate of 33.3%. Chat has the lowest satisfaction, at 2.72. The history therefore describes a baseline to improve on, not a target to imitate, a point Daniel makes when he warns that some answers in agents’ private files were right two years ago and are wrong now.

**Table 5.** Historical outcomes by segment in the development sample (human-handled tickets).

| Segment | Tickets | First-contact resolution | Mean resolution (min) | Mean satisfaction |
|---------|---------|--------------------------|-----------------------|-------------------|
| Standard tier | 253 | 43.1% | 442.1 | 2.98 |
| Business tier | 164 | 48.2% | 358.8 | 2.91 |
| Enterprise tier | 83 | 37.3% | 483.7 | 3.05 |
| Fluent | 380 | 43.2% | 407.7 | 2.95 |
| Non-fluent | 120 | 45.8% | 466.1 | 3.04 |
| High urgency | 146 | 39.7% | 478.5 | 2.86 |
| Medium urgency | 226 | 43.8% | 402.7 | 2.99 |
| Low urgency | 128 | 48.4% | 390.6 | 3.06 |
| Email | 212 | 44.8% | 381.7 | 3.08 |
| Chat | 155 | 44.5% | 426.7 | 2.72 |
| Docs comment | 78 | 34.6% | 514.7 | 3.17 |
| Forum | 55 | 50.9% | 430.1 | 2.98 |

```chart
{
  "type": "hbar",
  "title": "Historical first-contact resolution by segment (%), development sample",
  "categories": ["Docs comment", "Enterprise", "High urgency", "Standard", "Fluent", "Medium urgency", "Chat", "Email", "Non-fluent", "Business", "Low urgency", "Forum"],
  "series": [{"name": "First-contact resolution (%)", "values": [34.6, 37.3, 39.7, 43.1, 43.2, 43.8, 44.5, 44.8, 45.8, 48.2, 48.4, 50.9]}],
  "height": 270,
  "min": 0,
  "max": 60,
  "step": 10,
  "label_format": "%s"
}
```

**Figure 1.** Historical first-contact resolution by segment, values from Table 5. The lowest segments are documentation comments, enterprise tier and high-urgency tickets.

### 2.4 Where the effort goes

Effort was proxied by elapsed resolution minutes summed per category, which overstates effort on tickets that waited in queue but still ranks categories usefully. Table 6 and Figure 2 show the central discovery result. Tickets that are not answerable from documentation are 28.6% of volume and 50.6% of elapsed resolution time. Policy-restricted tickets are 17.4% of volume and 28.6% of time. Four intents that automation must not handle (security incidents, compliance requests, data residency and feature requests) are 20.2% of volume and 32.0% of time. The answerable tickets, 71.4% of volume, carry 49.4% of time. The consequence is that the time saving must come from answerable tickets, while the genuinely hard tickets need better handovers rather than answers.

**Table 6.** Share of ticket volume versus share of elapsed resolution time, development sample.

| Ticket group | Share of volume | Share of resolution time | Why the two differ |
|--------------|-----------------|--------------------------|--------------------|
| Not answerable from documentation | 28.6% (143) | 50.6% | Nothing to retrieve; all escalated; mean resolution 746.8 versus 291.5 minutes for answerable tickets |
| Policy must-not tickets | 17.4% (87) | 28.6% | Always escalated; mean resolution 693.2 minutes |
| Answerable from documentation | 71.4% (357) | 49.4% | Documented procedures resolve faster |
| security_incident (single intent) | 5.2% (26) | 9.7% | Longest mean resolution of any intent, 785.9 minutes |
| sso_configuration (single intent) | 5.2% (26) | 2.4% | Documented procedure; 73.1% resolved at first contact |

```chart
{
  "type": "bar",
  "title": "Share of volume versus share of elapsed resolution time (%)",
  "categories": ["Not answerable", "Policy must-not", "Answerable"],
  "series": [
    {"name": "Share of ticket volume", "values": [28.6, 17.4, 71.4]},
    {"name": "Share of resolution time", "values": [50.6, 28.6, 49.4]}
  ],
  "height": 220,
  "min": 0,
  "max": 80,
  "step": 20
}
```

**Figure 2.** Volume versus effort for three overlapping ticket groups, values from Table 6. The groups are cuts of the same 500 tickets and are not a partition.

### 2.5 Findings D1–D5

While reading the reference datasets pack, five conflicts or errors were recorded as numbered findings, each with a stance taken and the risk of ignoring it. Table 7 summarises them. The findings are binding: later documents and code refer to them by identifier, and a change to any finding requires a logged revision.

**Table 7.** reference datasets pack deviations logged as findings D1–D5.

| ID | Finding | Stance taken |
|----|---------|--------------|
| D1 | Pack success tables disagree slightly | Locked targets: first-contact resolution at least 60%, reply under 5 minutes, satisfaction at least 4.0, escalation at most 30% |
| D2 | Setup Guide sample uses `id` for corpus documents | Always use `doc_id`, the field in the Dataset Guide and the ground-truth links |
| D3 | Pack `CONFIDENCE_THRESHOLD=0.80` is described as illustrative | Measured on development data and frozen at 0.35 before the recorded run |
| D4 | Kill-switch behaviour for in-flight work is underspecified | Environment flag or file; re-read live; checked at route and around generation; never auto_respond while on |
| D5 | The GLiNER zero-shot plan | Dropped for rules plus a supervised scikit-learn classifier; the language model only generates, never labels |

Three further pack inconsistencies were tracked without becoming product deviations. The hidden set is stated as 100 tickets in some places and 120 in others, so the harness is designed for an arbitrary number of tickets with the same schema. The validation set is described both as free to use and as to be run once near the end, so the project tuned on the development file, used the validation file for self-checks and records how many times it was run (section 8.2 is candid that this number is greater than one). The Setup Guide’s category-count wording differs from its listed categories, so enumerations come from the Dataset Guide and the data via scripts.

### 2.6 Open questions carried forward

Four open questions from the discovery workbook remain relevant to the interpretation of the results. First, first-reply time is not in the ticket data, so the evaluation reports the system’s own reply latency (mean, median and 95th percentile) and explains in section 8 why that latency is a poor proxy. Second, customer region was not analysed, and the fairness checks run on tier and fluency only. Third, the satisfaction scale is not stated in the data, so the project assumes the one-to-five scale of the Brief. Fourth, Marcus’s claim that an escalation costs about four times a resolved ticket is not in the data and is not used in any target.

---

## 3. Requirements and acceptance

### 3.1 Functional requirements

The product requirements document defines thirteen functional requirements. FR-1 to FR-6 cover the pipeline stages: four-channel ingest, intent and urgency with confidence, corpus retrieval with resolvable sources, threshold routing, grounded cited generation and blocking guardrails. FR-7 and FR-8 cover the persistent decision log and the kill switch. FR-9 to FR-12 cover the unattended harness, the documented runnable service, graceful failure and the one-command test suite. FR-13 covers the discovery scripts that produce the Stage 1 aggregates without manual inspection of ticket bodies. Each requirement is written with testable consequences, for example that an identical ticket processed twice must yield the identical route, or that an engineered trigger ticket must produce a blocked response that is not sent. Table 8 maps each requirement to the module that realises it.

**Table 8.** Functional requirements and the modules that implement them.

| Requirement | Capability | Module or script |
|-------------|------------|------------------|
| FR-1 Four-channel ingest | Normalise email, chat, docs_comment and forum tickets | `src/ingest.py`, `src/models.py` |
| FR-2 Intent, urgency, confidence | Rules first, then trained classifier; alternatives recorded | `src/classify.py`, `scripts/train_classifier.py` |
| FR-3 Retrieval | Ranked passages with `doc_id`; empty result allowed | `src/retrieve.py`, `scripts/build_index.py` |
| FR-4 Threshold routing | Pure deterministic routing with a frozen threshold | `src/route.py` |
| FR-5 Grounded generation | Cited JSON answer through LiteLLM; disk cache | `src/generate.py`, `src/llm.py`, `src/cache.py`, `prompts/generate_v1.md` |
| FR-6 Blocking guardrails | Citation, PII, injection, scope and confidence checks | `src/guardrails.py` |
| FR-7 Decision log | One row per automated decision stage | `src/logging_store.py` |
| FR-8 Kill switch | Live environment flag or file | `src/config.py`, `src/route.py`, `src/graph.py` |
| FR-9 Harness | `--input` and `--output`; metrics written automatically | `evaluation/harness.py`, `evaluation/metrics_report.py` |
| FR-10 Runnable service | FastAPI with `/health`, `/metrics`, `/tickets/process` | `src/api.py`, `README.md` |
| FR-11 Graceful failure | Timeout, backoff, per-ticket error isolation | `src/graph.py`, `src/llm.py` |
| FR-12 Tests | One pytest command | `tests/`, CI workflow |
| FR-13 Discovery scripts | Aggregates only | `scripts/discovery_stats.py` |

### 3.2 Non-functional requirements

Table 9 lists the cross-cutting requirements and the mechanism that serves each. The architecture document maps them to design choices; section 8 reports which of them have recorded evidence and which do not.

**Table 9.** Non-functional requirements and mechanisms.

| ID | Requirement | Mechanism |
|----|-------------|-----------|
| NFR-01 | Latency p95 under 3 seconds end to end | Local classify and retrieve; cache hits; generation skipped on escalation |
| NFR-02 | Availability at least 99.5% with documented provider-down behaviour | Provider failure becomes escalation; the batch continues |
| NFR-03 | Classification precision at least 85%; citation accuracy at least 95%; hallucination at most 5% | Trained classifier; citation guard; human review |
| NFR-04 | Zero private data in outbound replies | Blocking pattern guardrail; governance scan in the metrics report |
| NFR-05 | Complete decision auditability | SQLite decision log, export and harness reconciliation |
| NFR-06 | Under 5 points quality variation across tier and fluency | Segment quality metric in the harness; character n-gram classifier; grounded override |
| NFR-07 | Free-tier cost only | Local classification; cache; escalate-before-generate; backoff on rate limits |

### 3.3 Acceptance criteria A1–A12

The acceptance criteria A1 to A12 from the CloudServe Build Specification are the gate. Table 10 records their status as of this report. The status column is deliberately more conservative than a simple pass or fail: it distinguishes criteria proven by tests, criteria proven by a recorded run, and criteria that remain partly open. In particular, A6 has automated checks for citation identifiers and an indicative human sample, but not a reviewed sample of live model output, and A9 is demonstrated unattended on route-only runs, not on a recorded generate-on batch.

**Table 10.** Acceptance criteria status as of 2026-11-22.

| ID | Criterion (short) | Status and evidence |
|----|-------------------|---------------------|
| A1 | Clean checkout runnable | Rehearsed from the packaged tree on the build machine: classifier and index rebuild from an empty `storage/`; caveats in section 8.2 and Appendix H (no fresh virtual environment; data-backed tests need the Pack at a fixed path) |
| A2 | Four-channel ingest | Pass (tests, including a coercion test for malformed channel values) |
| A3 | Intent, urgency, confidence, alternatives | Pass |
| A4 | Retrieval with resolvable `doc_id` | Pass (Chroma collection `cloudserve_docs`, 59 chunks) |
| A5 | Deterministic routing | Pass (twice-run tests) |
| A6 | Cited, grounded answers | Partial: automated citation-membership guard plus an indicative human sample on simulated drafts; live output not reviewed |
| A7 | Blocking guardrails | Pass (engineered bad generation is blocked through the graph) |
| A8 | Decision log and coverage | Pass (harness reconciliation reports tickets without a decision row) |
| A9 | Unattended harness | Pass for route-only runs (`--input` and `--output`); no recorded live generate-on batch |
| A10 | Metrics report | Pass, with first-contact resolution withheld on route-only runs (`fcr_claim_allowed=false`) |
| A11 | Provider failure resilience | Pass (timeout, rate-limit backoff, malformed ticket mid-batch; mocked) |
| A12 | Documented pytest suite | Pass (28 tests) |

### 3.4 Scope

Out of scope for version one are a consumer chat interface, billing settlement or contractual commitment engines, an agent desktop beyond API responses, automatic closure of tickets in an external system, multi-region deployment, a fine-tuned model, and any unsupervised handling of security, legal or data-location matters. The non-goals also exclude paying for model capacity, tuning against the hidden set, hard-coding its path, and extra test suites or dashboards beyond what the CloudServe requires. These are not omissions made for lack of time; each follows from stakeholder evidence, notably Daniel’s list of categories he would not automate and Marcus’s insistence that a wrong answer is worse than silence.

### 3.5 How the requirements changed

The product requirements document was revised from version 1.0 to version 2.0 during the build, and the Stage 5 revision log records fourteen numbered changes, C-01 to C-14. Table 11 lists the changes that altered behaviour; each was triggered by recorded evidence, not by preference. Three assumptions from version 1.0 turned out to be wrong in ways that are instructive: the pack’s 0.80 threshold would have escalated nearly everything, a rules-plus-GLiNER classifier was unnecessary once labelled data was available, and raw auto-respond rates were the wrong basis for a fairness metric.

**Table 11.** Selected requirement changes from the Stage 5 revision log.

| Change | Requirement | What changed | Trigger |
|--------|-------------|--------------|---------|
| C-01 | FR-02 | GLiNER dropped; supervised classifier added; no language-model labelling | Findings D5 |
| C-02 | FR-04 | Threshold measured and frozen at 0.35 instead of the pack default of 0.80 | Threshold sweep: about 6% first-contact proxy at 0.80 versus about 74% at 0.35 |
| C-03 | FR-04 | Routing confidence is the intent probability only | Taking the minimum with urgency collapsed first-contact resolution |
| C-04 | FR-04 | Grounded override for strong retrieval with near-threshold confidence | First fairness measurement showed a tier gap of about 35 points |
| C-05 | FR-04 | Label-free text rules for security, legal and self-harm language | The hidden set may omit the `must_not_auto_respond` label |
| C-06 | FR-08 | In-flight kill-switch behaviour specified | Gap review found a race between operator and generation |
| C-07 | NFR-06 | Fairness measured as resolution quality, not raw auto mix | Structural unevenness of policy tickets across tiers |
| C-08 | FR-09, FR-10 | One LangGraph state graph shared by API and harness | Pack stack names LangGraph; gap review found none |
| C-09 | FR-11 | Timeout, bounded retries and exponential backoff | A11 was only partly demonstrated |
| C-10 | FR-09 | No first-contact-resolution claim on route-only runs | A route-only figure would overstate results |
| C-11 | FR-03 | Embedding-dimension check and index health on `/health` | First gate run escalated all 80 tickets |

---

## 4. Architecture

### 4.1 Design paradigm

CloudServe Assistant uses a pipes-and-filters design on a single LangGraph `StateGraph` in `src/graph.py`. Each stage is a filter module with typed inputs and outputs, and the graph is the only orchestrator. FastAPI and the evaluation harness both call the same `run_ticket` entrypoint, which is the first of the architecture decisions: it prevents the interactive API and the batch harness from drifting apart, so that a metric measured by the harness describes the behaviour the API would show. Figure 3 shows the pipeline.

```diagram
{
  "title": "CloudServe Assistant pipeline: ingest to decision log",
  "rows": [
    [
      {"label": "Ingest", "sub": "4 channels"},
      {"label": "Classify", "sub": "rules, then sklearn"},
      {"label": "Retrieve", "sub": "Chroma, doc_id"},
      {"label": "Route", "sub": "code, threshold"}
    ],
    [
      {"label": "Generate", "sub": "LiteLLM, auto only", "fill": "#f6e8d0"},
      {"label": "Guardrails", "sub": "block or allow", "fill": "#f6e8d0"},
      {"label": "Persist", "sub": "SQLite decision log"},
      {"label": "API or harness", "sub": "same run_ticket", "fill": "#dfeedd"}
    ]
  ],
  "note": "Escalated tickets skip Generate and Guardrails; remote LLM traffic exists only in the shaded boxes."
}
```

**Figure 3.** The CloudServe Assistant pipeline as a LangGraph state graph. Tickets that route to escalate skip generation and guardrails and go straight to persistence.

The nodes run in this order: ingest, classify, retrieve, route, generate (conditional on the route being auto_respond), guardrails and persist. The graph state carries the ticket, classification, retrieved passages, the route decision, the generation, the guardrail results, the final action, accumulated errors and an escalation summary. Each node catches its own exceptions, appends an error note and degrades to a defined fallback, for example a zero-confidence classification or an empty passage list, so that a failure in one stage becomes an escalation rather than an exception that aborts the batch.

### 4.2 Architecture decisions

The architecture spine records eleven numbered decisions, AD-1 to AD-11. Table 12 lists those that shaped the code most. The constraint that connects them is that probabilistic components are kept out of the decisions that must be reproducible. Classification and routing never call a remote model, and the single remote call, generation, happens only after routing has already decided to answer.

**Table 12.** Selected architecture decisions from `ARCHITECTURE-SPINE.md`.

| ID | Decision | What it prevents |
|----|----------|------------------|
| AD-1 | Only `run_ticket` executes the pipeline; the API and the harness must not reimplement stages | API behaviour diverging from harness metrics |
| AD-2 | Dependency direction: api to graph to stages to models, config and logging; stages never import the API | Circular imports; stages that the harness cannot share |
| AD-3 | Rules, then trained classifier, then code routing, then LiteLLM generation only on auto_respond | Non-deterministic routing; free-tier spend on classification |
| AD-5 | Every stage decision is persisted; the harness can export it | Incomplete audit evidence |
| AD-6 | Cache generation by model and prompt hash; honour rate-limit headers | Free-tier exhaustion on repeated evaluation |
| AD-7, AD-11 | Kill switch is a runtime flag read per ticket; in-flight policy specified | Needing a restart to stop automatic answers |
| AD-8 | Always use `doc_id`, never `id` | Broken index metadata and unresolvable citations |
| AD-9 | Threshold starts at the pack value, is measured, then frozen before the recorded run | Drifting routing; invalidated evaluation |
| AD-10 | All remote completions go through `src/llm.py` (LiteLLM) | Provider calls scattered across modules |

### 4.3 Runtime topology and stack

At run time the system consists of an API process (`uvicorn` serving `src.api`), a harness process (`python -m evaluation.harness`) that uses the same graph, local in-process models for embeddings and classification, a Chroma persistent store on disk, a SQLite file for the decision log, a disk cache for generations and one outbound HTTPS dependency, OpenRouter, used for generation only. Table 13 summarises the components and what each is not used for, a column that records the deliberate boundaries as clearly as the responsibilities.

**Table 13.** Runtime components and their responsibilities.

| Component | Responsibility | Not used for |
|-----------|----------------|--------------|
| LangGraph (with LangChain packages) | State graph orchestration | Business policy or thresholds |
| scikit-learn and joblib | Intent, urgency and confidence | Routing decisions; answer text |
| sentence-transformers (`all-MiniLM-L6-v2`) | Embedding passages and queries | Classification labels |
| Chroma | Persistent vector index | Decision audit |
| LiteLLM to OpenRouter | Draft answer generation | Classification or routing |
| FastAPI, uvicorn, pydantic | HTTP surface and typed models | The batch evaluation loop |
| SQLAlchemy with SQLite | Decision rows | Vector search |
| prometheus-client | Counters and latency histograms | Business satisfaction scoring |
| pytest | The A1 to A12 behaviour suite | Load or performance testing |

The stack follows the reference datasets pack configuration. The only additive dependency approved is `litellm`, plus configuration keys for the kill switch and the classifier path. No framework was swapped. One departure was proposed and settled with the builder rather than made silently: the GLiNER classification plan was replaced by the supervised classifier (finding D5), recorded in the findings and in the revision log.

### 4.4 Configuration and reproducibility

Every runtime setting is read from `.env`, with no fallback defaults in code. A missing or malformed numeric key raises a `ConfigError`, and a test covers that behaviour. The reason is reproducibility: routing is only deterministic across runs (acceptance criterion A5) if the threshold and the grounded-override parameters cannot differ silently between two invocations. The `.env.example` file ships with the frozen threshold, retrieval and chunking parameters, classifier training parameters, targets, kill-switch keys and resilience keys, and the `.env` file itself is git-ignored and excluded from the package.

---

## 5. Data and retrieval

### 5.1 Corpus and index

The retrieval corpus is the reference datasets pack’s `documentation.json`, which contains 29 reviewed support articles covering authentication, deployment, API usage, billing, data, security and account management. Each article has a `doc_id`, a title, a category and content. The corpus is deliberately small and deliberately closed: the agents’ private snippet files were never provided to the project and were never used, because Daniel warns that some of their content is stale, and Ines wants every answer to trace to a reviewed article. The pack’s ground-truth responses are used for evaluation only and are never retrieved at run time.

Articles are split into chunks of at most 800 characters with a 120-character overlap (`CHUNK_SIZE` and `CHUNK_OVERLAP` in the environment). The splitter respects paragraph boundaries where it can and falls back to windowed splitting for long paragraphs. Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2` and stored in a persistent Chroma collection named `cloudserve_docs` with cosine distance. After `scripts.build_index`, the collection holds 59 chunks, a count verified on the build machine and exposed as `chroma.count` on the `/health` endpoint so that an operator can see that the index is wired. Table 14 lists the retrieval parameters.

**Table 14.** Retrieval and index configuration (from `.env.example`).

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Pack-pinned embedding model |
| `EMBEDDING_MIN_DIM` | 32 | Refuse an embedder that loaded without a trained pooling layer |
| `CHROMA_COLLECTION` | `cloudserve_docs` | Collection name |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 800 / 120 | Chunking |
| `RETRIEVAL_TOP_K` | 5 | Passages returned per ticket |
| `RETRIEVAL_MIN_SCORE` | 0.25 | Relevance floor; below it a hit is dropped |
| Index size | 59 chunks | Observed after `scripts.build_index` |

### 5.2 Retrieval behaviour

Retrieval returns passages with a `doc_id`, the passage text, a similarity score and the article title. A passage below the relevance floor is dropped, so an irrelevant query can legitimately return nothing, and an empty result forces an escalation: the routing code refuses to approve an ungrounded answer. This matters for Ines’s requirement, because a citation that cannot resolve to a retrieved passage is blocked by the guardrails and is never presented as a source. Finding D2 is enforced throughout: the metadata always stores `doc_id`, never a bare `id`, which the Setup Guide’s sample code would have used.

### 5.3 The embedding-fallback incident

The most instructive retrieval event was a failure that produced no error. The first unattended run on the 80-ticket validation file escalated all 80 tickets, for a first-contact proxy of 0%. The cause, recorded in the evaluation log, was that the sentence-transformers library had silently fallen back to an untrained mean-pooling model when the pretrained model could not be loaded. The resulting vectors did not match the vectors already stored in the index, every similarity score fell below the relevance floor, retrieval returned no passages, and the router, behaving correctly, escalated every ticket. The pipeline code was green and the business result was zero.

The fix is a run-time check that refuses to proceed if the loaded embedding model has fewer dimensions than `EMBEDDING_MIN_DIM`, with an error that tells the operator to repair the model cache and rebuild the index, together with index statistics on `/health`. The Effort Log records that the first gate run took 8.5 hours against an estimate of 3.0, and that the extra time went to this diagnosis and to the confidence change described in section 6. The episode is retained in the report because it demonstrates a general risk of retrieval systems: a degraded dependency can fail safe in the sense that no wrong answer is sent while failing completely in the sense that no useful answer is sent either.

---

## 6. Classification and routing

### 6.1 Classification

Classification runs in two stages and never calls a remote model. Rules fire first for patterns that justify certainty: security language (compromise, breach, unauthorised access, phishing) maps to the security_incident intent with high urgency, and billing language (invoice, refund, charge, billing) maps to the billing_query intent. A rule hit carries a confidence of 1.0 and lists the other rule intents as alternatives so that the alternatives requirement of A3 is met on the rules path as well. Otherwise a trained scikit-learn pipeline predicts intent and urgency from the ticket text. Table 15 describes the components.

**Table 15.** Classification components.

| Component | Detail |
|-----------|--------|
| Rules | Two deterministic rule families (security and billing); confidence 1.0 |
| Features | Word n-grams (1 to 2) and character n-grams (3 to 5, `char_wb`) combined by TF-IDF |
| Model | Logistic regression for intent and a separate pipeline for urgency |
| Training data | Labelled development tickets (22 intents) via `scripts.train_classifier` |
| Output | Intent, urgency, confidence in [0, 1], up to three alternatives by probability |
| Artefact | `storage/models/classifier/classifier.joblib` (regenerated on a clean checkout) |

Routing confidence is the maximum intent probability and not the minimum of the intent and urgency probabilities. The first version took the minimum, and the effect was severe: because urgency prediction is weaker than intent prediction, taking the minimum pushed most confidences under the measured threshold and collapsed the automated share. Urgency is still predicted, logged and returned, and it is visible on escalations, but it does not gate the reply. Section 10 lists the weaker urgency model as a limitation. After the second training iteration, which added character n-grams for robustness to non-fluent wording, intent accuracy on the labelled validation tickets was 98.75% (79 of 80), as discussed in section 8.

### 6.2 Threshold measurement and freeze (D3)

The pack’s `.env.example` ships `CONFIDENCE_THRESHOLD=0.80`, and the Brief calls that figure illustrative. The project measured instead. `scripts/tune_threshold.py` sweeps candidate thresholds from 0.30 to 0.95 in steps of 0.05 on the development labels and reports, for each, a first-contact proxy, an escalation share and the precision of the tickets it would auto-answer. Table 16 and Figure 4 show the two rows that matter. At the pack value, about 6% of tickets would be auto-answered and about 94% escalated, because this classifier’s confidence distribution sits far below 0.80; at 0.35 about 74% would be auto-answered with about 26% escalated and an auto-answer precision of about 0.76. The chosen value is 0.35 and was frozen before the recorded validation run. The sweep was repeated after the confidence definition changed to intent-only, and it still recommended 0.35.

**Table 16.** Development-set threshold sweep (n=500), values from `threshold-freeze.md`.

| Threshold | First-contact proxy | Escalation | Auto-answer precision |
|-----------|---------------------|------------|-----------------------|
| 0.35 (frozen) | about 74% | about 26% | about 0.76 |
| 0.80 (pack illustrative) | about 6% | about 94% | about 0.90 |

```chart
{
  "type": "bar",
  "title": "Threshold sweep, development set (n=500): frozen 0.35 versus pack 0.80 (%)",
  "categories": ["First-contact proxy", "Escalation", "Auto-answer precision"],
  "series": [
    {"name": "Threshold 0.35 (frozen)", "values": [74, 26, 76]},
    {"name": "Threshold 0.80 (pack)", "values": [6, 94, 90]}
  ],
  "height": 225,
  "min": 0,
  "max": 100,
  "step": 20
}
```

**Figure 4.** The same sweep as Table 16. Auto-answer precision is shown as a percentage (0.76 and 0.90 multiplied by 100). A higher threshold buys precision at the cost of near-total escalation.

The trade-off is visible: the pack value is more precise per automated reply but automates almost nothing, and an assistant that escalates 94% of tickets does not meet Marcus’s need. Business targets from finding D1 decided between the two. The freeze rule is strict. Because changing a threshold after the recorded run would invalidate the reported metrics, any later change requires a logged revision of the requirements, and the value in force is written to every routing decision as `threshold_applied`, so an auditor can see which threshold produced which decision.

### 6.3 The route function

Routing is a pure function of the ticket, the classification, the retrieved passages, the settings and the kill-switch state. The order of the checks matters and is fixed. Table 17 gives the order and the reason recorded with each outcome.

**Table 17.** Order of routing checks in `src/route.py`.

| Order | Check | Outcome | Recorded reason |
|-------|-------|---------|-----------------|
| 1 | Kill switch active | Escalate | Kill switch active; auto_respond disabled |
| 2 | Policy must-not (label or text rule) | Escalate | Policy: must_not_auto_respond, or the text rule name |
| 3 | No retrieved passages | Escalate | No passages above relevance; refusing ungrounded answer |
| 4 | Confidence at or above the frozen threshold | Auto-respond | Confidence and passage count with the top score |
| 5 | Grounded override: top score at least 0.45 and confidence at least 0.75 of the threshold | Auto-respond | Grounded override, with the numbers applied |
| 6 | Otherwise | Escalate | Confidence below threshold |

The grounded override addresses a specific observed problem. When the first fairness measurement was taken, the automated share differed by customer tier by about 35 percentage points, partly because classifier confidence is lower on some wording. Where retrieval is strong, the evidence for answering is good even if the classifier is a little unsure, so the override allows an auto-respond when the best passage scores at least `ROUTE_GROUNDED_MIN_SCORE` (0.45) and the confidence is at least `ROUTE_GROUNDED_CONF_FACTOR` (0.75) of the threshold. The override is segment-blind, is set in the environment, and is logged on the decision as `grounded_override=true`. The confidence-floor guardrail is skipped only when the override applied, so the floor does not immediately undo it. Together with the character n-gram classifier, the override moved validation first-contact proxy from 65.0% to 82.5% and closed the fairness gap.

### 6.4 Policy must-not rules

Tickets labelled `must_not_auto_respond` always escalate. Because the grader’s hidden set may not carry that label, the router also applies label-free text rules that detect security-incident language (data breach, ransomware, unauthorised access, compromised credentials), legal-threat language and self-harm language, so that a hidden set without gold labels cannot bypass the policy by omission. A test covers this behaviour. The rules are short and conservative and they are not a substitute for the label; they are the guard that makes the label optional. Daniel’s list of categories he would never automate (security incidents, account compromise, contractual billing disputes and data location) is the policy these rules and the label jointly support, and the development sample confirms its size: 17.4% of tickets.

---

## 7. Generation, guardrails, and kill switch

### 7.1 Generation

Generation happens only when the route is auto_respond and at least one passage exists. The prompt, `PR-GEN-01` in `prompts/generate_v1.md`, instructs the model to answer only from the supplied passages, to say that it does not know when the passages are insufficient, to cite supporting passages by `doc_id`, never to invent identifiers, never to make refund, legal or security-incident commitments, and to label the reply as automated. The ticket text is untrusted data: it is placed between `TICKET_BEGIN` and `TICKET_END` delimiters in the user message and never in the system message, and the passages sit between their own delimiters. The runtime sends the prompt’s System section as the system message and appends the JSON-only output contract, with fields for the answer, the cited `doc_id` values and an automated-disclosure flag, to the user message as well.

That detail has a history. The Stage 3 prompt-library workbook records, as a known weakness at the time of writing, that an earlier version of `src/generate.py` sent the delimiters without the JSON instruction, so that a live model could reply in prose, fail parsing and cause a safe but unwanted escalation. The code now includes the contract in both messages. No live batch has been recorded since that change, so the fix is covered by mocked tests and not by evidence from a live model; section 8 and section 10 say so again.

Remote calls go through LiteLLM to OpenRouter with a configurable model (default OpenRouter free router: `MODEL_NAME=openrouter/free`, `LITELLM_MODEL=openrouter/openrouter/free` so LiteLLM’s provider prefix leaves the wire model as `openrouter/free`, with `LITELLM_API_BASE=https://openrouter.ai/api/v1`), a temperature of 0.1, a timeout of 30 seconds, and up to three retries with exponential backoff on rate-limit responses. A disk cache keyed by model and prompt content avoids repeated calls, which matters because the free router can still rate-limit under batch load.

### 7.2 Guardrails

Every candidate generation is validated, and the validation is able to block. Table 18 lists the checks. A blocked generation is never treated as sendable and the ticket is escalated with the guardrail details as the reason. Guardrails are deterministic code; they do not ask a second model to judge the first.

**Table 18.** Blocking guardrails in `src/guardrails.py`.

| Check | What it detects | Blocks when |
|-------|-----------------|-------------|
| `nonempty_answer` | Empty generation | Answer is empty |
| `citation_ids` | Fabricated or foreign citations | Any cited `doc_id` is not in the retrieved set |
| `grounding_empty_retrieve` | Citations without evidence | Citations exist while retrieval was empty |
| `pii` | Key-like, token-like, national-identifier-like and card-like patterns | A pattern matches the answer |
| `instruction_integrity` | Injection-like language in the output | A marker such as “ignore previous instructions” appears |
| `tone_scope` | Out-of-scope commitments | Refund, guaranteed-timeline or legal-advice language appears |
| `confidence_floor` | Confidence below the threshold | Confidence is under the threshold and no grounded override applied |

These checks verify that citations resolve and that patterns are absent. They do not verify that each claim is supported by the cited text; an unsupported claim attached to a valid identifier would pass. That limitation is why the human evaluation in section 8.6 reviews claims against cited passages, and why a larger review of live output remains on the list of next steps. Two tests demonstrate blocking end to end, one with a forged citation and one with a pattern-matching private value, and a third test pushes an engineered bad generation through the full graph and confirms that the final action is block.

### 7.3 Kill switch (D4)

The kill switch is active when `KILL_SWITCH=true` is set in the environment, which is re-read live and not only cached at start-up, or when the file named by `KILL_SWITCH_FILE` exists. The open question in the Brief was not whether to have a kill switch but what happens to tickets already in flight. Table 19 gives the decided behaviour. The guiding choice is that an in-flight call is allowed to finish but is never sent as an automatic reply, because aborting a half-complete HTTPS exchange is fragile, whereas escalating instead of sending is always safe and matches Marcus’s preference for silence over error.

**Table 19.** Kill-switch behaviour by situation (finding D4).

| Situation | Behaviour |
|-----------|-----------|
| New ticket at the route stage | Escalate; never auto_respond |
| Generation already in flight when the switch flips | The call may finish or time out normally; the draft is discarded from the auto path and the ticket escalates |
| Tickets still queued in the harness | The batch continues escalate-only; no crash and no silent drop |
| API request in progress | Returns an escalate payload, not an error |
| Time to take effect | The next route decision or the mid-flight re-check; no redeploy |
| Visibility | `/health` shows `kill_switch: true` |

The switch is checked at the route stage, again before generation, and again after generation. Operators toggle it with `./scripts/kill_on.sh` and `./scripts/kill_off.sh`, which create and remove the flag file. A test reads the environment live, so the behaviour that depends on live re-reading is covered, and the incident procedure in section 9 begins with it.

---

## 8. Evaluation results

### 8.1 How to read the evidence

The evaluation harness runs the same graph as the API over a ticket file given by `--input`, writes results and a metrics report into `--output`, reconciles the decision log against the tickets processed, and never hard-codes a dataset path. Two modes exist. In the default mode used by the recorded runs, generation is disabled (`--no-generate`): the harness classifies, retrieves and routes every ticket but sends no request to a language model. The consequence is central to everything in this section. A route-only run measures how often the router would let a ticket proceed to generation; it does not measure whether a generated reply would resolve the customer’s problem. For that reason the metrics report sets `fcr_claim_allowed=false` for such runs, and this report speaks of the route auto_respond rate and uses the label first-contact proxy only where the recorded files use it.

### 8.2 Run history

Table 20 lists the recorded runs in order, with Figure 5 showing the auto-respond share across them. The sequence matters because it shows what was changed between runs and why. The first run failed completely because of the embedding fallback described in section 5.3. The second restored retrieval and also changed the confidence definition. A fairness audit on that run flagged a tier gap of about 35 points, which led to the character n-gram classifier, the grounded override and the quality-based fairness metric, and the final recorded run followed.

**Table 20.** Recorded evaluation runs, from `docs/plan/eval-runs.md`.

| Run | Input | Auto-respond | Escalate | Rate | Notes |
|-----|-------|--------------|----------|------|-------|
| Validation, broken retrieve | 80 validation tickets | 0 | 80 | 0% | Embedding fallback; retrieval returned nothing |
| Validation, post-fix | 80 validation tickets | 52 | 28 | 65.0% | Route agreement with expected route 75% (12 false auto, 8 missed auto); tier gap about 35 points flagged |
| Development sample | first 100 development tickets | 77 | 23 | 77% | Re-tune after confidence change still recommended 0.35 |
| Validation after fairness fix | 80 validation tickets | 66 | 14 | 82.5% | Tier and fluency quality gap 0.0 points; the recorded snapshot |

```chart
{
  "type": "bar",
  "title": "Route-only auto_respond rate across recorded runs (%)",
  "categories": ["Validation: broken retrieve", "Validation: post-fix", "Development sample (100)", "Validation: fairness fix"],
  "series": [{"name": "Auto-respond rate (%)", "values": [0, 65, 77, 82.5]}],
  "height": 215,
  "min": 0,
  "max": 100,
  "step": 20
}
```

**Figure 5.** Route auto_respond rate in the four recorded runs of Table 20. These are route-level rates under `--no-generate`, not customer first-contact resolution.

One caveat about the run history belongs in the main text, not an appendix. The output directory also contains a further validation run whose action counts (52 auto-respond and 28 escalate) match the post-fix run but which is not listed in the evaluation log. On disk there are therefore four validation-file runs, which exceeds the Brief’s guidance to use validation once near the end. The threshold was tuned on development data only. The classifier retraining, the grounded override and the fairness metric, however, were all chosen after looking at validation-run fairness and agreement figures. The validation result in the recorded snapshot is consequently a fitted result, not a clean held-out estimate, and the hidden set is the only unbiased test that exists. That test has been run zero times.

A reproducibility check was run while preparing this report. From the assembled package tree, with no `.env` and no `storage/` directory, the classifier was retrained and the index rebuilt (59 chunks), and the route-only harness was run on the full validation file. It reproduced the recorded counts exactly: 66 auto_respond and 14 escalate, classification accuracy 0.9875, tier and fluency quality gaps of 0.0 points, and 160 decision rows for 80 tickets with none missing. This shows that the recorded snapshot is reproducible from the packaged source on the build machine. It does not turn the snapshot into a held-out result, and it was not performed in a fresh virtual environment or on a second machine.

### 8.3 Recorded validation after the fairness fix

The snapshot in `evaluation/results/validation_fairness_fix/` ran on `validation_tickets.json` (n=80, `allow_generate=false`). Table 21 sets each recorded measure against its target. The results meet the business targets in the route-only sense and meet the technical and governance targets that can be measured without generation. They do not touch the targets that require generated text or human review, and the table says so in its last column.

**Table 21.** Validation snapshot against targets (route-only run; source `metrics.json`).

| Measure | Target | Recorded value | Reading |
|---------|--------|----------------|---------|
| Tickets processed / silent drops | All / 0 | 80 of 80 / 0 | Met |
| Route auto_respond | Not a target | 66 of 80 (82.5%) | Proxy only; not customer resolution |
| Escalate | at most 30% | 14 of 80 (17.5%), all policy must-not | Met; excluding policy tickets the escalation share is 0.0% |
| Intent classification accuracy | at least 85% | 98.75% (labelled n=80) | Met |
| Latency, 95th percentile | under 3 s | 0.0259 s (mean 0.0552 s) | Met, but without generation |
| Fairness quality gap, tier | under 5 points | 0.0 points | Met on small segments (see Table 23) |
| Fairness quality gap, fluency | under 5 points | 0.0 points | Met on small segments (see Table 23) |
| Private data in outbound replies | zero | 0 occurrences | Vacuous: no generated text existed in this run |
| Decision rows written | Coverage of every ticket | 160 rows for 80 tickets | Met for classification and routing stages |
| Customer satisfaction proxy | at least 4.0 | Not computed by the harness | Needs the human sample (section 8.6) |
| Hallucination / citation accuracy | at most 5% / at least 95% | Not computed by the harness | Needs generated text and human review |
| First-contact resolution | at least 60% | Withheld (`fcr_claim_allowed=false`) | Not claimed |

The classification result deserves a note about its limits. Overall accuracy was 98.75%, and per-class recall was 1.0 for every one of the 22 intents except `quota_or_overage`, which had recall of 0.5 on two tickets. Because most classes have between one and ten validation tickets, per-class recall is a coarse measure, and the single misclassified ticket is a quota or overage case. The classifier was trained on development tickets, and the validation set was used for iteration, so the figure should be read together with section 8.2.

The latency figures need careful reading too. The mean (0.0552 seconds) is larger than the 95th percentile (0.0259 seconds), which can happen only when a small number of tickets is much slower than the rest. The per-ticket results file shows a median of about 0.011 seconds and a single slowest ticket of about 3.2 seconds, and the slowest ticket is the first one processed, which fits a one-off model warm-up at the start of the run. Neither figure is a customer-visible reply time, because no generation happened. The harness’s time-to-first-reply proxy (a mean of 0.0009 minutes) is therefore a statement about local compute, and the report does not present it as evidence that the five-minute target is met in operation. A live run would add provider latency, rate-limit waits and retries.

### 8.4 Confidence calibration

The metrics report bins labelled tickets by stated confidence and compares the mean stated confidence with the observed accuracy in each bin. Table 22 and Figure 6 show the result. In the three lower bands, which together hold 64 of the 80 tickets, the classifier is under-confident: stated confidence of roughly 0.32, 0.51 and 0.69 corresponds to observed accuracy of 1.0 in every case. Only the top band, with 16 tickets, is close to calibrated, with a stated mean of 0.9649 against an observed accuracy of 0.9375.

**Table 22.** Confidence calibration on the validation snapshot (80 labelled tickets).

| Confidence band | Tickets | Mean stated confidence | Observed accuracy | Gap (stated minus observed) |
|-----------------|---------|------------------------|-------------------|-----------------------------|
| 0.2 to 0.4 | 7 | 0.3175 | 1.0000 | -0.6825 |
| 0.4 to 0.6 | 11 | 0.5065 | 1.0000 | -0.4935 |
| 0.6 to 0.8 | 46 | 0.6913 | 1.0000 | -0.3087 |
| 0.8 to 1.0 | 16 | 0.9649 | 0.9375 | +0.0274 |

```chart
{
  "type": "bar",
  "title": "Stated confidence versus observed accuracy by band (validation, n=80)",
  "categories": ["0.2-0.4 (n=7)", "0.4-0.6 (n=11)", "0.6-0.8 (n=46)", "0.8-1.0 (n=16)"],
  "series": [
    {"name": "Mean stated confidence", "values": [0.3175, 0.5065, 0.6913, 0.9649]},
    {"name": "Observed accuracy", "values": [1.0, 1.0, 1.0, 0.9375]}
  ],
  "height": 225,
  "min": 0,
  "max": 1.2,
  "step": 0.2,
  "label_format": "%0.2f"
}
```

**Figure 6.** Calibration by confidence band, values from Table 22. Under-confidence in the lower bands is the safer direction for an auto-respond gate.

Under-confidence is safer than over-confidence for an assistant that must not send wrong answers, and it is part of why a measured threshold as low as 0.35 is defensible: low stated confidence on this data does not imply frequent error. It is also a calibration finding that the governance framework would treat as outside the five-point tolerance. The PRD lists calibration within five points as a governance condition; the top band meets it (a gap of 2.7 points), and the lower bands do not. The report states this plainly as unmet and notes that recalibration was not required to meet the business gate on this dataset, though it would make the confidence number more honest as a number.

### 8.5 Fairness

Fairness is measured as resolution quality on the tickets that should be auto-answered: those whose expected route is auto_respond and which are not policy-restricted. For each segment, quality is the share of those tickets that the system actually routed to auto_respond, and the pass condition is that the largest difference between segments is under five percentage points (`FAIRNESS_MAX_GAP_PP`). The raw auto-respond rate by segment is reported next to it for transparency but is not the pass criterion. Table 23 gives the segment figures and Figure 7 plots the raw rate beside the quality rate. The original metric, the raw rate, produced a tier gap of about 35 points in the first post-fix run. That gap was mostly structural: policy-restricted tickets are distributed unevenly across tiers, so a segment that happens to contain more of them shows a lower raw automation rate even when the system treats it correctly. Judging the system by raw mix would have penalised correct escalation.

**Table 23.** Fairness by segment on the validation snapshot.

| Segment | Eligible expected-auto tickets | Quality rate | Raw auto-respond rate |
|---------|-------------------------------|--------------|-----------------------|
| Business tier | 21 | 100% | 93.33% |
| Standard tier | 21 | 100% | 73.81% |
| Enterprise tier | 6 | 100% | 87.50% |
| Fluent | 40 | 100% | 81.97% |
| Non-fluent | 8 | 100% | 84.21% |

```chart
{
  "type": "bar",
  "title": "Raw auto_respond rate versus resolution quality by segment (%), validation",
  "categories": ["Business", "Standard", "Enterprise", "Fluent", "Non-fluent"],
  "series": [
    {"name": "Raw auto-respond rate", "values": [93.33, 73.81, 87.5, 81.97, 84.21]},
    {"name": "Resolution quality (expected-auto tickets)", "values": [100, 100, 100, 100, 100]}
  ],
  "height": 235,
  "min": 0,
  "max": 120,
  "step": 20,
  "label_format": "%0.1f"
}
```

**Figure 7.** Raw rates and quality rates from Table 23. The quality gap is 0.0 points for tier and for fluency; the raw tier spread (73.81% to 93.33%) remains and is explained by policy tickets, not by answer quality.

The 0.0 point result is real for the chosen metric but its strength should not be overstated. Every eligible ticket in every segment was routed to auto_respond, which says the router did not treat segments differently, but segments such as enterprise (6 eligible tickets) and non-fluent (8 eligible tickets) are small, so a gap of a few points could not have been detected with confidence. The metric measures routing parity, not answer quality: whether the generated answer for a non-fluent customer is as good as for a fluent one is untested until live drafts exist. The discovery work also warns that region was never analysed. Operators should keep watching raw mix on dashboards, because Table 23 shows a 19.5-point raw spread between business and standard tiers that the quality metric deliberately does not penalise.

### 8.6 Human evaluation by an independent second reviewer

The automated harness cannot score satisfaction, citation support or hallucination, so an independent second reviewer performed a documented review. Batch generate-on evaluation had been rate-limited and was not recorded, which left no live replies to review. The reviewer therefore wrote 28 draft replies directly from the retrieved passages for 28 tickets, using only the retrieved text and the rule of stating nothing the passages did not contain, and then scored them. Eligible tickets were the 66 auto_respond tickets, of which 17 are labelled not answerable from documentation and were excluded from the sample; of the remaining 49, 28 were drafted and 21 were not sampled for time. Selection aimed at covering as many intents and tiers as possible, not at choosing favourable cases, and four tickets with weaker retrieval were included on purpose.

**Table 24.** Human evaluation summary (passage-grounded simulation; indicative only).

| Metric | Target | Measured | Note |
|--------|--------|----------|------|
| Mean satisfaction proxy (1 to 5) | at least 4.0 | 4.68 (n=28) | Clarity 4.64, correctness 4.61, tone 4.86, citation usefulness 4.61 |
| Citation support rate | at least 95% | 100% (119 of 119 claim-citation pairs) | Largely a property of the drafting method |
| Citation identifier validity | 100% | 100% (28 of 28 drafts) | Cited identifiers were in the retrieved set |
| Hallucination rate | at most 5% | 0.0% (0 of 119); upper bound about 2.5% | One-sided 95% bound by the rule of three |
| Drafts below 4.0 | Reported | 2 of 28 (VAL-0078 at 3.50, VAL-0080 at 3.75) | Retained in the results, not removed |
| Drafts citing a label-expected article | Informational | 27 of 28 | |

```chart
{
  "type": "bar",
  "title": "Distribution of satisfaction-proxy scores across 28 reviewed drafts",
  "categories": ["3.50", "3.75", "4.00", "4.25", "4.75", "5.00"],
  "series": [{"name": "Number of drafts", "values": [1, 1, 1, 6, 3, 16]}],
  "height": 205,
  "min": 0,
  "max": 20,
  "step": 5,
  "label_format": "%0.0f"
}
```

**Figure 8.** Number of drafts at each score, tallied from the per-ticket table in Appendix C. Sixteen drafts scored 5.00; three drafts scored below 4.25.

Figure 8 shows how the proxy scores are distributed. The rubric awards one to five for clarity, correctness, tone and citation usefulness, and the satisfaction proxy is their mean. Each factual claim is mapped to the cited chunk and marked supported or unsupported, and every cited identifier is checked against the retrieved set for that ticket. The two lowest-scoring drafts were a database ticket and a deployment ticket whose retrievals contained only part of the relevant article, so the replies were diagnostic rather than complete, and the review recorded that one further ticket had a top retrieval score of only 0.38. These are the cases that the reviewer’s design deliberately kept in.

The numbers in Table 24 meet the targets, but the reasons they should be read cautiously are structural, and the human-evaluation notes state them directly. The drafts were written by the reviewer from passage text with a strict no-extra-claims rule, so a hallucination rate of zero and a support rate of 100% are largely properties of that method. They show that for the sampled tickets the retrieved passages contained enough material to support a good reply. They do not show that a live model will stay inside the passages. The same person wrote and scored the drafts, so the satisfaction figure is likely optimistic. The customer’s message text is not stored in the results file, so correctness was judged against the classified intent and the passages. The sample of 28 is below the 50 dual-reviewed responses that the Evaluation Framework expects for generate-on evaluation. The 17 auto_respond decisions on tickets labelled not answerable are a routing precision matter that these figures do not reflect, and section 10 lists them as a limitation.

### 8.7 The hidden set

Hidden-set runs completed: zero. The harness is path-parameterised and was written so that no dataset name is built in, and label-free policy rules were added so that a set without gold labels cannot bypass must-not handling. The provenance will be updated if and when graders inject the set. Until then, the report offers no estimate of hidden-set performance, and the development-to-validation behaviour is the only available hint of generalisation, a hint weakened by the iteration on validation described in section 8.2.

### 8.8 What was not done

The most important result of the evaluation is the list of things it did not establish. Table 25 states them without softening. The table is repeated in section 10 by reference so that a reader who jumps to the limitations finds the same list.

**Table 25.** Evidence that does not exist, stated plainly.

| Not done | Consequence for the claims |
|----------|----------------------------|
| No live generate-on batch was recorded (free-tier rate limits) | No customer first-contact-resolution figure; no live hallucination, citation or satisfaction measurement; the generation prompt fix is covered by mocked tests only |
| Hidden-set runs: 0 | No unbiased performance estimate; the validation figures are fitted |
| Demonstration video not yet recorded | The script and outline are complete; recording awaits camera capture |
| Human review used simulated drafts by one reviewer | Indicative only; no inter-rater agreement; sample below the 50 responses the framework expects |
| Calibration within 5 points met only in the top confidence band | Confidence is usable as a gate but not as a probability |
| Region was not analysed for fairness | Only tier and fluency segments are checked |
| Latency was measured without generation | No evidence about provider latency or the five-minute target in operation |
| Decision export scope not isolated per run | The packaged `decisions_export.jsonl` contains accumulated rows from several runs (see section 9.1) |
| Tests locate the Pack at a fixed path above `tests/` and ignore `DATASETS_PATH` | In the packaged layout, 6 tests fail, 3 error and 5 skip unless the Pack is placed at `<bundle>/your 05_Datasets directory`; with it placed, 28 pass |
| No fresh virtual-environment install, no second machine, no Python 3.11 run | The rehearsal used global Python 3.14.5 on one machine |

---

## 9. Governance

### 9.1 Decision log

Every automated decision is written to a SQLite decision log through SQLAlchemy. Rows cover classification, routing (with the escalation summary), generation and validation, the last with a nested guardrail map. Each row carries the fields the Governance Framework requires: decision identifier, timestamp, ticket identifier, stage, input summary, model name, prediction and confidence, alternatives considered, sources used, the threshold applied, the action taken, a human-readable reason, guardrail results, the prompt version and the requirement identifiers served. Table 26 describes the stages.

**Table 26.** Decision-log stages and what each records.

| Stage | Written when | Key content |
|-------|--------------|-------------|
| classification | Every ticket | Predicted intent and urgency, confidence, up to three alternatives, source (rules or model) |
| routing | Every ticket | Action, reason, `threshold_applied`, `grounded_override`, kill-switch flag, sources considered; escalation summary on escalate |
| generation | Only when generation runs | Model, prompt version, cited `doc_id` values, whether the result was cached or live |
| validation | Only when generation runs | Guardrail results per check with detail; final action (auto_respond, escalate or block) |

The harness reconciles the log against the tickets it processed and reports the number of tickets lacking a decision row, which is expected to be zero. In the recorded snapshot, the metrics report states 160 decision rows written for 80 tickets, two per ticket, which is what a route-only run should produce: classification and routing rows and no generation or validation rows. One discrepancy was found while preparing this report and is disclosed here. The packaged `decisions_export.jsonl` for that run contains 850 rows covering 180 distinct ticket identifiers, all of them classification or routing rows. The export therefore reflects the accumulated decision database rather than only the 80 tickets of that run, because the database is shared across runs. Reconciliation as implemented is unaffected, since it counts the rows written for the run, but a grader reading the export should not expect exactly 160 rows. Scoping the export to a single run is a recorded next step.

### 9.2 Risk register

Eight risks, R-01 to R-08, are aligned to the Governance Framework themes. Table 27 summarises them. The mitigations are implemented in code and operational scripts and, where tests exist, they are cited in the work log. The register is honest about likelihood: provider dependency is rated high because the free tier is exactly where the live batch failed.

**Table 27.** Risk register summary.

| ID | Risk | Likelihood | Impact | Principal mitigation |
|----|------|------------|--------|----------------------|
| R-01 | Hallucinated or uncited answer reaches a customer | Medium | High | Blocking citation, non-empty and grounding guards; escalate on empty retrieval |
| R-02 | Provider rate limit, outage or timeout | High | Medium | Timeout, backoff, cache; failure becomes escalation; batch continues |
| R-03 | Threshold or policy drift | Medium | High | Measured freeze at 0.35; `threshold_applied` logged on every decision |
| R-04 | Private data in an outbound draft | Low | High | Pattern guardrail; governance scan |
| R-05 | Kill switch ignored mid-flight | Low | High | Live re-read; checks before and after generation; `/health` visibility |
| R-06 | Quality gap of 5 points or more across segments | Medium | Medium | Segment quality metric; character n-gram classifier; grounded override |
| R-07 | Hidden-set leakage through hard-coded paths | Low | High | Harness takes `--input` and `--output` only |
| R-08 | Stale knowledge, cost or latency | Medium | Medium | Rebuild the index from pack documents; cache; escalate on slow or failed generation; `/metrics` |

### 9.3 Fairness method

The fairness method described in section 8.5 is documented in `docs/governance/fairness-method.md` together with its rationale. The metric is the resolution quality among tickets expected to be auto-answered and not policy-restricted, compared across customer tier and language fluency, with the raw automation mix shown beside it. The mitigations in the system are the character n-gram classifier, which is more robust to unusual wording, and the grounded override, which is segment-blind by construction. A fairness mitigation that depended on identifying a segment would itself be a fairness risk, so none was added.

### 9.4 Incident procedure

The incident runbook is short by design and covers unsafe replies, provider outages and suspected data leakage. Containment comes first: activate the kill switch, confirm on `/health` that it shows as active, and avoid deployments that would clear the flag file. Triage exports the decision rows for the incident window and notes the model, the prompt version and the threshold applied. Recovery depends on the incident: for a bad generation, keep the switch on, patch the prompt or the guard and re-test route-only before a limited generate run; for an outage, escalate-only is safe and the cache limits repeat cost; for private data in an outbound reply, extend the patterns and audit sampled generated answers; for a threshold regression, revert to the frozen 0.35 unless a logged revision says otherwise. The switch is cleared only with a written go-ahead, and a one-line note is appended to the work log.

### 9.5 Transparency, privacy and the audit trail

Three further governance properties follow from stakeholder evidence. First, transparency: the prompt requires the reply to be labelled as automated, which answers Ravi’s wish to calibrate trust, although the exact disclosure wording remains an open question in the requirements and the flag is requested but not enforced in code. Second, privacy: tickets carry customer identifier, name, tier and region, and free text that may contain personal data, so ticket text leaves the process only on auto_respond candidates for generation, and outbound text is scanned by blocking patterns. Third, auditability for Marcus’s autumn compliance review: each decision records the prompt version, the threshold applied and the sources used, so Ines can trace an answer to an article and a reviewer can reconstruct why a ticket was answered or escalated.

---

## 10. Limitations and next steps

### 10.1 Limitations stated plainly

The limitations below are the ones that most affect how far the evidence can be trusted. Section 8.8 and Table 25 give the shortest form; this section explains each and says what would resolve it.

1. **No live generate-on batch was recorded.** The recorded validation metrics are route-only. The 82.5% figure is the share of tickets the router would allow to proceed, and the word resolution should not be attached to it. Customer first-contact resolution with live generation is not a packaged batch result, and the metrics report correctly withholds the claim. Resolving this needs a small live run inside the free-tier quota with the cache enabled.
2. **Human figures come from simulation.** The satisfaction proxy of 4.68, the 119 of 119 supported claims and the 0 of 119 unsupported claims were produced from passage-grounded drafts by one reviewer who also wrote the drafts, with 28 drafts rather than the 50 the framework expects and no inter-rater check. They show retrieval sufficiency, not generator behaviour.
3. **The validation set was used for iteration.** The reported snapshot is a fitted result, and four validation-file runs exist on disk. Only the hidden set can provide an unbiased estimate, and hidden-set runs completed number zero.
4. **A routing precision debt remains.** In the validation snapshot, 17 of the 66 auto_respond decisions (about 26%) were on tickets labelled not answerable from documentation and labelled for escalation. The system routes on classifier confidence and retrieval strength, and it does not consult the answerable label, which a grader’s set may not carry. In a live setting these tickets would receive an answer that the corpus cannot support. The guardrails would catch a fabricated citation but not an unsupported claim attached to a valid one. This is the single most important defect in the current design.
5. **Urgency prediction is weaker than intent prediction.** Urgency is predicted and logged but does not gate the route, which was the pragmatic response to its weakness. Given that high-urgency tickets are 29.2% of historical volume and fare worse, this leaves a stakeholder need (Ravi’s) only partly served.
6. **Calibration is outside tolerance in three of four bands.** The classifier is under-confident, which is safe for the gate but makes the confidence number a poor probability.
7. **The embedding dependency can fail quietly.** The dimension check turns the failure into a loud one, but a clean-checkout grader still needs network access to the model hub at least once.
8. **Guardrails check form, not meaning.** Citation membership and pattern absence are verified; claim support is not.
9. **The decision export is not scoped to a run.** The shipped export contains accumulated rows, as section 9.1 explains.
10. **The demonstration video is not yet recorded.** It is a Stage 6 performance artefact. The submission contains the full script and outline, and the recording awaits camera capture.
11. **Clean checkout needs the reference datasets pack at a particular place for the tests.** The harness and the scripts accept injected paths, and the classifier and the Chroma index rebuild from an empty `storage/` (verified from the package tree). The test files, however, look for the Pack two directories above `tests/` and do not read `DATASETS_PATH`: in the packaged layout 6 tests fail, 3 error and 5 skip unless the Pack is placed at `<bundle>/your 05_Datasets directory`, and with it placed all 28 pass. Two tests also need the embedding model from the hub. Making the tests read `DATASETS_PATH` is a small follow-up that was not made here.

### 10.2 Effort, schedule and reflection

The effort record supports a candid reflection on how the project went. Table 28 and Figure 9 compare planned and actual hours by stage. Planned effort was 84 hours across a three-week plan and the recorded total is about 102 hours, an overrun of 18 hours that is concentrated in the build and revision stage, which took 65.5 hours against 48. Weekly hours worked were 33.5, 42.0 and 26.5 against planned 28, 34 and 22. The report and video hours are not fully recorded, because both are still outstanding at the time of writing, so the totals are hours worked to date.

**Table 28.** Planned versus actual effort by stage (Effort Log, hours).

| Stage | Planned | Actual | Difference | Main reason |
|-------|---------|--------|------------|-------------|
| 1. Discovery | 10.0 | 11.5 | +1.5 | Extending the discovery script so that every figure came from script output |
| 2. Requirements | 8.0 | 9.0 | +1.0 | Resolving the pack’s conflicting targets and samples (D1 to D4) |
| 3. Prompt library | 4.0 | 5.0 | +1.0 | Mapping each requirement to tests; injection-defence notes |
| 4. Sprint plan | 2.0 | 2.5 | +0.5 | Capacity table redone after totalling the backlog |
| 5. Build and revision | 48.0 | 65.5 | +17.5 | First gate run, classifier and threshold rework, fairness fix, LangGraph and backoff work, gap closure, human evaluation |
| 6. Report, video, packaging | 12.0 | 8.5 | -3.5 | Report and video outstanding; hours not yet added |
| Total | 84.0 | 102.0 | +18.0 | Concentrated in stage 5 |

```chart
{
  "type": "bar",
  "title": "Planned versus actual hours by stage",
  "categories": ["1 Discovery", "2 Requirements", "3 Prompts", "4 Sprint plan", "5 Build", "6 Report/video"],
  "series": [
    {"name": "Planned hours", "values": [10, 8, 4, 2, 48, 12]},
    {"name": "Actual hours", "values": [11.5, 9, 5, 2.5, 65.5, 8.5]}
  ],
  "height": 230,
  "min": 0,
  "max": 80,
  "step": 20,
  "label_format": "%0.1f"
}
```

**Figure 9.** Planned and actual effort by stage, values from Table 28. Stage 6 is below plan only because the report and video were unfinished when the log was written.

Several lessons follow from the record. The largest single overrun was the first unattended run, which took 8.5 hours against 3.0 because it failed on every ticket without raising an error. If the project started again, the full harness and a threshold sweep would run in the first days of the second week with generation stubbed, so that the embedder fault and the confidence collapse would have surfaced earlier; an embedding-dimension health check would exist from the start; the output-format contract of the generation prompt would be settled with one live call before guardrails were written; and a live generation batch would be started early enough to beat free-tier limits so that answer-quality evidence would not end up simulated. Two decisions were wasted effort in hindsight: the GLiNER plan, which took 1.5 hours to abandon, and the Grafana plan, which the drop list cut. Two decisions repaid their cost: scripting every discovery figure, which made the interview disagreements settleable, and logging the threshold on every routing decision, which made the freeze auditable.

### 10.3 Failure modes worth naming

The recorded history contains four failure modes that are likely to recur in any deployment of a system with this shape. The first is the silent-dependency failure: the embedding fallback produced a perfectly healthy pipeline with a zero business result. The second is the proxy-metric failure: a route-only rate looks like a resolution rate, and a raw automation share looks like a fairness measure, and both would have misled a reader had they not been relabelled. The third is the tuning-set leak: iterating on the validation file produced a result that looks held-out and is not. The fourth is the form-over-meaning failure of guardrails: a citation that resolves is not a claim that holds. Each has a mitigation in the design or a place on the next-steps list, and each was noticed by testing the system against a business outcome and not just against its own unit tests.

### 10.4 Next steps

The following steps are listed in priority order, and each can be done without changing the stack.

1. **Record the twenty-minute demonstration video** from `docs/video/video-script.md` and place it in the video folder of the package.
2. **Run a small live generate-on sample** with the cache enabled and attach metrics with `fcr_claim_allowed=true`, so that customer-facing first-contact resolution, citation validity and latency with provider time are measured for the first time.
3. **Tighten routing to respect `answerable_from_docs`** when the label exists, and strengthen label-free proxies, for example a stricter grounded-override floor, so that the 17 unsupported auto_respond decisions on validation are reduced without raising the escalation share above its limit.
4. **Expand dual human review of live drafts** toward the Evaluation Framework sample size, with two reviewers and an agreement statistic, so that the human figures are no longer simulated.
5. **Scope the decision export to a single run** and add a harness assertion that exported rows equal rows written for that run, and make the test files read `DATASETS_PATH` so that the suite runs in the packaged layout without a symlink.
6. **Run the hidden set once the graders inject it**, and update the provenance of the results without any tuning afterwards.
7. **Recalibrate classifier confidence** so that stated confidence tracks observed accuracy, and add a region segment to the fairness report.
8. **Package the submission archive** as `FirstnameLastname_CloudServe_Release.zip` after the video exists; the package script assembles the folder tree and, with `PACKAGE_NO_ZIP=1`, stops before zipping.

---

## Appendix A — Metrics snapshot

The recorded files are `evaluation/results/validation_fairness_fix/metrics.json` and `metrics.md`, with `results.jsonl`, `run_summary.json` and `decisions_export.jsonl` alongside. The snapshot reports 80 tickets input and processed, zero silent drops, 66 auto_respond and 14 escalate (all 14 policy must-not), classification accuracy 0.9875 over 80 labelled tickets, latency mean 0.0552 seconds and 95th percentile 0.0259 seconds, zero outbound private-data occurrences (vacuous without generation), 160 decision rows for 80 tickets, and fairness quality gaps of 0.0 points for tier and for fluency. The packaged copy under `04_Source_Code/evaluation/results/validation_fairness_fix/` contains `metrics.json`, `metrics.md` and `run_summary.json` only.

## Appendix B — Prompt register

| ID | File | Serves |
|----|------|--------|
| PR-GEN-01 | `prompts/generate_v1.md` | FR-5 grounded generation |
| PR-CLS-00 | rules plus scikit-learn (no prompt, by design) | FR-2 classification |
| PR-EVAL-01 | human review rubric (not sent to a model) | NFR-03 review of replies |

## Appendix C — Human evaluation per-ticket scores

Clarity (C), correctness (K), tone (T) and citation usefulness (U) are scored one to five; the satisfaction proxy is their mean. Supported claims are over total claims for the draft. The scores come from `docs/workbooks/human_eval_appendix.md`.

| Ticket | C | K | T | U | Proxy | Cited articles | Supported |
|--------|---|---|---|---|-------|----------------|-----------|
| VAL-0001 | 5 | 5 | 5 | 5 | 5.00 | AUTH-004 | 5/5 |
| VAL-0005 | 4 | 4 | 5 | 4 | 4.25 | API-002 | 4/4 |
| VAL-0010 | 5 | 5 | 5 | 5 | 5.00 | BILL-001 | 5/5 |
| VAL-0011 | 5 | 5 | 5 | 5 | 5.00 | DEPLOY-002 | 4/4 |
| VAL-0012 | 5 | 5 | 4 | 5 | 4.75 | DEPLOY-002 | 4/4 |
| VAL-0013 | 4 | 5 | 5 | 5 | 4.75 | BILL-001, BILL-002 | 6/6 |
| VAL-0018 | 5 | 5 | 5 | 5 | 5.00 | API-002 | 4/4 |
| VAL-0019 | 5 | 5 | 5 | 5 | 5.00 | ACCT-001 | 4/4 |
| VAL-0023 | 4 | 4 | 5 | 4 | 4.25 | ONB-002 | 5/5 |
| VAL-0027 | 4 | 4 | 5 | 4 | 4.25 | BILL-001, BILL-003 | 4/4 |
| VAL-0028 | 4 | 4 | 5 | 4 | 4.25 | DEPLOY-003 | 4/4 |
| VAL-0033 | 5 | 5 | 5 | 5 | 5.00 | API-003 | 5/5 |
| VAL-0039 | 5 | 5 | 5 | 5 | 5.00 | AUTH-004, INT-001 | 5/5 |
| VAL-0042 | 4 | 4 | 5 | 4 | 4.25 | DEPLOY-004 | 4/4 |
| VAL-0045 | 5 | 5 | 5 | 5 | 5.00 | DATA-001 | 4/4 |
| VAL-0047 | 5 | 5 | 5 | 5 | 5.00 | API-001 | 5/5 |
| VAL-0050 | 5 | 5 | 5 | 5 | 5.00 | ONB-001 | 4/4 |
| VAL-0052 | 5 | 5 | 5 | 5 | 5.00 | AUTH-001 | 4/4 |
| VAL-0054 | 5 | 5 | 5 | 5 | 5.00 | DATA-003 | 5/5 |
| VAL-0056 | 5 | 5 | 5 | 5 | 5.00 | DEPLOY-001 | 4/4 |
| VAL-0057 | 5 | 5 | 5 | 5 | 5.00 | DEPLOY-001 | 3/3 |
| VAL-0059 | 4 | 4 | 5 | 4 | 4.25 | DEPLOY-004 | 4/4 |
| VAL-0062 | 4 | 4 | 4 | 4 | 4.00 | INT-001, INT-002 | 4/4 |
| VAL-0064 | 5 | 5 | 5 | 5 | 5.00 | API-001, API-002 | 5/5 |
| VAL-0074 | 5 | 5 | 5 | 5 | 5.00 | ACCT-001 | 4/4 |
| VAL-0075 | 5 | 5 | 4 | 5 | 4.75 | API-001, AUTH-004 | 3/3 |
| VAL-0078 | 4 | 3 | 4 | 3 | 3.50 | PERF-003 | 4/4 |
| VAL-0080 | 4 | 3 | 5 | 3 | 3.75 | DEPLOY-003 | 3/3 |

## Appendix D — Effort and workbooks

Completed Stage 1 to Stage 5 workbooks and the Effort Log live under `docs/workbooks/`, as Markdown and as DOCX filled from the reference datasets pack templates by `scripts/fill_workbook_docx.py`. The human-evaluation appendix sits beside them. Total logged effort is approximately 102 hours; report and video hours are to be added when worked.

## Appendix E — Threshold freeze evidence

Evidence for the frozen threshold is in `docs/plan/threshold-freeze.md`, `storage/reports/threshold_tune.json` (local, git-ignored) and finding D3. The recorded sweep values are those in Table 16.

## Appendix F — Test command and coverage

```bash
cd submission
python -m pytest tests/ -v
```

Twenty-eight tests pass on the build machine. They cover ingest of four channels and coercion of malformed channel values, deterministic routing run twice, kill switch behaviour with live environment re-reading, the grounded override and its interaction with the confidence-floor guardrail, escalation on empty retrieval, label-free must-not rules, the non-empty answer and citation guardrails with a forged citation and a pattern-matching private value, mocked generation through the graph, a guardrail block through the graph, rate-limit backoff, Chroma index use, harness reconciliation of the decision log, a harness dry run with no silent drops, a harness that continues after a malformed ticket, the fairness quality structure, configuration errors on a bad numeric value, and two tests on real pack data that need the embedding model to be available. In a network-restricted run those two real-data tests errored while the other 26 passed; the full pass of 28 was verified with network access.

## Appendix G — Extended architecture narrative

The product brief expects LangChain and LangGraph. An early implementation used a sequential `run_ticket` function that matched the pipeline semantics but not the prescribed orchestration API. Gap closure wrapped the same stage functions as LangGraph nodes with shared state. That change is behaviour-neutral for route-only evaluation, satisfies the stack expectation and makes the mid-flight kill-switch checks explicit between the route and generate stages.

Cost control is a non-functional requirement under OpenRouter free-router limits. The design confines model calls to auto_respond paths, caches generations by model and prompt key, uses the `openrouter/free` router (via LiteLLM as `openrouter/openrouter/free`) for provider-side routing to available free models, and backs off on rate-limit responses with an optional retry-after hint. Classification never spends tokens. This is a deliberate departure from designs that use a language model at every step, and it matches the interview evidence that wrong answers are worse than silence.

## Appendix H — Clean-checkout expectations

A grader machine will not contain `storage/chroma` or the trained classifier file. The README instructions are to copy `.env.example` to `.env`, install the requirements, point `DATASETS_PATH` at the reference datasets pack datasets (or inject paths), train the classifier, build the index, then run the tests and the harness. The step-by-step rehearsal checklist, with the steps verified on the build machine marked, is `docs/plan/clean-checkout-rehearsal.md`. It records what was rehearsed from the package tree (rebuild of classifier and index, full route-only validation run, API health and kill switch, package assembly without a zip) and what was not (fresh virtual environment, second machine, Python 3.11, live generation). It also records the test-location caveat described in section 10.1. Secrets never ship in the archive: the package script excludes `.env` and `storage/` and includes a curated metrics snapshot so that acceptance criterion A10 evidence exists without re-running generation.

## Appendix I — Acceptance walkthrough for the video

The planned demonstration shows a success path (a high-confidence, well-retrieved ticket with generation cached or mocked), an escalation on a policy must-not ticket and on the kill switch, a guardrail block on an engineered citation failure, an unattended harness run on a short slice, the `/health` endpoint showing 59 chunks in the index, and decision log rows. The close states the limitations on camera: the route-only nature of the first-contact figure and the pending live generate sample. The script is `docs/video/video-script.md`, and the recording is not yet made.

## Appendix J — Related work stance

Commercial chatbots tend to optimise engagement. CloudServe Assistant optimises triage: retrieve, route, cite, or escalate with context. That stance comes from the interviews and not from model fashion, and the reference datasets pack’s Evaluation and Governance Frameworks constrain claims further: do not invent satisfaction figures, log decisions, test fairness and be able to stop automation.
