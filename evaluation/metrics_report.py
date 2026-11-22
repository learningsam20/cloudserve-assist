"""Automatic metrics report for harness runs (A10 / Evaluation Framework)."""

from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from src import __version__
from src.config import get_settings
from src.models import RouteAction


def _targets() -> dict[str, float]:
    s = get_settings()
    return {
        "fcr_pct": s.target_fcr_pct,
        "reply_mean_minutes": s.target_reply_mean_minutes,
        "csat": s.target_csat,
        "escalation_pct": s.target_escalation_pct,
        "classification_precision": s.target_classification_precision,
        "latency_p95_seconds": s.target_latency_p95_seconds,
    }


def _pct(n: int, d: int) -> float:
    return 100.0 * n / d if d else 0.0


def _percentile(values: list[float], p: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = max(0, min(len(ordered) - 1, int(math.ceil(p * len(ordered))) - 1))
    return ordered[idx]


def build_metrics(
    records: list[dict[str, Any]],
    *,
    input_path: str,
    run_started_at: str,
    allow_generate: bool,
    decisions_logged: int,
) -> dict[str, Any]:
    """Compute volume / business / technical / governance sections from harness records."""
    TARGETS = _targets()
    n = len(records)
    actions = Counter(str(r.get("action")) for r in records)
    auto = actions.get(RouteAction.AUTO_RESPOND.value, 0)
    escalate = actions.get(RouteAction.ESCALATE.value, 0)
    block = actions.get(RouteAction.BLOCK.value, 0)
    errors = sum(1 for r in records if r.get("errors"))
    silent = sum(1 for r in records if not r.get("action"))
    latencies = [float(r["latency_seconds"]) for r in records if r.get("latency_seconds") is not None]

    # Business: distinguish route-only auto rate from generate-on FCR proxy
    auto_rate = _pct(auto, n)
    fcr = auto_rate if allow_generate else None
    escalation_rate = _pct(escalate + block, n)
    reply_mean_min = (statistics.mean(latencies) / 60.0) if latencies else None
    reply_median_min = (statistics.median(latencies) / 60.0) if latencies else None
    reply_p95_min = None
    p95_sec = _percentile(latencies, 0.95)
    if p95_sec is not None:
        reply_p95_min = p95_sec / 60.0

    # Classification vs labels when present
    y_true: list[str] = []
    y_pred: list[str] = []
    conf_pairs: list[tuple[float, bool]] = []
    for r in records:
        labels = r.get("labels") or {}
        clf = r.get("classification") or {}
        true_intent = labels.get("intent")
        pred_intent = clf.get("intent")
        if true_intent and pred_intent:
            y_true.append(str(true_intent))
            y_pred.append(str(pred_intent))
            conf = clf.get("confidence")
            if conf is not None:
                conf_pairs.append((float(conf), str(true_intent) == str(pred_intent)))

    precision_overall = None
    per_class: dict[str, Any] = {}
    if y_true:
        correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
        precision_overall = correct / len(y_true)
        by_true: dict[str, list[bool]] = defaultdict(list)
        for t, p in zip(y_true, y_pred):
            by_true[t].append(t == p)
        per_class = {
            k: {"n": len(v), "recall": sum(v) / len(v) if v else 0.0} for k, v in by_true.items()
        }

    # Citation ID validity among generated replies (automated proxy for citation accuracy)
    cite_ok = 0
    cite_total = 0
    pii_hits = 0
    for r in records:
        gen = r.get("generation") or {}
        passages = r.get("passages") or []
        retrieved = {p.get("doc_id") for p in passages}
        cites = gen.get("citation_doc_ids") or []
        if cites:
            cite_total += 1
            if all(c in retrieved for c in cites):
                cite_ok += 1
        answer = gen.get("answer") or ""
        if answer and _scan_pii(answer):
            pii_hits += 1

    # Segment quality gap (auto_respond rate by tier / fluency) — <5pp requirement
    segment_gaps = _segment_gaps(records)

    # Calibration bands
    calibration = _calibration_table(conf_pairs)

    escalate_reasons: Counter[str] = Counter()
    must_not = 0
    for r in records:
        if r.get("action") != RouteAction.ESCALATE.value:
            continue
        reason = str((r.get("route") or {}).get("reason") or "unknown")
        if "must_not_auto_respond" in reason:
            must_not += 1
            escalate_reasons["policy_must_not"] += 1
        elif "No retrieved passages" in reason:
            escalate_reasons["empty_retrieval"] += 1
        elif "below threshold" in reason:
            escalate_reasons["low_confidence"] += 1
        elif "Kill switch" in reason:
            escalate_reasons["kill_switch"] += 1
        else:
            escalate_reasons["other"] += 1

    volume = {
        "tickets_input": n,
        "tickets_processed": n,
        "silent_drops": silent,
        "action_counts": dict(actions),
        "tickets_with_errors": errors,
        "allow_generate": allow_generate,
        "escalate_reason_counts": dict(escalate_reasons),
        "policy_must_not_count": must_not,
    }

    business = {
        "targets": {
            "fcr_pct": TARGETS["fcr_pct"],
            "reply_mean_minutes": TARGETS["reply_mean_minutes"],
            "csat": TARGETS["csat"],
            "escalation_pct": TARGETS["escalation_pct"],
        },
        "route_auto_respond_pct": round(auto_rate, 2),
        "first_contact_resolution_pct": round(fcr, 2) if fcr is not None else None,
        "fcr_definition": (
            "auto_respond / total after generate+validate (customer-facing FCR proxy)"
            if allow_generate
            else "N/A for --no-generate runs; use route_auto_respond_pct only"
        ),
        "fcr_claim_allowed": bool(allow_generate),
        "escalation_rate_pct": round(escalation_rate, 2),
        "escalation_definition": "(escalate + block) / total",
        "time_to_first_reply_minutes": {
            "mean": round(reply_mean_min, 4) if reply_mean_min is not None else None,
            "median": round(reply_median_min, 4) if reply_median_min is not None else None,
            "p95": round(reply_p95_min, 4) if reply_p95_min is not None else None,
            "note": "Harness wall-clock latency used as reply-time proxy for batch eval",
        },
        "csat_proxy": {
            "value": None,
            "n": 0,
            "method": "human_rubric_sample_pending",
            "note": "Requires human rubric sample; not invented by harness (Evaluation Framework)",
        },
        "meets_fcr_target": (fcr is not None and fcr >= TARGETS["fcr_pct"]),
        "meets_route_auto_target": auto_rate >= TARGETS["fcr_pct"],
        "meets_escalation_target": escalation_rate <= TARGETS["escalation_pct"],
        "meets_reply_target": (
            reply_mean_min is not None and reply_mean_min < TARGETS["reply_mean_minutes"]
        ),
        "escalation_excluding_policy_pct": round(
            _pct(escalate + block - must_not, n), 2
        ),
        "note_policy": (
            "must_not_auto_respond tickets are forced escalate by policy and inflate "
            "raw escalation rate; see volume.escalate_reason_counts. "
            "Do not report --no-generate route_auto_respond_pct as customer FCR."
        ),
    }

    technical = {
        "targets": {
            "classification_precision": TARGETS["classification_precision"],
            "latency_p95_seconds": TARGETS["latency_p95_seconds"],
        },
        "classification": {
            "labeled_n": len(y_true),
            "overall_accuracy": round(precision_overall, 4) if precision_overall is not None else None,
            "per_class_recall": per_class,
            "note": "Overall accuracy on tickets that include labels.intent; full confusion matrix in report appendix when labeled",
        },
        "latency_seconds": {
            "mean": round(statistics.mean(latencies), 4) if latencies else None,
            "p95": round(p95_sec, 4) if p95_sec is not None else None,
            "n": len(latencies),
        },
        "citation_id_validity": {
            "valid_generations": cite_ok,
            "generations_with_citations": cite_total,
            "rate": round(cite_ok / cite_total, 4) if cite_total else None,
            "note": "Automated proxy: citation doc_ids ⊆ retrieved set",
        },
        "hallucination_rate": {
            "value": None,
            "note": "Requires dual human review of ≥50 responses (Evaluation Framework); not auto-scored",
        },
        "availability_note": "Provider failures escalate per-ticket without aborting the batch (A11)",
    }

    governance = {
        "private_data_in_outbound": {
            "occurrences": pii_hits,
            "requirement": "zero",
            "pass": pii_hits == 0,
        },
        "decision_log_coverage": {
            "tickets_processed": n,
            "decision_rows_written": decisions_logged,
            "note": "Multiple decision rows per ticket (classify/route/generate/validate); coverage = every ticket logged when persist=true",
        },
        "quality_across_segments": segment_gaps,
        "confidence_calibration": calibration,
    }

    return {
        "meta": {
            "service": "CloudServe Assistant",
            "version": __version__,
            "run_started_at": run_started_at,
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "input_path": input_path,
            "targets_source": "findings D1 success table + Evaluation Framework",
        },
        "volume": volume,
        "business": business,
        "technical": technical,
        "governance": governance,
    }


def _scan_pii(text: str) -> bool:
    import re

    patterns = [
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bsk-[A-Za-z0-9]{20,}\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
    ]
    return any(re.search(p, text) for p in patterns)


def _segment_gaps(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Fairness on resolution quality (Evaluation Framework), not raw auto mix.

    Primary: among tickets with expected_route=auto_respond and not must_not,
    share that received auto_respond — gap across segments must be < FAIRNESS_MAX_GAP_PP.
    Also report raw auto rate and eligible (non-must_not, has passages) for transparency.
    """
    max_gap = get_settings().fairness_max_gap_pp

    def _bucket(key: str) -> dict[str, list[dict[str, Any]]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in records:
            buckets[str(r.get(key) or "unknown")].append(r)
        return buckets

    def _rate(items: list[dict[str, Any]], pred) -> float:
        if not items:
            return 0.0
        return sum(1 for i in items if pred(i)) / len(items)

    out: dict[str, Any] = {}
    for key in ("customer_tier", "language_fluency"):
        buckets = _bucket(key)
        raw: dict[str, float] = {}
        eligible: dict[str, float] = {}
        quality: dict[str, float] = {}
        quality_n: dict[str, int] = {}
        for seg, items in buckets.items():
            raw[seg] = _rate(items, lambda r: r.get("action") == RouteAction.AUTO_RESPOND.value)
            elig = [
                r
                for r in items
                if not (r.get("labels") or {}).get("must_not_auto_respond")
                and (r.get("passages") or [])
            ]
            eligible[seg] = _rate(
                elig, lambda r: r.get("action") == RouteAction.AUTO_RESPOND.value
            )
            q = [
                r
                for r in items
                if (r.get("labels") or {}).get("expected_route") == "auto_respond"
                and not (r.get("labels") or {}).get("must_not_auto_respond")
            ]
            quality[seg] = _rate(
                q, lambda r: r.get("action") == RouteAction.AUTO_RESPOND.value
            )
            quality_n[seg] = len(q)

        q_vals = [v for seg, v in quality.items() if quality_n.get(seg, 0) > 0]
        gap_pp = (max(q_vals) - min(q_vals)) * 100.0 if len(q_vals) >= 2 else 0.0
        out[key] = {
            "metric": "resolution_quality_on_expected_auto",
            "quality_rate": {k: round(v, 4) for k, v in quality.items()},
            "quality_n": quality_n,
            "eligible_auto_rate": {k: round(v, 4) for k, v in eligible.items()},
            "raw_auto_respond_rate": {k: round(v, 4) for k, v in raw.items()},
            "max_gap_pp": round(gap_pp, 2),
            "requirement_pp": max_gap,
            "pass": gap_pp < max_gap if len(q_vals) >= 2 else True,
        }
    return out


def _calibration_table(
    pairs: list[tuple[float, bool]], bands: int = 5
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(bands):
        low, high = i / bands, (i + 1) / bands
        group = [(c, ok) for c, ok in pairs if low <= c < high or (i == bands - 1 and c == high)]
        if not group:
            continue
        stated = sum(c for c, _ in group) / len(group)
        observed = sum(1 for _, ok in group if ok) / len(group)
        rows.append(
            {
                "band": f"{low:.1f}-{high:.1f}",
                "n": len(group),
                "mean_stated": round(stated, 4),
                "observed_accuracy": round(observed, 4),
                "gap": round(stated - observed, 4),
            }
        )
    return rows


def write_metrics_report(metrics: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    """Write metrics.json and metrics.md under output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "metrics.json"
    md_path = output_dir / "metrics.md"
    json_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_to_markdown(metrics), encoding="utf-8")
    return json_path, md_path


def _to_markdown(m: dict[str, Any]) -> str:
    meta = m["meta"]
    vol = m["volume"]
    biz = m["business"]
    tech = m["technical"]
    gov = m["governance"]
    lines = [
        "# CloudServe Assistant — Evaluation Metrics",
        "",
        f"- **Version:** {meta['version']}",
        f"- **Run started:** {meta['run_started_at']}",
        f"- **Report generated:** {meta['report_generated_at']}",
        f"- **Input:** `{meta['input_path']}`",
        f"- **Targets source:** {meta['targets_source']}",
        "",
        "## Volume",
        "",
        f"- Tickets input / processed: **{vol['tickets_input']}** / **{vol['tickets_processed']}**",
        f"- Silent drops: **{vol['silent_drops']}**",
        f"- Action counts: `{vol['action_counts']}`",
        f"- Tickets with stage errors: **{vol['tickets_with_errors']}**",
        f"- allow_generate: `{vol['allow_generate']}`",
        "",
        "## Business outcomes (success table)",
        "",
        f"| Measure | Target | Achieved |",
        f"|---------|--------|----------|",
        f"| Route auto_respond rate | (informational) | {biz['route_auto_respond_pct']}% |",
        f"| First contact resolution | ≥{biz['targets']['fcr_pct']}% | {biz['first_contact_resolution_pct']} |",
        f"| Escalation rate | ≤{biz['targets']['escalation_pct']}% | {biz['escalation_rate_pct']}% |",
        f"| Mean time to first reply | <{biz['targets']['reply_mean_minutes']} min | {biz['time_to_first_reply_minutes']['mean']} min |",
        f"| CSAT proxy | ≥{biz['targets']['csat']} | {biz['csat_proxy']['value']} ({biz['csat_proxy']['note']}) |",
        "",
        f"_FCR definition:_ {biz['fcr_definition']}",
        f"_FCR claim allowed:_ `{biz.get('fcr_claim_allowed')}`",
        "",
        "## Technical performance",
        "",
        f"- Classification labeled n: {tech['classification']['labeled_n']}; "
        f"overall accuracy: {tech['classification']['overall_accuracy']}",
        f"- Latency mean / p95 (s): {tech['latency_seconds']['mean']} / {tech['latency_seconds']['p95']}",
        f"- Citation ID validity: {tech['citation_id_validity']}",
        f"- Hallucination: {tech['hallucination_rate']['note']}",
        "",
        "## Governance conditions",
        "",
        f"- PII occurrences in outbound: **{gov['private_data_in_outbound']['occurrences']}** "
        f"(pass={gov['private_data_in_outbound']['pass']})",
        f"- Decision rows written: **{gov['decision_log_coverage']['decision_rows_written']}** "
        f"for {gov['decision_log_coverage']['tickets_processed']} tickets",
        f"- Segment gaps: `{gov['quality_across_segments']}`",
        f"- Calibration bands: `{gov['confidence_calibration']}`",
        "",
    ]
    return "\n".join(lines) + "\n"
