#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
target="${1:-lib/list_sort.c}"
turns="${2:-1}"
config="$DEMO_ROOT/.runtime/kres/models/codex-codes.json"
results="$DEMO_ROOT/results/review-$(date -u +%Y%m%dT%H%M%S)-$$"
cd "$DEMO_ROOT/linux"
exec "$DEMO_ROOT/scripts/kres" --no-tui \
  --fast-agent "$config" --slow-agent "$config" \
  --main-agent "$config" --todo-agent "$config" \
  --fast-model gpt-5.6-sol --slow-model gpt-5.6-sol \
  --main-model gpt-5.6-sol --todo-model gpt-5.6-sol \
  --skills "$DEMO_ROOT/.runtime/kres/skills" \
  --max-parallel 2 --results "$results" \
  --turns "$turns" --prompt "review: $target"
