# Demonstration video script — CloudServe Assistant (≤18 min)

**Status:** not recorded yet  
**Hard stop:** 18:00 · **Live system on screen:** ≥7:00  
**Numbers:** only from the [product report](../report/CloudServe_Assistant_Report.md), [eval-runs.md](../plan/eval-runs.md), recorded `metrics.json`, and [human_eval_appendix.md](../workbooks/human_eval_appendix.md)

Format for every beat:

- **[SHOW]** what is on screen (director notes — not spoken)  
- **[SAY]** full spoken lines — read aloud as written

---

## Demo fixtures

Fixtures are in `storage/demo_tickets/`:

| File | Ticket | Expected outcome |
|------|--------|------------------|
| `ticket_auto.json` | VAL-0010 (billing) | `auto_respond` |
| `ticket_auto_generate.json` | VAL-0010 | `auto_respond` plus cited draft |
| `ticket_escalate.json` | VAL-0002 | `escalate` (policy must-not) |
| `ticket_auto_again.json` | VAL-0010 | `auto_respond` normally; `escalate` when kill switch is on |

| Reference numbers |
|-------------------|
| Threshold **0.35** · Chroma **59** chunks · **66 auto / 14 escalate** · Generate-on **FCR 82.5%** (LiteLLM → Groq) · Fairness gap **0.0 pp** · **28** pytest tests |

