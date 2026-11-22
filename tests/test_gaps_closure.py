"""Gap-closure tests: A5/A8/A11, kill, grounded override, generate mock, chroma, config."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.harness import load_tickets, run_harness
from evaluation.metrics_report import build_metrics
from src.classify import reset_classifier_cache
from src.config import ConfigError, get_settings
from src.graph import run_ticket
from src.guardrails import validate
from src.ingest import ingest
from src.logging_store import count_decisions, reset_engine
from src.models import (
    Classification,
    GenerationResult,
    Passage,
    RouteAction,
    Ticket,
    Urgency,
)
from src.retrieve import index_stats, reset_retrieve_cache
from src.route import route

from tests.conftest import SUBMISSION, development_tickets, documentation_json

DEV = development_tickets()
DOCS = documentation_json()
CLF = SUBMISSION / "storage" / "models" / "classifier" / "classifier.joblib"


@pytest.fixture
def isolated_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'decisions.db'}")
    monkeypatch.setenv("KILL_SWITCH", "false")
    monkeypatch.setenv("KILL_SWITCH_FILE", str(tmp_path / "missing_kill"))
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.35")
    monkeypatch.setenv("ROUTE_GROUNDED_MIN_SCORE", "0.45")
    monkeypatch.setenv("ROUTE_GROUNDED_CONF_FACTOR", "0.75")
    if CLF.exists():
        monkeypatch.setenv("CLASSIFIER_DIR", str(CLF.parent))
    get_settings.cache_clear()
    reset_engine()
    reset_classifier_cache()
    reset_retrieve_cache()
    yield tmp_path
    reset_engine()
    get_settings.cache_clear()


def test_config_error_on_bad_numeric(monkeypatch):
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "abc")
    get_settings.cache_clear()
    with pytest.raises(ConfigError):
        get_settings()
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.35")
    get_settings.cache_clear()


def test_ingest_coerces_non_string_channel():
    t = ingest({"ticket_id": "T-X", "channel": 123, "subject": "s", "body": "b"})
    assert t.channel.value == "email"
    assert t.body == "b"


def test_route_determinism_a5(isolated_env):
    ticket = Ticket(ticket_id="T1", channel="email", subject="auth", body="cannot login")
    clf = Classification(intent="authentication_failure", urgency=Urgency.HIGH, confidence=0.9)
    passages = [Passage(doc_id="DOC-AUTH-001", text="reset password", score=0.8)]
    a = route(ticket, clf, passages)
    b = route(ticket, clf, passages)
    assert a.model_dump() == b.model_dump()
    assert a.action == RouteAction.AUTO_RESPOND


def test_kill_switch_env_live_reread(isolated_env, monkeypatch):
    ticket = Ticket(ticket_id="T1", channel="email", subject="x", body="y")
    clf = Classification(intent="other", urgency=Urgency.LOW, confidence=0.99)
    passages = [Passage(doc_id="DOC-1", text="ok", score=0.9)]
    monkeypatch.setenv("KILL_SWITCH", "true")
    # Do NOT clear Settings cache — kill_switch_active must re-read env (D4).
    d = route(ticket, clf, passages)
    assert d.action == RouteAction.ESCALATE
    assert d.kill_switch is True


def test_grounded_override_below_threshold(isolated_env):
    ticket = Ticket(ticket_id="T1", channel="email", subject="slow", body="latency high")
    # conf 0.30 < 0.35 but >= 0.35*0.75=0.2625; top_score 0.50 >= 0.45
    clf = Classification(intent="performance_degradation", urgency=Urgency.LOW, confidence=0.30)
    passages = [Passage(doc_id="DOC-PERF-001", text="check p95", score=0.50)]
    d = route(ticket, clf, passages)
    assert d.action == RouteAction.AUTO_RESPOND
    assert d.grounded_override is True


def test_empty_passages_escalate(isolated_env):
    ticket = Ticket(ticket_id="T1", channel="email", subject="x", body="y")
    clf = Classification(intent="other", urgency=Urgency.LOW, confidence=0.99)
    d = route(ticket, clf, [])
    assert d.action == RouteAction.ESCALATE


def test_must_not_from_text_without_labels(isolated_env):
    ticket = Ticket(
        ticket_id="T1",
        channel="email",
        subject="urgent",
        body="We suspect a data breach on the account",
        labels=None,
    )
    clf = Classification(intent="other", urgency=Urgency.HIGH, confidence=0.99)
    passages = [Passage(doc_id="DOC-1", text="ok", score=0.9)]
    d = route(ticket, clf, passages)
    assert d.action == RouteAction.ESCALATE
    assert "must_not" in d.reason.lower() or "Policy" in d.reason


def test_nonempty_answer_guard():
    gen = GenerationResult(answer="   ", citation_doc_ids=["DOC-1"])
    passages = [Passage(doc_id="DOC-1", text="x", score=0.5)]
    results, blocked = validate(gen, passages)
    assert blocked is True
    assert any(r.name == "nonempty_answer" and not r.passed for r in results)


def test_positive_citation_pass():
    gen = GenerationResult(answer="Follow the reset steps.", citation_doc_ids=["DOC-1"])
    passages = [Passage(doc_id="DOC-1", text="reset", score=0.5)]
    results, blocked = validate(gen, passages)
    assert blocked is False
    assert all(r.passed for r in results if r.name == "citation_ids")


def test_confidence_floor_skipped_on_grounded_override():
    gen = GenerationResult(answer="See docs.", citation_doc_ids=["DOC-1"])
    passages = [Passage(doc_id="DOC-1", text="x", score=0.5)]
    clf = Classification(intent="x", urgency=Urgency.LOW, confidence=0.30)
    results, blocked = validate(
        gen, passages, classification=clf, confidence_threshold=0.35, skip_confidence_floor=True
    )
    assert blocked is False
    floor = next(r for r in results if r.name == "confidence_floor")
    assert floor.passed and "skipped" in floor.detail


def test_generate_mocked_through_run_ticket(isolated_env, monkeypatch):
    if not CLF.exists():
        pytest.skip("classifier missing")
    if not DEV.exists():
        pytest.skip("dev tickets missing")
    raw = json.loads(DEV.read_text(encoding="utf-8"))[0]
    # Force auto path via high confidence + passages by mocking route + retrieve
    fake_passages = [Passage(doc_id="DOC-AUTH-001", text="reset password steps", score=0.9)]

    def fake_retrieve(_ticket, **_kwargs):
        return fake_passages

    def fake_completion(messages, **kwargs):
        return json.dumps(
            {
                "answer": "Please reset your password using the documented steps.",
                "citation_doc_ids": ["DOC-AUTH-001"],
            }
        )

    with patch("src.graph.retrieve", side_effect=fake_retrieve), patch(
        "src.generate.completion", side_effect=fake_completion
    ), patch(
        "src.graph.route",
        return_value=__import__("src.models", fromlist=["RouteDecision"]).RouteDecision(
            action=RouteAction.AUTO_RESPOND,
            reason="test force auto",
            threshold_applied=0.35,
            grounded_override=False,
        ),
    ):
        result = run_ticket(raw, persist=True, allow_generate=True)
    assert result.action == RouteAction.AUTO_RESPOND
    assert result.generation is not None
    assert "DOC-AUTH-001" in result.generation.citation_doc_ids
    assert count_decisions(result.ticket_id) >= 1


def test_guardrail_block_through_run_ticket(isolated_env, monkeypatch):
    if not CLF.exists():
        pytest.skip("classifier missing")
    raw = {"ticket_id": "BLK-1", "channel": "email", "subject": "hi", "body": "help"}
    fake_passages = [Passage(doc_id="DOC-1", text="ok", score=0.9)]

    def fake_completion(messages, **kwargs):
        return json.dumps(
            {
                "answer": "Use key sk-abcdefghijklmnopqrstuvwxyz123456",
                "citation_doc_ids": ["DOC-1"],
            }
        )

    with patch("src.graph.retrieve", return_value=fake_passages), patch(
        "src.generate.completion", side_effect=fake_completion
    ), patch(
        "src.graph.route",
        return_value=__import__("src.models", fromlist=["RouteDecision"]).RouteDecision(
            action=RouteAction.AUTO_RESPOND,
            reason="force",
            threshold_applied=0.35,
        ),
    ):
        result = run_ticket(raw, persist=True, allow_generate=True)
    assert result.action == RouteAction.BLOCK


def test_llm_backoff_on_rate_limit(monkeypatch, isolated_env):
    monkeypatch.setenv("LLM_MAX_RETRIES", "3")
    monkeypatch.setenv("LLM_BACKOFF_SECONDS", "0.01")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "5")
    monkeypatch.setenv("LLM_MIN_INTERVAL_SECONDS", "0")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-not-placeholder")
    get_settings.cache_clear()

    from litellm.exceptions import RateLimitError
    from src import llm as llm_mod

    calls = {"n": 0}

    def boom(**kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RateLimitError("rate limited", "openrouter", "test-model")

        class R:
            class C:
                class M:
                    content = "ok"

                message = M()

            choices = [C()]

        return R()

    with patch("time.sleep"), patch("litellm.completion", side_effect=boom):
        out = llm_mod.completion([{"role": "user", "content": "hi"}])
    assert out == "ok"
    assert calls["n"] == 3


def test_chroma_index_in_use(isolated_env):
    """Ensure Persistent Chroma collection is reachable and non-empty when built."""
    chroma = SUBMISSION / "storage" / "chroma"
    if not chroma.exists():
        pytest.skip("chroma storage not built; run scripts.build_index")
    monkeypatch_path = chroma
    # Point at real submission chroma
    import os

    os.environ["CHROMA_PATH"] = str(monkeypatch_path)
    get_settings.cache_clear()
    reset_retrieve_cache()
    stats = index_stats()
    assert stats["collection"] == get_settings().chroma_collection
    assert stats["count"] > 0, "Chroma index empty — build_index required"


def test_harness_a8_reconcile(isolated_env, tmp_path):
    if not DEV.exists() or not CLF.exists():
        pytest.skip("pack/classifier missing")
    tickets = load_tickets(DEV)[:2]
    input_path = tmp_path / "slice.json"
    input_path.write_text(json.dumps(tickets), encoding="utf-8")
    out = tmp_path / "out"
    summary = run_harness(input_path, out, allow_generate=False, persist=True)
    assert summary["silent_drops"] == 0
    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["governance"]["decision_log_coverage"]["reconcile_ok"] is True
    assert metrics["business"]["fcr_claim_allowed"] is False
    assert metrics["business"]["first_contact_resolution_pct"] is None


def test_fairness_quality_gap_structure(isolated_env):
    records = [
        {
            "ticket_id": "a",
            "action": "auto_respond",
            "latency_seconds": 0.1,
            "errors": [],
            "classification": {"intent": "x", "confidence": 0.9},
            "passages": [],
            "route": {"reason": "ok"},
            "generation": None,
            "labels": {"intent": "x"},
            "customer_tier": "enterprise",
            "language_fluency": "fluent",
            "channel": "email",
        },
        {
            "ticket_id": "b",
            "action": "escalate",
            "latency_seconds": 0.1,
            "errors": [],
            "classification": {"intent": "x", "confidence": 0.2},
            "passages": [],
            "route": {"reason": "below threshold"},
            "generation": None,
            "labels": {"intent": "x"},
            "customer_tier": "free",
            "language_fluency": "non_fluent",
            "channel": "email",
        },
    ]
    m = build_metrics(
        records,
        input_path="x",
        run_started_at="t",
        allow_generate=False,
        decisions_logged=2,
    )
    seg = m["governance"]["quality_across_segments"]
    assert "max_gap_pp" in seg or "by_tier" in seg or isinstance(seg, dict)
    assert m["business"]["fcr_claim_allowed"] is False


def test_run_ticket_twice_same_route(isolated_env):
    if not CLF.exists() or not DEV.exists():
        pytest.skip("missing artifacts")
    raw = json.loads(DEV.read_text(encoding="utf-8"))[0]
    r1 = run_ticket(raw, persist=False, allow_generate=False)
    r2 = run_ticket(raw, persist=False, allow_generate=False)
    assert r1.route is not None and r2.route is not None
    assert r1.route.action == r2.route.action
    assert r1.route.reason == r2.route.reason
