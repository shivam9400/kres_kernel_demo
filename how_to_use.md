# How to use this demo

## Prepare

```bash
git clone https://github.com/shivam9400/kres_kernel_demo.git
cd kres_kernel_demo
bash scripts/bootstrap.sh
```

Use the existing checkout in a cloud task. See [setup.md](setup.md) for exact
versions, prerequisites and network requirements. The bootstrap builds KRes,
downloads Linux and review guides, and generates local config. It does not
install Gemini CLI or perform company login.

## Current LLM

`config/llm.json` defaults to provider `codex` and model `gpt-5.6-sol` for
fast, slow, main and todo roles; classification falls back to fast. That is
the requested model, not evidence of a completed inference: the original cloud
run was blocked by networking. KRes itself is provider-independent.

```bash
codex login status
python3 scripts/run.py --test
bash scripts/review.sh lib/list_sort.c 1
```

The first review target defaults to `lib/list_sort.c`. The second argument is
the number of research rounds. Start small: one round can issue many requests.
The configured `max_parallel` bounds task concurrency, not total cost.

## Switch to the company's Gemini CLI

1. Have your company-provided `gemini` executable and authentication configured
   through your internal installation/login procedure. No company credentials
   are needed in this repository. Check `gemini --version` and `gemini --help`.
2. Copy `config/gemini.example.json` to `.runtime/company-llm.json`. Set `model`
   to the model your company authorizes; `gemini-2.5-pro` is only an example.
   Set `gemini_cli` to the executable's absolute path if it is not on PATH.
3. Run a provider check, then a public-source review:

```bash
cp config/gemini.example.json .runtime/company-llm.json
# Edit .runtime/company-llm.json with your approved executable/model.
python3 scripts/run.py --config .runtime/company-llm.json --test
bash scripts/review.sh --config .runtime/company-llm.json lib/list_sort.c 1
```

For a persistent default, edit `config/llm.json` to contain the same non-secret
settings. Change `provider` back to `codex` and `model` to an authorized Codex
model to switch back. Do not store keys, tokens or credential paths in tracked
configuration. The bridge inherits CLI authentication and proxy/CA settings.
Ask your administrator for the actual required Gemini/Vertex/company endpoint
domains; they vary by company deployment and are not guessed by this demo.

The integration expects Gemini CLI headless support for `--model`,
`--output-format json`, `--approval-mode default`, `-p`, stdin context, and a
JSON `response` string. Each request uses a fresh CLI process in an empty
temporary directory. It asks the CLI to answer from supplied text without tools;
that instruction is not an OS security boundary. Enforce tool restrictions
through your company's CLI policies. No YOLO or automatic tool approval is used.
Company-global extensions/settings may still apply. Check them with your admin.

The bridge is tested with a fake CLI and the real KRes binary. A real Gemini
provider check and full review are required before relying on it. Gemini CLI
is not installed in the original cloud environment. CLI JSON/flag changes can
require updating the adapter. Responses are buffered and token cost accounting
is unavailable. Context/output limits and thinking settings are provider-specific;
the initial adapter settings are not a promise of any company's model capacity.

## Inspect and use results

Each review writes a new directory under `results/review-<timestamp>-<pid>/`.
Read `report.md`, `findings.json` and `session.json`, plus `.kres/logs/` inside
the Linux tree. Verify the process completed: empty findings after cancellation
or a provider failure do not mean the code is clean.

```bash
scripts/kres --export results/export --results results/<completed-run>
```

Use upstream's [workflow guide](vendor/kres/docs/workflow.md) for per-finding
validation, triage, summaries and patch generation. `scripts/run.py` currently
wraps provider tests and reviews; it does not wrap those additional workflows.
Direct model-dependent KRes commands need explicit provider/role/skills config;
Gemini commands also need the bridge running. Do not assume a global provider
was installed. This is a review pilot, not an automated fix deployment.

For vendor backports, first fetch relevant base/history: the Linux checkout is
shallow. For real products, use the exact product source and config and your
approved data-handling process. Confirm findings with tests, traces or hardware
before proposing a patch. See [architecture](docs/architecture.md) and
[kernel engineering use cases](docs/kernel-engineering.md).

## Troubleshooting

- Codex HTTP CONNECT 403: apply the saved `chatgpt.com` domain change in cloud
  settings. A GitHub login does not grant model access.
- Gemini 502: verify the CLI executable, company auth, approved model, headless
  JSON flags and network route. CLI stderr is intentionally not returned by the
  bridge because it can contain confidential details.
- Timeout: inspect company service readiness first; then adjust
  `timeout_seconds` in your local config if legitimate requests need more time.
- Test the adapter without credentials using `python3 tests/test_gemini_bridge.py`.
