# Hugging Face Context Engineering Labs: Project Portfolio

A comprehensive suite of production-grade reference implementations, tool harnesses, and multi-agent coordination architectures built for the [Hugging Face Context Engineering Course](https://huggingface.co/learn/context-course).

---

## Portfolio Matrix

| Project | Unit | Domain | Primary Tech Stack | Passing Tests | Production Readiness |
|---|---|---|---|---|---|
| [**HF Dataset Validation**](unit-01-agent-skills/hf-dataset-validation/) | Unit 1 | Agent Skills | Python, JSON Schema, OpenCode CLI | 10 / 10 | Production Reference |
| [**Text Processor MCP**](unit-02-mcp/text-processor-mcp/) | Unit 2 | Model Context Protocol | Python FastMCP, JSON-RPC 2.0, stdio | 9 / 9 | Production Reference |
| [**Text Processor Plugin**](unit-03-plugins/text-processor-plugin/) | Unit 3 | Cross-Agent Packaging | ES2022, Node.js, Claude/Codex Manifests | 6 / 6 | Production Reference |
| [**Code Quality Pipeline**](unit-04-subagents/code-quality-pipeline/) | Unit 4 | Multi-Agent Orchestration | Python ThreadPool, OpenCode API, Nemotron | 11 / 11 | Production Reference |
| [**Agent Activity Dashboard**](unit-05-hooks/agent-activity-dashboard/) | Unit 5 | Observability & Hooks | FastAPI, Server-Sent Events (SSE), JS Hooks | 9 / 9 | Production Reference |
| [**Nano Harness**](unit-06-nano-harness/) | Unit 6 | Sandboxing & Host Defense | Python, Subprocess Sandboxing, SSRF Defense | 15 / 15 | Hardened Core |
| **End-to-End Integration Suite** | Units 1–6 | System Audit | Pytest, Starlette TestClient | 12 / 12 | Rigorous Audit Pass |
| **Total Test Suite** | | | | **72 / 72** | **100% Pass** |

---

## Detailed Project Overviews

### 1. Unit 1: Hugging Face Dataset Validation (`unit-01-agent-skills/hf-dataset-validation/`)
- **Specification**: Open Agent Skills Standard (`SKILL.md` + YAML frontmatter).
- **Core Capabilities**:
  - Deterministic CSV/JSON structural validation without external dependencies.
  - Anomaly detection: empty splits, column mismatch, categorical imbalance, string length outliers.
  - Portable across OpenCode, Claude Code, and Codex.
- **Engineering Docs**: [README](unit-01-agent-skills/hf-dataset-validation/README.md) | [ARCHITECTURE](unit-01-agent-skills/hf-dataset-validation/ARCHITECTURE.md) | [CONTRIBUTING](unit-01-agent-skills/hf-dataset-validation/CONTRIBUTING.md) | [CHANGELOG](unit-01-agent-skills/hf-dataset-validation/CHANGELOG.md)

### 2. Unit 2: Text Processor MCP Server (`unit-02-mcp/text-processor-mcp/`)
- **Specification**: Model Context Protocol (MCP) FastMCP standard.
- **Core Capabilities**:
  - Exposes 4 analytical tools: `summarize_text`, `extract_keywords`, `count_words`, `sentiment_analysis`.
  - Exposes standardized resource: `hf://resources/supported-metrics`.
  - Exposes standardized prompt: `hf://prompts/summarize-report`.
  - Transports over `stdio` via JSON-RPC 2.0 with stderr-only logging.
- **Engineering Docs**: [README](unit-02-mcp/text-processor-mcp/README.md) | [ARCHITECTURE](unit-02-mcp/text-processor-mcp/ARCHITECTURE.md) | [CONTRIBUTING](unit-02-mcp/text-processor-mcp/CONTRIBUTING.md) | [CHANGELOG](unit-02-mcp/text-processor-mcp/CHANGELOG.md)

### 3. Unit 3: Text Processor Plugin (`unit-03-plugins/text-processor-plugin/`)
- **Specification**: Cross-agent packaging standard (OpenCode, Claude Code, Codex).
- **Core Capabilities**:
  - Multi-agent manifests: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `package.json`.
  - Auto-configures MCP server bindings via `.mcp.json`.
  - 3 bundled skills: `analyze-text`, `extract-keywords`, `check-reading-level`.
  - OpenCode JavaScript lifecycle hook module (`.opencode/plugins/text-processor-plugin.js`).
- **Engineering Docs**: [README](unit-03-plugins/text-processor-plugin/README.md) | [ARCHITECTURE](unit-03-plugins/text-processor-plugin/ARCHITECTURE.md) | [CONTRIBUTING](unit-03-plugins/text-processor-plugin/CONTRIBUTING.md) | [CHANGELOG](unit-03-plugins/text-processor-plugin/CHANGELOG.md)

### 4. Unit 4: Code Quality Multi-Agent Pipeline (`unit-04-subagents/code-quality-pipeline/`)
- **Specification**: Subagent topologies: Sequential Handoff & Fan-Out/Fan-In Parallelism.
- **Core Capabilities**:
  - 4 specialized personas: Architecture Researcher, Code Implementer, Security Reviewer, Performance Reviewer.
  - Strict Principle of Least Privilege: Reviewer roles are strictly confined to read-only tool sets.
  - Dual-mode execution: deterministic simulated heuristics and real live LLM orchestration via OpenCode with NVIDIA Nemotron at `cost: 0`.
  - Real execution trace recording in `traces/live_run_trace.json`.
- **Engineering Docs**: [README](unit-04-subagents/code-quality-pipeline/README.md) | [ARCHITECTURE](unit-04-subagents/code-quality-pipeline/ARCHITECTURE.md) | [CONTRIBUTING](unit-04-subagents/code-quality-pipeline/CONTRIBUTING.md) | [CHANGELOG](unit-04-subagents/code-quality-pipeline/CHANGELOG.md)

### 5. Unit 5: Agent Activity Dashboard & Real-Time Hooks (`unit-05-hooks/agent-activity-dashboard/`)
- **Specification**: Agent lifecycle observability via Server-Sent Events (SSE).
- **Core Capabilities**:
  - FastAPI backend receiving multi-platform telemetry at `POST /event`.
  - Real-time SSE streaming (`GET /stream`) to responsive web console.
  - Native OpenCode SSE bridge (`event_forwarder.py`) subscribing to `/api/event`.
  - Non-blocking, fail-soft network architecture ensuring agent stability during telemetry outages.
- **Engineering Docs**: [README](unit-05-hooks/agent-activity-dashboard/README.md) | [ARCHITECTURE](unit-05-hooks/agent-activity-dashboard/ARCHITECTURE.md) | [CONTRIBUTING](unit-05-hooks/agent-activity-dashboard/CONTRIBUTING.md) | [CHANGELOG](unit-05-hooks/agent-activity-dashboard/CHANGELOG.md)

### 6. Unit 6: Nano Harness Autonomous Agent Sandbox (`unit-06-nano-harness/`)
- **Specification**: Code-first autonomous agent execution harness.
- **Core Capabilities**:
  - Multi-layer security sandbox preventing host escalation and data leakage.
  - Path confinement defending against relative traversal, symlinks, percent-encoded escapes, and null bytes.
  - Subprocess command allowlist rejecting shell metacharacters and running with `shell=False`.
  - Write gating protecting `.git` and `.env` credentials.
  - Network tool with SSRF protection blocking localhost, private subnets, and cloud metadata (`169.254.169.254`).
- **Engineering Docs**: [README](unit-06-nano-harness/README.md) | [ARCHITECTURE](unit-06-nano-harness/ARCHITECTURE.md) | [CONTRIBUTING](unit-06-nano-harness/CONTRIBUTING.md) | [CHANGELOG](unit-06-nano-harness/CHANGELOG.md)

---

## Verification & Test Execution

Run the complete 72-test validation suite from the repository root:

```bash
python -m pytest -v
```

All 72 tests pass with zero external paid API dependencies or credentials required.
