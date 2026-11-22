# CloudServe Assistant

Capstone **support triage / assist** system (not a free-form chatbot). Same LangGraph pipeline powers FastAPI and the evaluation harness.

| | |
|--|--|
| **Product** | Classify → retrieve → route in code → optional generate → guardrails → decision log |
| **Threshold** | `CONFIDENCE_THRESHOLD=0.35` (measured; pack 0.80 was illustrative — findings D3) |
| **Repo root** | This folder (`submission/` / packaged `04_Source_Code/`) |
| **Datasets** | Capstone Pack `05_Datasets/` via `CAPSTONE_DATASETS` (not vendored here) |

---

## Key steps (clean machine → demo)

```bash
cd submission   # or: cd 04_Source_Code after unzip

python3.11 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt

cp -n .env.example .env
# Edit .env:
#   CAPSTONE_DATASETS=/absolute/path/to/Capstone_Pack/05_Datasets
#   OPENROUTER_API_KEY=...   # only if you will GENERATE=1

./scripts/setup_all.sh          # 1) train classifier  2) build Chroma + lexical index
./scripts/status.sh             # expect chroma count 59, classifier present
./scripts/run_tests.sh          # A1–A12 behaviour matrix
./scripts/run_eval.sh validation
# Results land in evaluation/results/<tag>_<UTC>/  (metrics.json + metrics.md + results.jsonl)

./scripts/start_api.sh
curl -s localhost:8000/health
./scripts/stop_api.sh
```

**Optional (demo / video):**

```bash
./scripts/run_hybrid_eval.sh validation   # RETRIEVAL_MODE=hybrid + Grafana export
./scripts/start_api.sh
./scripts/grafana_up.sh && ./scripts/grafana_load_dashboards.sh
# Grafana http://127.0.0.1:3000  (admin / cloudserve)
```

**Order matters:** `setup_all.sh` before pytest / eval / API, or index-backed paths skip/fail.

---

## Key modules (`src/`)

| Module | Role |
|--------|------|
| `config.py` | All knobs from `.env` (no silent defaults) |
| `models.py` | Ticket / Classification / Passage / Route / PipelineResult |
| `ingest.py` | Channel normalisation |
| `classify.py` | **Rules first**, then trained sklearn (no LLM labelling) |
| `retrieve.py` | Chroma dense + optional hybrid TF-IDF RRF; `auto` fallback |
| `route.py` | Threshold, grounded override, must_not, kill switch |
| `generate.py` | LiteLLM → OpenRouter **only** on `auto_respond` |
| `guardrails.py` | Blocking checks (citation / PII / …) |
| `graph.py` | LangGraph: ingest→classify→retrieve→route→(generate)→validate→log |
| `logging_store.py` | SQLite decision audit |
| `api.py` | FastAPI `/health`, `/metrics`, `/tickets/process` |
| `observability.py` | Prometheus counters / histograms |

| Path | Role |
|------|------|
| `evaluation/harness.py` | Unattended batch (`--input` / `--output`) |
| `evaluation/metrics_report.py` | `metrics.json` / `metrics.md` |
| `scripts/train_classifier.py` | Fit intent/urgency pipelines → `storage/models/` |
| `scripts/build_index.py` | Chroma + `lexical_index.joblib` |
| `prompts/generate_v1.md` | Generation prompt (`PROMPT_VERSION`) |
| `tests/` | Capstone A1–A12 matrix only |

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Language | Python **3.11** (recommended) |
| Orchestration | **LangGraph** `StateGraph` |
| Classify | rules + **scikit-learn** / joblib |
| Retrieve | **sentence-transformers** + **Chroma** (`cloudserve_docs`, 59 chunks); hybrid optional |
| Generate | **LiteLLM** → OpenRouter |
| API | **FastAPI** / uvicorn / pydantic v2 |
| Audit | **SQLAlchemy** → SQLite |
| Metrics | **prometheus-client** `/metrics` + harness JSON; optional Grafana |
| Config | **python-dotenv** (`.env` only) |

Pins: Pack `06_Configuration` exact pins do not install — resolvable set + log in `docs/plan/requirements-pin-log.md`. Additive pin: `litellm`. Findings D1–D5: `docs/plan/findings.md`.

```mermaid
flowchart LR
  T[Ticket] --> I[Ingest]
  I --> C[Classify]
  C --> R[Retrieve]
  R --> RT[Route]
  RT -->|escalate| E[Escalate + log]
  RT -->|auto| G[Generate]
  G --> V[Guardrails]
  V --> L[Decision log]
```

More diagrams: [`docs/design/architecture/data-flow.md`](docs/design/architecture/data-flow.md).

---

## Where results & metrics are stored

| Artifact | Location | Committed? |
|----------|----------|------------|
| Harness metrics (primary) | `evaluation/results/<run>/metrics.json` + `metrics.md` | **Yes** (curated runs) |
| Per-ticket records | `evaluation/results/<run>/results.jsonl` | **Yes** (curated runs) |
| Run summary | `evaluation/results/<run>/run_summary.json` | **Yes** |
| Retrieval mode tag | `evaluation/results/<run>/retrieval_mode.txt` | **Yes** (hybrid comparison) |
| Decision export | `evaluation/results/<run>/decisions_export.jsonl` | No (regenerate; can be large) |
| Live Prometheus | `GET /metrics` while API runs | Runtime only |
| Grafana gauges | `observability/prometheus/textfile/*.prom` | Seeded dense/hybrid `.prom` |
| Narrative history | `docs/plan/eval-runs.md` | Yes |
| Threshold freeze | `docs/plan/threshold-freeze.md` (+ local `storage/reports/`) | Doc yes; `storage/` no |

