# Human evaluation notes (A6 / A10 honesty)

**Reviewer:** Independent reviewer (second pass), 2026-11-22
**Status:** Completed as a **passage-grounded simulation**. This is not a record of live LLM output.
**System under review:** CloudServe Assistant, route-only validation snapshot `evaluation/results/validation_fairness_fix/` (80 validation tickets, 66 routed to `auto_respond`, 14 to `escalate`).

## 1. Purpose

The CloudServe Evaluation Framework sets three human-review targets that the automated harness cannot score: CSAT of at least 4.0, citation accuracy of at least 95%, and hallucination of at most 5%. This document records a second-pass review that scores replies against those targets, and states plainly how far the evidence goes.

## 2. Summary

| Metric | Target (Evaluation Framework) | Measured (this sample) | Result |
|--------|-------------------------------|------------------------|--------|
| Mean CSAT proxy (mean of clarity, correctness, tone, citation usefulness; 1–5) | ≥ 4.0 | **4.68** (n=28; per-dimension means: clarity 4.64, correctness 4.61, tone 4.86, citation usefulness 4.61) | Pass (simulated drafts; indicative only) |
| Citation support rate (claims supported by the cited passage / cited claims) | ≥ 95% | **100.0%** (119/119 claim–citation pairs) | Pass (simulated drafts; indicative only) |
| Citation ID validity (every cited `doc_id` ⊆ retrieved `doc_id` set for that ticket) | 100% (harness proxy) | **100%** (28/28 drafts) | Pass |
| Hallucination rate (unsupported factual claims / total factual claims) | ≤ 5% | **0.0%** (0/119); one-sided 95% upper bound ≈ 2.5% (rule of three) | Pass (simulated drafts; indicative only) |
| Drafts with CSAT below 4.0 | — | 2 of 28 (VAL-0078, VAL-0080) | Reported, not removed |
| Drafts citing at least one label-expected document | — | 27 of 28 | Informational |

**Reading these numbers.** The drafts were written by the reviewer directly from retrieved passage text, with a strict rule of stating nothing that the passages do not contain. A hallucination rate of 0% and a citation support rate of 100% are therefore largely properties of the drafting method, not measurements of how a live model behaves. They show that, for the sampled tickets, the retrieved passages contained enough material to produce supported replies. They do not show that the generator will stay within the passages. The CSAT figure is likewise an optimistic proxy, because the same reviewer wrote and scored the drafts.

## 3. Method

1. **Source.** `evaluation/results/validation_fairness_fix/results.jsonl` (route-only run, `--no-generate`; the `generation` field is `null` for every ticket). Each record supplies the classification, routing decision, and the retrieved passages with `doc_id`, text, and score. Chunk text was read only from those records.
2. **Why drafts were simulated.** Batch generate-on evaluation was rate-limited and was not recorded, so no live generated replies exist for this snapshot.
3. **Eligibility.** Only tickets with `action = auto_respond` were eligible (66 tickets). Of these, 17 carry the label `answerable_from_docs = false` (and `expected_route = escalate`); they were taken **out of the CSAT sample** (section 6), because a grounded answer would need facts the corpus does not provide. Of the remaining 49 answerable tickets, 28 were drafted (21 were not sampled for time).
4. **Selection.** The 28 drafted tickets were chosen to cover as many intents and customer tiers as possible (billing, API keys, authentication, account access, rollback, deployment, build, configuration, webhooks, rate limits, pagination, export, data residency, onboarding, integration, database). Selection was by intent and retrieval pattern, not by outcome. Four tickets with weaker retrieval (partial chunks, or a top document that differs from the label-expected document) were deliberately included: VAL-0027, VAL-0059, VAL-0078, VAL-0080.
5. **Drafting.** Each draft is a short customer reply using only facts present in that ticket's retrieved passages, with inline `[DOC-…]` citations, as the product's generate step is intended to produce.
6. **Ticket text.** `results.jsonl` does not contain the customer's message. The drafts therefore answer the *classified intent* and the retrieved guidance, not the customer's exact wording. Correctness is scored as fit to the intent and to the retrieved passages. Customer-specific details could not be addressed or checked.
7. **Rubric (1–5 integers).**
   - *Clarity:* the reply is easy to follow and ordered as steps or causes.
   - *Correctness:* the reply matches the classified intent and the content of the passages, and does not drift to an unrelated topic.
   - *Tone:* polite, appropriate for the customer's stated fluency, no blame.
   - *Citation usefulness:* the cited document is the one a customer would want, and the cited chunk carries the claim.
   - *CSAT proxy:* arithmetic mean of the four scores.
8. **Dual review of claims.** Each substantive factual claim in a draft was listed with its cited `doc_id` and the specific retrieved chunk that carries it, then marked *supported* or *unsupported*. A script checked that every cited chunk and `doc_id` appears in that ticket's retrieved passages; none failed. Courtesies, greetings, and requests for more information were not counted as factual claims.
9. **Definitions.** Citation support rate = supported claim–citation pairs / all claim–citation pairs (each claim carries exactly one citation). Hallucination rate = unsupported factual claims / all factual claims.
10. **No ground truth beyond result fields.** Only `labels.answerable_from_docs`, `labels.expected_doc_ids`, and `labels.expected_route` already present in `results.jsonl` were used, to choose eligibility and to annotate fit. No hidden-set data was used.

## 4. Per-ticket scoring

Scores are clarity / correctness / tone / citation usefulness.

