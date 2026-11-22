"""Shared pytest helpers — datasets resolve only under the service root."""

from __future__ import annotations

import os
from pathlib import Path

SUBMISSION = Path(__file__).resolve().parents[1]
DEFAULT_DATASETS = SUBMISSION / "datasets"


def datasets_dir() -> Path:
    """Resolve DATASETS_PATH relative to the service root; default ./datasets."""
    raw = os.getenv("DATASETS_PATH")
    if not raw or not str(raw).strip():
        try:
            from src.config import get_settings

            raw = str(get_settings().datasets_path)
        except Exception:
            raw = str(DEFAULT_DATASETS)

    p = Path(str(raw).strip())
    if not p.is_absolute():
        p = (SUBMISSION / p).resolve()
    else:
        p = p.resolve()

    # Refuse paths outside the service tree (keeps CI / checkout self-contained).
    try:
        p.relative_to(SUBMISSION.resolve())
    except ValueError as exc:
        raise FileNotFoundError(
            f"DATASETS_PATH must be inside the service root ({SUBMISSION}). "
            f"Got {p}. Use DATASETS_PATH=./datasets"
        ) from exc

    if not p.is_dir():
        raise FileNotFoundError(
            f"Datasets directory not found: {p}. "
            "Expected in-tree ./datasets with development_tickets.json, "
            "validation_tickets.json, documentation.json"
        )
    return p


def development_tickets() -> Path:
    path = datasets_dir() / "development_tickets.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Commit the ./datasets folder to the repo."
        )
    return path


def documentation_json() -> Path:
    path = datasets_dir() / "documentation.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Commit the ./datasets folder to the repo."
        )
    return path
