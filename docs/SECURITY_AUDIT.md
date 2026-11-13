# Security Audit

## Scope

Audit of the published `context-engineering-labs` repository (Units 1–6),
performed before publication to GitHub.

## Secrets & credentials scan

A scan for common secret patterns was performed across all tracked source,
documentation, and configuration files:

- AWS access keys (`AKIA...`)
- OpenAI-style keys (`sk-...`)
- Hugging Face tokens (`hf_...`)
- PEM / private-key blocks (`-----BEGIN ...-----`)
- Hardcoded `password=`, `API_KEY=`, or similar assignments
- `.env` files and environment-variable dumps

**Result: no real secrets or credentials were found.**

## Findings (documented, not vulnerabilities)

| Item | Location | Assessment |
| :--- | :--- | :--- |
| Simulated mock tokens | `unit-04-subagents/code-quality-pipeline/main.py` | `secret_token_123` / `secret_token_456` inside a toy `UserDatabase`. Clearly labeled "Intentional" / mock. Used to demonstrate the security reviewer detecting hardcoded credentials. Not real credentials. |
| Runtime env var reads | `unit-06-nano-harness/nano_harness.py` | `os.getenv("HF_TOKEN")` / `os.getenv("OPENAI_API_KEY")` read at runtime only; never written to disk or logged. No key material in source. |

## Excluded from publication

Per `.gitignore`: `.env`, virtual environments (`.venv/`), bytecode
(`__pycache__/`, `*.pyc`), test caches (`.pytest_cache/`), logs, IDE
directories, OS files, and build artifacts. No machine-specific paths are
committed.

## Dependency review

- `requirements.txt` (root) and each unit `requirements.txt` list only
  publicly available, version-pinned-minimum PyPI packages (pandas, datasets,
  numpy, pyarrow, mcp, gradio, fastapi, uvicorn, httpx, pytest, PyYAML,
  tomlkit). No paid or private services are required.

## Nano Harness sandbox limitations (Unit 6)

- Confinement is implemented in Python (`safe_path`, command allowlist,
  `allow_write` flag). It is a demonstration sandbox, not an OS-level
  sandbox.
- `web_fetch` and `hf_search` perform real outbound network calls when
  exercised and should not be pointed at untrusted hosts in production-like
  contexts.
- The embedded `exec` environment exposes a restricted `__builtins__` subset,
  but `nano_harness` is a learning artifact, not a hardened execution
  environment.

## Recommendations

- Continue scanning for secrets before each release.
- Never commit `.env` files or real tokens; use environment variables at
  runtime only.
- Treat Unit 6 as a demonstration harness; do not expose it to untrusted
  input without additional sandboxing.