| ticket_id | intent | conf | clarity | correctness | tone | citation usefulness | CSAT | cited doc_ids | claims supported | halluc. | cited ⊆ retrieved |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VAL-0001 | api_key_issue | 0.69 | 5 | 5 | 5 | 5 | 5.00 | DOC-AUTH-004 | 5/5 | 0% | yes |
| VAL-0005 | api_usage_question | 0.67 | 4 | 4 | 5 | 4 | 4.25 | DOC-API-002 | 4/4 | 0% | yes |
| VAL-0010 | billing_query | 1.00 | 5 | 5 | 5 | 5 | 5.00 | DOC-BILL-001 | 5/5 | 0% | yes |
| VAL-0011 | rollback_request | 0.77 | 5 | 5 | 5 | 5 | 5.00 | DOC-DEPLOY-002 | 4/4 | 0% | yes |
| VAL-0012 | rollback_request | 0.82 | 5 | 5 | 4 | 5 | 4.75 | DOC-DEPLOY-002 | 4/4 | 0% | yes |
| VAL-0013 | billing_query | 1.00 | 4 | 5 | 5 | 5 | 4.75 | DOC-BILL-001, DOC-BILL-002 | 6/6 | 0% | yes |
| VAL-0018 | api_usage_question | 0.81 | 5 | 5 | 5 | 5 | 5.00 | DOC-API-002 | 4/4 | 0% | yes |
| VAL-0019 | account_access | 0.45 | 5 | 5 | 5 | 5 | 5.00 | DOC-ACCT-001 | 4/4 | 0% | yes |
| VAL-0023 | onboarding | 0.69 | 4 | 4 | 5 | 4 | 4.25 | DOC-ONB-002 | 5/5 | 0% | yes |
| VAL-0027 | billing_query | 1.00 | 4 | 4 | 5 | 4 | 4.25 | DOC-BILL-001, DOC-BILL-003 | 4/4 | 0% | yes |
| VAL-0028 | deployment_failure | 0.64 | 4 | 4 | 5 | 4 | 4.25 | DOC-DEPLOY-003 | 4/4 | 0% | yes |
| VAL-0033 | webhook_issue | 0.67 | 5 | 5 | 5 | 5 | 5.00 | DOC-API-003 | 5/5 | 0% | yes |
| VAL-0039 | api_key_issue | 0.75 | 5 | 5 | 5 | 5 | 5.00 | DOC-AUTH-004, DOC-INT-001 | 5/5 | 0% | yes |
| VAL-0042 | configuration_help | 0.72 | 4 | 4 | 5 | 4 | 4.25 | DOC-DEPLOY-004 | 4/4 | 0% | yes |
| VAL-0045 | data_export | 0.77 | 5 | 5 | 5 | 5 | 5.00 | DOC-DATA-001 | 4/4 | 0% | yes |
| VAL-0047 | rate_limit | 0.43 | 5 | 5 | 5 | 5 | 5.00 | DOC-API-001 | 5/5 | 0% | yes |
| VAL-0050 | onboarding | 0.70 | 5 | 5 | 5 | 5 | 5.00 | DOC-ONB-001 | 4/4 | 0% | yes |
| VAL-0052 | authentication_failure | 0.57 | 5 | 5 | 5 | 5 | 5.00 | DOC-AUTH-001 | 4/4 | 0% | yes |
| VAL-0054 | data_residency | 0.73 | 5 | 5 | 5 | 5 | 5.00 | DOC-DATA-003 | 5/5 | 0% | yes |
| VAL-0056 | deployment_failure | 0.79 | 5 | 5 | 5 | 5 | 5.00 | DOC-DEPLOY-001 | 4/4 | 0% | yes |
| VAL-0057 | deployment_failure | 0.71 | 5 | 5 | 5 | 5 | 5.00 | DOC-DEPLOY-001 | 3/3 | 0% | yes |
| VAL-0059 | configuration_help | 0.77 | 4 | 4 | 5 | 4 | 4.25 | DOC-DEPLOY-004 | 4/4 | 0% | yes |
| VAL-0062 | integration_help | 0.70 | 4 | 4 | 4 | 4 | 4.00 | DOC-INT-001, DOC-INT-002 | 4/4 | 0% | yes |
| VAL-0064 | api_usage_question | 0.70 | 5 | 5 | 5 | 5 | 5.00 | DOC-API-001, DOC-API-002 | 5/5 | 0% | yes |
| VAL-0074 | account_access | 0.57 | 5 | 5 | 5 | 5 | 5.00 | DOC-ACCT-001 | 4/4 | 0% | yes |
| VAL-0075 | api_key_issue | 0.76 | 5 | 5 | 4 | 5 | 4.75 | DOC-API-001, DOC-AUTH-004 | 3/3 | 0% | yes |
| VAL-0078 | database_issue | 0.63 | 4 | 3 | 4 | 3 | 3.50 | DOC-PERF-003 | 4/4 | 0% | yes |
| VAL-0080 | deployment_failure | 0.51 | 4 | 3 | 5 | 3 | 3.75 | DOC-DEPLOY-003 | 3/3 | 0% | yes |

Mean across 28 drafts: clarity 4.64, correctness 4.61, tone 4.86, citation usefulness 4.61; CSAT proxy **4.68**. Claims supported: **119/119**.

## 5. Draft replies and claim ledgers

Each ledger lists every factual claim, the document it cites, the retrieved chunk that carries it (first six hex characters of the MD5 of the chunk text), and the support verdict.

