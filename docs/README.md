# CloudServe Assistant — product docs

Start with the root [`../README.md`](../README.md) for **key steps**, **key modules**, and **where metrics/results are stored**.

| Path | Contents |
|------|----------|
| `plan/findings.md` | Pack deviations D1–D5 |
| `plan/work-log.md` | Sequential changes + estimated phrs |
| `plan/eval-runs.md` | Evaluation history (dense + hybrid) |
| `plan/gaps.md` / `independent-verification.md` | Gate status |
| `plan/prd.md` / `epics.md` / `sprint-plan.md` | Requirements, stories + AC matrix, calendar |
| `plan/threshold-freeze.md` | `CONFIDENCE_THRESHOLD=0.35` |
| `design/spec/` | SPEC, stack-and-env, acceptance |
| `design/architecture/` | Spine, package design, **`data-flow.md` diagrams** |
| `report/` | Product report (PDF) |
| `workbooks/` | Stage 1–5 + Effort Log |
| `video/` | ≤18 min shooting script |
| `postman/` | Optional API collection |
| `governance/` | Risk, fairness, incident, kill-switch |

**Config:** reference datasets pack `06_Configuration/` is the baseline; `submission/requirements.txt` is the **resolvable** set (`plan/requirements-pin-log.md`).

**Evidence on disk:** curated harness outputs under `evaluation/results/validation_fairness_fix/` and `evaluation/results/validation_hybrid_*/` (`metrics.json`, `metrics.md`, `results.jsonl`).
