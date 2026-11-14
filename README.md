# Context Engineering Labs

Independent implementations completed for the **Hugging Face Context Engineering Course** (Units 1–6), published as a personal, independently maintained learning portfolio.

**Repository:** https://github.com/naresh-cn2/context-engineering-labs

---

## ⚠️ Important Disclaimers

- **Certification Status**: No official Hugging Face certificates are claimed or displayed by this repository. Completion status and quiz results reflected in `PROGRESS.md` are self-reported by the student and are **not verified certifications**.
- **Unit 4 Dual Execution**: The subagents pipeline supports both deterministic rule-based evaluation (for deterministic CI/CD) and a live LLM multi-agent mode powered by NVIDIA Nemotron via OpenCode's local REST API.
- **Unit 6 Sandbox Boundaries**: In-process Python evaluation via `exec()` with restricted `__builtins__` provides application-level gating (path containment, command allowlisting, SSRF protection). It is a learning artifact, not a substitute for kernel/OS-level container isolation.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Motivation and Objectives](#motivation-and-objectives)
3. [Technologies and Tools](#technologies-and-tools)
4. [Architecture Overview](#architecture-overview)
5. [Unit-by-Unit Implementation Details](#unit-by-unit-implementation-details)
6. [Installation Instructions & Windows WDAC Guide](#installation-instructions--windows-wdac-guide)
7. [Environment Setup](#environment-setup)
8. [Execution Instructions for Every Unit](#execution-instructions-for-every-unit)
9. [OpenCode Integration (Plugins, Subagents, Hooks)](#opencode-integration-plugins-subagents-hooks)
10. [MCP Configuration](#mcp-configuration)
11. [Testing Instructions](#testing-instructions)
12. [Security Considerations](#security-considerations)
13. [Hugging Face Course Attribution](#hugging-face-course-attribution)
14. [Project Progress and Certification Status](#project-progress-and-certification-status)

---

## Project Overview

`context-engineering-labs` publishes the hands-on lab implementations built while working through the Hugging Face Context Engineering Course. Each of the six course units is represented by a self-contained, runnable project:

| Unit | Focus | Project | Path | Tests | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Unit 1 | Agent Skills | `hf-dataset-validation` | `unit-01-agent-skills/hf-dataset-validation/` | 10/10 | **COMPLETE** |
| Unit 2 | Model Context Protocol (MCP) | `text-processor-mcp` | `unit-02-mcp/text-processor-mcp/` | 9/9 | **COMPLETE** |
| Unit 3 | Plugins — Bundling for Distribution | `text-processor-plugin` | `unit-03-plugins/text-processor-plugin/` | 6/6 | **COMPLETE** |
| Unit 4 | Subagents — Multi-Agent Workflows | `code-quality-pipeline` | `unit-04-subagents/code-quality-pipeline/` | 11/11 | **COMPLETE** |
| Unit 5 | Hooks — Observing and Guarding | `agent-activity-dashboard` | `unit-05-hooks/agent-activity-dashboard/` | 9/9 | **COMPLETE** |
| Unit 6 | Nano Harness — Build Your Own Agent | `nano_harness` | `unit-06-nano-harness/` | 15/15 | **COMPLETE** |
| — | Integration & Security Audit | Integration Suite | `tests/integration_audit_test.py` | 12/12 | **COMPLETE** |
| **Total** | **Comprehensive Course Suite** | — | — | **72/72** | **100% PASSING** |

---

## Technologies and Tools

| Category | Tools |
| :--- | :--- |
| Language | Python 3.12 |
| Data / ML | pandas, datasets, numpy, pyarrow |
| MCP | mcp (FastMCP / MCPServer) |
| Web UI / API | gradio, fastapi, uvicorn, httpx, starlette |
| Testing | pytest, PyYAML, tomlkit |
| Agent Runtime | OpenCode v2.2.6+, Claude Code, OpenAI Codex |
| LLM Provider | NVIDIA Nemotron (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` at `cost: 0`) |

---

## Unit-by-Unit Implementation Details

### Unit 1 — Agent Skills: `hf-dataset-validation`
A standardized Agent Skill (`SKILL.md` frontmatter per the Agent Skills Specification) wrapping a dataset validation engine.
- **`scripts/validate_dataset.py`**: Loads CSV/Parquet/JSON/Arrow datasets; validates required columns (`text`, `label`); detects missing values, duplicate rows, and empty/whitespace strings; emits structured JSON and CLI exit codes (0 = valid/warn, 1 = blocking error).
- **`scripts/generate_report.py`**: Human-readable ASCII validation report.
- **`test_data/`**: Clean, flawed, invalid-schema, and JSON samples.
- **Tests**: 10 passing (`tests/test_validation.py`).

### Unit 2 — MCP: `text-processor-mcp`
A Model Context Protocol server exposing text-analysis tools over stdio, plus a Gradio web UI.
- **`server.py`**: FastMCP/MCPServer with `analyze_text`, `extract_keywords`, `check_reading_level`, `reverse_text`, `detect_sentiment`.
- **`app.py`**: Gradio dashboard at `http://127.0.0.1:7860`.
- **Tests**: 9 passing (`tests/test_text_processor.py`).

### Unit 3 — Plugins: `text-processor-plugin`
A redistributable plugin bundle supporting manifest-first (Claude Code, Codex) and code-first (OpenCode) platforms, plus an MCP link to Unit 2.
- **`.claude-plugin/plugin.json`**, **`.codex-plugin/plugin.json`**: Platform manifests.
- **`.mcp.json`**: MCP server connection spec pointing to Unit 2 server.
- **`package.json`**: NPM/Git package manifest for OpenCode v2.2.6 package loading.
- **`.opencode/plugins/text-processor-plugin.js`**: OpenCode plugin module exporting `{ id: "text-processor-plugin", setup: async (ctx) => ... }`.
- **Verified Runtime Loading**: Installed via `opencode plugin add git+file://...` and confirmed active via `opencode api GET /api/plugin` (`status: active`).
- **Tests**: 6 passing (`tests/test_plugin.py`).

### Unit 4 — Subagents: `code-quality-pipeline`
A multi-agent Research → Implement → Verify pipeline using Fan-Out / Fan-In and Sequential Handoff patterns.
- **`main.py`**: Target application under analysis with intentional flaws (N+1 queries, timing attacks on tokens).
- **`pipeline_runner.py`**: Orchestrator supporting:
  - **Deterministic Simulation Mode**: Fast static rule checking for CI.
  - **Live LLM Multi-Agent Mode (`--live`)**: Connects to the local OpenCode server and orchestrates 4 subagents:
    1. `researcher`: Identifies architectural risks.
    2. `implementer`: Produces constant-time auth diff and batching/caching logic.
    3. `security-reviewer`: Concurrently reviews changes under enforced read-only permissions (`write` and `edit` tools denied).
    4. `performance-reviewer`: Concurrently reviews latency and query complexity under read-only permissions.
- **`traces/live_run_trace.json`**: Real LLM execution trace captured during live pipeline execution.
- **Tests**: 11 passing (`tests/test_pipeline.py`).

### Unit 5 — Hooks: `agent-activity-dashboard`
A cross-platform hook telemetry receiver built with FastAPI + Gradio.
- **`app.py`**: FastAPI receiver with payload normalizer, bounded in-memory ring buffer (500 events), `GET /health`, and mounted Gradio UI.
- **`event_forwarder.py`**: Native OpenCode event listener bridge that streams SSE events from OpenCode's `GET /api/event` and delivers them to the dashboard API. Implements fail-soft exception handling so offline dashboards never block agent execution.
- **`.opencode/plugins/dashboard.js`**: Code-first OpenCode plugin hook for in-process telemetry.
- **Tests**: 9 passing (`tests/test_dashboard.py` and `tests/test_opencode_hook_integration.py`).

### Unit 6 — Nano Harness: `nano_harness`
A hardened code-first autonomous agent harness demonstrating sandboxed Python execution:
- **`nano_harness.py`**:
  - **Path Confinement**: `resolve().relative_to(workspace)` verifies paths and symlink targets remain inside workspace. Null bytes and encoded sequences (`%2e%2e`) are blocked.
  - **Command Hardening**: Enforces binary allowlist, executes with `shell=False`, forbids binary path traversal, and rejects chaining operators (`;`, `&&`, `||`, `|`, `` ` ``, `$()`).
  - **Write Gating**: Disallows mutations targeting `.git/`, `.env`, or `.ssh/`.
  - **Network Sandboxing**: Restricts `web_fetch` to `http` and `https`, and blocks loopback, private IPs, and cloud metadata (`169.254.169.254`) for SSRF protection.
  - **Context Budgeting**: Output clipping and sanitized error messages preventing host path leakage.
- **Tests**: 15 passing (`tests/test_nano_harness.py`).

---

## Installation Instructions & Windows WDAC Guide

### 1. Clone the Repository
```bash
git clone https://github.com/naresh-cn2/context-engineering-labs.git
cd context-engineering-labs
```

### 2. Create Virtual Environment
> [!IMPORTANT]
> **Windows Application Control (WDAC / AppLocker) Notice**:
> Under default Windows Application Control policies, unsigned `.pyd` C-extensions (such as `pyarrow._json.pyd`) installed in user directories are blocked. To ensure whitelisted system C-extensions are linked cleanly:
> ```bash
> python -m venv --system-site-packages .venv
> ```

### 3. Install Dependencies
Always invoke pip through the virtual environment's Python executable:
```bash
# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt

# Linux / macOS
.venv/bin/python -m pip install -r requirements.txt
```

---

## Execution Instructions for Every Unit

### Unit 1 — Dataset Validation
```bash
python unit-01-agent-skills/hf-dataset-validation/scripts/validate_dataset.py \
  --file unit-01-agent-skills/hf-dataset-validation/test_data/clean_sample.csv \
  --columns text label
```

### Unit 2 — MCP Server & UI
```bash
# Run stdio MCP server
python unit-02-mcp/text-processor-mcp/server.py

# Launch Gradio dashboard
python unit-02-mcp/text-processor-mcp/app.py
```

### Unit 3 — OpenCode Plugin Installation
```bash
# Install plugin via Git package specifier
opencode plugin add git+file://C:/Users/nares/workspace/context-engineering-labs

# Verify runtime status
opencode api GET /api/plugin
```

### Unit 4 — Multi-Agent Code Quality Pipeline
```bash
# Deterministic simulated mode
python unit-04-subagents/code-quality-pipeline/pipeline_runner.py

# Live LLM multi-agent mode (NVIDIA Nemotron via OpenCode)
python unit-04-subagents/code-quality-pipeline/pipeline_runner.py --live
```

### Unit 5 — Activity Dashboard & OpenCode Hook Forwarder
```bash
# Start dashboard server (port 8000)
python unit-05-hooks/agent-activity-dashboard/app.py

# In another terminal: Start native OpenCode SSE event forwarder
python unit-05-hooks/agent-activity-dashboard/event_forwarder.py
```

### Unit 6 — Nano Harness
```bash
python unit-06-nano-harness/nano_harness.py
```

---

## Testing Instructions

Run the complete 72-test suite across all units:

```bash
# Using active virtual environment:
pytest -v

# Or directly targeting the python executable:
.venv\Scripts\python.exe -m pytest -v
```

Expected output:
```
============================= 72 passed in 29.19s =============================
```

---

## Security Considerations

Detailed in [docs/SECURITY_AUDIT.md](file:///C:/Users/nares/workspace/context-engineering-labs/docs/SECURITY_AUDIT.md):
- **Agent Isolation**: Reviewer agents in Unit 4 cannot mutate workspace files (`tool.write` and `tool.edit` denied).
- **Fail-Soft Hooks**: Offline telemetry receivers in Unit 5 never block agent execution.
- **SSRF Defense**: Nano Harness blocks requests to internal/private IPs and link-local cloud metadata endpoints.
- **Application vs. Kernel Isolation**: In-process Python evaluation is not a full container boundary. Production autonomous code execution requires OS-level containerization (Docker, gVisor, Firecracker).