#### VAL-0001 — api_key_issue (CSAT 5.00; scores 5/5/5/5)

> Hello, and thanks for contacting CloudServe about your API key. A key that previously worked can return 401 if it was revoked, reached its configured expiry, or was removed together with a deleted user's account [DOC-AUTH-004]. Please check the API keys page for the key's status and expiry, and review its scopes: read-only keys cannot write, and project-scoped keys cannot reach organisation endpoints [DOC-AUTH-004]. To replace a key without downtime, create the new key first, deploy it, confirm traffic has moved, then revoke the old one [DOC-AUTH-004]. For production workloads, use service accounts rather than keys issued to individual users [DOC-AUTH-004].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | 401 can result from revoked, expired, or deleted-user keys | DOC-AUTH-004 | `238893` | supported |
| 2 | API keys page shows key status and expiry | DOC-AUTH-004 | `3dadb6` | supported |
| 3 | Read-only keys cannot write; project-scoped keys cannot reach organisation endpoints | DOC-AUTH-004 | `3dadb6` | supported |
| 4 | Rotate by creating, deploying, confirming traffic, then revoking the old key | DOC-AUTH-004 | `3dadb6` | supported |
| 5 | Use service accounts for production | DOC-AUTH-004 | `3dadb6` | supported |

#### VAL-0005 — api_usage_question (CSAT 4.25; scores 4/4/5/4)

