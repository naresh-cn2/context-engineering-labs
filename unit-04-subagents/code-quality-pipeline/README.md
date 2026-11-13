# Multi-Agent Code Quality Pipeline (`code-quality-pipeline`)

Official practical implementation for **Unit 4: Subagents: Multi-Agent Workflows** of the Hugging Face Context Engineering Course.

## Architecture

Implements a multi-agent **Research → Implement → Verify** lifecycle using Fan-Out / Fan-In and Sequential Handoff patterns:

```
[Target Code: main.py]
          │
          ▼
   Stage 1: Researcher (Explores architecture & maps risks)
          │
          ▼
   Stage 2: Implementer (Applies minimal, focused code change)
          │
          ├─── Fan-Out ─────────────────────────┐
          │                                     │
          ▼                                     ▼
   Stage 3a: Security Reviewer           Stage 3b: Performance Reviewer
   (Read-Only: Auth & token leaks)       (Read-Only: N+1 & latency bottlenecks)
          │                                     │
          └─── Fan-In ──────────────────────────┘
          │
          ▼
   Stage 4: Orchestrator Sign-off (Synthesizes verdicts & approves merge)
```

## Agent Definitions

- **`.claude/agents/` & `.codex/agents/`**:
  - `researcher`: Read-only architecture explorer.
  - `implementer`: Implementation developer.
  - `security-reviewer`: Strictly read-only reviewer (no `Write` tools allowed).
  - `performance-reviewer`: Strictly read-only reviewer.

## Verification

```bash
python -m pytest tests/test_pipeline.py -v
```

