"""Disk cache for remote generation responses (model + prompt hash)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from src.config import get_settings


def _cache_dir() -> Path:
    path = get_settings().gen_cache_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def prompt_hash(model: str, prompt: str) -> str:
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"\0")
    h.update(prompt.encode("utf-8"))
    return h.hexdigest()


def get_cached(model: str, prompt: str) -> Optional[dict[str, Any]]:
    key = prompt_hash(model, prompt)
    path = _cache_dir() / f"{key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def put_cached(model: str, prompt: str, payload: dict[str, Any]) -> None:
    key = prompt_hash(model, prompt)
    path = _cache_dir() / f"{key}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
