# Demonstration video script — CloudServe Assistant (≤18 min)

**Status:** not recorded yet  
**Hard stop:** 18:00 · **Live system on screen:** ≥7:00  
**Numbers:** only from the [product report](../report/CloudServe_Assistant_Report.md), [eval-runs.md](../plan/eval-runs.md), recorded `metrics.json`, and [human_eval_appendix.md](../workbooks/human_eval_appendix.md)

Format for every beat:

- **[SHOW]** what is on screen  
- **[SAY]** spoken narration — product walkthrough voice; concrete and specific

---

## Demo fixtures

Fixtures are in `storage/demo_tickets/` (validation tickets prepared for the live section):

| File | Ticket | Expected outcome |
|------|--------|------------------|
| `ticket_auto.json` | VAL-0010 (billing) | `auto_respond` |
| `ticket_auto_generate.json` | VAL-0010 | `auto_respond` plus cited draft (optional) |
| `ticket_escalate.json` | VAL-0002 | `escalate` (policy must-not) |
| `ticket_auto_again.json` | VAL-0010 | `auto_respond` normally; `escalate` when kill switch is on |

| Reference numbers |
|-------------------|
| Threshold **0.35** · Chroma **59** chunks · Route-only / generate-on **66 auto / 14 escalate** · Generate-on **FCR 82.5%** (LiteLLM → Groq) · Fairness gap **0.0 pp** · **28** pytest tests |

**On camera / screen:** do not display `.env`, API keys, or billing pages.

---

## Opening visuals (0:00–1:15)

On camera for name and product (20–30 seconds), then screen share:

1. Report title — `docs/report/CloudServe_Assistant_Report.md`  
2. Pipeline diagram — [data-flow.md](../design/architecture/data-flow.md)  

Keep the terminal and Grafana closed until the live section.

---

## Prep

```bash
cd submission
./scripts/status.sh
./scripts/start_api.sh
# fixtures already at storage/demo_tickets/
```

Dry-run before recording: health → `ticket_auto` → `ticket_escalate` → kill on → `ticket_auto_again` → kill off → harness `--limit 5`.

---

## Script

### 0:00–1:15 · Open

**[SHOW]** Camera → report title → `data-flow.md` end-to-end pipeline  

**[SAY]**  
I'm Sameer. This is CloudServe Assistant.

CloudServe Solutions asked for a chatbot. After stakeholder interviews and the ticket data, that was the wrong product. A confident wrong reply is worse than a slow human one. CloudServe Assistant is a triage and assist service: it classifies a support ticket, retrieves passages from the reviewed knowledge base, and then — in code — either drafts a cited reply or escalates with a summary and sources.

I'll walk through the business problem, the design decisions, a live run of the API, and the recorded evaluation numbers. The generate-on validation batch reached 82.5% first-contact resolution through LiteLLM to Groq.

---

### 1:15–2:45 · Problem

**[SHOW]** Report Table 1 — stakeholder needs  

**[SAY]**  
Marcus Adeyemi runs support: roughly five hundred tickets a week, six agents. First reply averages eight to twelve hours against a two-hour service agreement. On the five-hundred-ticket development sample, historical first-contact resolution is 43.8% and escalation is 56.2%.

Sofia on Tier One needs the right article at hand instead of a private snippet file. Ines maintains twenty-nine reviewed knowledge-base articles that customers already use; agents rarely find them because search matches titles, not customer wording. Daniel on Tier Two needs escalations that show what was tried and which pages were considered. Ravi, as a customer, accepts an automated first reply when it is labelled, cites a page, and stays honest.

The pass bar we locked is finding D1: first-contact resolution at least 60%, mean reply under five minutes, satisfaction at least 4.0, escalation at most 30%.

---

### 2:45–4:15 · Discovery and findings

**[SHOW]** [findings.md](../plan/findings.md) — Discovery anchors table, then Pack findings D1–D5; for D3 switch to [threshold-freeze.md](../plan/threshold-freeze.md)  

