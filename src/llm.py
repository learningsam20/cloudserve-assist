"""LiteLLM wrapper — OpenRouter or Groq via env model prefix, with 429 backoff (A11)."""

from __future__ import annotations

import os
import time
from typing import Any

from src.config import get_settings

_last_call_monotonic: float = 0.0


def _throttle(min_interval: float) -> None:
    """Space out live provider calls to avoid free-tier per-minute limits."""
    global _last_call_monotonic
    if min_interval <= 0:
        return
    now = time.monotonic()
    wait = min_interval - (now - _last_call_monotonic)
    if wait > 0:
        time.sleep(wait)
    _last_call_monotonic = time.monotonic()


def completion(messages: list[dict[str, str]], **kwargs: Any) -> str:
    """Chat completion via LiteLLM. Retries rate limits with backoff."""
    settings = get_settings()
    env_name, key = settings.require_llm_api_key()
    os.environ[env_name] = key

    import litellm
    from litellm.exceptions import RateLimitError, Timeout, APIConnectionError

    params: dict[str, Any] = {
        "model": settings.litellm_model,
        "messages": messages,
        "api_key": key,
        "timeout": settings.llm_timeout_seconds,
        **kwargs,
    }
    if settings.litellm_api_base:
        params["api_base"] = settings.litellm_api_base

    attempts = max(1, settings.llm_max_retries)
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            _throttle(settings.llm_min_interval_seconds)
            response = litellm.completion(**params)
            return response.choices[0].message.content or ""
        except (RateLimitError, Timeout, APIConnectionError) as exc:
            last_exc = exc
            # Daily free-router quota cannot be cleared by waiting a few seconds.
            msg = str(exc).lower()
            if "free-models-per-day" in msg or "free_tier_daily" in msg:
                break
            if attempt >= attempts - 1:
                break
            sleep_s = settings.llm_backoff_seconds * (2**attempt)
            # Honor Retry-After when present — but OpenRouter often puts an absolute
            # epoch (ms) in X-RateLimit-Reset; only treat small values as wait seconds.
            retry_after = getattr(exc, "retry_after", None)
            if retry_after is None:
                resp = getattr(exc, "response", None)
                headers = getattr(resp, "headers", None) or {}
                raw = headers.get("Retry-After") or headers.get("retry-after")
                if raw is not None:
                    try:
                        retry_after = float(raw)
                    except (TypeError, ValueError):
                        retry_after = None
            if retry_after is not None:
                ra = float(retry_after)
                if 0 < ra <= 120:
                    sleep_s = max(sleep_s, ra)
            time.sleep(sleep_s)
    assert last_exc is not None
    raise last_exc
