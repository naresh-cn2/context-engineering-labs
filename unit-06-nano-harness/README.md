# Nano Harness (`nano_harness`)

Official practical implementation for **Unit 6 (Bonus): Nano Harness — Build Your Own Agent** of the Hugging Face Context Engineering Course.

## Architecture & Principles

`nano_harness` is a hardened, code-first autonomous agent harness demonstrating how code agents function under the hood:

```
[System Prompt + Task]
         │
         ▼
   Call LLM (Deterministic low-temperature output)
         │
         ▼
   Extract Executable Python
         │
         ▼
   Sandboxed Execution Environment
   ├── Path Confinement (safe_path: traversal, symlink, & encoding protection)
   ├── Command Allowlist (pure binary basenames; forbidden shell injection characters)
   ├── Write Gating (allow_write flag & protected .git/.env/.ssh patterns)
   ├── Network Sandboxing (HTTP/HTTPS only; SSRF private IP & metadata blocking)
   └── Context Budgeting (max_chars buffer clipping & sanitized error reporting)
         │
         ├─── if final_answer(result) ───► Task Complete!
         │
         └─── Observation / Error ────────► Feeds back into History -> Next Step
```

## Available Tools

- `list_dir(path='.')`: Lists workspace directory contents safely.
- `read_file(path, max_chars=4000)`: Reads file contents with context bounds.
- `write_file(path, content)`: Writes to file only when writes are explicitly enabled and destination is not a sensitive path.
- `exec_cmd(args)`: Runs allowlisted shell commands with injection protection.
- `web_fetch(url, max_bytes=10000)`: Fetches web page content with SSRF and scheme gating.
- `hf_search(query, resource_type='models', limit=5)`: Searches Hugging Face Hub.
- `final_answer(value)`: Signals task completion.

## Security Model & Sandboxing Boundaries

> [!IMPORTANT]
> **Application-Level Sandboxing vs. Kernel-Level Isolation**:
> `nano_harness` implements defensive controls within Python:
> 1. **Path Confinement**: `resolve().relative_to(workspace)` verifies paths and symlinks remain inside the workspace. Null bytes and encoded sequences are caught.
> 2. **Command Hardening**: Enforces an explicit binary allowlist, executes with `shell=False`, forbids absolute/relative binary paths, and rejects chaining operators (`;`, `&&`, `||`, `|`, `` ` ``, `$()`).
> 3. **SSRF Protection**: `web_fetch` enforces `http`/`https` schemes and resolves target hosts against IPv4/IPv6 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`) and link-local metadata addresses (`169.254.169.254`).
> 4. **Information Leakage**: Error reporting replaces absolute workspace and home paths with `<workspace>` and `<home>` tokens.
>
> **Sandbox Limitations**:
> In-process Python evaluation via `exec()` with restricted `__builtins__` is **not** an unbreakable security boundary. Python's object model allows class hierarchy introspection. For untrusted code execution in multi-tenant production systems, code agents MUST be executed within OS/container boundaries (e.g., Docker containers with dropped capabilities, gVisor, Firecracker microVMs, or seccomp profiles).

## Verification

```bash
python -m pytest tests/test_nano_harness.py -v
```
