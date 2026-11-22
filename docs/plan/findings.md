# Findings — reference datasets pack deviations and conflicts

Decisions taken where the reference datasets pack documents disagree or mislead. Source: pack text (Brief, Setup Guide, Dataset Guide, Evaluation Framework) and suggested config under `reference 06_Configuration/` (`.env.example`, `requirements.txt`). Used by the report, PRD revision log, and implementation.

**Config baseline:** always start from `06_Configuration`; document additives here or in the change-log — do not silently replace pack keys.

## Settled choices

| Topic | Choice | Date |
|-------|--------|------|
| Product name | **CloudServe Assistant** | 2026-11-22 |
| Business success targets | **Success table:** FCR ≥60%, reply &lt;5 min, CSAT ≥4.0, escalation ≤30% | 2026-11-22 |
| Classification | Deterministic **rules first**, then **trained local sklearn classifier**; low conf → escalate (no LLM labelling) | 2026-11-22 |
| Generation | **LiteLLM** → **OpenRouter** (swappable via env) | 2026-11-22 |
| Routing | Deterministic code over Confidence + frozen Threshold + kill switch | 2026-11-22 |
| Kill switch in-flight | See **D4** | 2026-11-22 |

---

## D1 — Duplicated / conflicting success criteria

**Where:** Project Brief has (at least) two target tables.

| Measure | Client / SLA-oriented row | Success / outcomes table (used) |
|---------|---------------------------|----------------------------------|
| FCR | 65%+ | **≥60%** |
| Time to first reply | under 2 hours (SLA language) | **&lt;5 minutes** |
| CSAT | 4.2 | **≥4.0** |
| Escalation | (implied via FCR) | **≤30%** |

**Deviation we adopt:** Report and evaluate against the **success / outcomes table** only. The stricter client wish-list row is mentioned in the report as aspirational context, not as the pass bar.

**Why:** The success table includes explicit calculation definitions (Evaluation Framework / Brief). Holding two incompatible bars would make metrics and the PRD ambiguous.

**Risk if ignored:** Marking/report mismatch; chasing 65% FCR or “under 2h” while the harness and Evaluation Framework speak in 60% / sub-5-minute terms.

---

## D2 — `doc_id` vs `id` in setup samples

**Where:** Dataset Guide and JSON schema use field **`doc_id`**. Setup Guide sample code refers to `doc["id"]` when loading the corpus into Chroma.

**Deviation we adopt:** Always read and store **`doc_id`**. Treat Setup Guide `id` as a documentation error.

**Why:** Schema and all ticket `expected_doc_ids` / ground-truth links use `doc_id`. Using `id` breaks indexing and citation resolution (A4/A6).

**Risk if ignored:** Empty or wrong metadata in the vector store; citations that cannot resolve.

---

## D3 — Confidence threshold duplication / illustrative default

**Where:**

- `.env.example` / Setup Guide ship `CONFIDENCE_THRESHOLD=0.80`.
- Project Brief states the 0.80 figure is **illustrative**; the operating threshold must be **determined from data**.
- Routing must be deterministic once set (A5).

**Deviation we adopt:**

1. Pack `0.80` is illustrative only (Brief); not used as the operating value.
2. Measure the operating threshold on development data via `scripts/tune_threshold.py`.
3. **Freeze** that value before the recorded evaluation run; further changes require a logged PRD revision.
4. Decision log records `threshold_applied` on every routing decision so the frozen value is auditable.

**Freeze (2026-11-22):** `CONFIDENCE_THRESHOLD=0.35` on `development_tickets.json` (n=500). At 0.35: FCR proxy ~74%, escalation ~26%, auto precision ~0.76. Pack 0.80 yields ~6% FCR on this classifier’s confidence distribution. Evidence: `storage/reports/threshold_tune.json`. Routing confidence uses **intent** `predict_proba` (not `min(intent, urgency)`). Recorded validation: `docs/plan/eval-runs.md`.

**Why:** Blindly shipping 0.80 without measurement contradicts the Brief; changing the threshold after eval invalidates reported metrics.

**Risk if ignored:** Untuned routing (over-auto-respond or over-escalate); non-reproducible A5 if the env drifts between runs.

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

## Related pack inconsistencies (tracked, not separate product deviations)

| ID | Issue | Working stance |
|----|-------|----------------|
| R1 | Hidden set size stated as 100 in some places, 120 in others | Design for arbitrary N; same schema |
| R2 | Validation set “use freely” vs Brief “run once near the end” | Tune on development; validation for self-check; record run counts |
| R3 | Setup Guide category count wording vs listed category names | Use Dataset Guide / data enums via scripts |

---

## D5 — Classification approach (GLiNER dropped)

**Earlier plan:** rules + GLiNER zero-shot.

**Adopted:** rules + **supervised local classifier** trained on development ticket labels (`scripts/train_classifier.py`, sklearn already in `06_Configuration/requirements.txt`). Persist with joblib under `CLASSIFIER_DIR`.

**LLM role:** generate cited answers only when route is `auto_respond`. If the classifier cannot meet the frozen confidence threshold → **escalate**, do not ask OpenRouter to classify.

---

## Change control

When implementation discovers another pack contradiction, append a new `D#` here and mirror a line in `_bmad-output/change-log.md`.
