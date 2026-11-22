"""Normalise tickets from four channels into Ticket models."""

from __future__ import annotations

from typing import Any

from src.models import Channel, Ticket


def ingest(raw: dict[str, Any]) -> Ticket:
    """Map a raw ticket dict into the internal Ticket representation (A2)."""
    channel_raw = str(raw.get("channel") or "email").strip().lower()
    try:
        channel = Channel(channel_raw)
    except ValueError:
        # Defined degrade: unknown channel → email + preserved text (no crash).
        channel = Channel.EMAIL

    return Ticket(
        ticket_id=str(raw.get("ticket_id") or raw.get("id") or "unknown"),
        channel=channel,
        subject=str(raw.get("subject") or ""),
        body=str(raw.get("body") or ""),
        received_at=raw.get("received_at") if raw.get("received_at") is None else str(raw.get("received_at")),
        customer_id=None if raw.get("customer_id") is None else str(raw.get("customer_id")),
        customer_name=None if raw.get("customer_name") is None else str(raw.get("customer_name")),
        customer_tier=None if raw.get("customer_tier") is None else str(raw.get("customer_tier")),
        customer_region=None if raw.get("customer_region") is None else str(raw.get("customer_region")),
        language_fluency=(
            None if raw.get("language_fluency") is None else str(raw.get("language_fluency"))
        ),
        labels=raw.get("labels") if isinstance(raw.get("labels"), dict) else None,
        history=raw.get("history") if isinstance(raw.get("history"), dict) else None,
    )
