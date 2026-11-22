# Optional Grafana + Prometheus (demo only)

Optional ops dashboards for demos and production monitoring.

## Start (full demo path)

```bash
cd submission
./scripts/start_api.sh                 # /metrics on :8000
./scripts/grafana_up.sh                # Grafana :3000, Prometheus :9090, eval exporter :9101
./scripts/grafana_load_dashboards.sh   # export harness KPIs + reload boards
./scripts/grafana_seed_live.sh         # process validation tickets so Live ops pies fill
```

Open http://127.0.0.1:3000 — login `admin` / `cloudserve` → folder **CloudServe**.

Without `grafana_seed_live.sh`, Live ops / Classification / Retrieval stay near zero (counters only grow when the API processes tickets). Eval boards need exported `*.prom` textfiles (the load script does this).

## Dashboards

| Dashboard | Use for |
|-----------|---------|
| **Live ops (demo)** | Tickets, auto/escalate, latency, pies, timeseries |
| **Eval dense vs hybrid (demo)** | Route-only dense vs hybrid KPIs |
| **Generate-on FCR (demo)** | Customer FCR, fairness gaps, citations (`allow_generate=true`) |
| Classification (compact) | Rules vs model + confidence |
| Retrieval (compact) | Dense vs hybrid mode mix |

## Recorded generate-on evidence

`evaluation/results/validation_20261122T131433Z/` — Groq `qwen/qwen3.8-27b`, **82.5% FCR**, 66/14, fairness **0pp**.

```bash
GENERATE=1 ./scripts/run_eval.sh validation   # needs GROQ_API_KEY or OPENROUTER_API_KEY
./scripts/grafana_load_dashboards.sh
```

## Stop

```bash
./scripts/grafana_down.sh
./scripts/stop_api.sh
```
