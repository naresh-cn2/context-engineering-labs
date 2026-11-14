"""Integration test verifying real-time OpenCode native event forwarding to the dashboard."""

import asyncio
import json
import threading
import time
import urllib.request
import pytest
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[3]
dashboard_dir = Path(__file__).resolve().parents[1]
unit04_dir = repo_root / "unit-04-subagents" / "code-quality-pipeline"

sys.path.insert(0, str(dashboard_dir))
sys.path.insert(0, str(unit04_dir))

from app import api, events
from event_forwarder import OpenCodeEventForwarder
from pipeline_runner import OpenCodeLiveClient


class TestOpenCodeHookIntegration:
    """Verifies OpenCode native event streaming, dashboard reception, and fail-soft behavior."""

    @classmethod
    def setup_class(cls):
        events.clear()

    def test_normalize_opencode_event(self):
        forwarder = OpenCodeEventForwarder()

        # Test session.created mapping
        raw_session = {"type": "session.created", "data": {"sessionID": "ses_123"}}
        norm = forwarder.normalize_event(raw_session)
        assert norm["platform"] == "opencode"
        assert norm["event"] == "SessionStart"

        # Test tool call mapping
        raw_tool = {
            "type": "session.tool.call",
            "data": {"tool": "read", "input": {"path": "main.py"}},
        }
        norm_tool = forwarder.normalize_event(raw_tool)
        assert norm_tool["platform"] == "opencode"
        assert norm_tool["event"] == "PreToolUse"
        assert norm_tool["tool"] == "read"

    def test_fail_soft_when_dashboard_unreachable(self):
        # Point forwarder to a non-existent port
        forwarder = OpenCodeEventForwarder(dashboard_url="http://127.0.0.1:59999/event")

        payload = {
            "platform": "opencode",
            "event": "SessionStart",
            "tool": "",
            "args": "test fail-soft",
        }

        # Must not raise an exception, must return False, and increment failed count
        delivered = forwarder.forward_to_dashboard(payload)
        assert delivered is False
        assert forwarder.failed_forward_count >= 1

    def test_end_to_end_event_forwarding(self):
        # 1. Start a local uvicorn server in a daemon thread on port 8765
        import uvicorn

        config = uvicorn.Config(api, host="127.0.0.1", port=8765, log_level="warning")
        server = uvicorn.Server(config)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        time.sleep(1)

        # 2. Check health endpoint of test dashboard
        req = urllib.request.Request("http://127.0.0.1:8765/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read().decode())
            assert health["ok"] is True
            initial_count = health["events"]

        # 3. Create OpenCode forwarder pointing to test dashboard
        forwarder = OpenCodeEventForwarder(dashboard_url="http://127.0.0.1:8765/event")

        # 4. Stream 3 events in background thread
        captured_events = []

        def listen():
            for evt in forwarder.stream_events(max_events=4, timeout=8):
                captured_events.append(evt)

        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()
        time.sleep(0.5)

        # 5. Trigger a real action on OpenCode
        client = OpenCodeLiveClient()
        session_id = client.create_session("hook-verification-session")
        client.prompt_and_wait(session_id, "Reply with: 'HOOK_VERIFIED'")

        listener_thread.join(timeout=10)

        # 6. Verify events arrived at dashboard API
        req = urllib.request.Request("http://127.0.0.1:8765/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read().decode())
            assert health["events"] > initial_count, "Dashboard events must increment after OpenCode actions"

        assert len(captured_events) > 0, "Forwarder must capture live OpenCode events"
        platform_set = {e["platform"] for e in captured_events}
        assert "opencode" in platform_set
