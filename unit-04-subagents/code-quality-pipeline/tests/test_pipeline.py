"""Automated test suite for Multi-Agent Code Quality Pipeline."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import tomlkit
import yaml

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENTS_DIR = PIPELINE_ROOT / ".claude" / "agents"
CODEX_AGENTS_DIR = PIPELINE_ROOT / ".codex" / "agents"

sys_path = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(sys_path))
from pipeline_runner import CodeQualityPipeline


class TestAgentConfiguration:
    """Verifies subagent definition files and tool isolation policies."""

    @pytest.mark.parametrize("agent_name", ["researcher", "implementer", "security-reviewer", "performance-reviewer"])
    def test_claude_agent_md_exists(self, agent_name: str):
        agent_file = CLAUDE_AGENTS_DIR / f"{agent_name}.md"
        assert agent_file.exists(), f"Missing Claude agent definition: {agent_file}"

        content = agent_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"Agent {agent_name} lacks YAML frontmatter"
        fm = yaml.safe_load(parts[1])
        assert fm.get("name") == agent_name
        assert "tools" in fm

    @pytest.mark.parametrize("agent_name", ["researcher", "implementer", "security-reviewer", "performance-reviewer"])
    def test_codex_agent_toml_exists(self, agent_name: str):
        # Allow hyphen or underscore for codex toml filename
        toml_file = CODEX_AGENTS_DIR / f"{agent_name}.toml"
        assert toml_file.exists(), f"Missing Codex agent definition: {toml_file}"

        content = toml_file.read_text(encoding="utf-8")
        data = tomlkit.parse(content)
        assert "description" in data
        assert "developer_instructions" in data

    def test_reviewer_read_only_sandbox(self):
        # Security reviewer and performance reviewer must be read-only
        for reviewer in ["security-reviewer", "performance-reviewer"]:
            md_file = CLAUDE_AGENTS_DIR / f"{reviewer}.md"
            content = md_file.read_text(encoding="utf-8")
            fm = yaml.safe_load(content.split("---", 2)[1])
            tools = fm.get("tools", "")
            assert "Write" not in tools, f"Reviewer agent {reviewer} must not have Write tool access!"


class TestPipelineOrchestration:
    """Verifies sequential handoff and fan-out/fan-in review patterns."""

    def test_pipeline_execution_simulated(self):
        target = PIPELINE_ROOT / "main.py"
        pipeline = CodeQualityPipeline(target, mode="simulated")

        # Stage 1: Researcher
        research = pipeline.run_researcher()
        assert len(research.identified_patterns) > 0
        assert len(research.potential_risks) >= 2

        # Stage 2 & 3: Run pipeline
        result = pipeline.execute_pipeline()
        assert result["mode"] == "simulated"
        assert result["target"] == "main.py"
        assert "security_verdict" in result
        assert "performance_verdict" in result
        assert result["security_verdict"]["permission_mode"] == "read_only"
        assert result["performance_verdict"]["permission_mode"] == "read_only"
        assert isinstance(result["pipeline_signed_off"], bool)

    def test_live_run_trace_artifact(self):
        trace_path = PIPELINE_ROOT / "traces" / "live_run_trace.json"
        assert trace_path.exists(), "live_run_trace.json must exist from live multi-agent execution."

        data = json.loads(trace_path.read_text(encoding="utf-8"))
        assert data.get("mode") == "live"
        assert data.get("provider") == "nvidia"
        assert data.get("cost") == 0
        assert "research" in data
        assert "security_verdict" in data
        assert "performance_verdict" in data
        assert data["security_verdict"]["permission_mode"] == "read_only"
        assert data["performance_verdict"]["permission_mode"] == "read_only"