**Curated snapshots in this repo**

| Directory | What it proves |
|-----------|----------------|
| `evaluation/results/validation_fairness_fix/` | Dense baseline validation (route-auto **82.5%**, fairness 0pp) |
| `evaluation/results/validation_hybrid_20261122T101209Z/` | Forced hybrid comparison (same route rates; more passages) |

New runs: `./scripts/run_eval.sh validation` writes a fresh `evaluation/results/validation_<UTC>/`. Keep curated folders; prune one-off smoke dirs before commit if huge.

**Honesty:** `--no-generate` → use `route_auto_respond_pct` (automation rate). Do **not** call it customer FCR (`fcr_claim_allowed=false`).

### Headline metrics (labelled validation, n=80, `--no-generate`)

| Metric | Dense | Hybrid |
|--------|------:|-------:|
| Route auto-respond % | 82.5 | 82.5 |
| Escalation % | 17.5 | 17.5 |
| Classification accuracy | 0.9875 | 0.9875 |
| Route agreement vs `expected_route` | 0.775 | 0.775 |
| Mean passages / ticket | 4.33 | 4.92 |
| Fairness gap (tier / fluency, expected_auto quality) | **0 pp** | (same classifier/route) |

Re-export Grafana textfiles after a new curated run:

```bash
python -m scripts.export_eval_metrics --results-dir evaluation/results/validation_fairness_fix --retrieval-mode dense
python -m scripts.export_eval_metrics --results-dir evaluation/results/validation_hybrid_<stamp> --retrieval-mode hybrid
```

---

## Ops scripts

| Script | Purpose |
|--------|---------|
| `./scripts/setup_all.sh` | Train classifier + build retrieval index |
| `./scripts/start_api.sh` / `stop_api.sh` | Background API |
| `./scripts/status.sh` | Classifier / chroma / kill / health |
| `./scripts/run_eval.sh [validation\|development\|path]` | Harness (default `--no-generate`) |
| `./scripts/run_hybrid_eval.sh` | `RETRIEVAL_MODE=hybrid` + `.prom` export |
| `./scripts/tune_threshold.sh` | Threshold sweep |
| `./scripts/run_tests.sh` | `pytest tests/ -v` |
| `./scripts/kill_on.sh` / `kill_off.sh` | Kill-switch file |
| `./scripts/grafana_up.sh` / `down` / `load_dashboards.sh` | Optional Grafana |
| `./scripts/package_submission.sh` | Assemble Capstone zip layout under `../_package/` |
| `./scripts/export_eval_metrics.py` | `metrics.json` → Prometheus textfile |

```bash
./scripts/run_eval.sh validation
GENERATE=1 ./scripts/run_eval.sh validation      # needs OpenRouter key
LIMIT=50 ./scripts/run_eval.sh development
USE_EVAL_LABELS=false ./scripts/run_eval.sh validation
./scripts/run_hybrid_eval.sh validation
```

### Retrieval modes (`.env`)

| `RETRIEVAL_MODE` | Behaviour |
|------------------|-----------|
| `dense` | Chroma only |
| `hybrid` | Dense + lexical TF-IDF (RRF) |
| `auto` (default) | Dense first; hybrid **only** if top dense score &lt; `HYBRID_DENSE_SCORE_FLOOR` |

### Optional Grafana

```bash
./scripts/start_api.sh
./scripts/grafana_up.sh && ./scripts/grafana_load_dashboards.sh
# Live ops + Eval dense vs hybrid dashboards under folder CloudServe
```

Details: [`observability/README.md`](observability/README.md).

---

## API

```bash
./scripts/start_api.sh
# GET  /health
# GET  /metrics
# POST /tickets/process  {"ticket": { ... }, "allow_generate": false}
./scripts/stop_api.sh
```

OpenAPI: `http://127.0.0.1:8000/docs`  
Postman (optional): `docs/postman/CloudServe_Assistant.postman_collection.json`

---

## Kill switch

`KILL_SWITCH=true` in `.env` **or** `./scripts/kill_on.sh`. Semantics: findings D4 / `docs/governance/kill-switch.md`.

---

## Docs map

| Path | Contents |
|------|----------|
| `docs/plan/` | Findings, gaps, eval-runs, verification, pin log, work-log, sprint/epics |
| `docs/design/architecture/` | Spine, design, data-flow diagrams |
| `docs/design/spec/` | SPEC, stack-and-env, acceptance |
| `docs/report/` | Capstone report (PDF) |
| `docs/workbooks/` | Stage 1–5 + Effort Log |
| `docs/video/` | ≤18 min shooting script |
| `docs/governance/` | Risk, fairness, incident, kill-switch |
| `docs/postman/` | Optional API collection |

Index: [`docs/README.md`](docs/README.md).

Package: `PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh` → `../_package/CloudServe_Capstone_Submission/`.
