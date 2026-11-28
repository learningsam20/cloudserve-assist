# CloudServe Assistant — Evaluation Metrics

- **Version:** 0.1.0
- **Run started:** 2026-11-22T13:14:38.654740+00:00
- **Report generated:** 2026-11-22T13:25:51.469130+00:00
- **Input:** `/Users/sameer_j/Documents/coding/fde/IIT_Capstone/submission/datasets/validation_tickets.json`
- **Targets source:** findings D1 success table + Evaluation Framework

## Volume

- Tickets input / processed: **80** / **80**
- Silent drops: **0**
- Action counts: `{'auto_respond': 66, 'escalate': 14}`
- Tickets with stage errors: **0**
- allow_generate: `True`

## Business outcomes (success table)

| Measure | Target | Achieved |
|---------|--------|----------|
| Route auto_respond rate | (informational) | 82.5% |
| First contact resolution | ≥60.0% | 82.5 |
| Escalation rate | ≤30.0% | 17.5% |
| Mean time to first reply | <5.0 min | 0.1402 min |
| CSAT proxy | ≥4.0 | None (Requires human rubric sample; not invented by harness (Evaluation Framework)) |

_FCR definition:_ auto_respond / total after generate+validate (customer-facing FCR proxy)
_FCR claim allowed:_ `True`

## Technical performance

- Classification labeled n: 80; overall accuracy: 0.9875
- Latency mean / p95 (s): 8.4096 / 19.2768
- Citation ID validity: {'valid_generations': 65, 'generations_with_citations': 65, 'rate': 1.0, 'note': 'Automated proxy: citation doc_ids ⊆ retrieved set'}
- Hallucination: Requires dual human review of ≥50 responses (Evaluation Framework); not auto-scored

## Governance conditions

- PII occurrences in outbound: **0** (pass=True)
- Decision rows written: **292** for 80 tickets
- Segment gaps: `{'customer_tier': {'metric': 'resolution_quality_on_expected_auto', 'quality_rate': {'business': 1.0, 'standard': 1.0, 'enterprise': 1.0}, 'quality_n': {'business': 21, 'standard': 21, 'enterprise': 6}, 'eligible_auto_rate': {'business': 1.0, 'standard': 1.0, 'enterprise': 1.0}, 'raw_auto_respond_rate': {'business': 0.9333, 'standard': 0.7381, 'enterprise': 0.875}, 'max_gap_pp': 0.0, 'requirement_pp': 5.0, 'pass': True}, 'language_fluency': {'metric': 'resolution_quality_on_expected_auto', 'quality_rate': {'fluent': 1.0, 'non_fluent': 1.0}, 'quality_n': {'fluent': 40, 'non_fluent': 8}, 'eligible_auto_rate': {'fluent': 1.0, 'non_fluent': 1.0}, 'raw_auto_respond_rate': {'fluent': 0.8197, 'non_fluent': 0.8421}, 'max_gap_pp': 0.0, 'requirement_pp': 5.0, 'pass': True}}`
- Calibration bands: `[{'band': '0.2-0.4', 'n': 7, 'mean_stated': 0.3175, 'observed_accuracy': 1.0, 'gap': -0.6825}, {'band': '0.4-0.6', 'n': 11, 'mean_stated': 0.5065, 'observed_accuracy': 1.0, 'gap': -0.4935}, {'band': '0.6-0.8', 'n': 46, 'mean_stated': 0.6913, 'observed_accuracy': 1.0, 'gap': -0.3087}, {'band': '0.8-1.0', 'n': 16, 'mean_stated': 0.9649, 'observed_accuracy': 0.9375, 'gap': 0.0274}]`

