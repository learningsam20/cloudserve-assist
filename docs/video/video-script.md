# Demonstration video script — CloudServe Assistant (**≤18 minutes**)

**Status:** detailed shooting script; recording not yet made.  
**Target length:** **18:00** maximum (Pack: ~20 ±2; this cut uses the extra time for **architecture diagrams + evaluation walkthrough** while staying under 18).  
**Live demo floor:** **≥7 minutes** of the system actually running (Submission Guide).  
**Pace:** ~130–140 words/minute; leave silence while commands run.  
**Rule:** every number must already exist in the report, `eval-runs.md`, `threshold-freeze.md`, `metrics.json`, or `human-eval-notes.md`.

---

## A. Day-before prep (~60 minutes)

### A1. Environment

```bash
cd submission
source .venv/bin/activate
# CAPSTONE_DATASETS = absolute path to Capstone_Pack/05_Datasets
./scripts/setup_all.sh
./scripts/status.sh
./scripts/run_tests.sh          # 28 passed
./scripts/run_eval.sh validation  # refresh familiarity with metrics.md
```

### A2. Demo ticket JSON files

```bash
python <<'PY'
import json, os
from pathlib import Path
ds = Path(os.environ["CAPSTONE_DATASETS"] if os.getenv("CAPSTONE_DATASETS") else "../capstone_guide/Capstone_Pack/05_Datasets")
rows = {t["ticket_id"]: t for t in json.loads((ds / "validation_tickets.json").read_text())}
out = Path("/tmp/cloudserve_demo"); out.mkdir(exist_ok=True)
Path(out/"ticket_auto.json").write_text(json.dumps({"ticket": rows["VAL-0010"], "allow_generate": False}, indent=2))
Path(out/"ticket_escalate.json").write_text(json.dumps({"ticket": rows["VAL-0002"], "allow_generate": False}, indent=2))
Path(out/"ticket_auto_again.json").write_text(json.dumps({"ticket": rows["VAL-0010"], "allow_generate": False}, indent=2))
print(out)
PY
```

| File | Ticket | Expect |
|------|--------|--------|
| `ticket_auto.json` | VAL-0010 | `auto_respond`, billing / DOC-BILL-* |
| `ticket_escalate.json` | VAL-0002 | `escalate`, must_not |
| `ticket_auto_again.json` | VAL-0010 | escalate when kill ON |

**Generation:** Plan **B** (route-only + pytest guardrail) is recommended on camera. Plan **A** = set `allow_generate: true` on VAL-0010 only if the key works.

### A3. Windows to keep open (switch with hotkeys)

1. Terminal (`submission/`, large font)  
2. `docs/design/architecture/data-flow.md` **or** report PDF (pipeline + routing figures)  
3. `docs/plan/eval-runs.md` + `evaluation/results/validation_fairness_fix/metrics.md`  
4. Optional: Postman with `docs/postman/CloudServe_Assistant.postman_collection.json` **or** stick to curl  
5. Cue card: 0.35 · 59 chunks · 66/14 · 82.5% route-auto · 0pp fairness · 28 tests · hidden=0 · simulated human eval  

### A4. Never show

`.env`, API keys, OpenRouter billing UI, secrets in history.

---

## B. Day-of (5 minutes)

- [ ] Kill OFF  
- [ ] Dry-run: health → VAL-0010 → VAL-0002 → kill → VAL-0010 → kill off → harness `--limit 5` → open metrics.md → stop  
- [ ] Timer set to **18:00**  
- [ ] Camera for open/close  

---

## C. Spoken script (18:00)

`[brackets]` = production cues, not spoken.

---

### 00:00–01:15 — On-camera open (1:15)

[ON CAMERA]

Hello — I'm Sameer. This is **CloudServe Assistant**, my Capstone project.

In the next **eighteen minutes** I will cover: the problem, discovery findings that changed the design, architecture and data flow **with diagrams on screen**, a **live demonstration of at least seven minutes**, a walkthrough of **evaluation runs and metrics**, governance, and what I would do next.

Framing: CloudServe asked for a **chatbot**. Evidence said that was wrong. This product is **triage and assist** — classify, retrieve real docs, route in code, then either draft a **cited** answer or escalate with context.

Gaps I will not hide: no full **live generate-on** eval batch recorded; **hidden set run count is zero**; the **82.5%** figure is a **route-level auto-respond rate**, not customer FCR; human-eval CSAT is on **simulated** drafts.

[SCREEN: report title → `data-flow.md` pipeline diagram]

---

