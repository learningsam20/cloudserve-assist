# Demonstration video script — CloudServe Assistant (≤18 min)

**Status:** not recorded yet  
**Hard stop:** 18:00 · **Live system on screen:** ≥7:00  
**Numbers:** only from the [product report](../report/CloudServe_Assistant_Report.md), [eval-runs.md](../plan/eval-runs.md), recorded `metrics.json`, and [human_eval_appendix.md](../workbooks/human_eval_appendix.md)

Format for every beat:

- **[SHOW]** what is on screen  
- **[SAY]** spoken narration (documentary register; third person about the product where natural)

---

## Demo fixtures

Fixtures are in `storage/demo_tickets/` — a deliberate mix from the validation set:

| File | Ticket | Expected outcome |
|------|--------|------------------|
| `ticket_auto.json` | VAL-0010 (billing) | `auto_respond` |
| `ticket_auto_generate.json` | VAL-0010 | auto + cited draft (optional live generate) |
| `ticket_escalate.json` | VAL-0002 | `escalate` (policy must-not) |
| `ticket_auto_again.json` | VAL-0010 | auto normally; escalate when kill switch is on |

| Cue card |
|----------|
| threshold **0.35** · Chroma **59** · **66 / 14** · generate-on **FCR 82.5%** (LiteLLM → Groq) · fairness **0 pp** · **28** tests |

**Never show:** `.env`, API keys, billing pages.

---

## Opening visuals (0:00–~1:15)

Start on camera briefly (name and product). Then screen:

1. Report title (`docs/report/CloudServe_Assistant_Report.md`)  
2. [data-flow.md](../design/architecture/data-flow.md) — end-to-end pipeline mermaid  

Do not open the terminal or Grafana in the first minute.

---

## Prep

```bash
cd submission
./scripts/status.sh
./scripts/start_api.sh
# fixtures already at storage/demo_tickets/
```

Day-of dry-run: health → `ticket_auto` → `ticket_escalate` → kill on → `ticket_auto_again` → kill off → harness `--limit 5`.

---

## Script

### 0:00–1:15 · Open

**[SHOW]** Camera → report title → `data-flow.md` pipeline  

**[SAY]**  
This is CloudServe Assistant — a support triage and assist system for CloudServe Solutions. The original ask was a chatbot. Discovery with support stakeholders and the ticket aggregates pointed elsewhere: wrong answers are worse than a slow human reply. The product classifies each ticket, retrieves reviewed knowledge-base passages, and decides in code whether to draft a cited reply or escalate with context.

The demonstration covers the problem, the architecture, a live run of at least seven minutes, and the recorded evaluation — including a generate-on first-contact resolution of 82.5% via LiteLLM to Groq.

---

### 1:15–2:45 · Problem

**[SHOW]** Report stakeholder table (section 1)  

**[SAY]**  
Marcus Adeyemi leads support — about five hundred tickets a week with six agents. First reply averages eight to twelve hours against a two-hour agreement. Historical first-contact resolution on the development sample is 43.8%; escalation is 56.2%.

Sofia on Tier One needs findable documentation instead of private snippet files. Ines maintains twenty-nine reviewed articles that customers use and agents largely do not. Daniel on Tier Two wants escalations that show sources and uncertainty. Ravi, as a customer, accepts automation when it is labelled, cited and honest.

The locked success bar is first-contact resolution at least 60%, reply under five minutes, satisfaction at least 4.0, and escalation at most 30%.

---

### 2:45–4:15 · Discovery and findings

**[SHOW]** [findings.md](../plan/findings.md) and/or [threshold-freeze.md](../plan/threshold-freeze.md)  

**[SAY]**  
Discovery figures come from scripts on the ticket JSON — not from reading ticket bodies by hand. About 71% of tickets are answerable from documentation; about 17% must not be auto-answered.

Five findings shaped the build: use `doc_id` for citations; freeze confidence at 0.35 because the pack’s 0.80 is illustrative and would automate almost nothing; define kill-switch behaviour for in-flight work; and keep the language model for drafting only. Classification is rules first, then a trained scikit-learn model.

---

### 4:15–5:30 · Architecture

**[SHOW]** [data-flow.md](../design/architecture/data-flow.md) — pipeline, topology, then routing flowchart  

**[SAY]**  
The path is ingest, classify, retrieve with MiniLM into Chroma, route in code, and — only on auto_respond — generate through LiteLLM to OpenRouter or Groq. The recorded generate-on batch used Groq. Guardrails follow; every decision is written to SQLite.

The stack is Python, LangGraph, scikit-learn, Chroma, LiteLLM, FastAPI and SQLite. Prometheus and Grafana are optional for the evaluation boards.

On the routing diagram: kill switch, then must-not policy, then empty retrieval, then confidence against 0.35, with a grounded override when retrieval is strong. The language model never chooses escalate versus auto — the code does. The API and the evaluation harness both call the same `run_ticket` entrypoint.

---

### 5:30–12:45 · Live demonstration (≥7 min)

