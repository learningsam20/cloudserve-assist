"""Rules-first classification, then trained local sklearn model."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import joblib

from src.config import get_settings
from src.models import Alternative, Classification, Ticket, Urgency
from src.observability import observe_classification

_BUNDLE: Optional[dict] = None

# Deterministic rules evaluated before the model (extend as discovery scripts justify).
_RULES: list[tuple[str, str, Urgency, str]] = [
    # (rule_id, intent, urgency, pattern)
    ("R-SECURITY", "security_incident", Urgency.HIGH, r"\b(compromised|breach|unauthorized access|phishing)\b"),
    ("R-BILLING", "billing_query", Urgency.MEDIUM, r"\b(invoice|refund|charge|billing)\b"),
]


def _load_bundle() -> dict:
    global _BUNDLE
    if _BUNDLE is not None:
        return _BUNDLE
    settings = get_settings()
    path = settings.classifier_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Classifier not found at {path}. Train with: "
            "python -m scripts.train_classifier --input <tickets.json> "
            f"--output {settings.classifier_dir}"
        )
    _BUNDLE = joblib.load(path)
    return _BUNDLE


def apply_rules(ticket: Ticket) -> Optional[Classification]:
    text = ticket.text_for_model().lower()
    for rule_id, intent, urgency, pattern in _RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            # Alternatives: other deterministic rules that did not fire (A3).
            alts = [
                Alternative(value=other_intent, confidence=0.0)
                for other_id, other_intent, _u, _p in _RULES
                if other_id != rule_id
            ]
            return Classification(
                intent=intent,
                urgency=urgency,
                confidence=1.0,
                alternatives=alts,
                source="rules",
                rule_id=rule_id,
            )
    return None


def classify(ticket: Ticket) -> Classification:
    """Return Intent/Urgency/Confidence. Never calls a remote LLM."""
    ruled = apply_rules(ticket)
    if ruled is not None:
        observe_classification(source=ruled.source, confidence=ruled.confidence)
        return ruled

    bundle = _load_bundle()
    intent_pipe = bundle["intent_pipeline"]
    urgency_pipe = bundle["urgency_pipeline"]
    text = ticket.text_for_model()

    intent = str(intent_pipe.predict([text])[0])
    intent_proba = intent_pipe.predict_proba([text])[0]
    intent_classes = list(intent_pipe.classes_)
    intent_conf = float(max(intent_proba))
    intent_alts = sorted(
        [
            Alternative(value=str(c), confidence=float(p))
            for c, p in zip(intent_classes, intent_proba)
            if str(c) != intent
        ],
        key=lambda a: a.confidence,
        reverse=True,
    )[:3]

    urgency_raw = str(urgency_pipe.predict([text])[0])
    urgency = Urgency(urgency_raw)

    # Route on intent confidence. Urgency is logged/returned but must not
    # tank the gate via min() — that collapsed FCR under a measured threshold.
    result = Classification(
        intent=intent,
        urgency=urgency,
        confidence=intent_conf,
        alternatives=intent_alts,
        source="model",
    )
    observe_classification(source=result.source, confidence=result.confidence)
    return result


def reset_classifier_cache() -> None:
    """Test helper to force reload."""
    global _BUNDLE
    _BUNDLE = None
