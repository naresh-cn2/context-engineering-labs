# Agent Activity Dashboard (`agent-activity-dashboard`)

Official practical implementation for **Unit 5: Hooks — Observing and Guarding the Lifecycle** of the Hugging Face Context Engineering Course.

## Architecture

A unified telemetry and visualization server combining **FastAPI** and **Gradio**:

```
[Agent Execution: OpenCode / Claude Code / Codex]
          │
          │ Lifecycle Hooks (SessionStart, PreToolUse, PostToolUse, Stop)
          ▼
   POST http://localhost:8000/event
          │
          ▼
┌───────────────────────────────────────────────┐
│              FastAPI Receiver                 │
│  - Endpoint: POST /event, GET /health         │
│  - Non-blocking fast 200 OK                   │
│  - Payload normalizer (cross-agent support)   │
│  - In-memory bounded ring buffer (500 events) │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│               Gradio UI                       │
│  - Mounted on FastAPI root (/)                │
│  - Tool usage frequency histogram (gr.BarPlot)│
│  - Recent events table (newest first)         │
│  - Auto-refresh polling timer                 │
└───────────────────────────────────────────────┘
```

## Agent Hooks Configuration
- **OpenCode**: Configured via `.opencode/plugins/dashboard.js`.
- **Claude Code**: Configured via `.claude/settings.json`.
- **Codex**: Configured via `.codex/hooks.json`.

## Testing
```bash
python -m pytest tests/test_dashboard.py -v
```

