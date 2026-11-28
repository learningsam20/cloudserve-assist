# Data flow — CloudServe Assistant

Use these diagrams in the README, report, and **video** (open PDF or this file beside the terminal).

## Purpose

CloudServe Assistant is a **support triage / assist** system (not a chatbot): ingest a ticket → classify locally → retrieve KB passages by `doc_id` → **route in code** → optionally generate a cited draft via LiteLLM (OpenRouter **or** Groq; recorded generate-on used **Groq**) → guardrails → SQLite decision log.

Canonical diagrams for the product report and demonstration video. Runtime topology and routing order below match [ARCHITECTURE-SPINE.md](ARCHITECTURE-SPINE.md) and the [product report](../../report/CloudServe_Assistant_Report.md) §4.

## End-to-end pipeline

```mermaid
flowchart LR
  T[Ticket JSON<br/>4 channels] --> I[Ingest]
  I --> C[Classify<br/>rules → sklearn]
  C --> R[Retrieve<br/>MiniLM → Chroma 59]
  R --> RT[Route<br/>kill / must_not / conf]
  RT -->|escalate / block| E[Escalation package<br/>+ decision log]
  RT -->|auto_respond| G[Generate<br/>LiteLLM → OpenRouter / Groq]
  G --> V[Guardrails]
  V -->|pass| A[auto_respond + log]
  V -->|fail| E
```

## Runtime topology

```mermaid
flowchart TB
  subgraph clients [Callers]
    API[FastAPI<br/>/tickets/process]
    HAR[evaluation.harness<br/>--input / --output]
  end
  subgraph local [Local process]
    G[LangGraph StateGraph]
    CLF[(classifier.joblib)]
    CH[(Chroma cloudserve_docs)]
    EMB[MiniLM embeddings]
    DB[(SQLite decisions)]
    CACHE[(gen_cache)]
  end
  LLM[LiteLLM<br/>OpenRouter or Groq]
  API --> G
  HAR --> G
  G --> CLF
  G --> EMB
  EMB --> CH
  G --> CH
  G --> DB
  G --> CACHE
  G -->|generate only if auto_respond| LLM
```

## Where MiniLM fits

```mermaid
flowchart LR
  KB[KB JSON doc_id] --> IDX[index: MiniLM encode chunks]
  IDX --> CH[(Chroma)]
  T[Ticket text] --> Q[query: MiniLM encode]
  Q --> CH
  CH --> P[Passages + scores]
  P --> RT[Route / Generate]
```

MiniLM is **retrieval only**. Classification is rules + sklearn. Draft text is LiteLLM → remote chat model.

## Routing decision order

```mermaid
flowchart TD
  S[Ticket + classification + passages] --> K{Kill switch?}
  K -->|yes| X1[escalate]
  K -->|no| M{must_not<br/>label / intent / text?}
  M -->|yes| X2[escalate]
  M -->|no| P{passages empty?}
  P -->|yes| X3[escalate]
  P -->|no| C{conf ≥ 0.35?}
  C -->|yes| A[auto_respond → LLM]
  C -->|no| G{grounded override?}
  G -->|yes| A
  G -->|no| X4[escalate — no LLM]
```

## Evaluation data flow

```mermaid
flowchart LR
  IN["tickets.json path"] --> H[harness]
  H --> G["run_ticket per row"]
  G --> OUT["results.jsonl"]
  G --> M["metrics.json and metrics.md"]
  G --> D["decisions_export.jsonl"]
  M --> EXP["export_eval_metrics to prom files"]
  EXP --> GRAF["Grafana FCR and eval boards"]
```

## Observability

```mermaid
flowchart LR
  API["FastAPI /metrics<br/>port 8000"] --> PROM[Prometheus]
  EXP["eval-exporter<br/>port 9101"] --> PROM
  PROM --> GRAF["Grafana<br/>port 3000"]
```

API process metrics and exported evaluation metrics are scraped by Prometheus and shown in Grafana. Compose and dashboards live under `observability/`; see [observability/README.md](../../../observability/README.md).
