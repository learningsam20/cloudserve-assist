# Data flow — CloudServe Assistant

Use these diagrams in the README, report, and **video** (open PDF or this file beside the terminal).

## Purpose

CloudServe Assistant is a **support triage / assist** system (not a chatbot): ingest a ticket → classify locally → retrieve KB passages by `doc_id` → **route in code** → optionally generate a cited draft via LiteLLM→OpenRouter → guardrails → SQLite decision log.

## End-to-end pipeline

```mermaid
flowchart LR
  T[Ticket JSON<br/>4 channels] --> I[Ingest]
  I --> C[Classify<br/>rules → sklearn]
  C --> R[Retrieve<br/>Chroma 59 chunks]
  R --> RT[Route<br/>kill / must_not / conf]
  RT -->|escalate / block| E[Escalation package<br/>+ decision log]
  RT -->|auto_respond| G[Generate<br/>LiteLLM → OpenRouter]
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
    DB[(SQLite decisions)]
    CACHE[(gen_cache)]
  end
  OR[OpenRouter]
  API --> G
  HAR --> G
  G --> CLF
  G --> CH
  G --> DB
  G --> CACHE
  G -->|generate only| OR
```

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
  C -->|yes| A[auto_respond]
  C -->|no| G{grounded override?}
  G -->|yes| A
  G -->|no| X4[escalate]
```

## Evaluation data flow

```mermaid
flowchart LR
  IN[tickets.json path] --> H[harness]
  H --> G[run_ticket per row]
  G --> OUT[results.jsonl]
  G --> M[metrics.json / .md]
  G --> D[decisions_export.jsonl<br/>scoped to run ticket_ids]
```
