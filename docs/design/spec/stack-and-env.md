# Stack and environment

**Config source of truth (pack):** `reference 06_Configuration/`
- `requirements.txt` — pinned CloudServe deps (copy into `submission/requirements.txt`, then add approved packages only)
- `.env.example` — suggested env keys (copy into `submission/.env.example`, then add approved keys only)

Starting point from product brief / Setup Guide + that folder. Departures need a short written justification in architecture notes / findings.

## Runtime

| Layer | Choice |
|-------|--------|
| Language | Python ≥3.10 (CI example uses 3.11) |
| Orchestration | LangChain + LangGraph `StateGraph` (shared by API + harness) |
| Vector store | Chroma on disk (`CHROMA_PATH`); dense baseline; optional hybrid (TF-IDF + dense RRF) via `RETRIEVAL_MODE` |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers / HuggingFace) — **local** |
| Classification | **Rules first**, then **trained local classifier** (sklearn on development labels; joblib artifact) |
| Routing | **Code** (Threshold + policy flags + kill switch) — not an LLM |
| Remote LLM | **LiteLLM** SDK → **OpenRouter** (default); swap provider via env without code rewrites |
| API | FastAPI + uvicorn |
| Decision log | SQLite via SQLAlchemy (`DATABASE_URL`) unless Postgres justified |
| Metrics | prometheus-client `/metrics`; optional Grafana+Prometheus compose under `observability/` (demo dashboards) |
| CI | GitHub Actions running pytest |

## Env vars

**From pack** `06_Configuration/.env.example` (keep these names):

```
OPENROUTER_API_KEY=your_key_here
MODEL_NAME=openrouter/free
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PATH=./storage/chroma
DATABASE_URL=sqlite:///./storage/decisions.db
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.80
RETRIEVAL_TOP_K=5
```

**Approved additions** (submission `.env.example` only):

```
# LiteLLM provider prefix + OpenRouter model id (API sees openrouter/free)
LITELLM_MODEL=openrouter/openrouter/free
LITELLM_API_BASE=https://openrouter.ai/api/v1
# Optional Groq: set GROQ_API_KEY and LITELLM_MODEL=groq/<model>
GROQ_API_KEY=your_key_here
CLASSIFIER_DIR=./storage/models/classifier
KILL_SWITCH=false
KILL_SWITCH_FILE=./storage/KILL_SWITCH
RETRIEVAL_MODE=auto
HYBRID_DENSE_SCORE_FLOOR=0.35
HYBRID_DENSE_ALPHA=0.6
LEXICAL_INDEX_PATH=./storage/lexical_index.joblib
LLM_MIN_INTERVAL_SECONDS=4.0
```

Optional demo only (not required at runtime): Docker Compose under `observability/` (Grafana + Prometheus + eval textfile exporter).

- Copy pack template → `submission/.env.example` → local `.env`; never commit `.env`.
- `CONFIDENCE_THRESHOLD` is a starting value; measure then freeze (findings D3).
- Fail loud if API key missing when generate path is used.
- Generation via LiteLLM. **OpenRouter:** `MODEL_NAME=openrouter/free`, `LITELLM_MODEL=openrouter/openrouter/free`, `LITELLM_API_BASE=https://openrouter.ai/api/v1`, key in `OPENROUTER_API_KEY`. **Groq:** `LITELLM_MODEL=groq/llama-3.1-8b-instant` (or another Groq id), `LITELLM_API_BASE=https://api.groq.com/openai/v1`, key in `GROQ_API_KEY`. Provider is inferred from the `LITELLM_MODEL` prefix.
- Kill switch: `KILL_SWITCH=true` **or** kill file present; checked at route (findings D4).
- Train classifier with `scripts/train_classifier.py`; artifact under `CLASSIFIER_DIR` (gitignored under `storage/`).

## Dependencies

1. Copy `reference 06_Configuration/requirements.txt` → `submission/requirements.txt`.
2. Append **only** approved additive: `litellm` (pin after clean venv resolve; log in change-log). Classifier uses pack-pinned `scikit-learn` (+ `joblib` via sklearn).
3. Verify install on Python ≥3.10 (CI 3.11). Pin conflicts → ask before changing CloudServe pins.

## Project modules (Setup Guide shape)

```
src/config.py
src/models.py
src/ingest.py
src/classify.py          # rules then trained classifier
src/retrieve.py
src/route.py             # threshold + kill switch
src/generate.py          # LiteLLM → OpenRouter or Groq
src/guardrails.py
src/logging_store.py
src/cache.py
src/llm.py               # LiteLLM wrapper (provider from model prefix)
src/graph.py
src/api.py
src/observability.py     # Prometheus counters / histograms
evaluation/harness.py
scripts/discovery_stats.py
scripts/train_classifier.py
scripts/tune_threshold.py
prompts/
tests/
```

## Chunking note

Setup Guide suggests trying ≥2 chunk configs (example starter `chunk_size=800`, `overlap=120`), measuring retrieval quality via scripts, and recording the choice. Do not split inside numbered resolution sequences inside articles (Dataset Guide).

## What uses a remote LLM vs local

| Stage | Engine | Remote LLM? |
|-------|--------|-------------|
| Ingest / normalise | Code | No |
| Intent + Urgency + Confidence | Rules, then trained sklearn classifier | No |
| Retrieve | Local embeddings + Chroma | No |
| Route auto_respond / escalate | Code over Confidence, Threshold, policy, kill switch | No |
| Generate cited answer | LiteLLM → OpenRouter | **Yes** (only if auto_respond) |
| Escalation summary prose | Template preferred; LLM optional | Avoid if possible |
| Guardrails | Code | No |
| Discovery / train / tune scripts | pandas / sklearn | No |

Low classifier confidence → **escalate** (no LLM labelling fallback). That keeps A5 deterministic and limits OpenRouter use to generation.

## Rate limits and A9

OpenRouter free models are commonly capped around **20 requests/minute** and **50 requests/UTC day**. Local classify+route plus escalate-before-generate keeps generate-calls within free caps.

- Persistent cache of **generation** responses keyed by prompt hash + model name.
- Skip generate when route is already escalate.
- Exponential backoff + honor `Retry-After` on 429; continue the batch (A11).

## Graph / policy split

- Nodes: ingest → classify (rules+model) → retrieve → route (code) → generate (remote, if auto_respond) → validate (code) → log.
- Code owns: Threshold compare, citation-ID ∈ retrieved set, PII/block rules, kill switch.
- Local model owns: Intent/Urgency/Confidence (+ alternatives from predict_proba).
- Remote LLM owns: draft answer text with claimed citation IDs (validated in code).
