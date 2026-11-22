#!/usr/bin/env bash
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage

echo "ROOT=$ROOT"
echo "PACK_DATA=$PACK_DATA"
echo "PYTHON=$("$PYTHON" -c 'import sys; print(sys.executable)')"
echo ".env: present"
echo "MODEL_NAME=$MODEL_NAME LITELLM_MODEL=$LITELLM_MODEL"
echo "CONFIDENCE_THRESHOLD=$CONFIDENCE_THRESHOLD"

clf="$ROOT/${CLASSIFIER_DIR#./}/$CLASSIFIER_FILENAME"
if [[ "$CLASSIFIER_DIR" = /* ]]; then clf="$CLASSIFIER_DIR/$CLASSIFIER_FILENAME"; fi
if [[ -f "$clf" ]]; then echo "classifier: $clf"; else echo "classifier: MISSING"; fi

chroma="$ROOT/${CHROMA_PATH#./}"
if [[ "$CHROMA_PATH" = /* ]]; then chroma="$CHROMA_PATH"; fi
if [[ -d "$chroma" ]] && [[ -n "$(ls -A "$chroma" 2>/dev/null || true)" ]]; then
  echo "chroma: present ($chroma)"
else
  echo "chroma: MISSING"
fi

ks="$ROOT/${KILL_SWITCH_FILE#./}"
if [[ "$KILL_SWITCH_FILE" = /* ]]; then ks="$KILL_SWITCH_FILE"; fi
if [[ -f "$ks" ]] || [[ "${KILL_SWITCH}" == "true" ]]; then
  echo "kill_switch: ON"
else
  echo "kill_switch: off"
fi

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "API: running pid=$(cat "$PID_FILE") port=$API_PORT"
  curl -sf "http://127.0.0.1:$API_PORT/health" && echo || echo "(health check failed)"
else
  echo "API: stopped"
fi
