"""Shared pytest helpers — resolve Capstone datasets via CAPSTONE_DATASETS / settings."""

from __future__ import annotations

import os
from pathlib import Path

SUBMISSION = Path(__file__).resolve().parents[1]


def datasets_dir() -> Path:
    """Prefer CAPSTONE_DATASETS env, then settings, then sibling Pack path."""
    raw = os.getenv("CAPSTONE_DATASETS")
    if raw and str(raw).strip():
        p = Path(raw.strip())
        if not p.is_absolute():
            p = (SUBMISSION / p).resolve()
        if p.is_dir():
            return p
    try:
        from src.config import get_settings

        p = get_settings().capstone_datasets
        if p.is_dir():
            return p
    except Exception:
        pass
    # Fallbacks: packaged tree may place Pack beside 04_Source_Code, or repo layout.
    candidates = [
        SUBMISSION.parent / "capstone_guide" / "Capstone_Pack" / "05_Datasets",
        SUBMISSION / "capstone_guide" / "Capstone_Pack" / "05_Datasets",
        SUBMISSION.parent.parent / "capstone_guide" / "Capstone_Pack" / "05_Datasets",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def development_tickets() -> Path:
    return datasets_dir() / "development_tickets.json"


def documentation_json() -> Path:
    return datasets_dir() / "documentation.json"
