"""Prometheus metrics for CloudServe Assistant (Story 6.3 + demo dashboards)."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

TICKETS_PROCESSED = Counter(
    "cloudserve_tickets_processed_total",
    "Tickets processed by pipeline",
    ["action"],
)
GUARDRAIL_BLOCKS = Counter(
    "cloudserve_guardrail_blocks_total",
    "Guardrail evaluations that blocked send",
    ["name"],
)
PIPELINE_LATENCY = Histogram(
    "cloudserve_pipeline_latency_seconds",
    "End-to-end run_ticket latency",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0),
)
STAGE_ERRORS = Counter(
    "cloudserve_stage_errors_total",
    "Non-fatal stage errors recorded on PipelineResult",
)
RETRIEVAL_REQUESTS = Counter(
    "cloudserve_retrieval_requests_total",
    "Retrieval calls by effective mode (dense / hybrid / auto_fallback_hybrid)",
    ["mode"],
)
RETRIEVAL_TOP_SCORE = Histogram(
    "cloudserve_retrieval_top_score",
    "Top passage score after retrieval",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)
RETRIEVAL_PASSAGES = Histogram(
    "cloudserve_retrieval_passages",
    "Passages returned per retrieval",
    buckets=(0, 1, 2, 3, 4, 5, 8, 10),
)
CLASSIFICATION_TOTAL = Counter(
    "cloudserve_classification_total",
    "Classifications by source (rules|model)",
    ["source"],
)
CLASSIFICATION_CONFIDENCE = Histogram(
    "cloudserve_classification_confidence",
    "Classifier confidence (intent)",
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)


def observe_result(
    action: str, latency_seconds: float, *, blocked_guards: list[str] | None = None
) -> None:
    TICKETS_PROCESSED.labels(action=action).inc()
    PIPELINE_LATENCY.observe(latency_seconds)
    for name in blocked_guards or []:
        GUARDRAIL_BLOCKS.labels(name=name).inc()


def observe_errors(n: int) -> None:
    if n:
        STAGE_ERRORS.inc(n)


def observe_retrieval(*, mode: str, top_score: float, n_passages: int) -> None:
    RETRIEVAL_REQUESTS.labels(mode=mode or "none").inc()
    RETRIEVAL_TOP_SCORE.observe(max(0.0, float(top_score)))
    RETRIEVAL_PASSAGES.observe(max(0, int(n_passages)))


def observe_classification(*, source: str, confidence: float) -> None:
    CLASSIFICATION_TOTAL.labels(source=source or "unknown").inc()
    CLASSIFICATION_CONFIDENCE.observe(max(0.0, min(1.0, float(confidence))))


@contextmanager
def track_latency() -> Iterator[list[float]]:
    """Yield a one-element list that receives elapsed seconds on exit."""
    box: list[float] = []
    start = time.perf_counter()
    try:
        yield box
    finally:
        box.append(time.perf_counter() - start)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
