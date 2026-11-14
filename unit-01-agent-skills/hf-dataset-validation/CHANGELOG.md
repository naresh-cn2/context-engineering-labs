# Changelog

All notable changes to the `hf-dataset-validation` project will be documented in this file.

## [1.1.0] - 2026-11-14
### Added
- Comprehensive 17-section documentation in `README.md`.
- `ARCHITECTURE.md` detailing the ingestion subsystem and exit code taxonomy.
- Developer setup guide in `CONTRIBUTING.md`.
- `.env.example` template for configuration.

## [1.0.0] - 2026-11-13
### Added
- Core validation engine `scripts/validate_dataset.py` with multi-format support (CSV, Parquet, JSON, Arrow).
- Human-readable ASCII diagnostic report generator `scripts/generate_report.py`.
- Standardized `SKILL.md` frontmatter per the Agent Skills Specification.
- Test suite with 10 unit and CLI regression tests in `tests/test_validation.py`.
