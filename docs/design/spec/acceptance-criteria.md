# Acceptance criteria (A1–A12)

Source: CloudServe Build Specification. Each is pass/fail.

| ID | Must hold | CAP / FR |
|----|-----------|----------|
| A1 | Runs from clean checkout via README commands | CAP-9, FR-10 |
| A2 | All four channels ingest and normalise | CAP-1, FR-1 |
| A3 | Intent + urgency + numeric confidence | CAP-2, FR-2 |
| A4 | Retrieval returns identifiable real passages | CAP-3, FR-3 |
| A5 | Threshold routing; same input → same decision | CAP-4, FR-4 |
| A6 | Citations resolve to retrieved passages | CAP-5, FR-5 |
| A7 | At least one Guardrail can block when triggered | CAP-6, FR-6 |
| A8 | Persistent decision log; reconciles with processed tickets | CAP-7, FR-7 |
| A9 | Full eval set in one unattended run; path-parameterised input | CAP-8, FR-9 |
| A10 | Metrics report produced automatically | CAP-8, FR-9 |
| A11 | Survives retrieval miss, provider outage/timeout, rate limit, malformed input | CAP-11, FR-11 |
| A12 | Tests: one documented command, suite passes | CAP-12, FR-12 |

## Illustrative commands (document the real ones in README)

```bash
python -m src.api
python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results/
python -m pytest tests/ -v
```

Harness **must** take input and output paths. Hardcoded dataset paths fail A9 when graders inject the hidden file.
