"""Emit Stage-1 aggregate tables from ticket JSON. No full body dumps."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _hist(row: dict, key: str):
    return (row.get("history") or {}).get(key)


def _seg_summary(rows: list[dict]) -> dict:
    """Aggregate human-baseline outcomes for one segment (counts/means only)."""
    n = len(rows)
    csat = [_hist(r, "csat_rating") for r in rows if isinstance(_hist(r, "csat_rating"), (int, float))]
    mins = [_hist(r, "resolution_time_minutes") for r in rows if isinstance(_hist(r, "resolution_time_minutes"), (int, float))]
    return {
        "n": n,
        "fcr": round(sum(1 for r in rows if _hist(r, "first_contact_resolution") is True) / n, 3) if n else None,
        "escalated": round(sum(1 for r in rows if _hist(r, "escalated") is True) / n, 3) if n else None,
        "repeat_contact": round(sum(1 for r in rows if _hist(r, "repeat_contact") is True) / n, 3) if n else None,
        "mean_csat": round(sum(csat) / len(csat), 2) if csat else None,
        "mean_resolution_min": round(sum(mins) / len(mins), 1) if mins else None,
        "sum_resolution_min": int(sum(mins)) if mins else 0,
    }


def _print_history_aggregates(rows: list[dict]) -> None:
    """Additive Stage-1 aggregates from the `history` block (no ticket text)."""
    overall = _seg_summary(rows)
    print("history_overall=", overall)
    total_min = overall["sum_resolution_min"] or 1

    def by(key_fn) -> dict:
        groups: dict = {}
        for r in rows:
            groups.setdefault(key_fn(r), []).append(r)
        return {k: _seg_summary(v) for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))}

    print("history_by_tier=", by(lambda r: r.get("customer_tier")))
    print("history_by_fluency=", by(lambda r: r.get("language_fluency")))
    print("history_by_urgency=", by(lambda r: (r.get("labels") or {}).get("urgency")))
    print("history_by_channel=", by(lambda r: r.get("channel")))
    print("history_by_answerable=", by(lambda r: (r.get("labels") or {}).get("answerable_from_docs")))
    print("history_by_must_not_auto=", by(lambda r: (r.get("labels") or {}).get("must_not_auto_respond")))
    by_intent = by(lambda r: (r.get("labels") or {}).get("intent"))
    print("history_by_intent=", by_intent)
    effort = {
        k: {"volume_share": round(v["n"] / len(rows), 3), "effort_share_by_resolution_min": round(v["sum_resolution_min"] / total_min, 3)}
        for k, v in by_intent.items()
    }
    print("effort_share_by_intent=", effort)

    esc = [r for r in rows if _hist(r, "escalated") is True]
    esc_ans = [r for r in esc if (r.get("labels") or {}).get("answerable_from_docs") is True]
    esc_ans_ok = [r for r in esc_ans if (r.get("labels") or {}).get("must_not_auto_respond") is not True]
    print(
        "escalation_composition=",
        {
            "escalated": len(esc),
            "escalated_and_answerable_from_docs": len(esc_ans),
            "escalated_answerable_and_not_must_not": len(esc_ans_ok),
            "share_answerable_of_escalated": round(len(esc_ans) / len(esc), 3) if esc else None,
            "share_answerable_not_must_not_of_escalated": round(len(esc_ans_ok) / len(esc), 3) if esc else None,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Discovery aggregates for CloudServe Assistant")
    parser.add_argument("--input", required=True, help="Path to tickets JSON array")
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    n = len(rows)
    channels = Counter(r.get("channel") for r in rows)
    intents = Counter((r.get("labels") or {}).get("intent") for r in rows)
    urgencies = Counter((r.get("labels") or {}).get("urgency") for r in rows)
    tiers = Counter(r.get("customer_tier") for r in rows)
    fluency = Counter(r.get("language_fluency") for r in rows)

    answerable = sum(1 for r in rows if (r.get("labels") or {}).get("answerable_from_docs") is True)
    must_not = sum(1 for r in rows if (r.get("labels") or {}).get("must_not_auto_respond") is True)
    fcr = sum(1 for r in rows if (r.get("history") or {}).get("first_contact_resolution") is True)
    escalated = sum(1 for r in rows if (r.get("history") or {}).get("escalated") is True)

    print(f"total_tickets={n}")
    print("channel_counts=", dict(channels))
    print("intent_counts=", dict(intents))
    print("urgency_counts=", dict(urgencies))
    print("tier_counts=", dict(tiers))
    print("fluency_counts=", dict(fluency))
    if n:
        print(f"answerable_from_docs_rate={answerable / n:.3f}")
        print(f"must_not_auto_respond_rate={must_not / n:.3f}")
        print(f"history_fcr_rate={fcr / n:.3f}")
        print(f"history_escalated_rate={escalated / n:.3f}")
        _print_history_aggregates(rows)


if __name__ == "__main__":
    main()
