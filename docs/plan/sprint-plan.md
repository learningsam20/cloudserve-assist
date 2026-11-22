# Sprint plan — CloudServe Assistant

Aligned with delivery stage 4 and SPEC epics. Cadence: **2–3 weeks**. Owner: sameer_j (individual).

Story catalogue with Given/When/Then: `docs/plan/epics.md` (and Stage 4 workbook). This file is the **execution plan** plus a compact acceptance matrix.

## Capacity (illustrative)

| Week | Weekday hours | Weekend hours | Rough total |
|------|---------------|---------------|-------------|
| 1 | 5×1.5 ≈ 7.5 | 2×4.5 ≈ 9 | ~16.5h |
| 2 | ~7.5 | ~9 | ~16.5h |
| 3 | ~7.5 | ~5 (packaging) | ~12.5h |

Keep **Epic 5 (harness gate)** before report/video polish.

## Epic order and exit criteria

| Order | Epic | delivery mapping | Exit criteria (must be demoable) |
|-------|------|------------------|----------------------------------|
| 1 | Foundation + discovery | Stage 1 | `discovery_stats` runs; scaffold + env |
| 2 | Ingest / classify / retrieve | Week2 | A2–A4; Chroma `doc_id`; classifier artifact |
| 3 | Route / generate / guards | Week2 | A5–A7; threshold logged; block works |
| 4 | Log / API / kill / README | Continuous | A1/A8 path; `/health`; kill switch |
| 5 | Harness / metrics / resilience | **GATE** | A9–A11; full validation file unattended |
| 6 | Tests / CI / gov / package | Week3 | A12; package dry-run; governance docs |

## User stories — acceptance criteria matrix (compact)

Full prose stories live in `epics.md`. Below is the **acceptance checklist** used during the build.

| ID | Story | Acceptance criteria (testable) | Maps to |
|----|-------|--------------------------------|---------|
| 1.1 | Scaffold + config | `requirements.txt`, `.env.example`, `.gitignore`; no secrets in tree | A1 |
| 1.2 | Config + models | Settings from `.env`; Ticket/Passage validate | — |
| 1.3 | Discovery script | `--input` path; prints channel/intent aggregates only | CAP-10 |
| 1.4 | Train classifier | Writes joblib; rules-first classify path | A3 / D5 |
| 2.1 | Four-channel ingest | email/chat/docs_comment/forum; coerce bad channel | A2 |
| 2.2 | Classify + alternatives | intent, urgency, confidence, alternatives; no LLM | A3 |
| 2.3 | Build index | documentation.json → Chroma; metadata `doc_id` | A4 / D2 |
| 2.4 | Retrieve | ranked passages or empty; scores; min_score | A4 |
| 3.1 | Deterministic route | same inputs → same action; threshold logged | A5 |
| 3.2 | Freeze threshold | measured value frozen; documented | D3 |
| 3.3 | Generate + cache | LiteLLM only on auto_respond; JSON citations | A6 |
| 3.4 | Blocking guardrails | bad citation/PII → block | A7 |
| 3.5 | Kill switch | env or file; mid-flight re-check | D4 / FR-8 |
| 4.1 | Decision log | SQLite rows; export; harness reconcile | A8 |
| 4.2 | FastAPI | `/health`, `/tickets/process`, `/metrics` | A1 |
| 4.3 | README clean path | setup → setup_all → pytest → harness | A1 |
| 5.1 | Harness CLI | `--input` / `--output` only; no hardcoded hidden path | A9 |
| 5.2 | Metrics report | volume/business/technical/governance written | A10 |
| 5.3 | Resilience | malformed ticket / provider fail → escalate, no abort | A11 |
| 5.4 | Recorded eval | validation run logged in `eval-runs.md` | gate |
| 6.1 | Pytest A12 | single `pytest tests/ -v` command | A12 |
| 6.2 | CI | GHA installs + tests when datasets available | — |
| 6.3 | Governance docs | risk, kill, fairness, incident | gov |
| 6.4 | Package script | 01–04 layout; no `.env` | Stage 6 |
| 6.5 | Fairness | quality gap &lt;5pp on recorded validation | NFR-06 |

## Week-by-week

### Week 1 — Understand + scaffold

- Stories **1.1–1.4**, start **2.1**
- Discovery workbook from **script output** + interviews
- PRD v1 / Stage 2 workbook
- Setup: venv, embeddings download

### Week 2 — Build to gate

| Focus | Stories | Must work |
|-------|---------|-----------|
| Early | 2.2–2.4 | Classify; retrieve with `doc_id` |
| Mid | 3.1–3.5 | Route; generate+cache; guardrail block; kill |
| Mid | 4.1–4.3 | Decision log; API; README |
| Late | 5.1–5.3 | **Full unattended harness** + failure modes |
| End | 5.4 | Freeze threshold; record validation run |

If behind: cut Grafana / prompt variants — **never** the harness.

### Week 3 — Prove + package

- **6.1–6.5**: tests, CI, governance, package dry-run
- Stage 5 PRD revision log
- Report + video (communication)
- Fresh-clone / clean-checkout rehearsal

## Drop list (timeboxed)

1. Grafana dashboard  
2. Hybrid retrieval / rerank  
3. LLM escalation prose  
4. Extra fairness visuals beyond required table  
5. Multiple generate prompt variants  

**Never drop:** harness `--input`/`--output`, blocking guardrail, decision log reconcile, clean README, threshold freeze log.

## Definition of done (story-level)

- Acceptance criteria testable or demoable  
- Decision log updated for pipeline stories  
- Change-log / work-log line if threshold/pins/findings change  
- No secrets committed  

## Tracking

- This plan: `docs/plan/sprint-plan.md`  
- Stories: `docs/plan/epics.md`  
- Workbook: `docs/workbooks/Stage_4_Sprint_Plan.md`  
- Effort: `docs/plan/work-log.md`, `docs/workbooks/Effort_Log.md`
