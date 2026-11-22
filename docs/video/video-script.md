# Demo video script — CloudServe Assistant (≤18 min)

**Status:** not recorded yet  
**Hard stop:** 18:00 · **Live system on screen:** ≥7:00  
**Numbers:** only from report / `eval-runs.md` / `metrics.json` / `human-eval-notes.md`

Format for every beat:

- **[SHOW]** what is on screen (nothing else)  
- **[SAY]** what you actually say (paraphrase if it feels stiff)

---

## Already done

Eval runs, tests, index, Grafana — already built. Demo fixtures are in `storage/demo_tickets/` — **not all escalate**; it’s a deliberate mix from the validation set:

| File | Ticket | What should happen | Why |
|------|--------|--------------------|-----|
| `ticket_auto.json` | VAL-0010 (invoice / billing) | **`auto_respond`** | Gold `expected_route=auto_respond`; dry-run hits DOC-BILL-* |
| `ticket_auto_generate.json` | VAL-0010 | **auto + draft** (Plan A) | Same ticket, `allow_generate: true` |
| `ticket_escalate.json` | VAL-0002 | **`escalate`** | Gold `must_not_auto_respond` — genuine policy escalate |
| `ticket_auto_again.json` | VAL-0010 again | **auto normally; escalate only if kill ON** | Same success ticket used to show the kill switch (D4), not a second must-not |

| Cue card (keep beside keyboard) |
|---------------------------------|
| threshold **0.35** · Chroma **59** · **66 / 14** · generate-on **FCR 82.5%** · fairness **0 pp** · **28** tests · hidden set **0** |

**Never show:** `.env`, keys, billing pages.

---

## Opening visuals (0:00–~1:15) — what to put on screen

Start **on camera** for ~20–30s (face + name). Then cut or share screen in this order — don’t linger on empty IDE:

1. **Report title page** (or `docs/report/…Report.md` H1) — 5s  
2. **`docs/design/architecture/data-flow.md`** — first mermaid (“End-to-end pipeline”) — stay here while you explain triage vs chatbot  
3. Optional: scroll to **routing** diagram later in the architecture section (4:15), not in the open  

Do **not** open terminal or Grafana in the first minute.

---

## Prep (short)

```bash
cd submission
./scripts/status.sh
./scripts/start_api.sh
# tickets already at storage/demo_tickets/
```

Day-of dry-run: health → `ticket_auto` → `ticket_escalate` → kill on → `ticket_auto_again` → kill off → harness `--limit 5`.

---

## Script

### 0:00–1:15 · Open

**[SHOW]** Camera → then report title → `data-flow.md` pipeline diagram  

**[SAY]**  
Hi — I’m Sameer. This is CloudServe Assistant.

CloudServe originally asked for a chatbot. After talking to support and looking at the ticket data, that didn’t fit. Wrong answers are worse than a slow human reply. So this is a triage and assist system: classify the ticket, pull real KB passages, decide in code whether to draft a cited reply or escalate with context.

I’ll show the problem, a few design choices, the architecture, a live run for about seven minutes, then the eval numbers — including a generate-on FCR of 82.5%. I’ll also say what I didn’t run: the hidden set is still zero, and the CSAT proxy is on simulated drafts.

---

### 1:15–2:45 · Problem

**[SHOW]** Report stakeholder table (section 1)  

**[SAY]**  
Marcus runs support — about 500 tickets a week, six agents. First reply is eight to twelve hours against a two-hour SLA. He cares most about first-contact resolution. In the development history, FCR was about 43.8% and escalation about 56.2%.

Sofia on Tier 1 said she could close more if she could find the right page — people keep private snippet files. Ines writes the KB: 29 articles that don’t get used because search mostly matches titles. Daniel on Tier 2 said about half the escalations look Tier-1 solvable; he wants context and sources, not a bare forward. Ravi, as a customer, is fine with automation if it’s honest and cited.

We locked the success bar to FCR at least 60%, reply under five minutes, CSAT at least 4.0, escalation at most 30%.

---

### 2:45–4:15 · Discovery

**[SHOW]** `docs/plan/findings.md` (D1–D5) and/or threshold-freeze note  

**[SAY]**  
Discovery numbers came from scripts on the ticket JSON — not me reading ticket bodies by hand. Roughly 71% look answerable from docs; about 17% must not auto-respond.

A few decisions that stuck: always use `doc_id` for citations; freeze confidence at 0.35 — the pack’s 0.80 was only illustrative and would have auto-answered almost nothing; kill switch has to work mid-flight; and the LLM is only for drafting, never for labelling or routing. Rules first, then a trained sklearn classifier.

---

### 4:15–5:30 · Architecture

**[SHOW]** `data-flow.md` — pipeline, then topology, then routing flowchart (point with cursor)  

**[SAY]**  
Here’s the path: ingest, classify, retrieve with MiniLM into Chroma, route in code, and only if we auto-respond do we call LiteLLM — Groq in the recorded generate-on run. Guardrails, then the decision log.

Stack is Python, LangGraph, sklearn, Chroma, LiteLLM, FastAPI, SQLite. Optional Prometheus and Grafana for the demo boards.

On the routing diagram: kill switch first, then must-not policy, then empty retrieval, then confidence against 0.35, with a grounded override if retrieval is strong. The language model never picks escalate vs auto — the code does. API and eval harness both call the same `run_ticket`.

---

### 5:30–12:45 · Live demo (≥7 min)

