#!/usr/bin/env bash
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ks="$ROOT/${KILL_SWITCH_FILE#./}"
if [[ "$KILL_SWITCH_FILE" = /* ]]; then ks="$KILL_SWITCH_FILE"; fi
rm -f "$ks"
echo "kill switch OFF (file removed; ensure KILL_SWITCH=false in .env)"
