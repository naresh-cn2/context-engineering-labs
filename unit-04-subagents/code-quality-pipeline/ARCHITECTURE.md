# Architecture & Technical Design: Code Quality Multi-Agent Pipeline

## Overview

The Code Quality Multi-Agent Pipeline models a production engineering department using specialized AI agent personas. It implements two canonical agentic interaction topologies:
1. **Sequential Handoff**: Researcher $\rightarrow$ Implementer.
2. **Fan-Out / Fan-In**: Implementer $\rightarrow$ [Security Reviewer, Performance Reviewer] $\rightarrow$ Orchestrator.

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Orchestrator
    participant Res as Architecture Researcher (Read-Only)
    participant Imp as Code Implementer (Read-Write)
    participant Sec as Security Reviewer (Read-Only)
    participant Perf as Performance Reviewer (Read-Only)

    Dev->>Res: Pass target source code (main.py)
    Note over Res: Analyzes architecture & risk vectors
    Res-->>Dev: ResearchReport (patterns, risks)

    Dev->>Imp: Pass code + ResearchReport risks
    Note over Imp: Refactors code & applies fixes
    Imp-->>Dev: Improved Source Code Diff

    par Parallel Review (Fan-Out)
        Dev->>Sec: Submit diff for security audit
        Note over Sec: Audits timing attacks & secrets
        Sec-->>Dev: Security ReviewVerdict
    and
        Dev->>Perf: Submit diff for performance audit
        Note over Perf: Audits N+1 queries & latency
        Perf-->>Dev: Performance ReviewVerdict
    end

    Note over Dev: Aggregate verdicts (Fan-In)
    Dev->>Dev: If Sec.approved AND Perf.approved -> Sign-off
```

---

## Agent Personas & Sandbox Policies

| Agent Persona | Configuration | Tools Permitted | Sandboxing & Permissions |
|---|---|---|---|
| **Researcher** | `.claude/agents/researcher.md`<br/>`.codex/agents/researcher.toml` | `Read`, `Grep`, `Glob` | Strictly Read-Only. No file mutation or execution. |
| **Implementer** | `.claude/agents/implementer.md`<br/>`.codex/agents/implementer.toml` | `Read`, `Write`, `Edit` | Scoped to project working tree. |
| **Security Reviewer** | `.claude/agents/security-reviewer.md`<br/>`.codex/agents/security-reviewer.toml` | `Read`, `Grep` | Strictly Read-Only. Enforces constant-time checks & credential safety. |
| **Performance Reviewer** | `.claude/agents/performance-reviewer.md`<br/>`.codex/agents/performance-reviewer.toml` | `Read`, `Grep` | Strictly Read-Only. Detects query loops & memory leaks. |

---

## Orchestrator Core (`pipeline_runner.py`)

- `execute_pipeline()` orchestrates lifecycle stages.
- Concurrent execution of reviewers via Python `concurrent.futures.ThreadPoolExecutor`.
- Fallback heuristic analysis guarantees zero-token testability for CI/CD environments.
