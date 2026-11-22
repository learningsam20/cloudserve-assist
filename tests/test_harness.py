"""Harness dry-run and resilience (A9–A11) using reference datasets pack tickets."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation.harness import load_tickets, run_harness
from src.classify import reset_classifier_cache
from src.config import get_settings
from src.logging_store import reset_engine
from src.retrieve import reset_retrieve_cache

from tests.conftest import SUBMISSION, development_tickets

DEV = development_tickets()
CLF = SUBMISSION / "storage" / "models" / "classifier" / "classifier.joblib"


@pytest.fixture
def harness_env(monkeypatch, tmp_path):
    if not DEV.exists():
        pytest.skip("development_tickets.json missing")
    if not CLF.exists():
        pytest.skip("classifier artifact not trained")
    monkeypatch.setenv("CLASSIFIER_DIR", str(CLF.parent))
    monkeypatch.setenv("KILL_SWITCH", "false")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'decisions.db'}")
    get_settings.cache_clear()
    reset_engine()
    reset_classifier_cache()
    reset_retrieve_cache()
    yield tmp_path
    reset_engine()
    get_settings.cache_clear()


def test_harness_dry_run_no_silent_drops(harness_env, tmp_path):
    tickets = load_tickets(DEV)[:3]
    input_path = tmp_path / "slice.json"
    input_path.write_text(json.dumps(tickets), encoding="utf-8")
    out = tmp_path / "out"

    summary = run_harness(
        input_path,
        out,
        allow_generate=False,
        persist=True,
    )

    assert summary["tickets"] == 3
    assert summary["silent_drops"] == 0
    assert (out / "metrics.json").exists()
    assert (out / "metrics.md").exists()
    assert (out / "results.jsonl").exists()

    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert "volume" in metrics and "business" in metrics
    assert "technical" in metrics and "governance" in metrics
    assert metrics["volume"]["tickets_processed"] == 3

    lines = (out / "results.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    for line in lines:
        rec = json.loads(line)
        assert rec["action"] in {"auto_respond", "escalate", "block"}


def test_harness_continues_on_malformed_ticket(harness_env, tmp_path):
    """A11: malformed mid-batch must not abort; ticket escalated/logged."""
    good = load_tickets(DEV)[:2]
    # Mandated failure-mode fixture (not a synthetic support narrative)
    batch = [good[0], "not-a-ticket", good[1]]
    input_path = tmp_path / "mixed.json"
    input_path.write_text(json.dumps(batch), encoding="utf-8")
    out = tmp_path / "out_mixed"

    summary = run_harness(input_path, out, allow_generate=False, persist=True)
    assert summary["tickets"] == 3
    assert summary["silent_drops"] == 0

    actions = []
    for line in (out / "results.jsonl").read_text(encoding="utf-8").strip().splitlines():
        actions.append(json.loads(line)["action"])
    assert actions[1] == "escalate"
