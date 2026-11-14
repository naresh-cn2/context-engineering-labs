# Changelog: Text Processor MCP

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Added
- Model Context Protocol (MCP) server implementation using FastMCP (`text_processor_server.py`).
- 4 production-grade deterministic text processing tools:
  - `summarize_text`: Extractive frequency-weighted summarizer.
  - `extract_keywords`: Lexical frequency keyword extractor with stop-word filtration.
  - `count_words`: Comprehensive text metrics counter.
  - `sentiment_analysis`: Rule-based lexical polarity analyzer.
- Standardized MCP resource: `hf://resources/supported-metrics`.
- Standardized MCP prompt template: `hf://prompts/summarize-report`.
- Comprehensive automated test suite in `tests/test_server.py` covering all tools, resources, prompts, and server lifecycle (9 passing tests).
- Ready-to-use configuration templates for OpenCode (`opencode.json`) and Claude Code (`claude_desktop_config.json`).
- Complete engineering documentation and architectural specifications.