Do not display `.env`, API keys, or billing pages on camera or on screen share.

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
```

Dry-run before recording: health → `ticket_auto` → `ticket_escalate` → kill on → `ticket_auto_again` → kill off → harness `--limit 5`.

---

## Script

### 0:00–1:15 · Open

**[SHOW]** Camera → report title → `data-flow.md` end-to-end pipeline  

**[SAY]**  
Hello — I'm Sameer, and this is CloudServe Assistant.

CloudServe Solutions originally asked for a chatbot. After talking with the support team and looking at the ticket data, that turned out to be the wrong product. A confident wrong answer is worse than a slow human reply. So we built a triage and assist service instead. CloudServe Assistant takes a support ticket, classifies it, retrieves passages from the reviewed knowledge base, and then decides in plain code whether to draft a cited reply or escalate with a summary and sources for an agent.

In this walkthrough I'll cover the business problem, the design decisions we locked, a live run of the API, and the evaluation results we recorded. On the generate-on validation batch — LiteLLM through Groq — first-contact resolution came in at 82.5 percent.

---

### 1:15–2:45 · Problem

**[SHOW]** Report Table 1 — stakeholder needs  

**[SAY]**  
Marcus Adeyemi leads support at CloudServe. His team handles about five hundred tickets a week with six agents. First reply averages eight to twelve hours, against a two-hour service agreement. On our five-hundred-ticket development sample, historical first-contact resolution is 43.8 percent, and escalation is 56.2 percent.

Sofia on Tier One wants the right article in front of her — not a private snippet file she has to maintain herself. Ines maintains twenty-nine reviewed knowledge-base articles. Customers already use them; agents mostly don't, because internal search matches titles rather than how customers actually write. Daniel on Tier Two wants escalations that show what was tried and which pages were considered, not a bare forward. And Ravi, speaking as a customer, will accept an automated first reply if it is clearly labelled, cites a page, and stays honest when it doesn't know.

The success bar we locked — finding D1 — is first-contact resolution of at least 60 percent, mean reply under five minutes, satisfaction of at least 4.0, and escalation of at most 30 percent.

---

### 2:45–4:15 · Discovery and findings

**[SHOW]** [findings.md](../plan/findings.md) — Discovery anchors, then Pack findings D1–D5; for D3 open [threshold-freeze.md](../plan/threshold-freeze.md)  

**[SAY]**  
We never read ticket bodies by hand for planning. Every development figure comes from a script — discovery_stats — which only looks at labels and history fields on the ticket JSON. On that five-hundred-ticket sample, 71.4 percent are answerable from documentation. 17.4 percent are policy must-not and must never be auto-answered. Historical first-contact resolution is 43.8 percent.

Five pack findings shaped what we built.

Finding D1: there are two conflicting success tables in the brief. We evaluate against one bar only — the Evaluation Framework table I just named.

Finding D2: the knowledge-base field is doc_id, not id. The Setup Guide sample used id, which would break citations. Everywhere in our index and replies, we use doc_id.

Finding D3 is the threshold freeze. The pack ships a confidence threshold of 0.80 and calls it illustrative. We measured on the development set and froze the operating value at 0.35. At 0.80, the tune set would auto-respond on only 5.8 percent of tickets and escalate 94.2 percent. At 0.35, it auto-responds on 74.2 percent and escalates 25.8 percent, with auto precision of 0.7574. Every recorded validation run used 0.35, and every routing decision logs threshold_applied so the freeze is auditable.

Finding D4: the kill switch is live. It is an environment flag or a flag file, re-read on every ticket. While it is on, the system never returns auto_respond — including work that is already mid-flight.

Finding D5: we dropped GLiNER. Classification is rules first, then a supervised scikit-learn model. The language model only drafts cited answers when the route is already auto_respond. It never labels intent or urgency.

---

### 4:15–5:30 · Architecture

**[SHOW]** [data-flow.md](../design/architecture/data-flow.md) — pipeline, runtime topology, routing flowchart  

**[SAY]**  
This is the end-to-end pipeline. A ticket comes in through ingest, then classify, then retrieve. Retrieval uses MiniLM embeddings into Chroma — fifty-nine chunks from those twenty-nine articles. Routing is deterministic code. Only when the route is auto_respond do we call LiteLLM. The generate-on batch we recorded used Groq; OpenRouter is still available by configuration. Every draft goes through guardrails, and every stage writes to a SQLite decision log.

The stack is Python, LangGraph, scikit-learn, Chroma, LiteLLM, FastAPI, and SQLite. Prometheus and Grafana show live API metrics and the evaluation boards.

On the routing flowchart, the order matters. Kill switch first. Then policy must-not. Then empty retrieval. Then confidence against the frozen 0.35. If confidence is a little low but the top passage is strong, a grounded override can still allow auto_respond. The language model never chooses escalate versus auto — route.py does. Both the FastAPI service and the evaluation harness call the same run_ticket entrypoint, so what you measure is what the API does.

---

### 5:30–12:45 · Live demonstration (≥7 min)

**[SHOW]** Terminal in `submission/` (large font)  

**[SAY]**  
I'm going to switch to the live API now and process real validation tickets.

First I'll send VAL-0010 — a billing ticket that should auto-respond. Then VAL-0002, which is marked must-not and should escalate on policy. After that I'll turn the kill switch on and send VAL-0010 again, so you can see the same success ticket forced to escalate. I'll also run a guardrail test that blocks a forged citation, and finish with a short unattended harness run.

#### Health

**[SHOW]**

```bash
./scripts/start_api.sh
curl -s localhost:8000/health | python3 -m json.tool
```

**[SAY]**  
Here's the health endpoint. Status is ok, the kill switch is off, and Chroma reports fifty-nine chunks — so the knowledge-base index is loaded and ready.

#### Success path — VAL-0010

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_auto.json | python3 -m json.tool
```

**[SAY]**  
This is VAL-0010 — a customer saying their invoice looks higher than expected. The classifier labels it as billing with confidence above our frozen threshold of 0.35. Retrieval returns billing passages with real doc_id values, and the route is auto_respond. So the happy path works — this is not a demo that only shows escalations.

*(If showing live generate: use `ticket_auto_generate.json` and say: "Same ticket with generation on — here is the cited draft from Groq.")*

#### Policy escalate — VAL-0002

**[SHOW]**

```bash
curl -s -X POST localhost:8000/tickets/process \
  -H 'content-type: application/json' \
  -d @storage/demo_tickets/ticket_escalate.json | python3 -m json.tool
```

