# Architecture Overview

`context-engineering-labs` is an independent, per-unit publication of the implementations completed for the Hugging Face Context Engineering Course (Units 1–6). Each unit is a self-contained, runnable project under its own directory, with its own tests, dependencies, and documentation.

## Repository Layout

```
context-engineering-labs/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── .gitignore
├── requirements.txt            # Aggregated dependencies (all units)
├── PROGRESS.md                 # Progress & certification status
├── PUBLISH_REPORT.md           # Publication & verification report
├── package.json                # Root Git package manifest for OpenCode plugin distribution
├── tests/
│   └── integration_audit_test.py   # End-to-end integration & security audit
├── docs/
│   ├── ARCHITECTURE.md         # Architecture overview & per-unit design
│   ├── SECURITY_AUDIT.md       # Pre-publication security audit
│   └── RUNTIME_VERIFICATION.md # Final runtime verification report
├── unit-01-agent-skills/
│   └── hf-dataset-validation/  # Unit 1 — Agent Skills
├── unit-02-mcp/
│   └── text-processor-mcp/     # Unit 2 — MCP server + Gradio UI
├── unit-03-plugins/
│   └── text-processor-plugin/  # Unit 3 — Plugin bundle (manifests + skills + OpenCode runtime)
├── unit-04-subagents/
│   └── code-quality-pipeline/  # Unit 4 — Multi-agent pipeline (deterministic + live LLM mode)
├── unit-05-hooks/
│   └── agent-activity-dashboard/  # Unit 5 — Hook telemetry dashboard + native OpenCode bridge
└── unit-06-nano-harness/       # Unit 6 — Hardened Nano Agent Harness (bonus)
```

Each unit directory is intentionally independent: scripts reference their own siblings via relative imports / `sys.path` insertion, so any unit can be run in isolation without installing the whole repository.

---

## Unit-by-Unit Architecture

### Unit 1 — Agent Skills: `hf-dataset-validation`

A standardized Agent Skill (`SKILL.md` frontmatter per the Agent Skills Specification) wrapping a dataset validation engine.

- `scripts/validate_dataset.py` — loads CSV/Parquet/JSON/Arrow, validates required columns (`text`, `label` by default), detects missing values, duplicate rows, and empty/whitespace strings; emits structured JSON and CLI exit codes (0 = valid/warn, 1 = blocking error).
- `scripts/generate_report.py` — human-readable ASCII validation report.
- `test_data/` — clean, flawed, invalid-schema, and JSON samples.
- `tests/test_validation.py` — 10 tests.

### Unit 2 — MCP: `text-processor-mcp`

A Model Context Protocol server exposing text-analysis tools over stdio, plus a Gradio web UI.

- `server.py` — FastMCP/MCPServer with `analyze_text`, `extract_keywords`, `check_reading_level`, `reverse_text`, `detect_sentiment`.
- `app.py` — Gradio dashboard (`http://127.0.0.1:7860`) wrapping the same tools.
- `tests/test_text_processor.py` — 9 tests.

### Unit 3 — Plugins: `text-processor-plugin`

A redistributable plugin bundle supporting manifest-first (Claude Code, Codex) and code-first (OpenCode) platforms, plus an MCP link to Unit 2.

- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` — platform manifests.
- `.mcp.json` — MCP server connection spec pointing at the Unit 2 server (`../../unit-02-mcp/text-processor-mcp/server.py`).
- `package.json` — NPM / Git package manifest declaring the module entrypoint for OpenCode runtime loading.
- `.opencode/plugins/text-processor-plugin.js` — OpenCode plugin module exporting `{ id: "text-processor-plugin", setup: async (ctx) => ... }`.
- `skills/{analyze-text,extract-keywords,check-reading-level}/SKILL.md` — bundled agent skills.
- `tests/test_plugin.py` — 6 tests.

### Unit 4 — Subagents: `code-quality-pipeline`

A multi-agent **Research → Implement → Verify** pipeline with sequential handoff and parallel review:

```
[Target Code: main.py]
          │
          ▼
   Stage 1: Researcher (Explores architecture & maps risks)
          │
          ▼
   Stage 2: Implementer (Applies minimal, focused code change)
          │
          ├─── Fan-Out ─────────────────────────┐
          │                                     │
          ▼                                     ▼
   Stage 3a: Security Reviewer           Stage 3b: Performance Reviewer
   (Read-Only: Auth & token leaks)       (Read-Only: N+1 & latency bottlenecks)
          │                                     │
          └─── Fan-In ──────────────────────────┘
          │
          ▼
   Stage 4: Orchestrator Sign-off (Synthesizes verdicts & approves merge)
```

- `pipeline_runner.py` — orchestrator supporting two modes:
  - **Deterministic Simulation**: Fast static rule evaluation for CI.
  - **Live LLM Execution**: Connects to the local OpenCode server (`http://127.0.0.1:28894`) and invokes NVIDIA Nemotron (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` at `cost: 0`).
- **Agent Confinement**: Reviewer sessions enforce `{"action": "write", "resource": "*", "effect": "deny"}` and `{"action": "edit", "resource": "*", "effect": "deny"}`.
- `traces/live_run_trace.json` — verified multi-agent execution trace.
- `tests/test_pipeline.py` — 11 tests.

### Unit 5 — Hooks: `agent-activity-dashboard`

A telemetry receiver and live dashboard combining FastAPI and Gradio.

- `app.py` — FastAPI receiver (`POST /event`, `GET /health`) with a bounded ring buffer (500 events) mounted with a Gradio UI.
- `event_forwarder.py` — native OpenCode event forwarder bridge that streams SSE events from OpenCode's `GET /api/event` and delivers them to the dashboard API. Implements fail-soft exception handling so offline dashboards never block agent execution.
- `.opencode/plugins/dashboard.js` — code-first OpenCode plugin hook for in-process telemetry.
- `.claude/settings.json`, `.codex/hooks.json` — hook configuration for Claude Code and Codex.
- `tests/test_dashboard.py` & `tests/test_opencode_hook_integration.py` — 9 tests.

### Unit 6 — Nano Harness: `nano_harness`

A hardened code-first autonomous agent harness demonstrating sandboxed Python execution:

- `nano_harness.py`:
  - **Path Confinement**: `resolve().relative_to(workspace)` verifies paths and symlink targets remain inside workspace. Null bytes and encoded sequences are caught.
  - **Command Hardening**: Enforces binary allowlist, executes with `shell=False`, forbids binary path traversal, and rejects chaining operators (`;`, `&&`, `||`, `|`, `` ` ``, `$()`).
  - **Write Gating**: Disallows mutations targeting `.git/`, `.env`, or `.ssh/`.
  - **Network Sandboxing**: Restricts `web_fetch` to `http` and `https`, and blocks loopback, private IPs, and cloud metadata (`169.254.169.254`) for SSRF protection.
  - **Context Budgeting**: Output clipping and sanitized error messages.
- `tests/test_nano_harness.py` — 15 tests.
