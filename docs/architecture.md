# KRes architecture and complete workflow

This diagram describes the pinned upstream engine and this demo's provider
selection. Dashed optional paths need additional configuration or explicit use.

```mermaid
flowchart TB
  User[Kernel engineer: file, directory, commit or range] --> Config[config/llm.json: provider, model, parallelism]
  Config --> Launcher[scripts/review.sh → scripts/run.py]
  Bootstrap[scripts/bootstrap.sh] --> Rust[Rust 1.96 + locked release build]
  Bootstrap --> Linux[Linux v6.12 source + optional fetched history]
  Bootstrap --> Guides[Kernel review guides + generated local config]
  Rust --> CLI[KRes CLI / REPL: kres crate]
  Launcher --> CLI
  CLI --> Session[kres-repl: session, consent, workflow dispatch]
  Session --> Contracts[Embedded JSON workflows + schema/invariant checks]
  Contracts --> Review[Review bootstrap: workspace detection, inventory, change survey]
  Linux --> Review
  Guides --> Review
  Review --> Plan[Plan + prioritized todo queue]
  Plan --> Task[kres-core task manager: bounded concurrency, cancellation]
  Task --> Fast[Fast role: scope task and request evidence]
  Fast --> Gather[kres-agents deterministic gather service]
  Gather --> Local[read / grep / git evidence]
  Gather -. optional .-> MCP[kres-mcp → semcode MCP: symbols and call graph]
  MCP -. missing or failed lookup .-> Local
  Local --> Evidence[Source bodies, callers, types, history and citations]
  MCP --> Evidence
  Evidence --> Fast
  Fast --> Lenses[Slow roles: independent review lenses]
  Lenses --> Memory[Memory and lifetime]
  Lenses --> Bounds[Bounds and arithmetic]
  Lenses --> Races[Concurrency and locking]
  Lenses --> General[General correctness]
  Lenses -. commit reviews .-> Assertions[Changelog and comment assertions]
  Memory & Bounds & Races & General & Assertions --> Merge[Consolidate and deduplicate findings]
  Merge --> Missing{Blocking evidence missing?}
  Missing -->|bounded requeue| Gather
  Missing -->|settled| Store[Finding deltas + status, severity, evidence, open questions]
  Store --> Follow[Deduplicate and prioritize follow-up tasks]
  Follow --> Stop{Turn cap or no remaining work?}
  Stop -->|continue| Plan
  Stop -->|stop / cancel| Artifacts[Per-run findings.json, report.md, session.json, logs]
  Artifacts --> Export[Export: individual finding directories + index]
  Export --> Validate[Validate: challenge claims and reachability]
  Export --> Triage[Triage: assess defect and severity]
  Validate --> Verdict[Typed verdict + evidence + summary.md]
  Triage --> Verdict
  Verdict --> Human[Engineer verifies with reproducer, KUnit, sanitizers and hardware]
  Human -. explicit fix invocation .-> Fix[Fix: research → patch → changelog → commit]
  Fix --> Build[Kernel build with prepared config and toolchain]
  Build --> PatchReview[Review / triage patch and iterate]
  PatchReview -->|defect| Fix
  PatchReview -->|accepted| Patch[Export patch and fix artifacts]
  Human --> Final[Human decision and normal team review process]
  Patch --> Final

  Fast & Lenses & Review & Merge & Follow & Validate & Triage & Fix --> LLM[kres-llm transport]
  LLM --> Select{Configured provider}
  Select -->|codex| Codex[Codex SDK → authenticated Codex CLI → selected model]
  Select -->|gemini-cli| Bridge[Loopback OpenAI-chat bridge: random token, per-run lifetime]
  Bridge --> Gemini[Fresh Gemini CLI process per call: company authentication]
  Gemini --> Model[Company-authorized Gemini model / endpoint]
```

The model roles are responsibilities, not separate model subscriptions. This demo
selects one model for all roles. A second independent model requires additional
upstream configuration. Classification defaults to the fast provider.

The Gemini bridge translates KRes chat requests to a text conversation on CLI
stdin and converts CLI JSON responses to chat-completion responses. It buffers
each response; it does not stream tokens, implement tool calling, share CLI
sessions or report reliable token costs. KRes continues to gather source itself.
The bridge binds only loopback and requires an ephemeral bearer token.

Retained files include source, toolchain, build outputs and configuration.
Processes are transient. Each Gemini run starts and stops its own bridge.
No bridge or CLI process needs to survive a cloud snapshot. Review output is
evidence for engineering investigation, not proof of correctness.