### 01:15–02:45 — Problem and stakeholders (1:30)

[SCREEN: report §1 stakeholder table]

Marcus (Head of Support): ~**500** tickets/week, six agents, first response **8–12 hours** vs **2-hour** SLA; he cares most about **first-contact resolution**. Development history: FCR ~**43.8%**, escalation ~**56.2%**.

Sofia (Tier 1): repeats she could answer if she could **find the page** — private snippet files.  
Ines (writer): **29** KB articles under-used because search matches **titles**.  
Daniel (Tier 2): ~**half** of escalations look Tier-1-solvable; wants **context + sources**, not bare forwards.  
Ravi (customer): automation OK if **honest and cited**.

Targets locked (D1): FCR ≥**60%**, reply &lt;**5** min, CSAT ≥**4.0**, escalation ≤**30%**.

---

### 02:45–04:15 — Discovery and findings (1:30)

[SCREEN: findings D1–D5; threshold-freeze metrics]

Aggregates from `discovery_stats` — not hand-mined ticket bodies. About **71%** answerable from docs; about **17%** must_not.

- **D2:** always `doc_id`  
- **D3:** freeze threshold **0.35** (Pack 0.80 illustrative → ~**6%** auto on this model; 0.35 → ~**74%** auto / ~**26%** esc on development tune)  
- **D4:** kill switch mid-flight  
- **D5:** rules + sklearn; LLM only for generate  

---

### 04:15–05:30 — Architecture + diagrams (1:15)

[SCREEN: `docs/design/architecture/data-flow.md` — pipeline, then topology, then routing order. Spend time pointing.]

**Purpose on screen:** ingest → classify → retrieve → route → (generate) → guards → log.

**Stack:** Python 3.11 · LangGraph · sklearn · Chroma · LiteLLM/OpenRouter · FastAPI · SQLite · Prometheus.

**Routing order diagram:** kill → must_not → empty retrieve → confidence ≥ 0.35 → grounded override → else escalate.

**Key sentence:** the **model never decides the route; code does.** API and harness share `run_ticket`.

[Optional 10s: open `src/graph.py` node list]

---

### 05:30–12:45 — Live demonstration (7:15)

[SCREEN: terminal. State Plan B or A.]

Tickets from Capstone validation: **VAL-0010**, **VAL-0002**. I am using **[Plan B: allow_generate false + guardrail pytest / Plan A: live generate on VAL-0010]**.

#### 05:30–06:10 — Health (0:40)

```bash
./scripts/status.sh
./scripts/start_api.sh
curl -s localhost:8000/health | python -m json.tool
```

Point: `status: ok`, `kill_switch: false`, `chroma.count` **59**.

[Optional Postman:] Import collection → **Health** request — same JSON. Say: “Postman is optional; curl is the scripted path.”

#### 06:10–07:40 — Success VAL-0010 (1:30)

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @/tmp/cloudserve_demo/ticket_auto.json | python -m json.tool
```

Walk fields slowly:

1. `classification` — intent / confidence / alternatives  
2. `passages[]` — `doc_id`, score (expect billing docs)  
3. `route.action` = **auto_respond**, `threshold_applied` **0.35**  
4. Plan A only: `generation` + `guardrails`  

#### 07:40–08:50 — Escalate VAL-0002 (1:10)

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @/tmp/cloudserve_demo/ticket_escalate.json | python -m json.tool
```

Point: **escalate**, must_not reason, **`escalation_summary`**.

#### 08:50–09:50 — Guardrail block (1:00)

```bash
python -m pytest tests/test_gaps_closure.py -k guardrail_block_through_run_ticket -v
```

Engineered bad generation → **block**. Code path, not hoping the LLM misbehaves live.

#### 09:50–11:10 — Kill switch (1:20)

```bash
./scripts/kill_on.sh
curl -s localhost:8000/health | python -m json.tool
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @/tmp/cloudserve_demo/ticket_auto_again.json | python -m json.tool
./scripts/kill_off.sh
```

Same VAL-0010 now escalates. D4 mid-flight policy.

#### 11:10–12:45 — Unattended harness slice (1:35)

```bash
python -m evaluation.harness \
  --input "$CAPSTONE_DATASETS/validation_tickets.json" \
  --output /tmp/demo_harness_run \
  --no-generate \
  --limit 5
cat /tmp/demo_harness_run/run_summary.json
```

Injected `--input` / `--output`; silent drops **0**.

---

### 12:45–15:30 — Evaluation walkthrough (2:45)  ← extra time vs 15-min cut

