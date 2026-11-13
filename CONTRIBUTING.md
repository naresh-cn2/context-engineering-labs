# Contributing to context-engineering-labs

Thank you for your interest in contributing! This repository publishes the
independent implementations completed as part of the Hugging Face Context
Engineering Course (Units 1–6), maintained as a personal learning portfolio.

## How to contribute

1. **Fork the repository** and create a feature branch from `main`.
2. **Run the test suite** before and after your changes:
   ```bash
   pytest -q
   ```
   Expected baseline: **61 passing tests**.
3. **Keep changes scoped to a single unit** where possible, and update the
   corresponding unit README if you change behavior.
4. **Do not commit secrets.** No `.env` files, API keys, HF tokens, passwords,
   or machine-specific paths. See `SECURITY.md` and `.gitignore`.
5. **Open a pull request** describing the change, the unit affected, and test
   results. Maintainer review is required before merging.

## Code style

- Follow the conventions already used in each unit (docstrings, type hints,
  `from __future__ import annotations`).
- Keep unit implementations self-contained; each unit has its own tests and
  `requirements.txt`.

## Attribution

This project is based on the public Hugging Face Context Engineering Course
materials. Implementations are original student work and are not official
Hugging Face code. See the Hugging Face course attribution section of
`README.md`.

## Certificate status

No official Hugging Face certificates are claimed by this repository. See
`PROGRESS.md` for the current progress and certification status.
