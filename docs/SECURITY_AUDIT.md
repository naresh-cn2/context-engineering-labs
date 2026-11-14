# Security Audit

## Scope

Comprehensive audit of the `context-engineering-labs` repository (Units 1–6), including hardened controls implemented for plugin loading, multi-agent permissions, lifecycle event delivery, and sandbox boundaries.

## Secrets & Credentials Scan

A scan for common secret patterns was performed across all tracked source, documentation, and configuration files:

- AWS access keys (`AKIA...`)
- OpenAI-style keys (`sk-...`)
- Hugging Face tokens (`hf_...`)
- PEM / private-key blocks (`-----BEGIN ...-----`)
- Hardcoded `password=`, `API_KEY=`, or similar assignments
- `.env` files and environment-variable dumps

**Result: No real secrets or credentials are present in repository tracking.**

## Findings & Architectural Hardening

| Component | Security Concern | Hardened Mitigation |
| :--- | :--- | :--- |
| **Unit 4 Subagents** | Reviewer agents modifying source files or escalating privileges | **Agent Confinement**: Security and performance reviewer sessions have permissions strictly locked to read-only (`tools: Read, Grep`; OpenCode actions `write` and `edit` set to `deny`). Verified by automated tests. |
| **Unit 5 Hooks** | Agent hanging/crashing if dashboard crashes | **Fail-Soft Architecture**: Both `.opencode/plugins/dashboard.js` and `event_forwarder.py` employ bounded timeouts and non-blocking exception suppression. If the dashboard is offline, OpenCode operations execute uninterrupted. |
| **Unit 6 Nano Harness** | Path traversal attacks | **Confinement Enforcement**: `safe_path()` checks URL percent-encoding (`%2e%2e`), null bytes (`\0`), and verifies `resolved.relative_to(workspace)`. Symlink targets pointing outside the workspace root are blocked. |
| **Unit 6 Nano Harness** | Command injection & chaining | **Execution Hardening**: `exec_cmd()` enforces an explicit command allowlist, disallows explicit binary paths (`/bin/sh`), enforces `shell=False`, and scans for forbidden shell chaining tokens (`;`, `&&`, `\|\|`, `\|`, `>`, `<`, `` ` ``, `$()`). |
| **Unit 6 Nano Harness** | Server-Side Request Forgery (SSRF) | **Network Sandboxing**: `web_fetch()` restricts protocols to `http` and `https` (blocking `file://`, `ftp://`). Hostnames and IP literals are resolved against private, loopback, and link-local ranges, blocking requests to `localhost`, `127.0.0.1`, and cloud metadata (`169.254.169.254`). |
| **Unit 6 Nano Harness** | Information leakage | **Path Sanitization**: Error messages replace host-specific paths and user directories with sanitized `<workspace>` and `<home>` tokens. |

## Application-Level Sandbox vs. Kernel/OS Isolation

> [!WARNING]
> **Defensive Boundaries**:
> The sandbox implemented in `nano_harness.py` is an **application-level** demonstration harness. It restricts tools, paths, commands, and network endpoints at the Python interpreter layer.
>
> However, in-process Python execution using `exec()` with restricted `__builtins__` is **not an unbreakable security boundary** against adversarial code. Python's dynamic object model allows class navigation (`().__class__.__bases__[0].__subclasses__()`).
>
> **Production Recommendation**:
> In multi-tenant production systems, code-generating autonomous agents MUST execute inside kernel-enforced sandboxes, such as:
> - Container sandboxes with non-root users and dropped Linux capabilities (Docker/Podman).
> - MicroVMs (Firecracker, Kata Containers).
> - Sandboxed kernel runtimes (gVisor).
> - Strict system call filtering (seccomp-bpf, Landlock, AppArmor).

## Dependency Review

All pinned dependencies in `requirements.txt` are standard, publicly available packages on PyPI. No proprietary or paid services are required.
