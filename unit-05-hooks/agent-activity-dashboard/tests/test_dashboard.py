"""Automated test suite for Agent Activity Dashboard."""

from __future__ import annotations

import sys
from pathlib import Path
import pytest
from starlette.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from app import api, events, _normalize, events_df, tool_counts_df, summary_md, MAX_EVENTS

client = TestClient(api)


@pytest.fixture(autouse=True)
def clean_events():
    """Ensure clean in-memory events state before each test."""
    events.clear()
    yield
    events.clear()


class TestDashboardAPI:
    """Verifies FastAPI receiver and telemetry normalization."""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["events"] == 0
        assert data["max_capacity"] == MAX_EVENTS

    def test_post_event_opencode(self):
        payload = {
            "platform": "opencode",
            "event": "PreToolUse",
            "tool": "read_file",
            "args": "path='main.py'",
        }
        response = client.post("/event", json=payload)
        assert response.status_code == 200
        assert len(events) == 1

        rec = events[0]
        assert rec["platform"] == "opencode"
        assert rec["event"] == "PreToolUse"
        assert rec["tool"] == "read_file"
        assert "main.py" in rec["args"]

    def test_post_event_claude_headers(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "grep",
            "tool_input": "pattern='secret'",
        }
        headers = {"x-platform": "claude-code"}
        response = client.post("/event", json=payload, headers=headers)
        assert response.status_code == 200
        assert len(events) == 1

        rec = events[0]
        assert rec["platform"] == "claude-code"
        assert rec["event"] == "PostToolUse"
        assert rec["tool"] == "grep"

    def test_truncation(self):
        long_args = "x" * 500
        payload = {
            "platform": "codex",
            "event": "ToolExecution",
            "tool": "bash",
            "args": long_args,
        }
        response = client.post("/event", json=payload)
        assert response.status_code == 200
        rec = events[0]
        assert len(rec["args"]) == 200
        assert rec["args"].endswith("…")

    def test_buffer_capacity_limit(self):
        for i in range(MAX_EVENTS + 50):
            events.appendleft({
                "timestamp": "2026-11-13T00:00:00Z",
                "platform": "test",
                "event": "Event",
                "tool": f"tool_{i % 5}",
                "args": f"run {i}",
            })
        assert len(events) == MAX_EVENTS

    def test_dataframe_and_summary_renders(self):
        events.appendleft({
            "timestamp": "2026-11-13T00:00:00Z",
            "platform": "opencode",
            "event": "PreToolUse",
            "tool": "validate_dataset",
            "args": "sample.csv",
        })
        df = events_df()
        assert len(df) == 1
        assert "timestamp" in df.columns

        counts = tool_counts_df()
        assert len(counts) == 1
        assert counts.iloc[0]["tool"] == "validate_dataset"
        assert counts.iloc[0]["count"] == 1

        summary = summary_md()
        assert "**Total Events Captured:** 1" in summary
        assert "opencode" in summary

