# Recorded Linux review run

This is an actual run against public Linux source, not a simulated review.
The review stopped during bootstrap because model inference did not complete.
The accompanying [console log](workflow-run-2026-10-28.log) contains the command,
source revisions, start/end times, exit status and captured output.

Target: `lib/list_sort.c` in Linux v6.12. Provider: Codex CLI. Requested model:
`gpt-5.6-sol`. Limit: one completed task, two parallel tasks, and a 60-second
outer timeout with SIGINT cancellation and a 10-second kill grace period.

## Observed workflow

| Stage | What happened in this run |
|---|---|
| Select configuration | Read `config/llm.json`; selected Codex and the configured model |
| Launch | `scripts/review.sh` invoked `scripts/run.py`, which generated temporary provider config and started the real KRes binary |
| Initialize session | Created a session ID, empty findings store and per-run artifact paths |
| Configure tools | Enabled the standard action allowlist; bash disabled; no semcode MCP server configured |
| Detect workspace | Identified the source tree as Linux, using make-oriented build assumptions |
| Load knowledge | Loaded one auto-invoked kernel skill referencing the downloaded review guides |
| Configure roles | Prepared fast, slow, main, todo and classifier roles; this does not establish successful model calls |
| Configure review | Loaded four lenses: memory/lifetime, bounds, races and general correctness |
| Submit target | Submitted `review: lib/list_sort.c`, granted target-directory access and saved prompt.md |
| Bootstrap source survey | Attempted the model-backed fallback file survey; no completed response before cancellation |
| Stop | Outer timeout requested cancellation; see console log for exact final messages and exit status |

The Python launcher emitted a `KeyboardInterrupt` traceback when the outer
timeout sent SIGINT. Its KRes and Codex child processes remained after the
launcher exited and were explicitly terminated as cleanup. The session recorded
`completed_run_count: 0`, and the findings store contained zero findings.

## Later stages that were not reached

The run did **not** complete the file inventory/change survey, create a useful
review plan, execute a completed lensed review task, consolidate findings,
prioritize follow-ups, or finish one review round. Export, per-finding validation,
triage, summary generation and automatic fixing were not invoked. Those are
separate operations, not automatic consequences of starting a review.

The initialized findings file contained zero findings. That is an incomplete
run artifact, not a clean review result. No kernel build, boot or hardware test
was performed.

## Why it stopped

A fresh credential-free HTTPS check to the model destination returned
`CONNECT tunnel failed, response 403`. The running cloud policy still has no
custom allowed hosts, so the previously saved `chatgpt.com` draft change has
not been applied to this runtime. This is concrete evidence of a network
prerequisite; it does not establish that the selected model will be authorized
after connectivity is restored. The CLI also warned that version 0.163.0 is
newer than the SDK's tested 0.145.0 version.

## Rerun after restoring model access

Review and save the existing network change in environment settings and publish
the environment. Then test the provider and run again:

```bash
cd /workspace/kres_kernel_demo
python3 scripts/run.py --test
bash scripts/review.sh lib/list_sort.c 1
```

For the company Gemini CLI, use the config instructions in
[how_to_use.md](../how_to_use.md). Gemini was not selected for this run and is
not installed here. Successful Gemini adapter tests from the previous change
do not represent real model inference.

Logs published here contain console/status output and a credential-free network
check. Credential files, temporary provider configuration, full model request
logs and global configuration have not been published. The local result and
session paths in the console log refer to this cloud instance; generated
artifacts remain ignored by Git.
