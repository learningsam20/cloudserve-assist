#!/usr/bin/env bash
set -euo pipefail
# shellcheck disable=SC1091
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"
ensure_storage
ks="$ROOT/${KILL_SWITCH_FILE#./}"
if [[ "$KILL_SWITCH_FILE" = /* ]]; then ks="$KILL_SWITCH_FILE"; fi
mkdir -p "$(dirname "$ks")"
touch "$ks"
echo "kill switch ON ($ks)"
