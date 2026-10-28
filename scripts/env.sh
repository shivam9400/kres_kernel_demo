#!/usr/bin/env bash
# Source this file; it does not change HOME or injected authentication.
DEMO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export DEMO_ROOT
export CARGO_HOME="$DEMO_ROOT/.tools/cargo"
export RUSTUP_HOME="$DEMO_ROOT/.tools/rustup"
export PATH="$CARGO_HOME/bin:$PATH"
export RUSTUP_TOOLCHAIN=1.96.0
