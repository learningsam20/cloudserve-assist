# Fairness method — CloudServe Assistant

## Goal

Keep automated resolution quality variation **under five percentage points** across customer segments (Evaluation Framework governance tier).

## Segments

Computed by the harness from ticket fields (no body dumps):

- `customer_tier` — enterprise / business / standard
- `language_fluency` — fluent / non_fluent (and any other labels present)

## Metric (primary)

**Resolution quality** on tickets with `labels.expected_route=auto_respond` and not `must_not_auto_respond`:

\[
\text{quality}(s) = \frac{\#\{\text{action}=\text{auto\_respond}\}}{\#\{\text{eligible expected-auto in } s\}}
\]

Pass if \(\max_s quality(s) - \min_s quality(s) &lt;\) `FAIRNESS_MAX_GAP_PP` (from `.env`, default 5).

Raw auto-respond mix is reported for transparency but is **not** the pass bar (policy `must_not` density differs by tier).

## Mitigations in system

- Word + char_wb TF-IDF classifier (robust to non_fluent wording)
- Env-driven grounded route override (`ROUTE_GROUNDED_MIN_SCORE`, `ROUTE_GROUNDED_CONF_FACTOR`) for strong retrieval + near-threshold confidence — **segment-blind**

## Where it appears

- `evaluation/metrics_report.py` → `governance.quality_across_segments`
- Latest pass: `docs/plan/eval-runs.md` (validation_fairness_fix)
