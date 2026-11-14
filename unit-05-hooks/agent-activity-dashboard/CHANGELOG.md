# Changelog: Agent Activity Dashboard

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Added
- Real-time observability dashboard backend (`app.py`) built with FastAPI and Server-Sent Events (SSE).
- Multi-agent configuration manifests:
  - `.claude/settings.json` for Claude Code HTTP hooks.
  - `.codex/hooks.json` for Codex CLI lifecycle webhooks.
  - `.opencode/plugins/dashboard.js` for OpenCode in-process hook plugins.
- Native SSE event forwarder bridge (`event_forwarder.py`) subscribing to OpenCode's `GET /api/event` stream.
- Fail-soft network architecture preventing agent blocking during telemetry outages.
- In-memory circular event buffer with automated argument truncation (max 200 chars).
- Automated test suite in `tests/test_dashboard.py` and `tests/test_opencode_hook_integration.py` (9 passing tests).
