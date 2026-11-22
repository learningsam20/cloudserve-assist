# Requirements pin log

**Date:** 2026-11-22  
**Policy:** Capstone Pack `06_Configuration/requirements.txt` is the baseline; changes are logged (AGENTS.md).

## Problem

A clean `pip install -r requirements.txt` using the Pack pins fails:

- `openai==1.0.0` vs `langchain-openai==0.0.7` (`openai>=1.10,<2`)
- `pydantic==2.0.0` excluded by `fastapi==0.104.0`
- `langchain==0.1.0` vs companion package `langsmith` ranges
- Even when partially relaxed, `chromadb==0.3.21` lacks `PersistentClient` used by `src/retrieve.py` and breaks on pydantic v2 (`BaseSettings` import)

Independent verification: `docs/plan/independent-verification.md` B1/B2.

## Decision

Ship a **resolvable range set** targeting **Python 3.11**, keeping Capstone stack components the product actually needs (`langgraph`, `chromadb`, `sentence-transformers`, `scikit-learn`, `fastapi`, `SQLAlchemy`, `prometheus-client`) plus approved additive **`litellm`**. Retain `langchain` / `langchain-community` / `langchain-core` for Brief alignment even though runtime orchestration imports `langgraph` only.

Removed from the install surface (not imported by `src/`): pinned `openai`, `langchain-openai`, `psycopg2-binary`, `jupyter`, `ipython`, `flake8`, `black`, `pytest-cov` (optional local tools).

## Verification

| Check | Result |
|-------|--------|
| `uv pip install -r requirements.txt` on CPython 3.11.14 | Success (2026-11-22) |
| Rebuild classifier + Chroma + `pytest` with Pack datasets | Re-verify after this change |

Do not claim Pack-exact pins; claim Capstone-compatible stack that installs and runs.