**[SHOW]** Terminal in `submission/` (large font). Say Plan B unless you deliberately use Plan A.

**[SAY]**  
Live demo — three beats, not “everything escalates.” First, VAL-0010, a real billing ticket that should auto-respond. Second, VAL-0002, a real must-not ticket that should escalate on policy. Third, I’ll turn the kill switch on and send VAL-0010 again so you see the same success ticket forced to escalate. Plan B for the curls — no generate — plus a guardrail unit test. If I have time, Plan A is the generate file for VAL-0010.

#### Health

**[SHOW]** Run:

```bash
./scripts/start_api.sh
curl -s localhost:8000/health | python3 -m json.tool
```

**[SAY]**  
Status ok, kill switch false, Chroma count 59 — that’s the KB index.

#### Success path — VAL-0010 (auto)

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_auto.json | python3 -m json.tool
```

**[SAY]**  
This is the happy path. Invoice higher than expected — classified as billing, confidence high. Passages are real billing `doc_id`s. Route is auto_respond at 0.35. So the demo isn’t only escalations.

*(Plan A optional: `ticket_auto_generate.json` — same ticket, live draft + citation ids.)*

#### Policy escalate — VAL-0002

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_escalate.json | python3 -m json.tool
```

**[SAY]**  
Different ticket. Gold label says must not auto-respond — so we escalate on policy, with an escalation summary for the agent. That’s a genuine must-not, not a failed retrieve.

#### Guardrail

**[SHOW]**

```bash
python3 -m pytest tests/test_gaps_closure.py -k guardrail_block_through_run_ticket -v
```

**[SAY]**  
This forces a bad generation in the test so we see a block — I’m not hoping the model messes up live.

#### Kill switch — same auto ticket, forced escalate

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
Same VAL-0010 that just auto-responded. Kill is on, so now it escalates — not because the ticket changed, because we flipped the stop switch. Kill off again so we’re back to normal.

#### Short harness

**[SHOW]**

```bash
python3 -m evaluation.harness \
  --input datasets/validation_tickets.json \
  --output evaluation/results/demo_dryrun_limit5 \
  --no-generate --limit 5
```

**[SAY]**  
Path in, path out, limit five, no silent drops. Full eighty is already on disk — I’ll open those metrics next.

---

### 12:45–15:30 · Eval walkthrough

**[SHOW]** `docs/plan/eval-runs.md`, then `evaluation/results/validation_fairness_fix/metrics.md`, then `validation_20261122T131433Z/metrics.md`  
*(Optional: Grafana → Generate-on FCR)*

**[SAY]**  
I’ll stick to the eval log.

First run: retrieve was broken — eighty tickets, all escalate, zero percent auto. Bad embeddings, empty passages — escalating was the right behaviour.

After the fix: about 65% auto, but fairness by tier looked awful — roughly a 35 point gap.

Then the fairness fix snapshot: 66 auto, 14 escalate, 82.5% route-auto, 17.5% escalation, classification about 98.75%, fairness gap zero. On that run generate was off, so 82.5% is automation rate, not customer FCR — `fcr_claim_allowed` is false.

Generate-on run with Groq: same 66 and 14, zero generate errors, customer FCR 82.5% with the claim flag true, fairness still zero, citation ids valid on the generations we checked.

Label-free routing without gold must-not labels was about 74 auto and 6 escalate. Human CSAT proxy 4.68 was on simulated drafts — useful for retrieval quality, not a live-model CSAT. Hidden set: still zero runs.

---

### 15:30–16:45 · Governance

**[SHOW]** Risk / kill-switch doc (or report governance section)  

**[SAY]**  
Every decision hits the SQLite log — classify, route, and generate when we use it. The harness checks coverage. Main risks are unsafe auto-replies and provider failures; first incident step is the kill switch we already flipped.

---

### 16:45–18:00 · Close

**[SHOW]** Brief next-steps list → back on camera  

**[SAY]**  
Next for me: spot-check live drafts with a second reviewer, cut autos on tickets that aren’t answerable from docs, and run the hidden set once without retuning.

To close: hidden set is zero; CSAT is still simulated. What you saw was the pipeline, live retrieve and route, escalate and kill, an honest zero-percent failure in the log, and a generate-on FCR of 82.5%. Report, workbooks, and source are in the package.

Thanks.

**[SHOW]** Hold 2s · end  

---

## Timing

| Clock | Beat |
|-------|------|
| 0:00–1:15 | Open (camera → report → pipeline diagram) |
| 1:15–2:45 | Problem |
| 2:45–4:15 | Discovery |
| 4:15–5:30 | Architecture diagrams |
| **5:30–12:45** | **Live demo** |
| 12:45–15:30 | Eval numbers |
| 15:30–16:45 | Governance |
| 16:45–18:00 | Close |

If you’re over time: shorten discovery first. Don’t cut the live demo under seven minutes.

---

## Claims checklist

- [ ] Route-only 82.5% = automation; generate-on 82.5% = customer FCR  
- [ ] Named the 0% retrieve failure  
- [ ] Hidden set = 0; human CSAT = simulated  
- [ ] Said the mix out loud: VAL-0010 auto · VAL-0002 policy escalate · kill forces VAL-0010 escalate  
- [ ] Plan A or B said out loud  
- [ ] On camera open + close; no secrets  

---

## After recording

1. Save `FirstnameLastname_CloudServe_Demo.mp4` under `docs/video/`  
2. Mark `docs/video/README.md` RECORDED  
3. Package per root `instructions.md`
