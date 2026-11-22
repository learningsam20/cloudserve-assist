# Shared helpers for CloudServe Assistant ops scripts.
# shellcheck shell=bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

if [[ -f "$ROOT/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
fi

load_env() {
  if [[ ! -f "$ROOT/.env" ]]; then
    echo "error: missing $ROOT/.env — copy .env.example to .env" >&2
    exit 2
  fi
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
}

load_env

PACK_DATA="${DATASETS_PATH}"
if [[ "$PACK_DATA" != /* ]]; then
  PACK_DATA="$ROOT/$PACK_DATA"
fi
PID_FILE="$ROOT/${API_PID_FILE#./}"
LOG_FILE="$ROOT/${API_LOG_FILE#./}"
# If paths already absolute via env resolution in scripts, prefer:
if [[ "${API_PID_FILE}" = /* ]]; then PID_FILE="$API_PID_FILE"; fi
if [[ "${API_LOG_FILE}" = /* ]]; then LOG_FILE="$API_LOG_FILE"; fi

ensure_storage() {
  mkdir -p "$ROOT/storage" "$ROOT/evaluation/results"
}

require_pack() {
  if [[ ! -f "$PACK_DATA/development_tickets.json" ]]; then
    echo "error: CloudServe datasets not found at $PACK_DATA" >&2
    echo "set DATASETS_PATH in .env" >&2
    exit 2
  fi
}