**[SHOW]** Terminal in `submission/`  

**[SAY]**  
Three live beats. First, VAL-0010 — a billing ticket that should auto-respond. Second, VAL-0002 — a policy must-not that should escalate. Third, the kill switch on the same success ticket so the stop behaviour is visible. Optional: live generate on VAL-0010; otherwise a guardrail unit test shows a block.

#### Health

**[SHOW]**

```bash
./scripts/start_api.sh
curl -s localhost:8000/health | python3 -m json.tool
```

**[SAY]**  
Status ok, kill switch false, Chroma count 59 — the knowledge-base index is wired.

#### Success path — VAL-0010

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_auto.json | python3 -m json.tool
```

**[SAY]**  
Invoice higher than expected — billing intent, high confidence, billing `doc_id` passages, route auto_respond at threshold 0.35.

*(Optional generate: `ticket_auto_generate.json` — same ticket with a live cited draft.)*

#### Policy escalate — VAL-0002

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_escalate.json | python3 -m json.tool
```

**[SAY]**  
Must-not policy — escalate with an escalation summary for the agent. This is a genuine policy escalate, not a retrieval failure.

#### Guardrail

**[SHOW]**

```bash
python3 -m pytest tests/test_gaps_closure.py -k guardrail_block_through_run_ticket -v
```

**[SAY]**  
An engineered bad generation is blocked through the full graph.

#### Kill switch

**[SHOW]**

```bash
./scripts/kill_on.sh
curl -s localhost:8000/health | python3 -m json.tool
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_auto_again.json | python3 -m json.tool
./scripts/kill_off.sh
```

**[SAY]**  
Same VAL-0010 that auto-responded a moment ago. With the kill switch on, the ticket escalates. Kill off restores normal operation.

#### Short harness

**[SHOW]**

```bash
python3 -m evaluation.harness \
  --input datasets/validation_tickets.json \
  --output evaluation/results/demo_dryrun_limit5 \
  --no-generate --limit 5
```

**[SAY]**  
Path in, path out, five tickets, no silent drops. The full eighty-ticket metrics are already on disk.

---

### 12:45–15:30 · Evaluation

**[SHOW]** [eval-runs.md](../plan/eval-runs.md), then `evaluation/results/validation_fairness_fix/metrics.md`, then `validation_20261122T131433Z/metrics.md`  
*(Optional: Grafana → Generate-on FCR board)*

**[SAY]**  
First recorded run: retrieval broken — eighty escalations, zero percent auto. Empty passages after a silent embedding fallback; escalating was correct.

After the fix: about 65% auto, with a fairness tier gap of roughly 35 points.

Fairness-fix snapshot: 66 auto, 14 escalate, 82.5% route-auto, 17.5% escalation, classification 98.75%, fairness gap zero. Generate was off on that run, so the metrics withhold a customer FCR claim.

Generate-on with LiteLLM to Groq: same 66 and 14, customer FCR 82.5% with the claim allowed, fairness still zero, citation identifiers valid on 65 generations. Human review on twenty-eight drafts: satisfaction proxy 4.68, 119 of 119 claims supported.

---

### 15:30–16:45 · Governance

**[SHOW]** Risk register or report governance section  

**[SAY]**  
Every automated decision is written to the SQLite log — classify, route, and generate when used. The harness reconciles coverage. Principal risks are unsafe auto-replies and provider failures; containment begins with the kill switch demonstrated earlier.

---

### 16:45–18:00 · Close

**[SHOW]** Next-steps list from the report → camera  

**[SAY]**  
Next engineering priorities: tighten routing on tickets not answerable from documentation, run the hidden set when graders inject it, and complete packaging after this recording.

CloudServe Assistant is triage and assist — retrieve, route, cite, or escalate with context. The recorded generate-on first-contact resolution is 82.5%. Report, workbooks and source are in the submission package.

**[SHOW]** Hold · end  

---

## Timing

| Clock | Beat |
|-------|------|
| 0:00–1:15 | Open (camera → report → pipeline) |
| 1:15–2:45 | Problem |
| 2:45–4:15 | Discovery and findings |
| 4:15–5:30 | Architecture |
| **5:30–12:45** | **Live demonstration** |
| 12:45–15:30 | Evaluation |
| 15:30–16:45 | Governance |
| 16:45–18:00 | Close |

If over time: shorten discovery first. Do not cut the live demonstration below seven minutes.

---

## Claims checklist

- [ ] Route-only 82.5% = automation rate; generate-on 82.5% = customer FCR (LiteLLM → Groq)  
- [ ] Named the 0% retrieve failure  
- [ ] Spoken mix: VAL-0010 auto · VAL-0002 policy escalate · kill forces VAL-0010 escalate  
- [ ] Generate plan (live or route-only + guardrail test) stated once  
- [ ] On camera open and close; no secrets  

---

## After recording

1. Save `FirstnameLastname_CloudServe_Demo.mp4` under `docs/video/`  
2. Mark [README.md](README.md) RECORDED  
3. Package per root `instructions.md`
