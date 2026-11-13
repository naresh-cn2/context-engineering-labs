# Architecture Overview

`context-engineering-labs` is an independent, per-unit publication of the
implementations completed for the Hugging Face Context Engineering Course
(Units 1–6). Each unit is a self-contained, runnable project under its own
directory, with its own tests, dependencies, and documentation.

## Repository layout

```
context-engineering-labs/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── .gitignore
├── requirements.txt            # aggregated dependencies (all units)
├── PROGRESS.md                 # progress & certification status
├── unit-01-agent-skills/
│   └── hf-dataset-validation/  # Unit 1 — Agent Skills
├── unit-02-mcp/
│   └── text-processor-mcp/     # Unit 2 — MCP server + Gradio UI
├── unit-03-plugins/
│   └── text-processor-plugin/  # Unit 3 — Plugin bundle (manifests + skills)
├── unit-04-subagents/
│   └── code-quality-pipeline/  # Unit 4 — Multi-agent quality pipeline
├── unit-05-hooks/
│   └── agent-activity-dashboard/  # Unit 5 — Hook telemetry dashboard
├── unit-06-nano-harness/       # Unit 6 — Nano agent harness (bonus)
├── tests/
│   └── integration_audit_test.py   # end-to-end integration & security audit
└── docs/
    ├── ARCHITECTURE.md
    ├── SECURITY_AUDIT.md
    └── RUNTIME_VERIFICATION.md
```

Each unit directory is intentionally independent: scripts reference their own
siblings via relative imports / `sys.path` insertion, so any unit can be run
in isolation without installing the whole repository.

## Unit-by-unit architecture

### Unit 1 — Agent Skills: `hf-dataset-validation`

A standardized Agent Skill (`SKILL.md` frontmatter per the Agent Skills
Specification) wrapping a dataset validation engine.

- `scripts/validate_dataset.py` — loads CSV/Parquet/JSON/Arrow, validates
  required columns (`text`, `label` by default), detects missing values,
  duplicate rows, and empty/whitespace strings; emits structured JSON and
  CLI exit codes (0 = valid/warn, 1 = blocking error).
- `scripts/generate_report.py` — human-readable ASCII validation report.
- `test_data/` — clean, flawed, invalid-schema, and JSON samples.
- `tests/test_validation.py` — 10 tests.

### Unit 2 — MCP: `text-processor-mcp`

A Model Context Protocol server exposing text-analysis tools over stdio,
plus a Gradio web UI.

- `server.py` — FastMCP/MCPServer with `analyze_text`, `extract_keywords`,
  `check_reading_level`, `reverse_text`, `detect_sentiment`.
- `app.py` — Gradio dashboard (`http://127.0.0.1:7860`) wrapping the same
  tools.
- `tests/test_text_processor.py` — 9 tests.

### Unit 3 — Plugins: `text-processor-plugin`

A redistributable plugin bundle supporting manifest-first (Claude Code,
Codex) and code-first (OpenCode) platforms, plus an MCP link to Unit 2.

- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` — platform
  manifests.
- `.mcp.json` — MCP server connection spec pointing at the Unit 2 server
  (`../../unit-02-mcp/text-processor-mcp/server.py`).
- `.opencode/plugins/text-processor-plugin.js` — OpenCode plugin module.
- `skills/{analyze-text,extract-keywords,check-reading-level}/SKILL.md` —
  bundled agent skills.
- `tests/test_plugin.py` — 5 tests.

### Unit 4 — Subagents: `code-quality-pipeline`

A simulated multi-agent Research → Implement → Verify pipeline using
Fan-Out/Fan-In and Sequential Handoff patterns.

- `main.py` — target application under analysis (with intentional, clearly
  marked flaws: N+1 queries, artificial latency, non-constant-time token
  comparison).
- `pipeline_runner.py` — orchestrator implementing researcher, implementer
  diff, parallel security & performance reviewers, and orchestrator sign-off.
- `.claude/agents/*.md` + `.codex/agents/*.toml` — four subagent specs
  (researcher, implementer, security-reviewer, performance-reviewer).
- `tests/test_pipeline.py` — 10 tests.

> **Simulated orchestration:** the agents are deterministic Python functions,
> not live LLM-powered agents. No LLM calls are made during tests.

### Unit 5 — Hooks: `agent-activity-dashboard`

A cross-platform hook telemetry receiver built with FastAPI + Gradio.

- `app.py` — FastAPI `POST /event` receiver with a payload normalizer
  (OpenCode / Claude Code / Codex / Pi), bounded in-memory ring buffer (500
  events), `GET /health`, and a mounted Gradio UI with tool-frequency chart
  and events table (`http://127.0.0.1:8000`).
- Hook configs: `.claude/settings.json`, `.codex/hooks.json`,
  `.opencode/plugins/dashboard.js`.
- `tests/test_dashboard.py` — 6 tests.

### Unit 6 — Nano Harness: `nano_harness` (bonus)

A minimal code-first autonomous agent loop with tool-boundary sandboxing.

- `nano_harness.py` — `NanoHarness` class with `safe_path` path confinement,
  command allowlist, write gating (`allow_write`), output clipping
  (`max_chars`), step-limited loop, observation reflection, and extended
  tools `web_fetch` / `hf_search`.
- `tests/test_nano_harness.py` — 9 tests.

> **Sandbox limitation:** `web_fetch` / `hf_search` make real network calls
> when exercised. Path confinement and command allowlisting are enforced in
> Python, not by an OS sandbox. See `docs/RUNTIME_VERIFICATION.md`.

## Integration & security audit

`tests/integration_audit_test.py` runs live, non-mocked integration tests
across Units 1–6 (CLI execution, live MCP tool invocation, plugin manifest
validation, pipeline orchestration, hook delivery, nano-harness security
boundaries). Together with the per-unit suites, the total is **61 tests**,
all of which must pass (`pytest -q`).

## Technology stack

Python 3.12; pandas, datasets, numpy, pyarrow; mcp; gradio; fastapi,
uvicorn, httpx; pytest, PyYAML, tomlkit. Nano Harness uses only the Python
standard library.

## Attribution

Implementations are original student work inspired by the public Hugging
Face Context Engineering Course. They are not official Hugging Face code,
and no official certificates are claimed. See `README.md` (Hugging Face
course attribution).
