#!/usr/bin/env python3
"""Agent Activity Dashboard with FastAPI and Gradio.

Conforms to Unit 5 of the Hugging Face Context Engineering Course:
Hooks: Observing and Guarding the Lifecycle.
"""

from __future__ import annotations

import datetime as dt
from collections import Counter, deque
from typing import Any, Dict, List, Optional

import gradio as gr
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ---------- Shared In-Memory State ----------
MAX_EVENTS = 500
events: deque[Dict[str, Any]] = deque(maxlen=MAX_EVENTS)
COLUMNS = ["timestamp", "platform", "event", "tool", "args"]


def _truncate(value: Any, n: int = 200) -> str:
    """Safely converts and truncates text representation to n characters."""
    text = "" if value is None else str(value)
    return text if len(text) <= n else text[: n - 1] + "…"


def _normalize(body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Map Claude Code / Codex / OpenCode / Pi hook payloads to a standardized shape."""
    platform = (
        body.get("platform")
        or headers.get("x-platform")
        or headers.get("x-agent-platform")
        or "unknown"
    )
    event_name = body.get("event") or body.get("hook_event_name") or "Unknown"
    tool = body.get("tool") or body.get("tool_name") or ""
    args = (
        body.get("args")
        or body.get("tool_input")
        or body.get("tool_response")
        or body.get("prompt")
        or ""
    )
    return {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "platform": str(platform),
        "event": str(event_name),
        "tool": str(tool),
        "args": _truncate(args, 200),
    }


# ---------- FastAPI Receiver ----------
api = FastAPI(title="Agent Activity Dashboard API")


@api.post("/event")
async def receive_event(req: Request):
    """Receives lifecycle and tool execution events from agent hooks."""
    try:
        body = await req.json()
    except Exception:
        body = {}
    record = _normalize(body, {k.lower(): v for k, v in req.headers.items()})
    events.appendleft(record)
    # Always return fast 200 OK with empty body so agent hooks never block
    return JSONResponse({"ok": True, "recorded": True})


@api.get("/health")
def health_check():
    """Health check endpoint reporting status and total event count."""
    return {"ok": True, "events": len(events), "max_capacity": MAX_EVENTS}


# ---------- Gradio Visualization ----------
def events_df() -> pd.DataFrame:
    """Builds dataframe of recent events."""
    if not events:
        return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(list(events), columns=COLUMNS)


def tool_counts_df() -> pd.DataFrame:
    """Calculates tool frequency metrics."""
    counter = Counter(e["tool"] for e in events if e["tool"])
    rows = [{"tool": tool, "count": n} for tool, n in counter.most_common(15)]
    if not rows:
        return pd.DataFrame(columns=["tool", "count"])
    return pd.DataFrame(rows, columns=["tool", "count"])


def summary_md() -> str:
    """Generates Markdown summary header."""
    total = len(events)
    platforms = sorted({e["platform"] for e in events}) or ["(none)"]
    tools = sorted({e["tool"] for e in events if e["tool"]})
    tools_display = ", ".join(tools) if tools else "(none)"
    return (
        f"**Total Events Captured:** {total} (in-memory ring buffer: {MAX_EVENTS})  \n"
        f"**Platforms Observed:** {', '.join(platforms)}  \n"
        f"**Distinct Tools Active:** {tools_display}"
    )


def refresh():
    return events_df(), tool_counts_df(), summary_md()


def clear_events():
    events.clear()
    return refresh()


with gr.Blocks(title="Agent Activity Dashboard") as ui:
    gr.Markdown("# Agent Activity & Lifecycle Dashboard")
    gr.Markdown(
        "Real-time hook observer for **OpenCode**, **Claude Code**, and **Codex**. "
        "Receives event telemetry at `POST /event`."
    )

    header = gr.Markdown(value=summary_md())

    with gr.Row():
        clear_btn = gr.Button("Clear Events", variant="secondary")

    chart = gr.BarPlot(
        value=tool_counts_df(),
        x="tool",
        y="count",
        title="Tool Execution Frequency",
        tooltip=["tool", "count"],
        height=260,
    )

    table = gr.Dataframe(
        value=events_df(),
        headers=COLUMNS,
        label="Observed Hook Events (Newest First)",
        wrap=True,
        interactive=False,
    )

    clear_btn.click(clear_events, outputs=[table, chart, header])


# Mount Gradio onto FastAPI root
app = gr.mount_gradio_app(api, ui, path="/")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

