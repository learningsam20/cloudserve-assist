"""LiteLLM wrapper — OpenRouter by default, with timeout + 429 backoff (A11)."""

from __future__ import annotations

import os
import time
from typing import Any

from src.config import get_settings


def completion(messages: list[dict[str, str]], **kwargs: Any) -> str:
    """Chat completion via LiteLLM. Retries rate limits with backoff."""
    settings = get_settings()
    key = settings.require_openrouter_key()
    os.environ["OPENROUTER_API_KEY"] = key

    import litellm
    from litellm.exceptions import RateLimitError, Timeout, APIConnectionError

    params: dict[str, Any] = {
        "model": settings.litellm_model,
        "messages": messages,
        "timeout": settings.llm_timeout_seconds,
        **kwargs,
    }
    if settings.litellm_api_base:
        params["api_base"] = settings.litellm_api_base

    attempts = max(1, settings.llm_max_retries)
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            response = litellm.completion(**params)
            return response.choices[0].message.content or ""
        except (RateLimitError, Timeout, APIConnectionError) as exc:
            last_exc = exc
            if attempt >= attempts - 1:
                break
            sleep_s = settings.llm_backoff_seconds * (2**attempt)
            # Honor Retry-After when present on the exception / response headers.
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
                sleep_s = max(sleep_s, float(retry_after))
            time.sleep(sleep_s)
    assert last_exc is not None
    raise last_exc
