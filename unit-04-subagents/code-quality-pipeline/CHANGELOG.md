# Changelog: Code Quality Multi-Agent Pipeline

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Added
- Multi-agent orchestration engine (`pipeline_runner.py`) implementing Sequential Handoff and Fan-Out/Fan-In patterns.
- 4 specialized agent persona definitions across both Claude Code (`.claude/agents/*.md`) and Codex (`.codex/agents/*.toml`):
  - Architecture Researcher
  - Code Implementer
  - Security Reviewer
  - Performance Reviewer
- Sandboxed permission boundaries strictly enforcing read-only access for reviewer roles.
- Dual execution support:
  - Deterministic simulated heuristics for CI/CD test automation.
  - Live LLM multi-agent sessions powered by OpenCode and free NVIDIA Nemotron reasoning models.
- Execution audit trace capture (`traces/live_run_trace.json`).
- Automated test suite in `tests/test_pipeline.py` verifying definitions, sandbox constraints, and orchestration results (11 passing tests).
