"""Environment configuration for CloudServe Assistant.

All runtime knobs come from `.env` (see `.env.example`). No product defaults
are embedded in code — missing required keys raise ConfigError.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")


class ConfigError(RuntimeError):
    """Raised when a required environment variable is missing or invalid."""


def _require(name: str) -> str:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        raise ConfigError(
            f"Missing required env var {name}. Copy .env.example to .env and set it."
        )
    return str(raw).strip()


def _optional(name: str) -> str | None:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return None
    return str(raw).strip()


def _bool_required(name: str) -> bool:
    raw = _require(name).lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{name} must be true/false (got {raw!r})")


def _float_require(name: str) -> float:
    raw = _require(name)
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number (got {raw!r})") from exc


def _int_require(name: str) -> int:
    raw = _require(name)
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer (got {raw!r})") from exc


def _path_from_env(name: str) -> Path:
    value = Path(_require(name))
    if not value.is_absolute():
        value = _ROOT / value
    return value


def _env_truthy(name: str) -> bool:
    """Live read of a bool-ish env flag (not cached Settings snapshot)."""
    raw = os.getenv(name)
    if raw is None:
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Resolved settings from environment only."""

    def __init__(self) -> None:
        self.root = _ROOT
        # Provider keys are optional at load time (placeholder OK). The active
        # provider key is enforced only when generation runs (require_llm_api_key).
        self.openrouter_api_key = _optional("OPENROUTER_API_KEY") or "your_key_here"
        self.groq_api_key = _optional("GROQ_API_KEY") or "your_key_here"
        self.model_name = _require("MODEL_NAME")
        self.litellm_model = _require("LITELLM_MODEL")
        self.litellm_api_base = _optional("LITELLM_API_BASE")
        self.embedding_model = _require("EMBEDDING_MODEL")
        self.embedding_min_dim = _int_require("EMBEDDING_MIN_DIM")
        self.chroma_path = _path_from_env("CHROMA_PATH")
        self.chroma_collection = _require("CHROMA_COLLECTION")
        self.database_url = _require("DATABASE_URL")
        self.log_level = _require("LOG_LEVEL")
        self.confidence_threshold = _float_require("CONFIDENCE_THRESHOLD")
        self.retrieval_top_k = _int_require("RETRIEVAL_TOP_K")
        self.retrieval_min_score = _float_require("RETRIEVAL_MIN_SCORE")
        # dense | hybrid | auto — auto uses dense first, falls back to hybrid if weak
        mode = _require("RETRIEVAL_MODE").lower()
        if mode not in {"dense", "hybrid", "auto"}:
            raise ConfigError(
                f"RETRIEVAL_MODE must be dense|hybrid|auto (got {mode!r})"
            )
        self.retrieval_mode = mode
        # When auto: if dense top score < this (or no hits), switch to hybrid
        self.hybrid_dense_score_floor = _float_require("HYBRID_DENSE_SCORE_FLOOR")
        # Fusion weight for dense score in [0,1]; lexical gets (1 - alpha)
        self.hybrid_dense_alpha = _float_require("HYBRID_DENSE_ALPHA")
        self.lexical_index_path = _path_from_env("LEXICAL_INDEX_PATH")
        self.route_grounded_min_score = _float_require("ROUTE_GROUNDED_MIN_SCORE")
        self.route_grounded_conf_factor = _float_require("ROUTE_GROUNDED_CONF_FACTOR")
        self.chunk_size = _int_require("CHUNK_SIZE")
        self.chunk_overlap = _int_require("CHUNK_OVERLAP")
        self.index_batch_size = _int_require("INDEX_BATCH_SIZE")
        self.classifier_dir = _path_from_env("CLASSIFIER_DIR")
        self.classifier_filename = _require("CLASSIFIER_FILENAME")
        self.kill_switch = _bool_required("KILL_SWITCH")
        self.kill_switch_file = _path_from_env("KILL_SWITCH_FILE")
        self.api_host = _require("API_HOST")
        self.api_port = _int_require("API_PORT")
        self.api_pid_file = _path_from_env("API_PID_FILE")
        self.api_log_file = _path_from_env("API_LOG_FILE")
        self.gen_cache_dir = _path_from_env("GEN_CACHE_DIR")
        self.prompt_file = _path_from_env("PROMPT_FILE")
        self.prompt_version = _require("PROMPT_VERSION")
        self.datasets_path = Path(_require("DATASETS_PATH"))
        if not self.datasets_path.is_absolute():
            self.datasets_path = (_ROOT / self.datasets_path).resolve()
        self.target_fcr_pct = _float_require("TARGET_FCR_PCT")
        self.target_reply_mean_minutes = _float_require("TARGET_REPLY_MEAN_MINUTES")
        self.target_csat = _float_require("TARGET_CSAT")
        self.target_escalation_pct = _float_require("TARGET_ESCALATION_PCT")
        self.target_classification_precision = _float_require(
            "TARGET_CLASSIFICATION_PRECISION"
        )
        self.target_latency_p95_seconds = _float_require("TARGET_LATENCY_P95_SECONDS")
        self.fairness_max_gap_pp = _float_require("FAIRNESS_MAX_GAP_PP")
        self.tune_threshold_min = _float_require("TUNE_THRESHOLD_MIN")
        self.tune_threshold_max = _float_require("TUNE_THRESHOLD_MAX")
        self.tune_threshold_step = _float_require("TUNE_THRESHOLD_STEP")
        self.train_test_size = _float_require("TRAIN_TEST_SIZE")
        self.train_seed = _int_require("TRAIN_SEED")
        self.llm_temperature = _float_require("LLM_TEMPERATURE")
        self.llm_timeout_seconds = _float_require("LLM_TIMEOUT_SECONDS")
        self.llm_max_retries = _int_require("LLM_MAX_RETRIES")
        self.llm_backoff_seconds = _float_require("LLM_BACKOFF_SECONDS")
        # Floor between OpenRouter calls (0 = off). Use ~4s to stay under free-router RPM.
        self.llm_min_interval_seconds = _float_require("LLM_MIN_INTERVAL_SECONDS")

    def kill_switch_active(self) -> bool:
        """True if live env flag or kill file exists (findings D4; re-reads env)."""
        return _env_truthy("KILL_SWITCH") or self.kill_switch_file.exists()

    def llm_provider(self) -> str:
        """LiteLLM provider inferred from LITELLM_MODEL prefix."""
        model = self.litellm_model.lower()
        if model.startswith("groq/"):
            return "groq"
        if model.startswith("openrouter/"):
            return "openrouter"
        # Bare model ids default to OpenRouter (historical pack behaviour).
        return "openrouter"

    def require_openrouter_key(self) -> str:
        if self.openrouter_api_key == "your_key_here":
            raise RuntimeError(
                "OPENROUTER_API_KEY is still the placeholder. Set a real key in .env."
            )
        return self.openrouter_api_key

    def require_llm_api_key(self) -> tuple[str, str]:
        """Return (env_var_name, api_key) for the active LiteLLM provider."""
        provider = self.llm_provider()
        if provider == "groq":
            key = (self.groq_api_key or "").strip()
            if not key or key == "your_key_here":
                raise RuntimeError(
                    "GROQ_API_KEY is still the placeholder. Set a real key in .env "
                    "(https://console.groq.com/keys)."
                )
            return "GROQ_API_KEY", key
        return "OPENROUTER_API_KEY", self.require_openrouter_key()

    def classifier_path(self) -> Path:
        return self.classifier_dir / self.classifier_filename


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
