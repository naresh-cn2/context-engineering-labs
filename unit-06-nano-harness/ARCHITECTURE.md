# Architecture & Technical Design: Nano Harness

## Overview

Nano Harness is a minimal, hardened execution harness designed for autonomous AI agents that operate via Python code-first interactions. It enforces strict boundary controls to guarantee host safety.

```mermaid
flowchart TD
    subgraph AgentRuntime["Agent Turn Execution"]
        CodeInput["LLM Python Code Block"] --> Namespace["Sandboxed Namespace"]
        Namespace --> DirectCall["Function Invocation (list_dir, read, write, exec, fetch)"]
    end

    subgraph DefenseGuards["Security Policy Layers"]
        DirectCall --> TraversalGuard["safe_path: Path Resolution & Containment"]
        DirectCall --> BinaryGuard["exec_cmd: Allowlist & No-Shell Subprocess"]
        DirectCall --> WriteGuard["write_file: allow_write Check & Path Blacklist"]
        DirectCall --> SSRFGuard["web_fetch: Scheme & Private IP Defense"]
        DirectCall --> ContextGuard["clip: Character Truncation"]
    end

    subgraph HostSystem["Host Operating System"]
        TraversalGuard --> SafeFS["Workspace Directory Only"]
        BinaryGuard --> SubProc["Subprocess (shell=False)"]
        SSRFGuard --> Web["Public Internet URLs Only"]
    end
```

---

## Defensive Guardrails

### 1. Filesystem Confinement (`safe_path`)
- All user-supplied paths are decoded (`urllib.parse.unquote`) and tested for null bytes.
- Resolves candidates against `workspace` root using `Path.resolve()`.
- Validates that `candidate.relative_to(workspace)` raises no `ValueError`.
- Checks symlink targets to prevent symbolic link traversal.

### 2. Command Sandboxing (`exec_cmd`)
- Commands must match an explicit allowlist of binary names.
- Explicit path invocations (`/bin/sh`, `C:\Windows\...`) are blocked.
- Commands run with `shell=False`.
- Arguments are scanned for forbidden shell metacharacters (`;`, `&&`, `|`, etc.).

### 3. Network Protection (`web_fetch`)
- Scheme restricted strictly to `http` and `https`.
- Hostname is resolved via `socket.getaddrinfo` and validated against `ipaddress.is_private`, `is_loopback`, `is_link_local`, `is_reserved`, and `is_multicast`.

### 4. Context Budgeting (`clip`)
- Output from commands, files, and web fetches is capped at `max_chars` to preserve prompt space and avoid token exhaustion.
