#!/usr/bin/env python3
"""OpenCode Native Event Forwarder Bridge for Agent Activity Dashboard.

Subscribes to OpenCode's native SSE event stream (GET /api/event) and forwards
lifecycle and tool events to the dashboard's POST /event endpoint.
Includes fail-soft exception handling ensuring OpenCode operations never block.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, Generator, Optional
import urllib.error
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OpenCodeEventForwarder")


class OpenCodeEventForwarder:
    def __init__(
        self,
        opencode_host: str = "http://127.0.0.1:28894",
        dashboard_url: str = "http://127.0.0.1:8000/event",
        service_config_path: Optional[Path] = None,
    ):
        self.opencode_host = opencode_host.rstrip("/")
        self.dashboard_url = dashboard_url
        self.service_config_path = (
            service_config_path
            or Path.home() / ".config" / "opencode" / "service.json"
        )
        self.auth_header = self._resolve_auth()
        self.forwarded_count = 0
        self.failed_forward_count = 0

    def _resolve_auth(self) -> str:
        if self.service_config_path.exists():
            try:
                data = json.loads(self.service_config_path.read_text(encoding="utf-8"))
                password = data.get("password", "")
                token = base64.b64encode(f"opencode:{password}".encode()).decode()
                return f"Basic {token}"
            except Exception as e:
                logger.warning(f"Could not read service auth: {e}")
        return ""

    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Maps OpenCode native SSE event to dashboard schema."""
        evt_type = raw_event.get("type", "unknown")
        data = raw_event.get("data", {}) or {}

        # Map OpenCode native event types to course dashboard taxonomy
        event_name = evt_type
        tool_name = ""
        args = ""

        if evt_type == "session.created":
            event_name = "SessionStart"
            args = f"Session {data.get('sessionID', '')} created"
        elif evt_type == "session.idle":
            event_name = "Stop"
            args = f"Session {data.get('sessionID', '')} became idle"
        elif "tool.call" in evt_type or "tool.execute.before" in evt_type:
            event_name = "PreToolUse"
            tool_name = data.get("tool", data.get("toolName", ""))
            args = str(data.get("input", data.get("args", "")))
        elif "tool.result" in evt_type or "tool.execute.after" in evt_type:
            event_name = "PostToolUse"
            tool_name = data.get("tool", data.get("toolName", ""))
            args = str(data.get("output", data.get("result", "")))
        elif "reasoning" in evt_type:
            event_name = "AgentReasoning"
            args = str(data.get("delta", ""))
        elif "message" in evt_type:
            event_name = "AgentMessage"
            args = str(data.get("payload", ""))

        return {
            "platform": "opencode",
            "event": event_name,
            "tool": tool_name,
            "args": args[:200],
            "raw_type": evt_type,
            "timestamp": time.time(),
        }

    def forward_to_dashboard(self, payload: Dict[str, Any]) -> bool:
        """Sends event to dashboard API. Fail-soft: catches all exceptions."""
        try:
            req = urllib.request.Request(
                self.dashboard_url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    self.forwarded_count += 1
                    return True
        except Exception as e:
            # Fail-soft design: do not raise or block OpenCode
            self.failed_forward_count += 1
            logger.debug(f"Dashboard forward skipped/offline: {e}")
        return False

    def stream_events(
        self, max_events: Optional[int] = None, timeout: Optional[float] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Connects to OpenCode SSE stream and yields events."""
        url = f"{self.opencode_host}/api/event"
        req = urllib.request.Request(url, headers={"Authorization": self.auth_header})

        start_time = time.time()
        count = 0

        with urllib.request.urlopen(req, timeout=10) as resp:
            for line in resp:
                if timeout and (time.time() - start_time) > timeout:
                    break

                line_str = line.decode("utf-8", errors="ignore").strip()
                if not line_str.startswith("data:"):
                    continue

                raw_json = line_str[5:].strip()
                if not raw_json:
                    continue

                try:
                    raw_event = json.loads(raw_json)
                    normalized = self.normalize_event(raw_event)
                    self.forward_to_dashboard(normalized)
                    count += 1
                    yield normalized
                    if max_events and count >= max_events:
                        break
                except json.JSONDecodeError:
                    continue


def main():
    forwarder = OpenCodeEventForwarder()
    logger.info("Starting OpenCode Event Forwarder bridge to %s...", forwarder.dashboard_url)
    try:
        for evt in forwarder.stream_events():
            logger.info("Forwarded [%s] event=%s tool=%s", evt["platform"], evt["event"], evt["tool"])
    except KeyboardInterrupt:
        logger.info("Forwarder stopped by user.")


if __name__ == "__main__":
    main()