**[SAY]**  
Every development figure comes from `scripts.discovery_stats` on the ticket JSON — channel, labels, and history fields — not from reading ticket bodies. On that sample of five hundred tickets: 71.4% are answerable from documentation; 17.4% are policy must-not and must never be auto-answered; historical first-contact resolution is 43.8%.

Five pack findings drove the build:

- D1 — One success bar. We evaluate against the Evaluation Framework table only: FCR at least 60%, reply under five minutes, CSAT at least 4.0, escalation at most 30%.
- D2 — Field name `doc_id`. Index metadata and citations always use `doc_id`. The Setup Guide sample that used `id` is wrong and would break citation resolution.
- D3 — Threshold freeze. The pack ships `CONFIDENCE_THRESHOLD=0.80` as an illustrative default. We tuned on the development set and froze the operating value at 0.35. At 0.80 the tune set auto-responds on 5.8% of tickets and escalates 94.2%. At 0.35 it auto-responds on 74.2% and escalates 25.8%, with auto precision 0.7574. Every recorded validation run used 0.35; each routing decision logs `threshold_applied`.
- D4 — Kill switch in flight. The switch is an environment flag or a flag file, re-read live. While it is on, the system never returns `auto_respond` — including tickets already past the route stage.
- D5 — Classification. GLiNER was dropped. Rules run first; then a supervised scikit-learn classifier. The language model only drafts cited answers on the auto-respond path. It never assigns intent or urgency.

---

### 4:15–5:30 · Architecture

**[SHOW]** [data-flow.md](../design/architecture/data-flow.md) — pipeline, then runtime topology, then routing flowchart (point with cursor)  

**[SAY]**  
Here is the pipeline on screen. A ticket enters ingest, then classify, then retrieve with MiniLM embeddings into Chroma — fifty-nine chunks from the twenty-nine articles. Routing is pure code. Only if the route is `auto_respond` does the system call LiteLLM. The recorded generate-on batch used Groq; OpenRouter remains a configuration option. Guardrails run on every draft. Every stage writes to the SQLite decision log.

Stack: Python, LangGraph, scikit-learn, Chroma, LiteLLM, FastAPI, SQLite. Prometheus and Grafana are optional for evaluation dashboards.

On the routing flowchart: kill switch first, then policy must-not, then empty retrieval, then confidence against the frozen 0.35, with a grounded override when the top passage is strong and confidence is near the threshold. The language model does not choose escalate versus auto — `src/route.py` does. FastAPI and the evaluation harness both call the same `run_ticket` entrypoint.

---

### 5:30–12:45 · Live demonstration (≥7 min)

**[SHOW]** Terminal in `submission/` (large font)  

**[SAY]**  
Live system next. Three tickets from the validation set. VAL-0010 should auto-respond. VAL-0002 should escalate on policy. Then I turn the kill switch on and send VAL-0010 again so the same success ticket is forced to escalate. I'll also show a guardrail block through the test suite, and a short harness run.

#### Health

**[SHOW]**

```bash
./scripts/start_api.sh
curl -s localhost:8000/health | python3 -m json.tool
```

**[SAY]**  
`/health` returns status ok, kill switch false, and Chroma count 59. The index is loaded.

#### Success path — VAL-0010

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_auto.json | python3 -m json.tool
```

**[SAY]**  
VAL-0010 — invoice higher than expected. Intent is billing, confidence is above 0.35, retrieved passages carry billing `doc_id` values, and the route is `auto_respond`.

*(Optional: repeat with `ticket_auto_generate.json` to show a live cited draft from Groq.)*

#### Policy escalate — VAL-0002

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_escalate.json | python3 -m json.tool
```

**[SAY]**  
VAL-0002 carries `must_not_auto_respond`. The action is `escalate`, with an escalation summary and the sources considered. That is policy, not a failed retrieve.

