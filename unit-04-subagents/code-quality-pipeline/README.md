# Multi-Agent Code Quality Pipeline (`code-quality-pipeline`)

Official practical implementation for **Unit 4: Subagents: Multi-Agent Workflows** of the Hugging Face Context Engineering Course.

## Architecture

Implements a multi-agent **Research → Implement → Verify** lifecycle using Fan-Out / Fan-In and Sequential Handoff patterns:

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

## Dual Execution Modes

The pipeline supports two distinct execution modes:

1. **Deterministic Simulated Mode (Default)**:
   - Evaluates code transformations using static pattern matching and rule validation.
   - Ideal for CI/CD environments and rapid regression testing.
   ```bash
   python pipeline_runner.py
   ```

2. **Live LLM Multi-Agent Mode**:
   - Connects to the running local OpenCode agent server (`http://127.0.0.1:28894`).
   - Delegates tasks to real LLM-backed subagents powered by NVIDIA Nemotron (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` at `cost: 0`).
   - Sequential handoff: The Researcher analyzes `main.py`, extracts architectural patterns and risks, and hands the report to the Implementer.
   - Parallel evaluation: Security and Performance Reviewers execute concurrently via `ThreadPoolExecutor` under strict read-only confinement (`write` and `edit` tools denied).
   - Generates full execution traces saved into `traces/live_run_trace.json`.
   ```bash
   python pipeline_runner.py --live
   ```

## Agent Definitions & Confinement

- **`.claude/agents/` & `.codex/agents/`**:
  - `researcher`: Read-only architecture explorer (`sandbox: read-only`, `tools: Read, Grep`).
  - `implementer`: Implementation developer (`sandbox: workspace-write`, `tools: Read, Edit, Write`).
  - `security-reviewer`: Strictly read-only reviewer (`sandbox: read-only`, `tools: Read, Grep`).
  - `performance-reviewer`: Strictly read-only reviewer (`sandbox: read-only`, `tools: Read, Grep`).

Reviewer agents are strictly prohibited from mutating files. During live execution, OpenCode enforces `{"action": "write", "resource": "*", "effect": "deny"}` and `{"action": "edit", "resource": "*", "effect": "deny"}` on reviewer sessions.

## Verification

```bash
python -m pytest tests/test_pipeline.py -v
```
