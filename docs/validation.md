# Validation evidence

Validated in the managed Linux x86-64 environment on 28 October 2026.

| Check | Observed result |
|---|---|
| Upstream KRes snapshot comparison | Identical to `4ef4b706358abfcb82d112213632f4a8edda2868`, excluding Git metadata and generated target outputs |
| Rust 1.96 release build with `--locked -j 4` | Passed; initial complete release build took about 6m25s |
| `bash scripts/bootstrap.sh` rerun | Passed; reused installed dependencies and build outputs |
| CLI version/help | Passed, `kres 0.1.0` |
| Review workflow schema | Passed, 1 step |
| Validate workflow schema | Passed, 5 steps |
| Triage workflow schema | Passed, 1 step |
| Fix workflow schema | Passed, 20 steps; workflow not executed |
| `cargo test --release --locked -p kres-core` | 248 passed, 0 failed, 0 ignored; 0 documentation tests |
| Script syntax and Python compilation | Passed |
| Whitespace check on added demo files | Passed; vendored upstream retains its pre-existing whitespace warnings |
| Codex CLI authentication status | Existing ChatGPT login present; credential values were not read |
| Direct Codex inference | Blocked: proxy HTTP CONNECT 403 to `chatgpt.com`; retries were interrupted |
| KRes provider test after local MCP correction | No response within the 35-second bound; timeout exit 124 |
| Linux source-review startup | Detected Linux, loaded kernel skill, configured roles and four review lenses; model analysis did not complete |

The SDK warns that CLI 0.163.0 is newer than its tested 0.145.0 version.
The initial app-server initialization failure was diagnosed as an invalid
transport-less `meta_core` entry and corrected in local generated config.
Compatibility beyond initialization and successful model responses remains
unverified while network access is blocked.

The environment draft contains the tested bootstrap command, startup/check
instructions and custom allowed domain `chatgpt.com`, preserving the existing
package-manager preset. Saving a draft does not apply or publish it. Review
and save the changes in environment settings, then publish the environment.
After the updated runtime is available, rerun the provider test and public
review from setup.md. If the account cannot use `gpt-5.6-sol`, select an
authorized model consistently in local provider config and review role flags.

No review findings, completed inference, independent-model validation, full
workspace test suite, kernel build, kernel boot or hardware behavior are claimed.
Only KRes core tests were selected; the other crate test suites were not run.
Live failed-review artifacts remain ignored under `results/` and Linux's
`.kres/logs/`; they are not demonstration findings.

The local tool build and source workspace are prepared. A working end-to-end
LLM review remains blocked on the network prerequisite and subsequent provider
validation. Do not treat an empty findings file from an interrupted run as a
clean review.

## Configurable Gemini CLI adapter

Two adapter tests passed using the real compiled KRes binary and a deterministic
fake Gemini executable: chat transport to CLI/stdin/JSON and rejection of an
unauthenticated loopback request. Run `python3 tests/test_gemini_bridge.py`.
The cloud command sandbox denies socket creation, so this test requires an
execution context permitting loopback listeners. KRes's explicit `proxy: ""`
is used only for its loopback bridge; the Gemini subprocess retains outbound
proxy and CA settings. No native KRes source was changed.

Gemini CLI was not installed and no company credentials or real Gemini inference
were tested. End-to-end kernel findings from Gemini remain unverified.
