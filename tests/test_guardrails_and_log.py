"""Guardrail block (A7) and decision log tests — no live LLM required."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import get_settings
from src.guardrails import validate
from src.ingest import ingest
from src.logging_store import count_decisions, log_pipeline_result, reset_engine
from src.models import (
    Classification,
    GenerationResult,
    Passage,
    PipelineResult,
    RouteAction,
    RouteDecision,
    Urgency,
)

from tests.conftest import development_tickets, documentation_json

PACK = development_tickets()
DOCS = documentation_json()


def _real_doc_id() -> str:
    docs = json.loads(DOCS.read_text(encoding="utf-8"))
    return str(docs[0]["doc_id"])


def _real_ticket() -> dict:
    return json.loads(PACK.read_text(encoding="utf-8"))[0]


def test_guardrail_blocks_fabricated_citation(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'decisions.db'}")
    get_settings.cache_clear()
    reset_engine()

    doc_id = _real_doc_id()
    passages = [Passage(doc_id=doc_id, text="resolution steps", score=0.9)]
    # Engineered bad generation: cites an ID that was not retrieved (A7)
    generation = GenerationResult(
        answer="Here is the fix. See the docs.",
        citation_doc_ids=["DOC-FAKE-NOT-IN-CORPUS"],
        model="test",
        cached=False,
    )
    results, blocked = validate(generation, passages)
    assert blocked is True
    assert any(r.name == "citation_ids" and not r.passed for r in results)


def test_guardrail_blocks_pii_pattern():
    doc_id = _real_doc_id()
    passages = [Passage(doc_id=doc_id, text="ok", score=0.8)]
    generation = GenerationResult(
        answer="Use key sk-abcdefghijklmnopqrstuvwxyz123456",
        citation_doc_ids=[doc_id],
    )
    results, blocked = validate(generation, passages)
    assert blocked is True
    assert any(r.name == "pii" and not r.passed for r in results)


def test_decision_log_writes_rows(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'decisions.db'}")
    get_settings.cache_clear()
    reset_engine()

    ticket = ingest(_real_ticket())
    doc_id = _real_doc_id()
    result = PipelineResult(
        ticket_id=ticket.ticket_id,
        classification=Classification(
            intent="unclear_request",
            urgency=Urgency.LOW,
            confidence=0.4,
            source="model",
        ),
        passages=[Passage(doc_id=doc_id, text="x", score=0.5)],
        route=RouteDecision(
            action=RouteAction.ESCALATE,
            reason="low confidence",
            threshold_applied=0.8,
        ),
        action=RouteAction.ESCALATE,
    )
    ids = log_pipeline_result(result, ticket_text_summary=ticket.text_for_model()[:100])
    assert len(ids) >= 2
    assert count_decisions(ticket.ticket_id) >= 2