#### Guardrail

**[SHOW]**

```bash
python3 -m pytest tests/test_gaps_closure.py -k guardrail_block_through_run_ticket -v
```

**[SAY]**  
This test injects a generation with a forged citation through the full graph. The guardrail blocks it; the ticket does not leave as an auto-reply.

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
Kill switch is now on — `/health` shows it. I send VAL-0010 again, the same ticket that auto-responded earlier. The action is now `escalate`. Clearing the switch restores normal routing.

#### Short harness

**[SHOW]**

```bash
python3 -m evaluation.harness \
  --input datasets/validation_tickets.json \
  --output evaluation/results/demo_dryrun_limit5 \
  --no-generate --limit 5
```

**[SAY]**  
Unattended harness: `--input` and `--output` paths, five tickets, generation off. No silent drops. The full eighty-ticket results are already under `evaluation/results/`.

---

### 12:45–15:30 · Evaluation

**[SHOW]** [eval-runs.md](../plan/eval-runs.md) → `evaluation/results/validation_fairness_fix/metrics.md` → `evaluation/results/validation_20261122T131433Z/metrics.md`  
*(Optional: Grafana Generate-on FCR dashboard)*

**[SAY]**  
Evaluation history, starting with the first gate run. Retrieval was broken: the embedding model had fallen back silently, every similarity score fell below the floor, all eighty tickets escalated, auto-respond rate 0%. Escalating was the correct behaviour for empty evidence.

After the embedding fix and intent-only confidence: 65.0% auto-respond on validation, with a tier fairness gap near 35 percentage points on the raw mix.

After the fairness fix — character n-grams, grounded override, quality-based fairness metric — the route-only snapshot is 66 auto-respond, 14 escalate, all fourteen policy must-not. That is 82.5% route auto and 17.5% escalation. Classification accuracy is 98.75%. Fairness quality gap is 0.0 points for tier and for fluency. Generation was off, so that run does not claim customer first-contact resolution.

Generate-on batch, LiteLLM to Groq, same eighty tickets: again 66 and 14, customer FCR 82.5% with `fcr_claim_allowed` true, fairness gap still 0.0, citation ID validity 1.0 on 65 generations. Human review of twenty-eight drafts: satisfaction proxy 4.68, 119 of 119 claims supported.

---

### 15:30–16:45 · Governance

**[SHOW]** [risk-register.md](../governance/risk-register.md) or report section 9  

**[SAY]**  
Every automated decision is persisted in SQLite — classification, routing, and generation when it runs. The harness reconciles decision rows to tickets processed. The main operational risks are an unsafe auto-reply reaching a customer and a provider outage or rate limit. Containment starts with the kill switch we just exercised.

---

### 16:45–18:00 · Close

**[SHOW]** Report section 10.4 next steps → back on camera  

**[SAY]**  
Remaining work: tighten routing where tickets are labelled not answerable from documentation, run the hidden set when it is injected, and package the release after this recording.

CloudServe Assistant retrieves, routes in code, cites, or escalates with context. The recorded generate-on first-contact resolution is 82.5%. The product report, workbooks, and source are in the submission package.

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

If over time: shorten discovery first. Keep the live demonstration at or above seven minutes.

---

## Claims checklist

- [ ] Route-only 82.5% stated as automation rate; generate-on 82.5% stated as customer FCR (LiteLLM → Groq)  
- [ ] Named the 0% retrieve failure and the silent embedding fallback  
- [ ] Spoken mix: VAL-0010 auto · VAL-0002 policy escalate · kill forces VAL-0010 escalate  
- [ ] Optional generate vs guardrail test stated once  
- [ ] On-camera open and close; no secrets on screen  

---

## After recording

1. Save `FirstnameLastname_CloudServe_Demo.mp4` under `docs/video/`  
2. Mark [README.md](README.md) as RECORDED  
3. Package per root `instructions.md`
