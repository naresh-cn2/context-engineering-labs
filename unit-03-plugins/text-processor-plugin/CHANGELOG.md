# Changelog: Text Processor Plugin

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Added
- Standardized plugin packaging with `package.json` for ES Module distribution.
- Multi-agent manifests:
  - `.claude-plugin/plugin.json` for Claude Code.
  - `.codex-plugin/plugin.json` for Codex CLI.
- 3 bundled Agent Skills:
  - `analyze-text`: Structural text analysis.
  - `extract-keywords`: Keyword frequency extraction.
  - `check-reading-level`: Automated readability formula grading.
- OpenCode JavaScript plugin module (`.opencode/plugins/text-processor-plugin.js`) with `{ id, setup }` lifecycle contract.
- MCP client configuration (`.mcp.json`).
- Automated test suite in `tests/test_plugin.py` verifying manifests, skills, JS module, and package declarations (6 passing tests).
