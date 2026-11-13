# Context Engineering Labs

Independent implementations completed for the **Hugging Face Context Engineering
Course** (Units 1–6), published as a personal, independently maintained
learning portfolio.

**Repository:** https://github.com/naresh-cn2/context-engineering-labs

---

## ⚠️ Important disclaimers

- **No official Hugging Face certificates are claimed or displayed by this
  repository.** Completion status and quiz results reflected in `PROGRESS.md`
  are self-reported by the student and are **not verified certifications**.
- **Unit 4 (subagents) is a simulated orchestration.** The researcher,
  implementer, security-reviewer, and performance-reviewer roles are executed
  by deterministic Python functions — **not by real LLM-powered agents**. No
  live LLM calls are made during tests.
- **Unit 6 (Nano Harness) sandbox limitations:** `web_fetch` and `hf_search`
  perform real network calls when exercised; path confinement and command
  allowlisting are enforced in Python, not by an OS-level sandbox. It is a
  learning artifact, not a hardened execution environment.

---

## Table of contents

1. [Project overview](#project-overview)
2. [Motivation and objectives](#motivation-and-objectives)
3. [Technologies and tools](#technologies-and-tools)
4. [Architecture overview](#architecture-overview)
5. [Unit-by-unit implementation details](#unit-by-unit-implementation-details)
6. [Installation instructions](#installation-instructions)
7. [Environment setup](#environment-setup)
8. [Execution instructions for every unit](#execution-instructions-for-every-unit)
9. [MCP configuration](#mcp-configuration)
10. [Testing instructions](#testing-instructions)
11. [Security considerations](#security-considerations)
12. [Known limitations](#known-limitations)
13. [Hugging Face course attribution](#hugging-face-course-attribution)
14. [Project progress and certification status](#project-progress-and-certification-status)

---

## Project overview

`context-engineering-labs` publishes the hands-on lab implementations built
while working through the Hugging Face Context Engineering Course. Each of the
six course units is represented by a self-contained, runnable project:

| Unit | Focus | Project | Path |
| :--- | :--- | :--- | :--- |
| Unit 1 | Agent Skills | `hf-dataset-validation` | `unit-01-agent-skills/hf-dataset-validation/` |
| Unit 2 | Model Context Protocol (MCP) | `text-processor-mcp` | `unit-02-mcp/text-processor-mcp/` |
| Unit 3 | Plugins — Bundling for Distribution | `text-processor-plugin` | `unit-03-plugins/text-processor-plugin/` |
| Unit 4 | Subagents — Multi-Agent Workflows | `code-quality-pipeline` | `unit-04-subagents/code-quality-pipeline/` |
| Unit 5 | Hooks — Observing and Guarding | `agent-activity-dashboard` | `unit-05-hooks/agent-activity-dashboard/` |
| Unit 6 | Nano Harness — Build Your Own Agent | `nano_harness` | `unit-06-nano-harness/` |

An end-to-end integration and security audit suite lives in
`tests/integration_audit_test.py`. The full verified baseline is **61 passing
tests** (`pytest -q`).

Each unit is independent — it carries its own scripts, dependencies
(`requirements.txt`), tests, and documentation — so any unit can be executed in
isolation.

---

## Motivation and objectives

- Consolidate the course lab implementations into one clean, version-controlled
  repository separate from the upstream Hugging Face course materials.
- Preserve original implementations and their functionality without copying the
  entire upstream course repository.
- Demonstrate practical context-engineering concepts: portable agent skills,
  MCP servers, plugin distribution manifests, simulated multi-agent workflows,
  hook telemetry, and a sandboxed agent harness.
- Provide reproducible installation, execution, and testing instructions so the
  labs can be run independently.
- Maintain professional repository hygiene: licensing, contributing and
  security policies, a `.gitignore`, and no exposed secrets or credentials.

## Technologies and tools

| Category | Tools |
| :--- | :--- |
| Language | Python 3.12 |
| Data / ML | pandas, datasets, numpy, pyarrow |
| MCP | mcp (FastMCP / MCPServer) |
| Web UI / API | gradio, fastapi, uvicorn, httpx, starlette |
| Testing | pytest, PyYAML, tomlkit |
| Agent specifications | Agent Skills Specification frontmatter (SKILL.md) |

Install everything at once: `pip install -r requirements.txt`

## Architecture overview

```
context-engineering-labs/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── .gitignore
├── requirements.txt
├── PROGRESS.md
├── unit-01-agent-skills/hf-dataset-validation/
├── unit-02-mcp/text-processor-mcp/
├── unit-03-plugins/text-processor-plugin/
├── unit-04-subagents/code-quality-pipeline/
├── unit-05-hooks/agent-activity-dashboard/
├── unit-06-nano-harness/
├── tests/integration_audit_test.py
└── docs/
    ├── ARCHITECTURE.md
    ├── SECURITY_AUDIT.md
    └── RUNTIME_VERIFICATION.md
```

Each unit is self-contained: imports resolve within the unit via `sys.path`
insertion, so units can be run independently. See `docs/ARCHITECTURE.md` for
per-unit diagrams and design notes.

## Unit-by-unit implementation details

### Unit 1 — Agent Skills: `hf-dataset-validation`

A standardized Agent Skill (frontmatter per the Agent Skills Specification)
wrapping a dataset validation engine.

- **`scripts/validate_dataset.py`** — loads CSV / Parquet / JSON / Arrow
  datasets; validates required columns (default `text`, `label`); detects
  missing values, duplicate rows, and empty/whitespace strings; emits
  structured JSON (`status`: PASS / WARNING / FAIL) and CLI exit codes
  (0 = valid/warn, 1 = blocking error).
- **`scripts/generate_report.py`** — human-readable ASCII validation report.
- **`test_data/`** — clean, flawed, invalid-schema, and JSON samples.
- **Tests:** 10 (`tests/test_validation.py`).

### Unit 2 — MCP: `text-processor-mcp`

A Model Context Protocol server exposing text-analysis tools over stdio, plus a
Gradio web UI.

- **`server.py`** — FastMCP/MCPServer with `analyze_text`, `extract_keywords`,
  `check_reading_level`, `reverse_text`, `detect_sentiment`.
- **`app.py`** — Gradio dashboard at `http://127.0.0.1:7860`.
- **Tests:** 9 (`tests/test_text_processor.py`).

### Unit 3 — Plugins: `text-processor-plugin`

A redistributable plugin bundle supporting manifest-first (Claude Code, Codex)
and code-first (OpenCode) platforms, plus an MCP link to the Unit 2 server.

- **`.claude-plugin/plugin.json`**, **`.codex-plugin/plugin.json`** — platform
  manifests.
- **`.mcp.json`** — MCP server connection spec
  (`../../unit-02-mcp/text-processor-mcp/server.py`).
- **`.opencode/plugins/text-processor-plugin.js`** — OpenCode plugin module.
- **`skills/{analyze-text,extract-keywords,check-reading-level}/SKILL.md`** —
  bundled agent skills.
- **Tests:** 5 (`tests/test_plugin.py`).

### Unit 4 — Subagents: `code-quality-pipeline`

A simulated multi-agent Research → Implement → Verify pipeline using Fan-Out /
Fan-In and Sequential Handoff patterns.

- **`main.py`** — target application under analysis (intentional, clearly marked
  flaws: N+1 queries, artificial latency, non-constant-time token comparison).
- **`pipeline_runner.py`** — orchestrator: researcher, implementer diff,
  parallel security & performance reviewers, orchestrator sign-off.
- **`.claude/agents/*.md` + `.codex/agents/*.toml`** — four subagent specs
  (researcher, implementer, security-reviewer, performance-reviewer).
- **Tests:** 10 (`tests/test_pipeline.py`).

> **Simulated orchestration:** agent roles are deterministic Python functions,
> not live LLM-powered agents. No LLM calls are made during tests.


### Unit 5 — Hooks: `agent-activity-dashboard`

A cross-platform hook telemetry receiver built with FastAPI + Gradio.

- **`app.py`** — FastAPI `POST /event` receiver with a payload normalizer
  (OpenCode / Claude Code / Codex / Pi), bounded in-memory ring buffer (500
  events), `GET /health`, mounted Gradio UI with tool-frequency chart and
  events table at `http://127.0.0.1:8000`.
- **Hook configs:** `.claude/settings.json`, `.codex/hooks.json`,
  `.opencode/plugins/dashboard.js`.
- **Tests:** 6 (`tests/test_dashboard.py`).

### Unit 6 — Nano Harness: `nano_harness` (bonus)

A minimal code-first autonomous agent loop with tool-boundary sandboxing.

- **`nano_harness.py`** — `NanoHarness` class: `safe_path` path confinement,
  command allowlist, write gating (`allow_write`), output clipping
  (`max_chars`), step-limited loop, observation reflection, and extended tools
  `web_fetch` / `hf_search` / `final_answer`.
- **Tests:** 9 (`tests/test_nano_harness.py`).

> **Sandbox limitation:** `web_fetch` / `hf_search` make real network calls
> when exercised. Confinement is enforced in Python, not by an OS sandbox.
> Not a hardened execution environment.

## Installation instructions

### 1. Clone the repository

```bash
git clone https://github.com/naresh-cn2/context-engineering-labs.git
cd context-engineering-labs
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
# All units at once
pip install -r requirements.txt

# Or per unit (each unit has its own requirements.txt):
pip install -r unit-01-agent-skills/hf-dataset-validation/requirements.txt
pip install -r unit-02-mcp/text-processor-mcp/requirements.txt
pip install -r unit-05-hooks/agent-activity-dashboard/requirements.txt
```

Unit 6 (`nano_harness`) uses only the Python standard library — no
installation required beyond Python 3.12.

## Environment setup

- Python 3.12+ is required (type union syntax `X | Y` is used throughout).
- No API keys, HF tokens, or passwords are required to run the tests.
- `nano_harness` optionally reads `HF_TOKEN` / `OPENAI_API_KEY` from the
  environment for authenticated Hugging Face Hub search; these are **optional**
  and never written to disk.
- Do **not** create or commit `.env` files. See `.gitignore` and `SECURITY.md`.


## Execution instructions for every unit

### Unit 1 — `hf-dataset-validation`

```bash
cd unit-01-agent-skills/hf-dataset-validation
# Validate a dataset (JSON report to stdout, exit code 0/1)
python scripts/validate_dataset.py test_data/clean_sample.csv
# Generate a human-readable ASCII report
python scripts/generate_report.py test_data/clean_sample.csv
```

### Unit 2 — `text-processor-mcp`

```bash
cd unit-02-mcp/text-processor-mcp
# Run the MCP server over stdio
python server.py
# Launch the Gradio web UI
python app.py   # http://127.0.0.1:7860
```

### Unit 3 — `text-processor-plugin`

This is a distribution bundle; review the manifests and skills:

```bash
cd unit-03-plugins/text-processor-plugin
cat .claude-plugin/plugin.json
cat .codex-plugin/plugin.json
cat .mcp.json
ls skills/*/SKILL.md
```

The `.mcp.json` MCP link references `../../unit-02-mcp/text-processor-mcp/server.py`
(Unit 2 must be present for live MCP use).

### Unit 4 — `code-quality-pipeline`

```bash
cd unit-04-subagents/code-quality-pipeline
# Run the simulated multi-agent pipeline
python pipeline_runner.py
```

### Unit 5 — `agent-activity-dashboard`

```bash
cd unit-05-hooks/agent-activity-dashboard
# Start the FastAPI + Gradio dashboard
python app.py   # http://127.0.0.1:8000
# POST /event receives hook telemetry; GET /health reports event count
```

### Unit 6 — `nano_harness`

```bash
cd unit-06-nano-harness
# Nano Harness is imported and driven in Python:
python - <<'PY'
from nano_harness import NanoHarness
import tempfile
with tempfile.TemporaryDirectory() as d:
    h = NanoHarness(workspace=d, allow_write=True)
    print(h.step("print(read_file('hello.txt'))"))
PY
```

## MCP configuration

Unit 2 exposes its tools over stdio via `server.py` (`mcp.run()`). Consumers
can register it as a local MCP server:

```json
{
  "mcpServers": {
    "text-processor": {
      "command": "python",
      "args": ["<absolute-or-relative-path>/unit-02-mcp/text-processor-mcp/server.py"]
    }
  }
}
```

Unit 3's `.mcp.json` already links to the Unit 2 server at
`../../unit-02-mcp/text-processor-mcp/server.py`. The Gradio UI (`app.py`)
provides an interactive browser alternative at `http://127.0.0.1:7860`.

## Testing instructions

Run the complete verified suite from the repository root:

```bash
pytest -q
```

Expected baseline: **61 passed**.

Run a single unit:

```bash
# Unit 1
pytest unit-01-agent-skills/hf-dataset-validation/tests/test_validation.py -v
# Unit 2
pytest unit-02-mcp/text-processor-mcp/tests/test_text_processor.py -v
# Unit 3
pytest unit-03-plugins/text-processor-plugin/tests/test_plugin.py -v
# Unit 4
pytest unit-04-subagents/code-quality-pipeline/tests/test_pipeline.py -v
# Unit 5
pytest unit-05-hooks/agent-activity-dashboard/tests/test_dashboard.py -v
# Unit 6
pytest unit-06-nano-harness/tests/test_nano_harness.py -v
# Integration & security audit
pytest tests/integration_audit_test.py -v
```


## Security considerations

- No API keys, HF tokens, passwords, or real credentials are stored in this
  repository.
- `nano_harness` reads `HF_TOKEN` / `OPENAI_API_KEY` from the environment at
  runtime only; it never writes them to disk.
- `code-quality-pipeline` contains **simulated mock tokens**
  (`secret_token_123`, `secret_token_456`) inside a toy `UserDatabase`, used to
  demonstrate security-reviewer detection of hardcoded credentials. These are
  deliberately fake example values, not real credentials.
- `.env`, virtual environments, bytecode, caches, logs, and build artifacts
  are excluded via `.gitignore`.
- See `SECURITY.md`, `docs/SECURITY_AUDIT.md`, and `.gitignore`.

## Known limitations

| Area | Limitation |
| :--- | :--- |
| Unit 4 subagents | Simulated orchestration — deterministic Python functions, not live LLM-powered agents. |
| Unit 6 sandbox | Confinement is in Python, not OS-level; `web_fetch`/`hf_search` make real network calls when exercised. |
| Unit 5 dashboard | In-memory ring buffer (500 events); state resets on restart. |
| Certificates | No official Hugging Face certificates are claimed. |
| Network | Unit 6 `hf_search` calls the public Hugging Face Hub API; offline use returns errors. |

## Hugging Face course attribution

This repository contains **original student implementations** created while
working through the public Hugging Face Context Engineering Course (Units
1–6). The course concepts, unit structure, and specifications (Agent Skills,
MCP, Plugins, Subagents, Hooks, Nano Harness) derive from that public course.

- These implementations are **not official Hugging Face code**.
- The upstream Hugging Face course repository was **not** copied, modified,
  or republished here — only the student's own lab implementations are
  included.
- No official Hugging Face certificate is earned, claimed, or displayed by
  this repository. See `PROGRESS.md` for self-reported progress.

## Project progress and certification status

See `PROGRESS.md` for the full status table.

| Project element | Status |
| :--- | :--- |
| Units 1–6 implemented | ✅ Complete |
| Unit tests (49) | ✅ 49/49 passing |
| Integration & audit tests (12) | ✅ 12/12 passing |
| **Total test suite** | ✅ **61/61 passing** |
| Repository hygiene (`.gitignore`, LICENSE, SECURITY, CONTRIBUTING) | ✅ Complete |
| Documentation (README, docs/*) | ✅ Complete |
| Published to GitHub | `main` branch |
| Official Hugging Face certificates | ❌ **Not claimed** |

---

*Maintained by nares. This is an independent learning portfolio — not an
official Hugging Face product or certificate.*


