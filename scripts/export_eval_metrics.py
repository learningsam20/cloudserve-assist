#!/usr/bin/env python3
"""Export harness metrics.json → Prometheus textfile for Grafana eval dashboard.

Usage:
  python -m scripts.export_eval_metrics --results-dir evaluation/results/<run>
  python -m scripts.export_eval_metrics --all
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_OUT = _ROOT / "observability" / "prometheus" / "textfile"


def _sanitize(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_:\-./]", "_", value)[:120]


def _gauge(name: str, value: float | int | None, labels: dict[str, str]) -> str | None:
    if value is None:
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    label_str = ",".join(f'{k}="{_sanitize(v)}"' for k, v in labels.items())
    return f"{name}{{{label_str}}} {num}"


def _from_results(results_path: Path) -> dict[str, float | None]:
    if not results_path.exists():
        return {
            "mean_passages": None,
            "mean_top_score": None,
            "route_agreement": None,
        }
    n = 0
    passages = 0
    top_sum = 0.0
    tops = 0
    agree = 0
    agree_n = 0
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        ps = rec.get("passages") or []
        n += 1
        passages += len(ps)
        if ps:
            top_sum += max(float(p.get("score") or 0.0) for p in ps)
            tops += 1
        expected = (rec.get("labels") or {}).get("expected_route")
        action = rec.get("action")
        if expected and action:
            agree_n += 1
            if str(expected) == str(action):
                agree += 1
    return {
        "mean_passages": (passages / n) if n else None,
        "mean_top_score": (top_sum / tops) if tops else None,
        "route_agreement": (agree / agree_n) if agree_n else None,
    }


def export_one(metrics_path: Path, *, retrieval_mode: str | None = None) -> list[str]:
    data: dict[str, Any] = json.loads(metrics_path.read_text(encoding="utf-8"))
    run_id = metrics_path.parent.name
    mode = retrieval_mode or data.get("meta", {}).get("retrieval_mode") or "unknown"
    sidecar = metrics_path.parent / "retrieval_mode.txt"
    if sidecar.exists():
        mode = sidecar.read_text(encoding="utf-8").strip() or mode

    labels = {"run_id": run_id, "retrieval_mode": mode}
    volume = data.get("volume") or {}
    business = data.get("business") or {}
    technical = data.get("technical") or {}
    clf = technical.get("classification") or {}
    latency = technical.get("latency_seconds") or {}
    derived = _from_results(metrics_path.parent / "results.jsonl")

    auto_pct = business.get("route_auto_respond_pct")
    if auto_pct is None:
        auto_pct = business.get("first_contact_resolution_pct")

    lines = [
        "# HELP cloudserve_eval_tickets Harness tickets processed",
        "# TYPE cloudserve_eval_tickets gauge",
    ]
    for item in [
        _gauge("cloudserve_eval_tickets", volume.get("tickets_processed"), labels),
        _gauge("cloudserve_eval_route_auto_pct", auto_pct, labels),
        _gauge(
            "cloudserve_eval_escalation_pct",
            business.get("escalation_rate_pct"),
            labels,
        ),
        _gauge(
            "cloudserve_eval_classification_accuracy",
            clf.get("overall_accuracy"),
            labels,
        ),
        _gauge(
            "cloudserve_eval_route_agreement",
            derived["route_agreement"],
            labels,
        ),
        _gauge(
            "cloudserve_eval_latency_p95_seconds",
            latency.get("p95"),
            labels,
        ),
        _gauge(
            "cloudserve_eval_mean_passages",
            derived["mean_passages"],
            labels,
        ),
        _gauge(
            "cloudserve_eval_mean_top_score",
            derived["mean_top_score"],
            labels,
        ),
    ]:
        if item:
            lines.append(item)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", help="Single evaluation/results/<run> directory")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export every evaluation/results/*/metrics.json",
    )
    parser.add_argument("--retrieval-mode", help="Override retrieval_mode label")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_DEFAULT_OUT,
        help="Prometheus textfile directory",
    )
    args = parser.parse_args()

    paths: list[Path] = []
    if args.all:
        paths = sorted((_ROOT / "evaluation" / "results").glob("*/metrics.json"))
    elif args.results_dir:
        p = Path(args.results_dir)
        if not p.is_absolute():
            p = _ROOT / p
        paths = [p / "metrics.json"]
    else:
        parser.error("Provide --results-dir or --all")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for metrics_path in paths:
        if not metrics_path.exists():
            print(f"skip missing {metrics_path}")
            continue
        lines = export_one(metrics_path, retrieval_mode=args.retrieval_mode)
        out = args.out_dir / f"{metrics_path.parent.name}.prom"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {out}")
        written += 1
    print(f"exported={written}")


if __name__ == "__main__":
    main()
