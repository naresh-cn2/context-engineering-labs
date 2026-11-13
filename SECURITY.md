# Security Policy

## Supported versions

This is a personal course-lab repository. Security patches are applied on a
best-effort basis to the `main` branch only.

## Reporting a vulnerability

If you discover a security issue, please open a public issue or contact the
repository owner directly. Do not submit secrets, tokens, or credentials
through issues or pull requests.

## Repository security notes

- No API keys, HF tokens, passwords, or real credentials are stored in this
  repository. The `nano_harness` Unit 6 example reads `HF_TOKEN` / `OPENAI_API_KEY`
  from the environment at runtime only; it never writes them to disk.
- `code-quality-pipeline` Unit 4 contains **simulated mock tokens**
  (`secret_token_123`, `secret_token_456`) inside a toy `UserDatabase` used to
  demonstrate security-reviewer detection of hardcoded credentials. These are
  deliberately fake example values, not real credentials.
- All dependency files are reviewed before commit (see `requirements.txt` and
  per-unit `requirements.txt` files).
- Run the test suite before publishing changes: `pytest -q` (baseline: 61
  passing tests).

## Secrets scanning

Before any release, the repository is scanned for common secret patterns
(AWS keys, `sk-`, `hf_`, `-----BEGIN`, hardcoded passwords/keys). Nothing
was found beyond the documented simulated mock tokens above.
