#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
cd "$DEMO_ROOT"
mkdir -p .tools
if [[ ! -x "$CARGO_HOME/bin/rustup" ]]; then
  curl --proto '=https' --tlsv1.2 --fail --show-error --location \
    https://sh.rustup.rs -o .tools/rustup-init.sh
  sh .tools/rustup-init.sh -y --no-modify-path --profile minimal --default-toolchain 1.96.0
fi
rustup toolchain install 1.96.0 --profile minimal
if [[ ! -d linux ]]; then
  git clone --depth 1 --branch v6.12 https://github.com/torvalds/linux.git linux
fi
test "$(git -C linux rev-parse HEAD)" = adc218676eef25575469234709c2d87185ca223a
if [[ ! -d review-prompts ]]; then
  git clone https://github.com/masoncl/review-prompts.git review-prompts
  git -C review-prompts checkout --detach d048f8742f6740c38833adf02e87901412d771ca
fi
test "$(git -C review-prompts rev-parse HEAD)" = d048f8742f6740c38833adf02e87901412d771ca
cargo build --manifest-path vendor/kres/Cargo.toml --release --locked -j 4
bash vendor/kres/setup.sh --provider codex --dest "$DEMO_ROOT/.runtime/kres" \
  --semcode '' --review-prompts "$DEMO_ROOT/review-prompts"
python3 scripts/configure.py
scripts/kres --version
for workflow in review validate triage fix; do
  scripts/kres validate-workflow "vendor/kres/configs/workflows/$workflow.json"
done