**[SAY]**  
VAL-0002 is different. It carries the must_not_auto_respond label, so the system escalates on policy. You get an escalation summary and the sources that were considered. That is intentional policy handling — not a retrieval failure.

#### Guardrail

**[SHOW]**

```bash
python3 -m pytest tests/test_gaps_closure.py -k guardrail_block_through_run_ticket -v
```

**[SAY]**  
This test pushes a bad generation through the full graph — a forged citation that is not in the retrieved set. The guardrail blocks it, and the ticket never leaves as an auto-reply.

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
I've turned the kill switch on — health now shows it active. I'm sending VAL-0010 again, the same billing ticket that auto-responded a moment ago. This time the action is escalate. The ticket didn't change; we stopped automatic answering. Clearing the switch puts the system back to normal.

#### Short harness

**[SHOW]**

```bash
python3 -m evaluation.harness \
  --input datasets/validation_tickets.json \
  --output evaluation/results/demo_dryrun_limit5 \
  --no-generate --limit 5
```

**[SAY]**  
This is the unattended harness. You pass an input path and an output path. I'm running five tickets with generation off — no silent drops. The full eighty-ticket validation results are already on disk under evaluation/results, which I'll open next.

---

### 12:45–15:30 · Evaluation

**[SHOW]** [eval-runs.md](../plan/eval-runs.md) → `validation_fairness_fix/metrics.md` → `validation_20261122T131433Z/metrics.md`  
*(If Grafana is up: Generate-on FCR dashboard)*

**[SAY]**  
Here is the evaluation history.

The first gate run failed completely. The embedding model had fallen back silently to an untrained pooler, so every similarity score dropped below the floor, retrieval returned nothing, and all eighty tickets escalated — zero percent auto-respond. For empty evidence, escalating was the right behaviour.

After we fixed the embedder and switched routing confidence to intent only, validation sat at 65.0 percent auto-respond, but the raw fairness gap across customer tiers was about thirty-five percentage points.

Then we retrained with character n-grams, added the grounded override, and measured fairness as resolution quality rather than raw mix. The route-only snapshot after that fix is sixty-six auto-respond and fourteen escalate — all fourteen are policy must-not. That is 82.5 percent route automation and 17.5 percent escalation. Classification accuracy is 98.75 percent. The fairness quality gap is 0.0 points for both tier and fluency. Generation was off on that run, so we do not call that figure customer first-contact resolution.

The generate-on batch used LiteLLM to Groq on the same eighty tickets. Again sixty-six and fourteen. Customer first-contact resolution is 82.5 percent with the claim allowed. Fairness stays at 0.0 points. Citation identifiers were valid on all sixty-five generations that carried citations. On the human review of twenty-eight drafts, the satisfaction proxy is 4.68, and 119 of 119 claims were supported by the cited passages.

---

### 15:30–16:45 · Governance

**[SHOW]** [risk-register.md](../governance/risk-register.md) or report section 9  

**[SAY]**  
Every automated decision is written to SQLite — classification, routing, and generation when generation runs. The harness checks that every ticket has decision rows. The risks we care about most are an unsafe auto-reply reaching a customer, and a provider outage or rate limit. When something goes wrong, containment starts with the kill switch we just demonstrated.

---

### 16:45–18:00 · Close

**[SHOW]** Report section 10.4 → back on camera  

**[SAY]**  
What remains is engineering follow-up: tighten routing on tickets that are not answerable from the documentation, run the hidden set when graders inject it, and package the release after this recording.

CloudServe Assistant is triage and assist — retrieve, route in code, cite a real page, or escalate with context. The recorded generate-on first-contact resolution is 82.5 percent. The product report, the workbooks, and the source are in the submission package.

Thank you.

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
- [ ] Live generate or guardrail test stated once  
- [ ] On-camera open and close; no secrets on screen  

---

## After recording

1. Save `FirstnameLastname_CloudServe_Demo.mp4` under `docs/video/`  
2. Mark [README.md](README.md) as RECORDED  
3. Package per root `instructions.md`
