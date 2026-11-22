"""Blocking guardrails on candidate generations (A7)."""

from __future__ import annotations

import re
from typing import Optional

from src.models import (
    Classification,
    GenerationResult,
    GuardrailResult,
    Passage,
    RouteAction,
)

# Patterns that should never appear in outbound auto replies.
_PII_PATTERNS = [
    (r"\bAKIA[0-9A-Z]{16}\b", "aws_access_key"),
    (r"\bsk-[A-Za-z0-9]{20,}\b", "secret_token"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn_like"),
    (r"\b(?:\d[ -]*?){13,19}\b", "card_like"),
]

_INJECTION_MARKERS = [
    r"ignore (all )?previous instructions",
    r"disregard (the )?system prompt",
    r"you are now",
]

_SCOPE_MARKERS = [
    r"\bwe (will|can) refund\b",
    r"\bguaranteed timeline\b",
    r"\blegal advice\b",
]


def validate(
    generation: GenerationResult,
    passages: list[Passage],
    classification: Optional[Classification] = None,
    confidence_threshold: Optional[float] = None,
    *,
    skip_confidence_floor: bool = False,
) -> tuple[list[GuardrailResult], bool]:
    """Return (results, blocked). blocked True means must not auto-send."""
    results: list[GuardrailResult] = []
    retrieved_ids = {p.doc_id for p in passages}
    answer = generation.answer or ""

    # Nonempty answer required for auto_respond
    if not answer.strip():
        results.append(
            GuardrailResult(
                name="nonempty_answer",
                passed=False,
                detail="Empty generation answer",
            )
        )
    else:
        results.append(
            GuardrailResult(name="nonempty_answer", passed=True, detail="ok")
        )

    # Citation IDs must be subset of retrieved set
    bad_cites = [c for c in generation.citation_doc_ids if c not in retrieved_ids]
    if bad_cites:
        results.append(
            GuardrailResult(
                name="citation_ids",
                passed=False,
                detail=f"Citations not in retrieved set: {bad_cites}",
            )
        )
    else:
        results.append(
            GuardrailResult(name="citation_ids", passed=True, detail="All citations retrieved")
        )

    # Empty retrieval should never produce factual citations
    if not passages and generation.citation_doc_ids:
        results.append(
            GuardrailResult(
                name="grounding_empty_retrieve",
                passed=False,
                detail="Citations present with empty retrieval",
            )
        )
    else:
        results.append(
            GuardrailResult(name="grounding_empty_retrieve", passed=True, detail="ok")
        )

    pii_hits = []
    for pattern, label in _PII_PATTERNS:
        if re.search(pattern, answer):
            pii_hits.append(label)
    results.append(
        GuardrailResult(
            name="pii",
            passed=not pii_hits,
            detail=("detected: " + ",".join(pii_hits)) if pii_hits else "ok",
        )
    )

    inj = any(re.search(p, answer, flags=re.IGNORECASE) for p in _INJECTION_MARKERS)
    results.append(
        GuardrailResult(
            name="instruction_integrity",
            passed=not inj,
            detail="injection-like language in answer" if inj else "ok",
        )
    )

    scope = any(re.search(p, answer, flags=re.IGNORECASE) for p in _SCOPE_MARKERS)
    results.append(
        GuardrailResult(
            name="tone_scope",
            passed=not scope,
            detail="out-of-scope commitment language" if scope else "ok",
        )
    )

    if classification is not None and confidence_threshold is not None:
        if skip_confidence_floor:
            results.append(
                GuardrailResult(
                    name="confidence_floor",
                    passed=True,
                    detail=(
                        "skipped: grounded override already applied at route "
                        f"(conf={classification.confidence:.3f})"
                    ),
                )
            )
        else:
            ok = classification.confidence >= confidence_threshold
            results.append(
                GuardrailResult(
                    name="confidence_floor",
                    passed=ok,
                    detail=(
                        f"confidence {classification.confidence:.3f} "
                        f"vs threshold {confidence_threshold:.3f}"
                    ),
                )
            )

    blocked = any(not r.passed for r in results)
    return results, blocked


def final_action(route_action: RouteAction, blocked: bool) -> RouteAction:
    if blocked:
        return RouteAction.BLOCK
    return route_action
