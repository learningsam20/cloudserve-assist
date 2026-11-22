"""Deterministic routing over classification confidence + policy + kill switch."""

from __future__ import annotations

import os
import re

from src.config import get_settings
from src.models import Classification, Passage, RouteAction, RouteDecision, Ticket

# Label-free safety patterns (hidden set may omit must_not_auto_respond).
_MUST_NOT_PATTERNS: list[tuple[str, str]] = [
    ("security_incident_text", r"\b(data breach|ransomware|unauthorized access|compromised credentials?)\b"),
    ("legal_threat", r"\b(lawsuit|legal action|attorney|solicitor)\b"),
    ("self_harm", r"\b(kill myself|suicide)\b"),
]

# Intents that must never auto-respond even without gold labels.
_MUST_NOT_INTENTS = frozenset(
    {
        "security_incident",
        "compliance_request",
    }
)


def _use_eval_labels() -> bool:
    """When true, honour labels.must_not_auto_respond (eval datasets). Default true.

    Set USE_EVAL_LABELS=false to measure label-free routing (API / stripped tickets).
    """
    raw = os.getenv("USE_EVAL_LABELS", "true").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def policy_must_not(ticket: Ticket, classification: Classification | None = None) -> str | None:
    """Return reason if ticket must not auto-respond.

    Order: optional gold label (eval) → classified intent → text rules.
    """
    if _use_eval_labels():
        labels = ticket.labels or {}
        if labels.get("must_not_auto_respond") is True:
            return "Policy: must_not_auto_respond (label)."

    if classification is not None and classification.intent in _MUST_NOT_INTENTS:
        return f"Policy: must_not via classified intent {classification.intent}."

    text = ticket.text_for_model()
    for name, pattern in _MUST_NOT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return f"Policy: must_not via text rule {name}."
    return None


def route(
    ticket: Ticket,
    classification: Classification,
    passages: list[Passage],
) -> RouteDecision:
    settings = get_settings()
    threshold = settings.confidence_threshold
    kill = settings.kill_switch_active()

    if kill:
        return RouteDecision(
            action=RouteAction.ESCALATE,
            reason="Kill switch active; auto_respond disabled (findings D4).",
            threshold_applied=threshold,
            kill_switch=True,
            grounded_override=False,
        )

    must_not = policy_must_not(ticket, classification)
    if must_not:
        return RouteDecision(
            action=RouteAction.ESCALATE,
            reason=must_not,
            threshold_applied=threshold,
            kill_switch=False,
            grounded_override=False,
        )

    if not passages:
        return RouteDecision(
            action=RouteAction.ESCALATE,
            reason="No retrieved passages above relevance; refusing ungrounded answer.",
            threshold_applied=threshold,
            kill_switch=False,
            grounded_override=False,
        )

    top_score = max(p.score for p in passages)
    conf = classification.confidence

    if conf >= threshold:
        return RouteDecision(
            action=RouteAction.AUTO_RESPOND,
            reason=(
                f"Confidence {conf:.3f} >= {threshold:.3f} "
                f"with {len(passages)} passage(s) (chroma top_score={top_score:.3f})."
            ),
            threshold_applied=threshold,
            kill_switch=False,
            grounded_override=False,
        )

    # Frozen policy (D3): grounded override below CONFIDENCE_THRESHOLD when retrieval is strong.
    grounded_floor = threshold * settings.route_grounded_conf_factor
    if top_score >= settings.route_grounded_min_score and conf >= grounded_floor:
        return RouteDecision(
            action=RouteAction.AUTO_RESPOND,
            reason=(
                f"Grounded override: top_score {top_score:.3f} >= "
                f"{settings.route_grounded_min_score:.3f} and confidence {conf:.3f} >= "
                f"{grounded_floor:.3f} (factor {settings.route_grounded_conf_factor}; "
                f"frozen threshold {threshold:.3f})."
            ),
            threshold_applied=threshold,
            kill_switch=False,
            grounded_override=True,
        )

    return RouteDecision(
        action=RouteAction.ESCALATE,
        reason=(
            f"Classification confidence {conf:.3f} below threshold {threshold:.3f}."
        ),
        threshold_applied=threshold,
        kill_switch=False,
        grounded_override=False,
    )
