#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
exec python3 "$DEMO_ROOT/scripts/run.py" "$@"
