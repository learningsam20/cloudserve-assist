# Confidence threshold freeze

## Decision

| Field | Value |
|-------|-------|
| Operating threshold | **`CONFIDENCE_THRESHOLD=0.35`** |
| Freeze date | 2026-11-22 |
| Finding | D3 |
| Tune script | `python -m scripts.tune_threshold --input <development_tickets.json>` |
| Tune artefact | `storage/reports/threshold_tune.json` (local; `storage/` is gitignored) |
| Confidence used for routing | Intent `predict_proba` only (not `min(intent, urgency)`) |

**What “freeze” means:** The value `0.35` is the operating threshold used for all recorded evaluation runs. It is written to every routing decision as `threshold_applied`. Changing the operating threshold requires a logged PRD revision (Stage 5 revision log) and a new recorded evaluation; the previously published metrics remain tied to `0.35`.

**What was rejected:** Pack / Setup Guide `CONFIDENCE_THRESHOLD=0.80` is illustrative only (Project Brief). It is not the operating value.

## Why 0.35 (development sample, n=500)

| Threshold | First-contact proxy | Escalation | Auto precision | Role |
|-----------|---------------------|------------|----------------|------|
| **0.35** | **74.2%** | **25.8%** | **0.7574** | **Frozen operating point** |
| 0.80 (Pack) | 5.8% | 94.2% | 0.8966 | Illustrative only — not used |

Business targets (finding D1: FCR ≥60%, escalation ≤30%) select between the two rows. At 0.80 almost no tickets auto-respond on this classifier’s confidence distribution.

Re-confirmed 2026-11-22 after routing confidence was set to intent-only; the tune still recommended 0.35.

## Recorded evaluation under the freeze

Evidence under `CONFIDENCE_THRESHOLD=0.35`: [eval-runs.md](eval-runs.md) (80 validation tickets, 2026-11-22), including route-only `validation_fairness_fix` and generate-on `validation_20261122T131433Z` (LiteLLM → Groq, customer FCR 82.5%).
