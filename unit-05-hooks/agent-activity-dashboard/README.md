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

## Native OpenCode Hook Integration

OpenCode provides two integrated mechanisms for lifecycle telemetry:

1. **Native OpenCode Event Listener Bridge (`event_forwarder.py`)**:
   - Subscribes to OpenCode's native SSE event stream (`GET /api/event`) via authorized HTTP streaming.
   - Maps OpenCode native event types (`session.created`, `session.tool.call`, `session.tool.result`, `session.idle`) to the course dashboard taxonomy (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`).
   - Forwards events via HTTP POST to the dashboard's `/event` endpoint.
   - **Fail-Soft Reliability**: If the dashboard server is offline, the forwarder catches connection errors and continues listening without blocking or crashing OpenCode.

2. **OpenCode Code-First Plugin Hook (`.opencode/plugins/dashboard.js`)**:
   - Implements OpenCode's plugin lifecycle interface (`tool.execute.before`, `tool.execute.after`, and `event`).
   - Non-blocking HTTP POST requests with a 2-second timeout and try/catch error suppression.

## Cross-Agent Hooks Configuration
- **OpenCode**: Configured via `.opencode/plugins/dashboard.js` and `event_forwarder.py`.
- **Claude Code**: Configured via `.claude/settings.json`.
- **Codex**: Configured via `.codex/hooks.json`.

## Testing

```bash
# Unit tests: FastAPI endpoints, buffering, normalization
python -m pytest tests/test_dashboard.py -v

# Integration tests: Live OpenCode SSE event forwarder, fail-soft verification
python -m pytest tests/test_opencode_hook_integration.py -v
```
