# Confidence threshold freeze

| Field | Value |
|-------|-------|
| Date | 2026-11-22 |
| Value | **0.35** |
| Script | `python -m scripts.tune_threshold --input <development_tickets.json>` |
| Full report | `storage/reports/threshold_tune.json` (local; `storage/` gitignored) |
| Findings | D3 |

## Development-set snapshot (n=500)

### Frozen operating point — threshold **0.35**

- **Route auto % (FCR proxy on tune set):** ~74%
- **Escalation %:** ~26%
- **Auto precision (vs expected_route where labelled):** ~0.76

### Pack illustrative — threshold **0.80** (not used)

- **Route auto %:** ~6%
- **Escalation %:** ~94%
- **Auto precision:** ~0.90

Re-confirmed 2026-11-22 after routing confidence = **intent only** (not `min(intent, urgency)`).

Business targets (findings D1) lead selection; pack 0.80 is not used as the operating value.

Recorded validation run: `docs/plan/eval-runs.md` (80 tickets, 2026-11-22). Do not change after that without a PRD revision.
