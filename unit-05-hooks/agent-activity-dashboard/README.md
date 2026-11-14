# Agent Activity Dashboard & Real-Time Lifecycle Hooks

[![Hugging Face Context Course](https://img.shields.io/badge/HF%20Context%20Course-Unit%205-FFD21E.svg)](https://huggingface.co/learn/context-course)
[![Framework: FastAPI + SSE](https://img.shields.io/badge/Framework-FastAPI%20%2B%20SSE-009688.svg)](https://fastapi.tiangolo.com)
[![Automated Tests](https://img.shields.io/badge/Tests-9%20Passed-brightgreen.svg)](tests/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A unified real-time observability service capturing agent lifecycle events, tool usage telemetry, and security policy violations across OpenCode, Claude Code, and Codex.

---

## 1. Executive Summary

Autonomous AI agents execute complex tool invocations, bash scripts, and file edits. Without real-time observability, developers operate blindly when agents enter infinite loops, perform unapproved operations, or stall. The **Agent Activity Dashboard** provides a lightweight, real-time observability telemetry platform. It unifies telemetry across three agent platforms via native lifecycle hooks, Server-Sent Events (SSE), and a live web console.

---

## 2. Architectural Overview

```mermaid
flowchart TD
    subgraph AgentRuntimes["Agent Runtimes"]
        OC["OpenCode (v2.2.6+)<br/>SSE Event Stream / Plugins"]
        CC["Claude Code<br/>settings.json Hooks"]
        CX["Codex CLI<br/>hooks.json Webhooks"]
    end

    subgraph Bridges["Integration & Forwarding Layer"]
        Bridge["event_forwarder.py<br/>(Fail-Soft SSE Bridge)"]
        PluginJS[".opencode/plugins/dashboard.js"]
    end

    subgraph DashboardBackend["Observability Backend (FastAPI / Uvicorn)"]
        Ingest["POST /event (Ingestion API)"]
        SSEStream["GET /stream (Server-Sent Events)"]
        Health["GET /health (Telemetry Stats)"]
        WebUI["GET / (Live HTML/JS Dashboard)"]
        EventStore[("In-Memory Circular Event Buffer")]
    end

    subgraph MonitoringClients["Observability UI"]
        Browser["Live Web Browser Dashboard"]
    end

    OC -->|Native SSE /api/event| Bridge
    OC -->|Plugin hooks| PluginJS
    Bridge -->|POST /event| Ingest
    PluginJS -->|POST /event (Fail-Soft)| Ingest
    CC -->|HTTP Post Hook| Ingest
    CX -->|HTTP Post Hook| Ingest

    Ingest --> EventStore
    EventStore --> SSEStream
    EventStore --> Health
    EventStore --> WebUI
    SSEStream --> Browser
```

---

## 3. Problem Statement & Motivation

Agent execution telemetry is typically fragmented:
- **Claude Code** dispatches lifecycle hooks via shell/HTTP commands in `settings.json`.
- **Codex** notifies endpoints via `hooks.json`.
- **OpenCode** broadcasts native SSE events (`/api/event`) and executes in-process JavaScript plugin modules.

The Agent Activity Dashboard bridges all three paradigms into a common event taxonomy (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) with fail-soft guarantees ensuring agent execution is never halted by telemetry downtime.

---

## 4. Detailed Feature Specifications

1. **Multi-Platform Ingestion (`POST /event`)**:
   - Ingests events conforming to `{ platform, event, tool, args, timestamp }`.
   - Ring buffer storing recent events with bounded memory footprint.
2. **Real-Time SSE Streaming (`GET /stream`)**:
   - Streams live JSON events directly to connected web clients with automatic reconnection.
3. **OpenCode Native SSE Bridge (`event_forwarder.py`)**:
   - Connects to OpenCode daemon `GET /api/event`.
   - Translates raw OpenCode events into standard course taxonomy.
   - Fail-soft network retry logic.
4. **Code-First Plugin Module (`.opencode/plugins/dashboard.js`)**:
   - Subscribes to `tool.execute.before` and `tool.execute.after`.
   - Includes timeout-aborted asynchronous HTTP requests to prevent blocking the agent.

---

## 5. Prerequisites & Environment Setup

- **Python**: 3.10+ (tested on 3.12.10).
- **Dependencies**: `fastapi`, `uvicorn`, `pytest`.

```bash
cd course-workspace/unit5-hooks/agent-activity-dashboard
pip install -r requirements.txt
```

---

## 6. Installation & Quickstart

### 1. Launch Dashboard Server
```bash
python app.py
```
Server starts on `http://127.0.0.1:8000`.

### 2. Launch Event Forwarder (for OpenCode)
```bash
python event_forwarder.py
```

### 3. Open Web UI
Navigate to `http://localhost:8000` in your web browser to view the real-time activity stream.

---

## 7. Configuration & Environment Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `PORT` | `integer` | `8000` | HTTP listening port for dashboard service |
| `OPENCODE_HOST` | `string` | `http://127.0.0.1:28894` | OpenCode daemon host |
| `DASHBOARD_URL` | `string` | `http://localhost:8000/event` | Destination URL for forwarder and hooks |
| `MAX_EVENT_HISTORY` | `integer` | `500` | Maximum events retained in circular buffer |

---

## 8. Complete API / Interface Reference

### `POST /event`
Ingests an agent telemetry event.
- **Request Body**:
  ```json
  {
    "platform": "opencode",
    "event": "PreToolUse",
    "tool": "bash",
    "args": "pytest tests/"
  }
  ```
- **Response**: `200 OK` `{ "status": "ok", "total_events": 42 }`

### `GET /stream`
Server-Sent Events endpoint streaming realtime event objects as `data: {...}\n\n`.

### `GET /health`
Returns health status, active connections, and event counts.

### `GET /`
Serves the self-contained live web dashboard application.

---

## 9. End-to-End Usage Examples

### Manual Event Emission
```bash
curl -X POST http://127.0.0.1:8000/event \
  -H "Content-Type: application/json" \
  -d '{"platform":"claude","event":"SessionStart","tool":"","args":"Refactoring auth module"}'
```

The browser UI immediately renders a new log card with platform badge, timestamp, and metadata.

---

## 10. Testing & Quality Assurance

Run the automated test suite covering unit API contracts and live OpenCode event forwarding:

```bash
.venv\Scripts\python.exe -m pytest course-workspace/unit5-hooks/agent-activity-dashboard/tests -v
```

### Test Suite Details
- `test_dashboard.py`:
  - `test_health_check`: Validates server health and status responses.
  - `test_ingest_event`: Verifies ingestion payload validation and memory persistence.
  - `test_claude_settings_config`: Verifies Claude `settings.json` hook format.
  - `test_codex_hooks_config`: Verifies Codex `hooks.json` hook format.
  - `test_opencode_plugin_file`: Verifies JavaScript plugin hooks structure.
  - `test_sse_stream`: Validates event streaming format.
- `test_opencode_hook_integration.py`:
  - `test_normalize_opencode_event`: Verifies event translation matrix.
  - `test_fail_soft_when_dashboard_unreachable`: Asserts forwarder never raises or crashes on unreachable server.
  - `test_end_to_end_event_forwarding`: Verifies live forwarder event capture and delivery to dashboard.

---

## 11. Security, Sandboxing & Safety Considerations

- **Fail-Soft Isolation**: If the dashboard server crashes or network latency spikes, agent hooks fail silently without throwing exceptions or blocking developer tasks.
- **Payload Truncation**: Arguments are sanitized and truncated (max 200 chars in logs) to prevent credential leaks or buffer overload.
- **Localhost Binding**: Binds exclusively to loopback (`127.0.0.1`) by default.

---

## 12. Edge Cases & Known Failure Modes

1. **Dashboard Downtime**: Telemetry is discarded when offline; no local disk bloat or infinite retry loops occur.
2. **High-Frequency Events**: Ring buffer caps history at 500 events to prevent memory degradation during intensive agent workloads.

---

## 13. Troubleshooting & FAQ

**Q: Why don't I see events in the dashboard when using OpenCode?**
A: Ensure `python event_forwarder.py` is running alongside OpenCode so it can bridge OpenCode's native SSE stream to the dashboard.

**Q: Can I run this with Docker?**
A: Yes, expose port 8000 and bind to `0.0.0.0` within the container.

---

## 14. Contributing Guidelines

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflows and code standards.

---

## 15. Changelog & Versioning

See [CHANGELOG.md](CHANGELOG.md) for release notes. Current version: `1.0.0`.

---

## 16. License & Credits

- **License**: Apache 2.0.
- **Course**: Developed for Unit 5 of the [Hugging Face Context Engineering Course](https://huggingface.co/learn/context-course).