> Hello, thanks for your question about retrieving results. For data that may change while you iterate, use cursor pagination, because offset pagination will skip or repeat records when items are inserted mid-iteration [DOC-API-002]. Pass the next_cursor value from each response as the cursor parameter of the next request and stop when it is null [DOC-API-002]. Keep the page size at or below two hundred, as larger requests are rejected rather than truncated [DOC-API-002]. Cursors expire after one hour, so long-running iterations should restart from a recorded checkpoint [DOC-API-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Cursor pagination recommended for changing data; offset skips/repeats | DOC-API-002 | `0c6dad` | supported |
| 2 | Pass next_cursor as cursor; stop when null | DOC-API-002 | `0c6dad` | supported |
| 3 | Page size at or below 200; larger rejected | DOC-API-002 | `0c6dad` | supported |
| 4 | Cursors expire after one hour; restart from checkpoint | DOC-API-002 | `0c6dad` | supported |

*Reviewer note:* Top retrieval score only 0.38; guidance is correct but the original question was not re-read, so fit is judged by intent only.

#### VAL-0010 — billing_query (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for asking about your invoice. Please open the usage breakdown for the period, which itemises charges by service and by environment [DOC-BILL-001]. Resources left running in staging or development environments are billed at the same rate as production [DOC-BILL-001]. The billing period runs from the anniversary of your subscription date, not the first of the month [DOC-BILL-001]. You can set a usage alert on the billing page to catch unexpected accrual during the period [DOC-BILL-001]. Invoices are finalised three days after the period ends, and adjustments requested before then appear on the same invoice [DOC-BILL-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Usage breakdown itemises by service and environment | DOC-BILL-001 | `cbbadb` | supported |
| 2 | Staging/dev resources billed at production rate | DOC-BILL-001 | `cbbadb` | supported |
| 3 | Period runs from subscription anniversary | DOC-BILL-001 | `cbbadb` | supported |
| 4 | Usage alert can be set on billing page | DOC-BILL-001 | `cbbadb` | supported |
| 5 | Invoices finalised three days after period end; earlier adjustments on same invoice | DOC-BILL-001 | `cbbadb` | supported |

#### VAL-0011 — rollback_request (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for reaching out. To roll back a failed release, open the revisions page for the service, identify the last healthy revision and select roll back on it; traffic moves within roughly thirty seconds and no rebuild takes place [DOC-DEPLOY-002]. If the release included a database migration, roll the migration back before the service so the older code does not meet an unexpected schema [DOC-DEPLOY-002]. Please note that rollback restores the container image and its configuration together, but it does not restore data [DOC-DEPLOY-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Revisions page: select roll back on last healthy revision | DOC-DEPLOY-002 | `112aa0` | supported |
| 2 | Traffic moves in ~30 seconds, no rebuild | DOC-DEPLOY-002 | `112aa0` | supported |
| 3 | Roll back database migration before service | DOC-DEPLOY-002 | `112aa0` | supported |
| 4 | Rollback restores image and configuration together, not data | DOC-DEPLOY-002 | `112aa0` | supported |

#### VAL-0012 — rollback_request (CSAT 4.75; scores 5/5/4/5)

> Hello, thank you for your message. The revisions page for your service lists revisions; choose the last healthy one and select roll back, which moves traffic within roughly thirty seconds without a rebuild [DOC-DEPLOY-002]. If a database migration shipped with the release, roll it back before the service [DOC-DEPLOY-002]. Rollback restores the image and its configuration together but not data, and it is worth recording the incident and the reason before deploying a fix [DOC-DEPLOY-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Select roll back on last healthy revision; ~30s; no rebuild | DOC-DEPLOY-002 | `112aa0` | supported |
| 2 | Roll back migration before service | DOC-DEPLOY-002 | `112aa0` | supported |
| 3 | Rollback does not restore data | DOC-DEPLOY-002 | `112aa0` | supported |
| 4 | Record incident and reason before deploying a fix | DOC-DEPLOY-002 | `112aa0` | supported |

#### VAL-0013 — billing_query (CSAT 4.75; scores 4/5/5/5)

> Hello, thanks for your billing question. The usage breakdown for the period itemises charges by service and environment, and resources left running in non-production environments are billed at the production rate [DOC-BILL-001]. After a plan change, upgrades take effect immediately and are prorated for the remaining days, with the calculation shown as a separate invoice line [DOC-BILL-002]. Downgrades take effect at the start of the next period, and credits are applied to the next invoice by default rather than refunded [DOC-BILL-002]. If you need a refund instead, an account owner should raise the request within thirty days of the invoice [DOC-BILL-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Usage breakdown itemises by service/environment | DOC-BILL-001 | `cbbadb` | supported |
| 2 | Non-production resources billed at production rate | DOC-BILL-001 | `cbbadb` | supported |
| 3 | Upgrades immediate and prorated; separate invoice line | DOC-BILL-002 | `48c14e` | supported |
| 4 | Downgrades take effect next period | DOC-BILL-002 | `48c14e` | supported |
| 5 | Credits applied to next invoice by default, not refunded | DOC-BILL-002 | `48c14e` | supported |
| 6 | Refund request by account owner within 30 days | DOC-BILL-002 | `48c14e` | supported |

#### VAL-0018 — api_usage_question (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your question. If you are only receiving the first page, or records are missing or duplicated, the usual causes are not passing the previous cursor to the next request, using offset pagination on a changing collection, or requesting a page size above the maximum [DOC-API-002]. Pass next_cursor from each response as the cursor parameter and stop when it is null; keep page size at or below two hundred [DOC-API-002]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [DOC-API-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Causes: missing cursor, offset pagination on changing data, oversize page | DOC-API-002 | `8c77ae` | supported |
| 2 | Pass next_cursor; stop when null | DOC-API-002 | `0c6dad` | supported |
| 3 | Page size at or below 200 | DOC-API-002 | `0c6dad` | supported |
| 4 | Export endpoint is asynchronous and returns a download link | DOC-API-002 | `0c6dad` | supported |

#### VAL-0019 — account_access (CSAT 5.00; scores 5/5/5/5)

> Hello, thank you for contacting us about access. First check the effective permissions view for the user, which resolves direct roles and group memberships together [DOC-ACCT-001]. Please also confirm the invitation was accepted: pending invitations appear in a separate section and expire after seven days [DOC-ACCT-001]. A common cause is a role granted at project scope rather than organisation scope [DOC-ACCT-001]. Where someone is leaving, remove the user rather than only changing their password, and revoke any API keys they created [DOC-ACCT-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Effective permissions view resolves roles and groups | DOC-ACCT-001 | `5c954a` | supported |
| 2 | Pending invitations separate; expire after seven days | DOC-ACCT-001 | `5c954a` | supported |
| 3 | Role granted at project not organisation scope is a cause | DOC-ACCT-001 | `2da687` | supported |
| 4 | Remove departing user and revoke their API keys | DOC-ACCT-001 | `5c954a` | supported |

*Reviewer note:* Customer is labelled non-fluent; draft uses short, plain sentences.

#### VAL-0023 — onboarding (CSAT 4.25; scores 4/4/5/4)

> Hello, and welcome. When moving an existing application, externalise configuration first: anything read from a file on disk should move to environment variables or secrets [DOC-ONB-002]. Move local state such as uploaded files or session data to object storage or the managed database [DOC-ONB-002]. Run in parallel with your existing deployment and shift a small share of traffic before committing [DOC-ONB-002]. Plan the database migration separately from the application migration [DOC-ONB-002]. Applications that write to the local filesystem lose that data on every deployment and scaling event [DOC-ONB-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Externalise file-based configuration to env vars/secrets | DOC-ONB-002 | `d5dd46` | supported |
| 2 | Move local state to object storage or managed database | DOC-ONB-002 | `d5dd46` | supported |
| 3 | Run in parallel and shift small traffic share | DOC-ONB-002 | `d5dd46` | supported |
| 4 | Plan database migration separately | DOC-ONB-002 | `d5dd46` | supported |
| 5 | Local filesystem data lost on every deployment/scaling event | DOC-ONB-002 | `d5dd46` | supported |

#### VAL-0027 — billing_query (CSAT 4.25; scores 4/4/5/4)

> Hello, thanks for your question about charges. Usage-based charges accrue when usage goes beyond the plan allowance, and overage protection being disabled means usage continues past the allowance [DOC-BILL-003]. To investigate, open the usage breakdown for the period, which itemises charges by service and environment [DOC-BILL-001], and check the billing period dates at the top of the invoice, as the period runs from the subscription anniversary [DOC-BILL-001]. You can also set a usage alert on the billing page [DOC-BILL-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Charges accrue beyond plan allowance; disabled overage protection lets usage continue | DOC-BILL-003 | `4bac29` | supported |
| 2 | Usage breakdown itemises by service and environment | DOC-BILL-001 | `cbbadb` | supported |
| 3 | Billing period runs from subscription anniversary | DOC-BILL-001 | `cbbadb` | supported |
| 4 | Usage alert on billing page | DOC-BILL-001 | `cbbadb` | supported |

*Reviewer note:* Only the symptoms/causes chunk of DOC-BILL-003 was retrieved; its spend-cap resolution steps (the expected-doc content) were not, so the draft cannot cover them.

#### VAL-0028 — deployment_failure (CSAT 4.25; scores 4/4/5/4)

> Hello, thanks for your message. Builds that worked before can start failing when an unpinned dependency releases an incompatible version, or when the build environment uses a different language runtime than your machine [DOC-DEPLOY-003]. Please pin dependencies with exact versions and commit the lock file, and compare the runtime version in your build configuration with the one you use locally [DOC-DEPLOY-003]. Clearing the build cache from the settings page and triggering a fresh build rules out a corrupted artefact [DOC-DEPLOY-003]. Build logs keep the full resolution output for thirty days [DOC-DEPLOY-003].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Unpinned dependency or runtime mismatch can break builds | DOC-DEPLOY-003 | `bf5fa0` | supported |
| 2 | Pin exact versions, commit lock file, compare runtime versions | DOC-DEPLOY-003 | `359775` | supported |
| 3 | Clear build cache then fresh build rules out corrupted artefact | DOC-DEPLOY-003 | `359775` | supported |
| 4 | Build logs retain resolution output for 30 days | DOC-DEPLOY-003 | `359775` | supported |

*Reviewer note:* Customer labelled non-fluent; wording kept simple.

#### VAL-0033 — webhook_issue (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your webhook question. Check the webhook delivery log, which records every attempt with the response status and body for the last seven days [DOC-API-003]. Return a 2xx as quickly as possible and process the event asynchronously, because deliveries time out after five seconds [DOC-API-003]. Compute signatures over the raw request body before parsing, since re-serialising JSON changes the bytes [DOC-API-003]. Make your handler idempotent using the event identifier, as duplicates are expected with at-least-once delivery [DOC-API-003]. Failed deliveries are retried with backoff for twenty-four hours, after which the endpoint is disabled and the account notified [DOC-API-003].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Delivery log keeps attempts for seven days | DOC-API-003 | `8848bd` | supported |
| 2 | Return 2xx quickly; timeout after five seconds | DOC-API-003 | `8848bd` | supported |
| 3 | Sign over raw body; re-serialising invalidates signature | DOC-API-003 | `8848bd` | supported |
| 4 | Idempotent handler; duplicates expected | DOC-API-003 | `8848bd` | supported |
| 5 | Retries for 24h then endpoint disabled and account notified | DOC-API-003 | `8848bd` | supported |

#### VAL-0039 — api_key_issue (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for getting in touch. A previously working key may return 401 if it was revoked, expired, or belonged to a user who was deleted [DOC-AUTH-004]. Check the API keys page for the key's status, expiry and scopes [DOC-AUTH-004]. If a key has been exposed publicly, revoke it immediately rather than waiting for a rotation window [DOC-AUTH-004]. For pipelines, the CI guidance recommends a service account rather than a personal key, with an expiry set and rotation on a schedule [DOC-INT-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | 401 from revoked/expired/deleted-user keys | DOC-AUTH-004 | `238893` | supported |
| 2 | API keys page shows status, expiry, scopes | DOC-AUTH-004 | `3dadb6` | supported |
| 3 | Exposed key: revoke immediately | DOC-AUTH-004 | `3dadb6` | supported |
| 4 | Pipelines should use a service account, not a personal key | DOC-INT-001 | `61e80a` | supported |
| 5 | Service account keys do not expire by default; set expiry and rotate | DOC-INT-001 | `61e80a` | supported |

#### VAL-0042 — configuration_help (CSAT 4.25; scores 4/4/5/4)

> Hello, thanks for your configuration question. Check the scope where the variable was defined: service scope overrides project scope, and project scope overrides organisation defaults [DOC-DEPLOY-004]. Review the environment overrides page, which lists values that differ from the defaults for each environment [DOC-DEPLOY-004]. After changing configuration, redeploy, since running containers do not pick up new values without a restart [DOC-DEPLOY-004]. Store anything sensitive as a secret, which is masked in logs [DOC-DEPLOY-004].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Service > project > organisation precedence | DOC-DEPLOY-004 | `3d91fa` | supported |
| 2 | Environment overrides page lists differing values | DOC-DEPLOY-004 | `3d91fa` | supported |
| 3 | Redeploy; running containers need restart for new values | DOC-DEPLOY-004 | `3d91fa` | supported |
| 4 | Secrets masked in logs | DOC-DEPLOY-004 | `3d91fa` | supported |

*Reviewer note:* A BILL-003 passage was also retrieved at rank 2 but is irrelevant and was not used.

#### VAL-0045 — data_export (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your export question. Check the exports page for job status; jobs covering more than a million records commonly take several minutes [DOC-DATA-001]. If the download link has expired, request a fresh one from the exports page, as the underlying file is retained for seven days [DOC-DATA-001]. The export reflects the moment the job began, so records created during processing are not included [DOC-DATA-001]. For recurring needs, configure a scheduled export delivered to object storage [DOC-DATA-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Exports page shows status; >1M records take several minutes | DOC-DATA-001 | `c4f3ab` | supported |
| 2 | Fresh link available; file retained seven days | DOC-DATA-001 | `c4f3ab` | supported |
| 3 | Export is a snapshot of job start time | DOC-DATA-001 | `c4f3ab` | supported |
| 4 | Scheduled export to object storage for recurring needs | DOC-DATA-001 | `c4f3ab` | supported |

#### VAL-0047 — rate_limit (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your question about 429 responses. Read the rate limit headers returned with every response; they give the limit, remaining allowance and reset time [DOC-API-001]. Some endpoints have a lower limit, and search and export endpoints are limited more tightly than reads [DOC-API-001]. Use exponential backoff with jitter on 429 responses rather than retrying immediately [DOC-API-001]. Limits are enforced per organisation, so issuing more keys does not raise your quota [DOC-API-001]. On Business and Enterprise plans a higher sustained limit can be requested through an account request [DOC-API-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Rate-limit headers give limit, remaining, reset | DOC-API-001 | `ed6c24` | supported |
| 2 | Search/export endpoints limited more tightly | DOC-API-001 | `ed6c24` | supported |
| 3 | Exponential backoff with jitter on 429 | DOC-API-001 | `ed6c24` | supported |
| 4 | Per-organisation limits; more keys do not help | DOC-API-001 | `ed6c24` | supported |
| 5 | Higher limit via account request on Business/Enterprise | DOC-API-001 | `ed6c24` | supported |

#### VAL-0050 — onboarding (CSAT 5.00; scores 5/5/5/5)

> Hello, and welcome to CloudServe. To get started, create a project and then a service within it, since resources belong to services and services belong to projects [DOC-ONB-001]. Connect a repository or push a container image; the build service detects common project layouts automatically [DOC-ONB-001]. Set the environment variables your application needs before the first deployment rather than after it [DOC-ONB-001]. Then deploy and watch the logs for the first sixty seconds, as most first-deployment problems show up in startup output [DOC-ONB-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Create project, then service | DOC-ONB-001 | `25db8b` | supported |
| 2 | Connect repo/push image; build detects layouts | DOC-ONB-001 | `25db8b` | supported |
| 3 | Set env vars before first deployment | DOC-ONB-001 | `25db8b` | supported |
| 4 | Watch logs for first sixty seconds | DOC-ONB-001 | `25db8b` | supported |

#### VAL-0052 — authentication_failure (CSAT 5.00; scores 5/5/5/5)

> Hello, sorry you are having trouble signing in. Please check the console security page: a locked account shows a red banner and unlocks automatically after thirty minutes [DOC-AUTH-001]. Clear cookies for the CloudServe domain or try a private browsing window [DOC-AUTH-001]. If the CLI is failing, run `cloudserve auth logout` followed by `cloudserve auth login` to discard the cached token [DOC-AUTH-001]. If you need immediate access, an administrator on the account can release the lock from the team members page [DOC-AUTH-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Locked account: red banner on security page; unlocks after 30 min | DOC-AUTH-001 | `ca8f8a` | supported |
| 2 | Clear cookies or use private window | DOC-AUTH-001 | `ca8f8a` | supported |
| 3 | CLI logout/login discards cached token | DOC-AUTH-001 | `ca8f8a` | supported |
| 4 | Administrator can release lock from team members page | DOC-AUTH-001 | `ca8f8a` | supported |

#### VAL-0054 — data_residency (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your data residency question. The region shown on the organisation settings page is fixed at creation and determines where primary data is stored [DOC-DATA-003]. Read replicas in additional regions can reduce latency for distant users without moving primary storage [DOC-DATA-003]. If you have a single-region requirement, review the backup replication setting, because cross-region replication is enabled by default [DOC-DATA-003]. Moving an organisation between regions needs a planned migration with support and involves a maintenance window [DOC-DATA-003]. Metadata such as account names and billing records is stored centrally regardless of data region [DOC-DATA-003].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Region fixed at creation; determines primary storage | DOC-DATA-003 | `0453db` | supported |
| 2 | Read replicas reduce latency without moving primary | DOC-DATA-003 | `0453db` | supported |
| 3 | Cross-region backup replication on by default | DOC-DATA-003 | `0453db` | supported |
| 4 | Region migration needs support and maintenance window | DOC-DATA-003 | `0453db` | supported |
| 5 | Metadata stored centrally | DOC-DATA-003 | `0453db` | supported |

#### VAL-0056 — deployment_failure (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your message about the failing deployment. Please confirm the container listens on the port declared in the service definition, since a mismatch produces a health check failure that looks like a timeout [DOC-DEPLOY-001]. If the application needs time to warm up, increase the initial delay; thirty seconds is a reasonable starting point for services that load models or caches [DOC-DEPLOY-001]. Compare the deployment's environment variables against those the application requires [DOC-DEPLOY-001], and inspect the logs from the failed revision rather than the running one [DOC-DEPLOY-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Port mismatch looks like a health-check timeout | DOC-DEPLOY-001 | `595b57` | supported |
| 2 | Increase initial delay; 30s a reasonable start | DOC-DEPLOY-001 | `595b57` | supported |
| 3 | Compare env vars; missing config causes silent startup failure | DOC-DEPLOY-001 | `595b57` | supported |
| 4 | Inspect logs of failed revision, not running one | DOC-DEPLOY-001 | `595b57` | supported |

#### VAL-0057 — deployment_failure (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for contacting us. A deployment that reaches running and then rolls back is commonly caused by a health endpoint slower than its timeout, a container listening on a different port than the service declares, or a missing environment variable [DOC-DEPLOY-001]. Health checks must return within the timeout using only local state; endpoints that call a database fail during a database incident and take the service down [DOC-DEPLOY-001]. Inspect the logs from the failed revision, because the rollback replaces the logs shown by default [DOC-DEPLOY-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Rolling back after running: slow health endpoint, port mismatch, missing env var | DOC-DEPLOY-001 | `7ea698` | supported |
| 2 | Health checks must use only local state; DB-calling endpoints fail in DB incident | DOC-DEPLOY-001 | `4a13f4` | supported |
| 3 | Rollback replaces default logs; inspect failed revision | DOC-DEPLOY-001 | `595b57` | supported |

#### VAL-0059 — configuration_help (CSAT 4.25; scores 4/4/5/4)

> Hello, thanks for your configuration question. Check the scope at which a variable was defined: service scope overrides project scope, which overrides organisation defaults [DOC-DEPLOY-004]. Store sensitive values as secrets, which are masked in logs and not readable through the API after creation [DOC-DEPLOY-004]. Redeploy after changing configuration, as running containers do not pick up new values without a restart [DOC-DEPLOY-004]. If a secret has been printed to logs, treat it as exposed and rotate it [DOC-DEPLOY-004].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Service > project > organisation precedence | DOC-DEPLOY-004 | `3d91fa` | supported |
| 2 | Secrets masked and not readable via API after creation | DOC-DEPLOY-004 | `3d91fa` | supported |
| 3 | Redeploy after config change | DOC-DEPLOY-004 | `3d91fa` | supported |
| 4 | Secret printed to logs is exposed; rotate | DOC-DEPLOY-004 | `3d91fa` | supported |

*Reviewer note:* Label also lists DOC-ACCT-002 (project structure) as expected; it was not retrieved, so that part of a complete answer is absent.

#### VAL-0062 — integration_help (CSAT 4.00; scores 4/4/4/4)

> Hello, thanks for your message. If logs are not arriving at your external destination, check the forwarding status page, which shows the last successful delivery and any error returned by the destination [DOC-INT-002]. Metrics can be delayed by up to two minutes because they are aggregated before being sent [DOC-INT-002]. Forwarding pauses after one hour of consecutive failures and must be resumed manually once the destination is healthy [DOC-INT-002]. If your question concerns pipeline authentication, note that using a personal key rather than a service account is one listed cause of pipelines failing to authenticate [DOC-INT-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Forwarding status page shows last delivery and destination error | DOC-INT-002 | `f3e910` | supported |
| 2 | Metrics delay up to two minutes | DOC-INT-002 | `f3e910` | supported |
| 3 | Forwarding pauses after one hour of failures; manual resume | DOC-INT-002 | `f3e910` | supported |
| 4 | Personal key instead of service account is a listed cause of pipeline auth failure | DOC-INT-001 | `0b55bc` | supported |

*Reviewer note:* Two integration topics retrieved; the draft hedges between them because the exact integration was not re-read. Clarity and correctness capped for that reason. Customer labelled non-fluent.

#### VAL-0064 — api_usage_question (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your question. Use cursor pagination for data that may change while you iterate [DOC-API-002]. Pass the next_cursor value as the cursor parameter of the next request, and stop when it is null [DOC-API-002]. Keep page size at or below two hundred; larger requests are rejected [DOC-API-002]. Search and export endpoints are limited more tightly than reads, so for very large extracts use the asynchronous export endpoint [DOC-API-001][DOC-API-002].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Cursor pagination for changing data | DOC-API-002 | `0c6dad` | supported |
| 2 | next_cursor as cursor; stop when null | DOC-API-002 | `0c6dad` | supported |
| 3 | Page size at or below 200; larger rejected | DOC-API-002 | `0c6dad` | supported |
| 4 | Search/export endpoints limited more tightly than reads | DOC-API-001 | `ed6c24` | supported |
| 5 | Export endpoint is asynchronous for large extracts | DOC-API-002 | `0c6dad` | supported |

#### VAL-0074 — account_access (CSAT 5.00; scores 5/5/5/5)

> Hello, thanks for your message. Start with the effective permissions view for the user, which resolves direct roles and group memberships together [DOC-ACCT-001]. Pending invitations appear in a separate section and expire after seven days [DOC-ACCT-001]. Prefer group membership to direct role assignment so access can be reviewed in one place [DOC-ACCT-001]. Note that removing the last account owner is not permitted; transfer ownership first [DOC-ACCT-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Effective permissions view resolves roles and groups | DOC-ACCT-001 | `5c954a` | supported |
| 2 | Pending invitations expire after seven days | DOC-ACCT-001 | `5c954a` | supported |
| 3 | Prefer group membership to direct roles | DOC-ACCT-001 | `5c954a` | supported |
| 4 | Last account owner cannot be removed; transfer first | DOC-ACCT-001 | `5c954a` | supported |

#### VAL-0075 — api_key_issue (CSAT 4.75; scores 5/5/4/5)

> Hello, thanks for your message. A key that has stopped working has usually been revoked, reached its expiry, or been removed with a deleted user [DOC-AUTH-004]. Review the key's status on the API keys page and the scopes attached to it, because a key can work for some endpoints and not others when its scope excludes the endpoint [DOC-AUTH-004]. Note also that the rate limit applies per organisation rather than per key [DOC-API-001].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Revoked/expired/deleted-user keys stop working | DOC-AUTH-004 | `238893` | supported |
| 2 | API keys page shows status; scopes can exclude endpoints | DOC-AUTH-004 | `3dadb6` | supported |
| 3 | Rate limit applies per organisation rather than per key | DOC-API-001 | `731d4e` | supported |

#### VAL-0078 — database_issue (CSAT 3.50; scores 4/3/4/3)

> Hello, thanks for your message. The retrieved guidance on database connection problems lists these likely causes: the pool size multiplied by the instance count exceeds the database connection limit, connections are not returned to the pool after use, or long-running transactions hold connections open [DOC-PERF-003]. The same guidance notes that these symptoms include errors saying no connection is available and latency that rises sharply as traffic grows [DOC-PERF-003]. If none of these match what you see, please reply with the error text and the instance count so we can look further.

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Cause: pool size x instance count exceeds DB connection limit | DOC-PERF-003 | `f6aa03` | supported |
| 2 | Cause: connections not returned to pool | DOC-PERF-003 | `f6aa03` | supported |
| 3 | Cause: long-running transactions hold connections | DOC-PERF-003 | `f6aa03` | supported |
| 4 | Symptoms: no-connection errors; latency rises with traffic | DOC-PERF-003 | `f6aa03` | supported |

*Reviewer note:* Only the symptoms/causes chunk of DOC-PERF-003 was retrieved; no resolution steps were available, so the draft is diagnostic only and is a weaker answer.

#### VAL-0080 — deployment_failure (CSAT 3.75; scores 4/3/5/3)

> Hello, thanks for your message. If a build that previously succeeded now fails without code changes, the retrieved guidance points to an unpinned dependency that released an incompatible version, a different language runtime in the build environment than on your machine, or a partially written dependency cache artefact [DOC-DEPLOY-003]. Pin exact versions and commit the lock file, compare runtime versions, and clear the build cache from the settings page before a fresh build [DOC-DEPLOY-003].

| # | Factual claim | Cited doc_id | Passage chunk | Supported? |
|---|---|---|---|---|
| 1 | Causes: unpinned dependency, runtime mismatch, partial cache artefact | DOC-DEPLOY-003 | `bf5fa0` | supported |
| 2 | Pin versions, commit lock file, compare runtimes | DOC-DEPLOY-003 | `359775` | supported |
| 3 | Clear build cache and rebuild | DOC-DEPLOY-003 | `359775` | supported |

*Reviewer note:* Label lists DOC-DEPLOY-001 (health check) as the expected document, but retrieval ranked DOC-DEPLOY-003 first; the draft answers the retrieved topic. Correctness and citation usefulness reduced for possible topic mismatch.


## 6. Tickets excluded from the CSAT sample

These 17 tickets were routed to `auto_respond` by the route-only run, but their labels mark them as not answerable from the documentation (`answerable_from_docs = false`, `expected_route = escalate`). No draft was written, because a useful reply would need unretrieved facts. They were excluded from the means above rather than scored.

| ticket_id | classified intent | expected_route |
|---|---|---|
| VAL-0004 | authentication_failure | escalate |
| VAL-0014 | rollback_request | escalate |
| VAL-0016 | performance_degradation | escalate |
| VAL-0022 | performance_degradation | escalate |
| VAL-0024 | api_key_issue | escalate |
| VAL-0025 | deployment_failure | escalate |
| VAL-0026 | data_residency | escalate |
| VAL-0034 | rollback_request | escalate |
| VAL-0037 | data_residency | escalate |
| VAL-0046 | api_usage_question | escalate |
| VAL-0051 | integration_help | escalate |
| VAL-0055 | integration_help | escalate |
| VAL-0060 | webhook_issue | escalate |
| VAL-0066 | data_residency | escalate |
| VAL-0070 | sso_configuration | escalate |
| VAL-0071 | quota_or_overage | escalate |
| VAL-0072 | billing_query | escalate |

**Observation for the builder.** In this snapshot 17 of 66 `auto_respond` decisions (26%) are on tickets the labels expect to be escalated. That is a routing-precision matter outside the scope of this CSAT sample and is not reflected in the CSAT, citation, or hallucination figures above. If these were auto-answered by a live model, citation support and hallucination on them could differ materially from the sampled tickets. The routing and fairness metrics in `evaluation/results/validation_fairness_fix/metrics.md` are the right place to quantify it.

## 7. Limitations

- **Not live LLM output.** The drafts are reviewer-written simulations. They do not exercise the LiteLLM→OpenRouter generate step, its prompt, its guardrails, or its failure modes. The builder should still run live generate-on evaluation, record it, and use those outputs for the demonstration video and the final report.
- **Method-bound citation and hallucination figures.** Because every claim was written from the cited chunk, 100% support and 0% hallucination are expected. They validate retrieval sufficiency for the sampled tickets only.
- **Same-person author and scorer.** The reviewer wrote and scored the drafts, so CSAT is likely optimistic. A different human rating live outputs is needed for a credible CSAT figure.
- **Customer wording not available.** Correctness was not assessed against the actual customer message (see Method, item 6).
- **Sample size.** 28 drafts, 119 claims. This is above the minimum of 20 set for CSAT, but below the 50 dual-reviewed responses the framework expects once generate-on evaluation exists. The one-sided 95% upper bound on hallucination from 0 of 119 unsupported claims is about 2.5%.
- **Sampling bias.** Tickets labelled not answerable (17) were excluded, and 21 answerable tickets were not drafted. The sample is purposive, not random.
- **Partial chunks.** Some retrievals contained only the symptoms-and-causes chunk of a document (for example VAL-0027 and VAL-0078), so replies were diagnostic rather than complete. This is reflected in lower scores, and VAL-0078 and VAL-0080 fall below 4.0.
- **Hidden-set runs.** None have been completed; these notes make no claim about hidden-set performance.

## 8. Provenance

- Results file: `evaluation/results/validation_fairness_fix/results.jsonl` (80 records).
- Route-only run: `fcr_claim_allowed=false` for `--no-generate`.
- Review date: 2026-11-22. Reviewer: Independent reviewer (second pass).
- Application source code was not modified.
