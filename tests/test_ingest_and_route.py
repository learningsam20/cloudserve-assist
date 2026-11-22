"""Ingest + route tests using Capstone development tickets (real channels)."""

from __future__ import annotations

import json

from src.ingest import ingest
from src.models import Classification, Passage, RouteAction, Urgency
from src.route import route
from tests.conftest import development_tickets

PACK = development_tickets()


def _one_per_channel() -> dict[str, dict]:
    rows = json.loads(PACK.read_text(encoding="utf-8"))
    found: dict[str, dict] = {}
    for row in rows:
        ch = row.get("channel")
        if ch and ch not in found:
            found[ch] = row
        if len(found) == 4:
            break
    return found


def test_ingest_four_channels_from_pack():
    samples = _one_per_channel()
    assert set(samples) == {"email", "chat", "docs_comment", "forum"}
    for ch, raw in samples.items():
        t = ingest(raw)
        assert t.channel.value == ch
        assert t.ticket_id == raw["ticket_id"]


def test_route_escalates_on_low_confidence(monkeypatch, tmp_path):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.80")
    monkeypatch.setenv("KILL_SWITCH", "false")
    monkeypatch.setenv("KILL_SWITCH_FILE", str(tmp_path / "missing_kill"))
    from src.config import get_settings

    get_settings.cache_clear()

    raw = next(iter(_one_per_channel().values()))
    ticket = ingest(raw)
    clf = Classification(intent="other", urgency=Urgency.LOW, confidence=0.2, source="model")
    passages = [Passage(doc_id="DOC-AUTH-001", text="from-index", score=0.9)]
    decision = route(ticket, clf, passages)
    assert decision.action == RouteAction.ESCALATE


def test_route_auto_respond_when_confident(monkeypatch, tmp_path):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.50")
    monkeypatch.setenv("KILL_SWITCH", "false")
    monkeypatch.setenv("KILL_SWITCH_FILE", str(tmp_path / "missing_kill"))
    from src.config import get_settings

    get_settings.cache_clear()

    raw = next(iter(_one_per_channel().values()))
    ticket = ingest(raw)
    clf = Classification(intent="auth", urgency=Urgency.MEDIUM, confidence=0.9, source="model")
    passages = [Passage(doc_id="DOC-AUTH-001", text="from-index", score=0.9)]
    decision = route(ticket, clf, passages)
    assert decision.action == RouteAction.AUTO_RESPOND