[SCREEN: `docs/plan/eval-runs.md` first, then `validation_fairness_fix/metrics.md`]

I will walk the **eval log**, not invent new numbers.

**Run 1 — broken retrieve** (`validation_20261122T024216Z`):

- Tickets (N): **80**  
- auto_respond: **0**  
- escalate: **80**  
- Route auto %: **0%**  
- Cause: silent bad embeddings → empty retrieve → correct escalate  

**Run 2 — post-fix** (`…024619Z`):

- N: **80**  
- auto: **52**  
- escalate: **28**  
- Route auto %: **65%**  
- Fairness raw tier gap: ~**35 pp** (problem)  

**Run 3 — fairness fix (recorded)** (`validation_fairness_fix`):

- N: **80**  
- auto_respond: **66**  
- escalate: **14**  
- Route auto %: **82.5%**  
- Escalation %: **17.5%**  
- Classification accuracy: **98.75%**  
- Fairness quality gap (tier): **0.0 pp**  
- Fairness quality gap (fluency): **0.0 pp**  
- Silent drops: **0**  

[Point at metrics.md keys: `route_auto_respond_pct`, `fcr_claim_allowed: false`, `quality_across_segments`.]

Say clearly: **do not call 82.5% customer FCR** on a `--no-generate` run.

**Label-free note** (`USE_EVAL_LABELS=false`): independent check saw about **74 auto / 6 escalate** (~**92.5%** / ~**7.5%**). Gold must_not labels change the labelled snapshot — both numbers belong in the story.

**Human eval:** 28 simulated drafts · CSAT proxy **4.68** · **119/119** supported · **not** live LLM output.

**Hidden set:** **0** runs.

```bash
./scripts/stop_api.sh
```

---

### 15:30–16:45 — Governance (1:15)

[SCREEN: risk register + kill procedure]

Decision log: classification + routing (+ generate/validate when used). Harness reconcile. Risks **R-01…R-08** — highlight unsafe auto-response and provider/rate-limit. Incident step 1 = kill switch (already shown).

---

### 16:45–18:00 — Next steps + on-camera close (1:15)

[SCREEN: next steps 20s → ON CAMERA]

Next: live generate-on sample inside free tier; reduce auto on non-answerable tickets; dual review of **live** drafts; hidden set **once** without retuning; re-package zip with this video.

[ON CAMERA]

Limitations again: no full live generate-on batch; hidden set = 0; **82.5% is route-level**; human scores are **simulated**. What we showed: diagrams and stack, live retrieve/route/escalate/kill/harness, honest eval history including a **0%** failure, and governance that can stop the system.

Thank you. Report, workbooks, and source are in the package; README has setup and diagrams.

[Hold 2s. END.]

---

## D. Timing board (max 18:00)

| Clock | Section | Notes |
|-------|---------|--------|
| 0:00–1:15 | Open (camera) | Gaps named |
| 1:15–2:45 | Problem | Stakeholders |
| 2:45–4:15 | Discovery | D3 = 0.35 |
| 4:15–5:30 | Architecture + diagrams | data-flow.md |
| **5:30–12:45** | **Live demo** | **≥7:15** |
| **12:45–15:30** | **Eval walkthrough** | eval-runs + metrics.md |
| 15:30–16:45 | Governance | |
| 16:45–18:00 | Close (camera) | |

If over 18: shorten discovery quotes first; **never** cut demo below 7:00 or skip eval honesty.

---

## E. Claims checklist

- [ ] “Route auto-respond / route-level” for 82.5% — not customer FCR  
- [ ] Eval runs walked with metrics on separate lines / pointed on screen  
- [ ] Label-free ~74/6 mentioned  
- [ ] Human eval = simulated  
- [ ] Hidden set = 0  
- [ ] Diagrams shown (data-flow or report)  
- [ ] Plan A/B stated; tickets VAL-0010 / VAL-0002  
- [ ] On camera open + close  
- [ ] No secrets on screen  

---

## F. Postman vs curl

| Approach | Use when |
|----------|----------|
| **curl (default in this script)** | Reliable, matches README, easy to show in terminal |
| **Postman (optional)** | Import `docs/postman/CloudServe_Assistant.postman_collection.json`; paste full Pack bodies; good visual for `/health` and `/tickets/process` |

You do **not** need both. One successful path is enough. OpenAPI at `/docs` is a third option.

---

## G. After recording

1. Save `FirstnameLastname_Capstone_Video.mp4` (1080p) under `docs/video/`.  
2. Mark README status RECORDED.  
3. Follow root `instructions.md` package → zip steps.
