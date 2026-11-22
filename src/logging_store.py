"""SQLite decision log (Governance Framework fields, CloudServe A8)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import Column, Float, MetaData, String, Table, Text, create_engine, select
from sqlalchemy.engine import Engine

from src.config import get_settings
from src.models import PipelineResult

_metadata = MetaData()

decisions = Table(
    "decisions",
    _metadata,
    Column("decision_id", String(64), primary_key=True),
    Column("created_at", String(64), nullable=False),
    Column("ticket_id", String(128), nullable=False),
    Column("stage", String(64), nullable=False),
    Column("prediction", Text),
    Column("confidence", Float),
    Column("threshold", Float),
    Column("action_taken", String(64), nullable=False),
    Column("reason", Text, nullable=False),
    Column("sources_used", Text),
    Column("guardrails", Text),
    Column("prompt_version", String(128)),
    Column("requirement_ids", Text),
    Column("input_summary", Text),
    Column("model_name", String(256)),
    Column("alternatives", Text),
)

_engine: Optional[Engine] = None


def _sqlite_url(url: str) -> str:
    # Ensure parent dir exists for relative sqlite paths.
    if url.startswith("sqlite:///"):
        raw = url[len("sqlite:///") :]
        if raw.startswith("./") or (not raw.startswith("/") and ":" not in raw[:2]):
            path = get_settings().root / raw
            path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{path}"
    return url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        url = _sqlite_url(settings.database_url)
        _engine = create_engine(url, future=True)
        _metadata.create_all(_engine)
    return _engine


def reset_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def log_decision(
    *,
    ticket_id: str,
    stage: str,
    action_taken: str,
    reason: str,
    prediction: Any = None,
    confidence: Optional[float] = None,
    threshold: Optional[float] = None,
    sources_used: Any = None,
    guardrails: Any = None,
    prompt_version: Optional[str] = None,
    requirement_ids: Optional[list[str]] = None,
    input_summary: Optional[str] = None,
    model_name: Optional[str] = None,
    alternatives: Any = None,
) -> str:
    decision_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            decisions.insert().values(
                decision_id=decision_id,
                created_at=created_at,
                ticket_id=ticket_id,
                stage=stage,
                prediction=json.dumps(prediction) if prediction is not None else None,
                confidence=confidence,
                threshold=threshold,
                action_taken=action_taken,
                reason=reason,
                sources_used=json.dumps(sources_used) if sources_used is not None else None,
                guardrails=json.dumps(guardrails) if guardrails is not None else None,
                prompt_version=prompt_version,
                requirement_ids=json.dumps(requirement_ids or []),
                input_summary=input_summary,
                model_name=model_name,
                alternatives=json.dumps(alternatives) if alternatives is not None else None,
            )
        )
    return decision_id


def log_pipeline_result(result: PipelineResult, ticket_text_summary: str = "") -> list[str]:
    """Write classification, routing, generation, validation rows for one ticket."""
    ids: list[str] = []
    clf = result.classification
    if clf is not None:
        ids.append(
            log_decision(
                ticket_id=result.ticket_id,
                stage="classification",
                action_taken="classified",
                reason=f"source={clf.source}",
                prediction={"intent": clf.intent, "urgency": clf.urgency.value},
                confidence=clf.confidence,
                alternatives=[a.model_dump() for a in clf.alternatives],
                input_summary=ticket_text_summary[:500],
                requirement_ids=["FR-2", "A3"],
            )
        )

    if result.route is not None:
        route_reason = result.route.reason
        if result.escalation_summary and result.action.value == "escalate":
            route_reason = f"{route_reason}\n---\n{result.escalation_summary}"
        ids.append(
            log_decision(
                ticket_id=result.ticket_id,
                stage="routing",
                action_taken=result.route.action.value,
                reason=route_reason,
                confidence=clf.confidence if clf else None,
                threshold=result.route.threshold_applied,
                sources_used=[{"doc_id": p.doc_id, "score": p.score} for p in result.passages],
                prediction={
                    "grounded_override": result.route.grounded_override,
                    "kill_switch": result.route.kill_switch,
                },
                requirement_ids=["FR-4", "A5"],
            )
        )

    if result.generation is not None:
        ids.append(
            log_decision(
                ticket_id=result.ticket_id,
                stage="generation",
                action_taken="generated",
                reason="cached" if result.generation.cached else "live",
                prediction={"citation_doc_ids": result.generation.citation_doc_ids},
                sources_used=[{"doc_id": p.doc_id, "score": p.score} for p in result.passages],
                prompt_version=get_settings().prompt_version,
                model_name=result.generation.model,
                requirement_ids=["FR-5", "A6"],
            )
        )

    if result.guardrails:
        guard_map = {
            g.name: {"passed": g.passed, "detail": g.detail} for g in result.guardrails
        }
        ids.append(
            log_decision(
                ticket_id=result.ticket_id,
                stage="validation",
                action_taken=result.action.value,
                reason="guardrail evaluation",
                guardrails=guard_map,
                prompt_version=get_settings().prompt_version,
                model_name=result.generation.model if result.generation else None,
                prediction={
                    "model": {
                        "name": result.generation.model if result.generation else None,
                        "version": get_settings().prompt_version,
                    }
                },
                requirement_ids=["FR-6", "A7"],
            )
        )
    return ids


def count_decisions(ticket_id: Optional[str] = None) -> int:
    engine = get_engine()
    stmt = select(decisions.c.decision_id)
    if ticket_id:
        stmt = stmt.where(decisions.c.ticket_id == ticket_id)
    with engine.connect() as conn:
        return len(conn.execute(stmt).fetchall())


def export_decisions_jsonl(
    path: Path,
    *,
    ticket_ids: list[str] | None = None,
) -> int:
    """Export decision rows. Optionally restrict to ticket_ids from one harness run."""
    engine = get_engine()
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    stmt = select(decisions)
    id_set = {str(t) for t in ticket_ids} if ticket_ids is not None else None
    with engine.connect() as conn, path.open("w", encoding="utf-8") as fh:
        for row in conn.execute(stmt).mappings():
            if id_set is not None and str(row["ticket_id"]) not in id_set:
                continue
            fh.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
            n += 1
    return n
