# Optional Grafana + Prometheus (demo only)

Not required for Capstone grading. Two primary demo boards plus two compact drill-downs.

## Start

```bash
cd submission
./scripts/start_api.sh          # exposes /metrics on :8000
./scripts/grafana_up.sh         # Grafana :3000, Prometheus :9090
./scripts/grafana_load_dashboards.sh
```

Open http://127.0.0.1:3000 — login `admin` / `cloudserve`.

## Dashboards (use these for the video)

| Dashboard | Use for |
|-----------|---------|
| **Live ops (demo)** | Big numbers: tickets, auto/escalate, latency, pies for route / classify / retrieve |
| **Eval dense vs hybrid (demo)** | Side-by-side validation harness KPIs (route-auto %, escalation, accuracy, passages) |
| Classification (compact) | Rules vs model + confidence gauge |
| Retrieval (compact) | Dense vs hybrid fallback mode mix |

Panels use **absolute counts / means** (not `rate()`), so sparse demo traffic still shows clear numbers.

## Refresh eval gauges

```bash
./scripts/run_hybrid_eval.sh validation
./scripts/grafana_load_dashboards.sh
```

## Stop

```bash
./scripts/grafana_down.sh
./scripts/stop_api.sh
```
