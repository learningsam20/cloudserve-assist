"""Unattended evaluation harness (A9–A11).

Usage:
  python -m evaluation.harness --input <tickets.json> --output <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.graph import run_ticket
from src.logging_store import count_decisions, export_decisions_jsonl, reset_engine
from src.models import PipelineResult, RouteAction

from evaluation.metrics_report import build_metrics, write_metrics_report


def load_tickets(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "tickets" in raw and isinstance(raw["tickets"], list):
        return raw["tickets"]
    raise ValueError(f"Unsupported tickets JSON shape in {path}")


def _record_from_result(
    result: PipelineResult,
    *,
    latency_seconds: float,
    raw_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw = raw_ticket or {}
    return {
        "ticket_id": result.ticket_id,
        "action": result.action.value if result.action else None,
        "latency_seconds": latency_seconds,
        "errors": list(result.errors),
        "classification": result.classification.model_dump() if result.classification else None,
        "passages": [p.model_dump() for p in result.passages],
        "route": result.route.model_dump() if result.route else None,
        "generation": result.generation.model_dump() if result.generation else None,
        "guardrails": [g.model_dump() for g in result.guardrails],
        "labels": raw.get("labels"),
        "customer_tier": raw.get("customer_tier"),
        "language_fluency": raw.get("language_fluency"),
        "channel": raw.get("channel"),
    }


def process_one(
    ticket: Any,
    *,
    allow_generate: bool,
    persist: bool,
) -> dict[str, Any]:
    """Process a single ticket; never raises — always returns a record with an action."""
    started = time.perf_counter()
    raw: dict[str, Any] | None = ticket if isinstance(ticket, dict) else None
    try:
        if not isinstance(ticket, dict):
            raise TypeError(f"ticket must be an object, got {type(ticket).__name__}")
        result = run_ticket(ticket, persist=persist, allow_generate=allow_generate)
        if result.action is None:
            result.action = RouteAction.ESCALATE
            result.errors.append("missing_action_forced_escalate")
        return _record_from_result(
            result, latency_seconds=time.perf_counter() - started, raw_ticket=raw
        )
    except Exception as exc:  # noqa: BLE001 — A11: batch must not abort
        tid = "unknown"
        if isinstance(ticket, dict):
            tid = str(ticket.get("ticket_id") or "unknown")
        if persist:
            try:
                from src.logging_store import log_decision

                log_decision(
                    ticket_id=tid,
                    stage="routing",
                    action_taken=RouteAction.ESCALATE.value,
                    reason=f"Harness caught failure: {exc}",
                    threshold=0.0,
                    requirement_ids=["A8", "A11"],
                )
            except Exception:  # noqa: BLE001
                pass
        return {
            "ticket_id": tid,
            "action": RouteAction.ESCALATE.value,
            "latency_seconds": time.perf_counter() - started,
            "errors": [f"harness_uncaught: {exc}", traceback.format_exc(limit=3)],
            "classification": None,
            "passages": [],
            "route": {
                "action": RouteAction.ESCALATE.value,
                "reason": f"Harness caught failure: {exc}",
                "threshold_applied": 0.0,
                "kill_switch": False,
                "grounded_override": False,
            },
            "generation": None,
            "guardrails": [],
            "labels": raw.get("labels") if raw else None,
            "customer_tier": raw.get("customer_tier") if raw else None,
            "language_fluency": raw.get("language_fluency") if raw else None,
            "channel": raw.get("channel") if raw else None,
        }


def run_harness(
    input_path: Path,
    output_dir: Path,
    *,
    allow_generate: bool = True,
    persist: bool = True,
    limit: int | None = None,
) -> dict[str, Any]:
    tickets = load_tickets(input_path)
    if limit is not None:
        tickets = tickets[: max(0, limit)]

    output_dir.mkdir(parents=True, exist_ok=True)
    run_started = datetime.now(timezone.utc).isoformat()
    decisions_before = count_decisions() if persist else 0

    records: list[dict[str, Any]] = []
    results_path = output_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as fh:
        for ticket in tickets:
            rec = process_one(ticket, allow_generate=allow_generate, persist=persist)
            records.append(rec)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    decisions_after = count_decisions() if persist else 0
    decisions_logged = max(0, decisions_after - decisions_before)

    # A8 coverage: every processed ticket_id should appear in the decision log when persist=True
    ticket_ids = [str(r.get("ticket_id") or "unknown") for r in records]
    missing_log: list[str] = []
    if persist:
        from src.logging_store import count_decisions as _cd

        for tid in ticket_ids:
            if _cd(tid) < 1:
                missing_log.append(tid)

    metrics = build_metrics(
        records,
        input_path=str(input_path),
        run_started_at=run_started,
        allow_generate=allow_generate,
        decisions_logged=decisions_logged,
    )
    try:
        from src.config import get_settings

        metrics.setdefault("meta", {})["retrieval_mode"] = get_settings().retrieval_mode
    except Exception:  # noqa: BLE001
        metrics.setdefault("meta", {})["retrieval_mode"] = "unknown"
    metrics.setdefault("governance", {}).setdefault("decision_log_coverage", {})
    metrics["governance"]["decision_log_coverage"]["tickets_missing_decision_row"] = missing_log
    metrics["governance"]["decision_log_coverage"]["reconcile_ok"] = len(missing_log) == 0
    json_path, md_path = write_metrics_report(metrics, output_dir)

    export_path = output_dir / "decisions_export.jsonl"
    exported = 0
    if persist:
        try:
            # Scope export to ticket_ids from this run (shared SQLite accumulates otherwise).
            exported = export_decisions_jsonl(export_path, ticket_ids=ticket_ids)
        except TypeError:
            try:
                exported = export_decisions_jsonl(export_path)
            except Exception as exc:  # noqa: BLE001
                metrics.setdefault("volume", {})["decision_export_error"] = str(exc)
        except Exception as exc:  # noqa: BLE001
            metrics.setdefault("volume", {})["decision_export_error"] = str(exc)

    summary = {
        "tickets": len(records),
        "silent_drops": metrics["volume"]["silent_drops"],
        "metrics_json": str(json_path),
        "metrics_md": str(md_path),
        "results_jsonl": str(results_path),
        "decisions_exported": exported,
        "action_counts": metrics["volume"]["action_counts"],
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CloudServe Assistant evaluation harness")
    parser.add_argument("--input", required=True, type=Path, help="Path to tickets JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output directory for results")
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Skip LLM generate (classify/retrieve/route only); useful without API key",
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Do not write decision-log rows during this run",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap on tickets processed (dev/smoke only)",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    # Fresh engine binding if DATABASE_URL changed between runs/tests
    reset_engine()

    summary = run_harness(
        args.input,
        args.output,
        allow_generate=not args.no_generate,
        persist=not args.no_persist,
        limit=args.limit,
    )
    print(json.dumps(summary, indent=2))
    if summary["silent_drops"]:
        print("error: silent drops detected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
