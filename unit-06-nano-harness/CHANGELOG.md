# Changelog: Nano Harness

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-14

### Added
- Hardened multi-layer security sandbox:
  - Strict filesystem confinement (`safe_path`) with defenses against null bytes, percent-encoded traversals (`%2e%2e`), and symlink escapes.
  - Subprocess command allowlist with shell injection defense and execution without shell interpolation (`shell=False`).
  - Write gating with protection for sensitive project files (`.git`, `.env`, `.ssh`).
  - Network web fetch tool (`web_fetch`) with URL scheme restrictions and SSRF defense (blocking `127.0.0.1`, `localhost`, `169.254.169.254`, and private subnets).
  - Context budgeting (`clip`) with truncation notices.
  - Path sanitization in error traces preventing internal username or directory leakage.
- Automated security regression test suite in `tests/test_nano_harness.py` (15 passing tests).

## [1.0.0] - 2026-11-13

### Added
- Initial Unit 6 code-first agent loop prototype with basic tools (`list_dir`, `read_file`, `write_file`, `exec_cmd`, `final_answer`).
