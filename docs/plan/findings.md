# Findings — reference datasets pack deviations and conflicts

Decisions taken where the reference datasets pack documents disagree or mislead. Source: pack text (Brief, Setup Guide, Dataset Guide, Evaluation Framework) and suggested config under `reference 06_Configuration/` (`.env.example`, `requirements.txt`). Used by the report, PRD revision log, and implementation.

**Config baseline:** Pack `06_Configuration` is the starting point for environment keys and dependencies. Additive pins and departures are recorded here and in the change log.

## Pack findings D1–D5 (summary)

- **D1 — One success bar.** Adopt the Evaluation Framework success table only: FCR ≥60%, reply under 5 minutes, CSAT ≥4.0, escalation ≤30%. The Brief’s stricter wish-list row is context, not the pass bar.
- **D2 — `doc_id`, never `id`.** Corpus metadata and citations always use `doc_id`. Setup Guide `doc["id"]` is a documentation error.
- **D3 — Measure, then freeze the threshold.** Pack `CONFIDENCE_THRESHOLD=0.80` is illustrative. Operating value measured on development data and frozen at **0.35** before recorded evaluation. Detail: [threshold-freeze.md](threshold-freeze.md).
- **D4 — Kill switch with defined in-flight behaviour.** Switch is env flag or file, re-read live, checked at route and around generation; while on, never `auto_respond`; in-flight drafts are discarded from the auto path and escalated.
- **D5 — No GLiNER; supervised classifier.** Rules first, then a trained local scikit-learn classifier. The LLM generates cited drafts only on `auto_respond`; it never labels intent or urgency.

## Settled choices

| Topic | Choice | Date |
|-------|--------|------|
| Product name | **CloudServe Assistant** | 2026-11-22 |
| Business success targets | **Success table:** FCR ≥60%, reply &lt;5 min, CSAT ≥4.0, escalation ≤30% (D1) | 2026-11-22 |
| Classification | Deterministic **rules first**, then **trained local sklearn classifier**; low conf → escalate (D5) | 2026-11-22 |
| Generation | **LiteLLM** → **OpenRouter or Groq** (provider from `LITELLM_MODEL` prefix; recorded generate-on used Groq) | 2026-11-22 |
| Routing | Deterministic code over confidence + frozen threshold **0.35** (D3) + kill switch (D4) | 2026-11-22 |
| Kill switch in-flight | See **D4** | 2026-11-22 |

---

## Discovery anchors (development sample, n=500)

These figures are not pack deviations. They are produced by `python -m scripts.discovery_stats` on `development_tickets.json` (labels and history aggregates only; no ticket-body inspection). The Stage 1 workbook and the product report use the same values.

| Measure | Figure | Implication for the product |
|---------|--------|------------------------------|
| Answerable from documentation | **71.4%** (357 of 500) | Automation opportunity is findability, not rewriting the KB |
| Not answerable from documentation | **28.6%** (143 of 500) | Always escalate; hand over context, do not invent answers |
| Policy `must_not_auto_respond` | **17.4%** (87 of 500) | Never auto-answer; ceiling on automation |
| Historical first-contact resolution | **43.8%** (219 of 500) | Baseline before the system (Marcus quotes 42%) |
| Historical escalation rate | **56.2%** (281 of 500) | Of which 49.1% of escalations were still answerable from docs |
| Mean historical satisfaction | **2.97** | Human-handled baseline vs target ≥4.0 |
| Documentation corpus | **29** articles (`doc_id`) | Closed reviewed corpus only |

---

## D1 — Duplicated / conflicting success criteria

**Where:** Project Brief has (at least) two target tables.

| Measure | Client / SLA-oriented row | Success / outcomes table (used) |
|---------|---------------------------|----------------------------------|
| FCR | 65%+ | **≥60%** |
| Time to first reply | under 2 hours (SLA language) | **&lt;5 minutes** |
| CSAT | 4.2 | **≥4.0** |
| Escalation | (implied via FCR) | **≤30%** |

**Deviation we adopt:** Report and evaluate against the **success / outcomes table** only. The stricter client wish-list row is context, not the pass bar.

**Why:** The success table includes explicit calculation definitions (Evaluation Framework / Brief). Holding two incompatible bars would make metrics and the PRD ambiguous.

**Risk if ignored:** Marking/report mismatch; chasing 65% FCR or “under 2h” while the harness and Evaluation Framework speak in 60% / sub-5-minute terms.

---

## D2 — `doc_id` vs `id` in setup samples

**Where:** Dataset Guide and JSON schema use field **`doc_id`**. Setup Guide sample code refers to `doc["id"]` when loading the corpus into Chroma.

