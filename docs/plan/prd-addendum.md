# PRD addendum (non-PRD depth)

## Mechanism notes (for architecture, not FRs)

- Pipeline order: ingest → classify → retrieve → route → generate → validate → log (LangGraph `StateGraph`; same graph for API and harness).
- Cross-cutting: Prometheus metrics, decision log persistence, Guardrails, kill switch.
- Prompt injection: treat Ticket `body`/`subject` as untrusted data in delimited sections; never concatenate into the system instruction channel.
- Escalation is a successful outcome when confidence or grounding fails — not a harness failure.
- Provider choice (OpenRouter vs Groq) is an implementation swap behind one client interface.
- Citation fidelity: structured citation IDs checked in code against the retrieved set; fabricated IDs → block/escalate.
- Weak retrieval: escalate/abstain instead of drafting when top Passage score is below the measured relevance floor.
- Free-tier reality: OpenRouter `:free` ~20 RPM / ~50 req/day is too small for naive full-set live calls — response cache + few calls/ticket are mandatory for A9 under the pack’s free-tier rule.

## Pack inconsistencies to handle explicitly

| Topic | Variants in pack | Working stance |
|-------|------------------|----------------|
| Hidden set size | 100 vs 120 | Arbitrary N; same schema |
| Validation use | “freely” vs “once near end” | Tune on development; validation for checks; log run counts |
| FCR/CSAT targets | Client wish list vs success table | Report against success table; note both in report |

## Interview disagreements to settle with scripts (not hand-mining)

1. Share of tier-1-resolvable escalations (Daniel vs headline rate).
2. How repetitive volume is (Sofia ~70% vs Marcus lacking topic breakdown).
3. Docs quality vs findability (Sofia vs Ines framing).
4. Non-fluent CSAT gap (Sofia claim).
5. Flat SLA reporting vs urgency-dependent customer pain (Marcus vs Ravi).
