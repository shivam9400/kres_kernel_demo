# Applying KRes to kernel engineering

## What the repository does

At upstream revision `4ef4b706358abfcb82d112213632f4a8edda2868`, KRes is a
six-crate Rust workspace. `kres` supplies the CLI; `kres-repl` manages sessions,
the terminal and workflows; `kres-core` stores tasks and findings;
`kres-agents` implements evidence gathering and review pipelines;
`kres-llm` implements model transports; `kres-mcp` connects optional MCP tools.

A fast role scopes questions and gathers evidence through a source-retrieval
role. Slow roles review that evidence independently through memory/lifetime,
bounds/arithmetic, races and general-correctness lenses. Commit reviews also
check assertions made by changelogs and comments. Follow-up questions become
prioritized research tasks. A turn limit bounds the research rounds, but does
not strictly bound tokens, wall time or requests inside each round.

The review workflow records findings; export creates individual finding
directories; validate challenges their premises and reachability; triage assesses
them; fix can modify source, commit, build and export patches. JSON workflow
contracts and Rust checks govern transitions. LLM conclusions still need human
verification. See the pinned upstream [workflow documentation](../vendor/kres/docs/workflow.md).

## Useful work at Samsung R&D

These are candidate applications, since your precise subsystem and product tree
have not been specified.

| Your task | How KRes can help | Evidence you should require |
|---|---|---|
| Driver review: camera, display, GPU, storage or connectivity | Trace probe failures, remove paths, workqueue cancellation, reference ownership, DMA buffer lifetime and user-controlled lengths | Real callers, teardown ordering, locking context and a reproducible trigger |
| ARM64/SoC suspend and resume | Follow state transitions and concurrent workers through runtime PM and device teardown | Board-specific configuration, firmware contracts, suspend stress and hardware results |
| Vendor backports and Android/common merges | Review a commit/range and inspect unchanged users that depend on the changed contract | Correct base revision, required prerequisite commits, Kconfig coverage and target builds |
| Memory management or scheduling changes | Investigate lifetime, accounting, bounds and cross-file invariants | Allocation/error paths, lock ordering, reclaim context, performance measurements |
| Crash triage | Start from a suspect function or commit and ask for concrete reachability and lifetime evidence | Symbolized trace, exact source/config, reproducer and sanitizer output |
| Fix preparation | Validate an exported finding, then iterate on a candidate patch and build | Human-reviewed diff, subsystem tests, checkpatch and target-device tests |
| Review backlog | Export findings, deduplicate and validate them before assigning engineering effort | Distinguish active, unconfirmed and invalidated findings; preserve evidence and open questions |

Begin with one driver file or a small patch series. Compare KRes findings with
your normal review before expanding to whole subsystems. Keep stable identifiers,
source revision, model selection, results and test evidence with each run.

## Suggested pilot

1. Run the public-source demo on `lib/list_sort.c` for one round.
2. Review a small public commit using `bash scripts/review.sh <commit> 2`.
   The checkout is shallow, so first fetch the relevant base/history through the
   existing Git proxy. A missing parent limits commit/history analysis.
3. Export the run with `scripts/kres --export <export-dir> --results <run-dir>`.
4. Validate individual exported findings against the exact source tree. The
   upstream docs describe `--prompt 'validate: <finding-dir> <source-tree>'`.
   Use the same explicit provider arguments as `scripts/review.sh` when calling
   the CLI directly; the demo does not install global configuration.
5. Prove surviving issues with KUnit, kselftest, syzkaller, lockdep, KASAN/KCSAN,
   fault injection or device-specific tests, whichever exercises the claim.

For vendor code, use your organization's approved provider and data-handling
policy before sending source to a model. The demo uses only public source.
For independent second opinions configure a genuinely different model;
this demo uses one model for every role and does not claim independent-model
validation. Semcode can add indexed callers/callees and history search later;
the initial setup uses KRes's read/grep/git fallbacks.

KRes cannot establish firmware correctness, hardware behavior, battery impact,
thermal behavior, latency or throughput from source review alone. Its tests are
tests of KRes itself. A clean review is not proof that a kernel is bug-free.
Use `/fix` in a disposable development branch only after inspecting upstream's
mutating workflow and preparing the correct cross-toolchain and kernel config.
This demo does not run `/fix`, boot Linux, or claim a Samsung target build.
