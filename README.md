# KRes kernel engineering demo

KRes is an LLM-driven research and review tool for large source trees. This
repository packages an unchanged, pinned KRes source snapshot and reproducible
scripts for reviewing public Linux v6.12 source.

Read [setup.md](setup.md) for installation, validation, commands and limitations.
Read [docs/kernel-engineering.md](docs/kernel-engineering.md) for practical uses
in a Samsung kernel engineering workflow.

```bash
bash scripts/bootstrap.sh
bash scripts/review.sh lib/list_sort.c 1
```

The second command uses your authenticated Codex CLI and consumes model usage.
Results are local under `results/`. No proprietary source is included.

KRes upstream: https://github.com/masoncl/kres

Vendored revision: `4ef4b706358abfcb82d112213632f4a8edda2868`.
Upstream MIT and Apache-2.0 license files remain in `vendor/kres/`.
Linux and the review guides retain their own licenses in their downloaded trees.
