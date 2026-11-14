# Contributing to Nano Harness

Thank you for contributing to Nano Harness!

## Development Guidelines

1. **Security-First Mindset**:
   - Every new capability must be accompanied by security regression tests.
   - Never bypass `safe_path()` or subprocess argument parsing guards.
   - Maintain `shell=False` for all subprocess executions.
2. **SSRF Guardrails**:
   - Any network fetching tools must validate both the protocol scheme and resolved IP address.
3. **Running Security Tests**:
   - Execute the test suite:
     ```bash
     pytest tests/ -v
     ```
   - All 15 security regression tests must pass.
