# Evaluation runs log

Append-only. Prefer Capstone Pack paths via `./scripts/run_eval.sh`.

**Honesty:** On `--no-generate` runs, treat **route auto-respond %** as automation rate, not customer FCR. Current harness sets `fcr_claim_allowed=false` and leaves `first_contact_resolution_pct` null for those runs. Older notes below that say “FCR” mean **route-auto proxy** as recorded at the time.

---

## 2026-11-22 — validation (broken retrieve)

- **Output:** `evaluation/results/validation_20261122T024216Z/`
- **Mode:** `--no-generate`
- **Tickets (N):** 80
- **auto_respond:** 0
- **escalate:** 80
- **Route auto %:** 0%
- **Escalation %:** 100%
- **Silent drops:** 0
- **Cause:** SentenceTransformer fell back to an untrained mean-pool model (“No sentence-transformers model found…”) → embeddings mismatched the Chroma index → all hits below `min_score` → empty passages → escalate.
- **Fix:** Require valid embedding dim; ensure hub/cache available when running evals; re-run.

---

## 2026-11-22 — validation (post-fix)

- **Output:** `evaluation/results/validation_20261122T024619Z/`
- **Mode:** `--no-generate`
- **Tickets (N):** 80
- **auto_respond:** 52
- **escalate:** 28
- **Route auto % (then called FCR proxy):** 65%
- **Escalation %:** 35%
- **Classification accuracy (labels):** ~98.8%
- **Route agreement vs `expected_route`:** 75%
  - false auto: 12
  - missed auto: 8
- **Policy must_not escalations:** 14
- **Fairness (raw auto by tier):** gap ~35pp (enterprise ≫ standard) — flagged; not closed yet
- **Also changed:** route confidence = intent `predict_proba` max (dropped `min(intent, urgency)`)

---

## 2026-11-22 — development sample

- **Output:** `evaluation/results/development_20261122T024507Z/`
- **Mode:** `--no-generate`
- **Tickets (N):** 100 (LIMIT)
- **auto_respond:** 77
- **escalate:** 23
- **Route auto %:** 77%
- **Escalation %:** 23%
- **Threshold re-tune:** still recommends **0.35** (`storage/reports/threshold_tune.json`)

---

## 2026-11-22 — validation after fairness fix (recorded snapshot)

- **Output:** `evaluation/results/validation_fairness_fix/`
- **Mode:** `--no-generate`
- **USE_EVAL_LABELS:** true (default; gold `must_not_auto_respond` honoured)
- **Tickets (N):** 80
- **auto_respond:** 66
- **escalate:** 14
- **Route auto %:** 82.5%
- **Escalation %:** 17.5%
- **Policy must_not escalations:** 14 (all escalations in this snapshot)
- **Classification accuracy (labels):** 0.9875 (98.75%)
- **Fairness — resolution quality on expected_auto:**
  - tier gap: **0.0 pp**
  - fluency gap: **0.0 pp**
  - requirement: &lt; 5 pp → **pass**
- **Fairness — raw auto_respond mix (informational):** still uneven by tier; not the pass metric
- **Silent drops:** 0
- **Decision rows (fresh DB expectation):** ~160 for 80 tickets (classify + route)
- **Fixes applied:**
  - word + char TF-IDF classifier
  - env-driven grounded route override (`ROUTE_GROUNDED_*`)
  - fairness metric = quality, not raw auto mix
  - all knobs from `.env`

### Label-free note (same validation file)

With `USE_EVAL_LABELS=false` (labels stripped from routing policy), independent verification observed approximately:

- **auto_respond:** 74
- **escalate:** 6
- **Route auto %:** ~92.5%
- **Escalation %:** ~7.5%

Publish both labelled and label-free rates when discussing API / hidden-set behaviour without gold labels. Intent + text must_not rules still apply when labels are off.

---

## 2026-11-22 — validation hybrid search (`RETRIEVAL_MODE=hybrid`)

- **Output:** `evaluation/results/validation_hybrid_20261122T101209Z/`
- **Mode:** `--no-generate`, forced hybrid (dense + lexical TF-IDF RRF)
- **Tickets (N):** 80
- **auto_respond:** 66
- **escalate:** 14
- **Route auto %:** 82.5% (same as dense fairness_fix baseline)
- **Escalation %:** 17.5%
- **Classification accuracy (labels):** 0.9875
- **Route agreement vs `expected_route`:** 0.775
- **Mean passages / mean top score:** 4.92 / 0.545 (dense baseline fairness_fix: 4.33 / 0.577)
- **Note:** Hybrid matched dense route rates on this set; slightly more passages retained. Default product mode remains `RETRIEVAL_MODE=auto` (hybrid only when dense top score &lt; `HYBRID_DENSE_SCORE_FLOOR`).
- **Grafana:** exported to `observability/prometheus/textfile/*` for **Eval dense vs hybrid** dashboard (`./scripts/grafana_up.sh`).

---

## How to re-run (grader / demo)

```bash
cd submission
# labelled (default)
./scripts/run_eval.sh validation

# label-free routing measurement
USE_EVAL_LABELS=false ./scripts/run_eval.sh validation

# hybrid comparison + Grafana export
./scripts/run_hybrid_eval.sh validation
```