**Deviation we adopt:** Always read and store **`doc_id`**. Treat Setup Guide `id` as a documentation error.

**Why:** Schema and all ticket `expected_doc_ids` / ground-truth links use `doc_id`. Using `id` breaks indexing and citation resolution (A4/A6).

**Risk if ignored:** Empty or wrong metadata in the vector store; citations that cannot resolve.

---

## D3 — Confidence threshold: illustrative pack default vs measured freeze

**Where:**

- Pack `.env.example` / Setup Guide ship `CONFIDENCE_THRESHOLD=0.80`.
- Project Brief states 0.80 is **illustrative**; the operating threshold must be **determined from data**.
- Routing must be deterministic once set (A5).

**Deviation we adopt:**

1. Pack `0.80` is illustrative only; it is not the operating value.
2. Measure the operating threshold on development data via `scripts/tune_threshold.py`.
3. Freeze that value before the recorded evaluation run.
4. Log `threshold_applied` on every routing decision.

**Freeze record**

| Item | Value |
|------|-------|
| Operating threshold | **0.35** |
| Freeze date | 2026-11-22 |
| Tune set | `development_tickets.json` (n=500) |
| At 0.35 | FCR proxy 74.2%; escalation 25.8%; auto precision 0.7574 |
| At pack 0.80 | FCR proxy 5.8%; escalation 94.2%; auto precision 0.8966 |
| Routing confidence | Intent `predict_proba` only |
| Full note | [threshold-freeze.md](threshold-freeze.md) |
| Evaluation under freeze | [eval-runs.md](eval-runs.md) |

**Change control:** Subsequent changes to the operating threshold require a logged PRD revision and a new recorded evaluation. Metrics published under `0.35` remain tied to that freeze.

**Why:** Shipping 0.80 without measurement contradicts the Brief. An unlogged post-evaluation threshold change invalidates reported metrics.

**Risk if ignored:** Untuned routing (over-auto-respond or over-escalate); non-reproducible A5 if the environment drifts between runs.

---

## D4 — Kill switch: what the question meant, and what we decided

**The open question was not “do we need a kill switch?”** (CloudServe already requires one.) It was: **when the switch flips while work is already running, what happens to tickets mid-flight?**

Concrete cases:

| Situation | Options people confuse |
|-----------|------------------------|
| Ticket already past route, LLM generating | Abort HTTP call vs let it finish but don’t auto-send |
| Tickets still queued in harness | Stop process vs continue escalate-only |
| API request in progress | 500 vs return escalate payload |
| How fast must it take effect? | Next ticket vs next second vs redeploy |

**Decision we adopt:**

1. Kill switch is on when `KILL_SWITCH=true` **or** `KILL_SWITCH_FILE` exists (env re-read live — not only cached Settings).
2. Checked at **route** and again **before and after generate** for every Ticket (API and harness).
3. While on: **never** `auto_respond`.
4. If generate is already in flight when the switch flips: allow the call to finish (or time out normally), but **do not send** as auto — force **escalate** (draft discarded from auto path).
5. Harness **continues** remaining tickets under escalate-only (no crash, no silent drop) — satisfies A9/A11 spirit.
6. Effectivity: **next route / mid-flight re-check** after the flag/file changes; no redeploy (AD-7).

**Why:** Aborting in-flight HTTPS mid-body is flaky; continuing the batch keeps the gate green; escalate-not-send matches Marcus’s “wrong answer worse than silence.”

---

## D5 — Classification approach (GLiNER dropped)

**Earlier plan:** rules + GLiNER zero-shot.

**Adopted:** rules + **supervised local classifier** trained on development ticket labels (`scripts/train_classifier.py`, sklearn already in `06_Configuration/requirements.txt`). Persist with joblib under `CLASSIFIER_DIR`.

**LLM role:** generate cited answers only when route is `auto_respond` (LiteLLM → OpenRouter or Groq). If the classifier cannot meet the frozen confidence threshold → **escalate**; the LLM is not used for labelling.

---

## Related pack inconsistencies (tracked, not separate product deviations)

| ID | Issue | Working stance |
|----|-------|----------------|
| R1 | Hidden set size stated as 100 in some places, 120 in others | Design for arbitrary N; same schema |
| R2 | Validation set “use freely” vs Brief “run once near the end” | Tune on development; validation for self-check; record run counts |
| R3 | Setup Guide category count wording vs listed category names | Use Dataset Guide / data enums via scripts |

---

## Change control

When implementation discovers another pack contradiction, append a new `D#` here (builder change log stays outside this repository).
