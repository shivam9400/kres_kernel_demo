# KRes demo setup

## Scope and pinned inputs

This setup prepares the KRes CLI and a public Linux source-review workspace.
It does not build or boot a Samsung kernel. No Samsung source or credentials
are stored in the repository.

| Component | Source / version |
|---|---|
| KRes | https://github.com/masoncl/kres.git at `4ef4b706358abfcb82d112213632f4a8edda2868` |
| Rust | `1.96.0`, minimal rustup profile |
| Linux | https://github.com/torvalds/linux.git tag `v6.12`, commit `adc218676eef25575469234709c2d87185ca223a` |
| Review guides | https://github.com/masoncl/review-prompts.git at `d048f8742f6740c38833adf02e87901412d771ca` |
| Model transport | Existing authenticated Codex CLI, upstream model `gpt-5.6-sol` |

The unchanged KRes snapshot is in `vendor/kres/`, with its lockfile and licenses.
Linux, guides, Rust, generated configuration, build products and results are
ignored. Bootstrap downloads the pinned inputs instead of committing a kernel
tree or binary. Existing directories with different revisions cause bootstrap
to fail rather than resetting your work.

## Steps performed

1. Inspected the initially empty `kres_kernel_demo` checkout and verified public
   Git read access through the supplied HTTPS proxy.
2. Cloned KRes to an inspection directory, read its README, architecture,
   development, configuration and workflow documentation, and copied its source
   snapshot into `vendor/kres/` without upstream Git metadata.
3. Checked resources: five CPUs, about 32 GiB available memory and 30 GiB free
   disk initially. Selected four build jobs. No kernel build is needed for a
   source review. The environment already supplies a C compiler, make, Python,
   curl, Git and Codex CLI.
4. Installed Rust in `.tools/`, without modifying shell startup files or HOME.
   Rust 1.93 initially failed because locked `kstring 2.0.4` requires 1.96.
   Installed and pinned 1.96; kept Cargo.toml and Cargo.lock unchanged.
5. Built with `cargo build --release --locked -j 4`. Cargo verifies downloaded
   crate checksums. TLS and signature/checksum checks remain enabled.
6. Cloned Linux v6.12 with `--depth 1` and downloaded the pinned review guides.
   The shallow clone is enough for source review, but has no useful preceding
   history for KRes's six-month change survey. Fetch needed history before
   history-sensitive investigations.
7. Ran upstream `setup.sh --provider codex --dest <demo>/.runtime/kres
   --semcode '' --review-prompts <demo>/review-prompts`. The upstream script
   installed a local provider config and substituted the guide path in the
   kernel skill. Semcode is optional and intentionally absent.
8. Removed `codex_home` from the generated local provider config using
   `scripts/configure.py`. This lets the child CLI reuse injected authentication;
   no credential files or values are copied. Also replaced the upstream
   `mcp_servers.meta_core.enabled` dotted override with an empty `mcp_servers`
   table: in this environment the dotted override created an invalid entry
   without a transport, so app-server exited during initialization. The feature
   and project-document isolation overrides remain intact.
9. Added scripts with explicit local config paths so global KRes settings need
   not be changed. Each review gets a separate timestamped results directory.
10. Ran the validation commands documented below. See `docs/validation.md` for
    observed outcomes and limitations.

## Reproduce installation

Use Linux x86-64 with Git, curl, a C toolchain/linker, make, Python 3 and a working
Codex CLI. The pinned Rust toolchain is installed by bootstrap. Allow several
GiB for Linux, Rust, crate caches and build products.

```bash
cd /workspace/kres_kernel_demo   # or your clone's root
bash scripts/bootstrap.sh
```

Bootstrap is repeatable: it reuses toolchains and valid Cargo outputs, verifies
source revisions and leaves existing generated provider files intact. Use the
existing checkout; cloud tasks are already isolated, so no worktree is needed.

Network destinations include `github.com`, `sh.rustup.rs`,
`static.rust-lang.org`, `index.crates.io` and `static.crates.io`.
Codex inference additionally requires `chatgpt.com`. The onboarding run
observed HTTP CONNECT 403 for that destination and saved it as an additive
custom domain in the environment draft, preserving the package-manager preset.
Review and save the changes in environment settings, then publish the
environment. A draft save alone does not change the running network policy.
Keep the managed environment's proxy and CA trust. In this session sandboxed
network requests could not reach the proxy; approved commands outside that
sandbox could. Do not unset proxy variables or disable TLS to work around it.
Model access uses the existing Codex CLI routing and authorization, not GitHub
authentication. On another machine, configure your own approved CLI login.
Never paste credentials into this file or commit `.runtime/`.

## Run a review

```bash
cd /workspace/kres_kernel_demo
codex login status
bash scripts/review.sh lib/list_sort.c 1
```

Arguments are a review target and a turn count. Start with one turn and two
parallel tasks (the script default). One turn can still make many model calls.
Use a file, directory or commit/range target supported by upstream KRes. This
script performs review only; it does not invoke automatic fixes.

Run artifacts under `results/review-*/` include findings and session state.
Inspect actual logs and statuses before treating a run as completed. Model
findings are hypotheses until validated against source and tests.

For another authorized model, update the local generated provider's model entry
and the four role selectors in `scripts/review.sh` together. Do not assume every
account supports the upstream example model. For an API provider follow the
pinned upstream [configuration reference](vendor/kres/docs/configuration.md).

## Validate the installation

```bash
source scripts/env.sh
scripts/kres --version
scripts/kres --help
for workflow in review validate triage fix; do
  scripts/kres validate-workflow "vendor/kres/configs/workflows/$workflow.json"
done
cargo test --release --locked --manifest-path vendor/kres/Cargo.toml -p kres-core -j 2
scripts/kres test .runtime/kres/models/codex-codes.json \
  --model gpt-5.6-sol --prompt 'Reply with KRES_READY only.'
bash scripts/review.sh lib/list_sort.c 1
```

Workflow validation checks schema/invariants without calling a model. Core
tests exercise task, findings and persistence behavior. The provider test
checks real inference. The review checks source gathering plus the actual
review pipeline. None substitutes for the others.

No daemon is required: launch the CLI for each review. Processes do not need to
survive an environment snapshot. On a future cloud task, run bootstrap if
dependencies are missing, then rerun the provider check before reviewing.

## Export, validate and fix

Upstream documents export, validation, summaries and fixes in
[README](vendor/kres/README.md) and [workflow docs](vendor/kres/docs/workflow.md).
`scripts/kres` is a direct binary wrapper; when calling model-dependent CLI
commands directly, supply the local provider/role/skills flags from
`scripts/review.sh`. The default upstream lookup is global `.kres`, which this
demo deliberately does not populate.

The automated fix workflow can write files, make commits, build and export
patches. Prepare a development branch, kernel build config and correct
cross-toolchain before using it. Linux v6.12 is a reproducible example baseline,
not a claim that it matches a supported Samsung product release or includes
current security fixes.
