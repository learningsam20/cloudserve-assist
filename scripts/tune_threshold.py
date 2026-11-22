"""Score routing confidence cutoffs on labelled development tickets (findings D3).

Does not print ticket bodies. Chosen value must be frozen in CONFIDENCE_THRESHOLD
before the recorded evaluation run.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.classify import classify, reset_classifier_cache
from src.config import get_settings
from src.ingest import ingest
from src.retrieve import reset_retrieve_cache, retrieve


@dataclass
class Row:
    ticket_id: str
    confidence: float
    has_passages: bool
    must_not: bool
    expected_auto: bool


def _collect(rows: list[dict[str, Any]], limit: int | None) -> list[Row]:
    out: list[Row] = []
    for i, raw in enumerate(rows):
        if limit is not None and i >= limit:
            break
        labels = raw.get("labels") or {}
        expected = str(labels.get("expected_route") or "").strip().lower()
        if expected not in {"auto_respond", "escalate"}:
            continue
        ticket = ingest(raw)
        clf = classify(ticket)
        passages = retrieve(ticket)
        out.append(
            Row(
                ticket_id=ticket.ticket_id,
                confidence=float(clf.confidence),
                has_passages=bool(passages),
                must_not=bool(labels.get("must_not_auto_respond")),
                expected_auto=expected == "auto_respond",
            )
        )
    return out


def _decide(row: Row, threshold: float) -> bool:
    """Return True if system would auto_respond at this threshold (kill switch off)."""
    if row.must_not:
        return False
    if not row.has_passages:
        return False
    return row.confidence >= threshold


def score_threshold(rows: list[Row], threshold: float) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for row in rows:
        pred_auto = _decide(row, threshold)
        if pred_auto and row.expected_auto:
            tp += 1
        elif pred_auto and not row.expected_auto:
            fp += 1
        elif not pred_auto and not row.expected_auto:
            tn += 1
        else:
            fn += 1
    n = len(rows)
    auto = tp + fp
    precision = tp / auto if auto else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    escalation_rate = (tn + fn) / n if n else 0.0
    fcr_proxy = auto / n if n else 0.0
    # Cost: false auto (risky) weighs more than missed auto
    cost = 2.0 * fp + 1.0 * fn
    return {
        "threshold": round(threshold, 3),
        "n": n,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "auto_precision": round(precision, 4),
        "auto_recall": round(recall, 4),
        "auto_f1": round(f1, 4),
        "fcr_proxy_pct": round(100.0 * fcr_proxy, 2),
        "escalation_rate_pct": round(100.0 * escalation_rate, 2),
        "cost_2fp_1fn": round(cost, 2),
        "meets_escalation_le_30": escalation_rate <= 0.30,
        "meets_fcr_ge_60": fcr_proxy >= 0.60,
    }


def recommend(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Business targets lead (findings D1); then precision / cost among survivors."""
    business = [
        c for c in candidates if c["meets_escalation_le_30"] and c["meets_fcr_ge_60"]
    ]
    if business:
        return sorted(
            business,
            key=lambda c: (-c["auto_precision"], c["cost_2fp_1fn"], -c["auto_f1"]),
        )[0]
    prec_floor = get_settings().target_classification_precision
    precise = [c for c in candidates if c["auto_precision"] >= prec_floor]
    pool = precise or candidates
    return sorted(pool, key=lambda c: (c["cost_2fp_1fn"], -c["auto_f1"], -c["threshold"]))[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune CONFIDENCE_THRESHOLD on labelled tickets")
    parser.add_argument("--input", required=True, help="Path to labelled tickets JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for threshold_tune.json report",
    )
    parser.add_argument("--min", type=float, default=None, help="Override TUNE_THRESHOLD_MIN")
    parser.add_argument("--max", type=float, default=None, help="Override TUNE_THRESHOLD_MAX")
    parser.add_argument("--step", type=float, default=None, help="Override TUNE_THRESHOLD_STEP")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit("Input must be a non-empty JSON array")

    get_settings.cache_clear()
    settings = get_settings()
    reset_classifier_cache()
    reset_retrieve_cache()

    rows = _collect(data, args.limit)
    if len(rows) < 20:
        raise SystemExit(f"Need ≥20 labelled rows with expected_route; got {len(rows)}")

    t_min = args.min if args.min is not None else settings.tune_threshold_min
    t_max = args.max if args.max is not None else settings.tune_threshold_max
    t_step = args.step if args.step is not None else settings.tune_threshold_step

    thresholds: list[float] = []
    t = t_min
    while t <= t_max + 1e-9:
        thresholds.append(round(t, 3))
        t += t_step

    candidates = [score_threshold(rows, th) for th in thresholds]
    best = recommend(candidates)
    confidences = sorted(r.confidence for r in rows)

    report = {
        "n_scored": len(rows),
        "confidence_summary": {
            "min": round(confidences[0], 4),
            "p50": round(confidences[len(confidences) // 2], 4),
            "p90": round(confidences[int(0.9 * (len(confidences) - 1))], 4),
            "max": round(confidences[-1], 4),
            "share_with_passages": round(
                sum(1 for r in rows if r.has_passages) / len(rows), 4
            ),
        },
        "candidates": candidates,
        "recommended": best,
        "freeze_instructions": (
            "Set CONFIDENCE_THRESHOLD to recommended.threshold in .env, log freeze date "
            "in docs/plan/work-log.md and _bmad-output/change-log.md (findings D3). "
            "Do not change after the recorded validation harness run without a PRD revision."
        ),
    }

    text = json.dumps(report, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
