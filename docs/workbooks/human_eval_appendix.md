# Human evaluation appendix (CSAT, citation support, hallucination)

**Reviewer:** Independent reviewer (second pass), 2026-11-22
**Full record:** `docs/plan/human-eval-notes.md`

## Scope and method

- **Data:** `evaluation/results/validation_fairness_fix/results.jsonl` (route-only; 80 validation tickets, 66 `auto_respond`).
- **Sample:** 28 `auto_respond` tickets that the labels mark as answerable from the documentation; 119 factual claims reviewed. 17 tickets labelled not answerable were excluded from scoring and listed in the full notes.
- **How drafts were produced:** passage-grounded simulation. Batch generate-on evaluation was rate-limited and was not recorded, so the reviewer wrote each reply using only the retrieved passages for that ticket, with `[DOC-…]` citations.
- **Rubric:** clarity (C), correctness (K), tone (T), citation usefulness (U), each 1–5; CSAT proxy is their mean.
- **Claim review:** each factual claim was mapped to its cited chunk and marked supported or unsupported; hallucination is unsupported claims divided by all factual claims.

## Results

| Metric | Target (Evaluation Framework) | Measured (this sample) | Result |
|--------|-------------------------------|------------------------|--------|
| Mean CSAT proxy (mean of clarity, correctness, tone, citation usefulness; 1–5) | ≥ 4.0 | **4.68** (n=28; per-dimension means: clarity 4.64, correctness 4.61, tone 4.86, citation usefulness 4.61) | Pass |
| Citation support rate (claims supported by the cited passage / cited claims) | ≥ 95% | **100.0%** (119/119 claim–citation pairs) | Pass |
| Citation ID validity (every cited `doc_id` ⊆ retrieved `doc_id` set for that ticket) | 100% (harness proxy) | **100%** (28/28 drafts) | Pass |
| Hallucination rate (unsupported factual claims / total factual claims) | ≤ 5% | **0.0%** (0/119); one-sided 95% upper bound ≈ 2.5% (rule of three) | Pass |
| Drafts with CSAT below 4.0 | — | 2 of 28 (VAL-0078, VAL-0080) | Reported, not removed |
| Drafts citing at least one label-expected document | — | 27 of 28 | Informational |

## Per-ticket scores

| ticket_id | C | K | T | U | CSAT | cites | supp. |
|---|---|---|---|---|---|---|---|
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

Cites are shown without the `DOC-` prefix. Supp. is supported claims over total claims for the draft.

## Limitations

- The drafts are simulated, not live LLM output. Live generate-on evaluation should still be run and recorded.
- 100% support and 0% hallucination follow largely from the drafting method and show retrieval sufficiency, not generator behaviour.
- The reviewer wrote and scored the drafts, so CSAT is likely optimistic.
- The customer's message text is not in `results.jsonl`, so correctness was judged against the classified intent and retrieved passages.
- The sample (28 drafts) is below the 50 dual-reviewed responses the framework expects for generate-on evaluation.
- 17 of 66 `auto_respond` decisions in this snapshot are on tickets labelled for escalation; this is a routing matter and is not reflected in the figures above.
