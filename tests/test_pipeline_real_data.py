"""Pipeline tests using reference datasets pack files — no invented ticket bodies."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.classify import reset_classifier_cache
from src.config import get_settings
from src.graph import run_ticket
from src.ingest import ingest
from src.models import Channel
from src.retrieve import build_index, reset_retrieve_cache, retrieve

from tests.conftest import SUBMISSION as SUBMISSION_ROOT
from tests.conftest import development_tickets, documentation_json

DEV_TICKETS = development_tickets()
DOCS = documentation_json()


@pytest.fixture(scope="module")
def first_dev_ticket() -> dict:
    rows = json.loads(DEV_TICKETS.read_text(encoding="utf-8"))
    assert rows, "development_tickets.json missing or empty"
    return rows[0]


@pytest.fixture(scope="module")
def indexed_docs(tmp_path_factory):
    if not DOCS.exists():
        pytest.skip("documentation.json not found")
    chroma_dir = tmp_path_factory.mktemp("chroma")
    # Point settings at temp chroma for isolation
    import os

    os.environ["CHROMA_PATH"] = str(chroma_dir)
    get_settings.cache_clear()
    reset_retrieve_cache()
    n = build_index(DOCS, reset=True)
    assert n > 0
    yield n
    reset_retrieve_cache()
    get_settings.cache_clear()


def test_ingest_preserves_channel_from_real_ticket(first_dev_ticket):
    t = ingest(first_dev_ticket)
    assert t.ticket_id == first_dev_ticket["ticket_id"]
    assert t.channel in Channel
    assert isinstance(t.body, str)


def test_retrieve_returns_doc_ids_from_real_corpus(first_dev_ticket, indexed_docs):
    t = ingest(first_dev_ticket)
    passages = retrieve(t, top_k=3)
    # May be empty if min_score filters all; when non-empty, doc_id must be real
    doc_ids = {
        str(d["doc_id"])
        for d in json.loads(DOCS.read_text(encoding="utf-8"))
    }
    for p in passages:
        assert p.doc_id in doc_ids
        assert p.score >= 0.0


def test_run_ticket_on_real_sample(first_dev_ticket, indexed_docs, monkeypatch):
    # Classifier trained earlier under submission/storage/models/classifier
    clf_dir = SUBMISSION_ROOT / "storage" / "models" / "classifier"
    if not (clf_dir / "classifier.joblib").exists():
        pytest.skip("classifier artifact not trained yet")
    monkeypatch.setenv("CLASSIFIER_DIR", str(clf_dir))
    monkeypatch.setenv("KILL_SWITCH", "false")
    get_settings.cache_clear()
    reset_classifier_cache()

    # allow_generate=False so this test does not require OPENROUTER_API_KEY
    result = run_ticket(first_dev_ticket, persist=False, allow_generate=False)
    assert result.ticket_id == first_dev_ticket["ticket_id"]
    assert result.classification is not None
    assert result.route is not None
    assert result.action is not None
