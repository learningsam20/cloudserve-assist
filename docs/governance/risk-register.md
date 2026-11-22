# Risk register — CloudServe Assistant

Aligned to Capstone Governance Framework risk themes (R-01…R-08) with project IDs.

| ID | Framework theme | Risk | Likelihood | Impact | Mitigation | Owner |
|----|-----------------|------|------------|--------|------------|-------|
| R-01 | Unsafe auto-response | Hallucinated or uncited answer reaches customer | Med | High | Blocking citation + nonempty + grounding guards; escalate on empty retrieve | Builder |
| R-02 | Provider dependency | OpenRouter free-tier rate limit / outage / timeout during eval | High | Med | LiteLLM timeout + 429 backoff; disk cache; escalate on provider failure; harness does not abort batch (A11) | Builder |
| R-03 | Threshold / policy drift | Over-auto-respond from untuned threshold | Med | High | Measured freeze `CONFIDENCE_THRESHOLD=0.35` (D3); grounded override logged; decision log records threshold | Builder |
| R-04 | Privacy | PII / secrets in outbound draft | Low | High | Regex PII guard; governance scan in metrics report | Builder |
| R-05 | Control failure | Kill switch ignored mid-flight | Low | High | Live env re-read + file; re-check before and after generate (D4); `/health` exposes state | Ops |
| R-06 | Fairness | Quality gap across tier / fluency ≥5pp | Med | Med | Segment quality gap in harness governance; char TF-IDF + grounded override | Builder |
| R-07 | Eval integrity | Hidden-set leakage via hardcoded paths | Low | High | Harness requires `--input` / `--output` only | Assessor |
| R-08 | Stale knowledge / cost / latency | Docs drift; cost spikes; p95 latency under load | Med | Med | Rebuild Chroma from Pack docs; cache + Auto routing; escalate on slow/failed generate; monitor `/metrics` | Builder |

Project shorthand R1–R8 map 1:1 to R-01…R-08 above.
