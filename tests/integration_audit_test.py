"""Comprehensive End-to-End Integration and Security Audit Suite.

Conducts live, non-mocked integration tests across Units 1 through 6.

Adapted for the published repository layout:
- tests/ lives at the repository root
- each unit lives at <repo-root>/unit-XX-<family>/<project>/
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from starlette.testclient import TestClient

# Repository root (tests/ is at the root of this repo).
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]

# Paths to units (published layout).
UNIT1_DIR = WORKSPACE_ROOT / "unit-01-agent-skills" / "hf-dataset-validation"
UNIT2_DIR = WORKSPACE_ROOT / "unit-02-mcp" / "text-processor-mcp"
UNIT3_DIR = WORKSPACE_ROOT / "unit-03-plugins" / "text-processor-plugin"
UNIT4_DIR = WORKSPACE_ROOT / "unit-04-subagents" / "code-quality-pipeline"
UNIT5_DIR = WORKSPACE_ROOT / "unit-05-hooks" / "agent-activity-dashboard"
UNIT6_DIR = WORKSPACE_ROOT / "unit-06-nano-harness"

PY_EXE = sys.executable


# ==============================================================================
# 1. UNIT 1: Agent Skill Discovery & Functional Execution
# ==============================================================================
class TestUnit1Integration:
    """Verifies that the hf-dataset-validation skill is self-contained and executable."""

    def test_skill_spec_present_and_valid(self):
        """The published skill carries a valid Agent Skills Specification SKILL.md."""
        skill_md = UNIT1_DIR / "SKILL.md"
        assert skill_md.exists(), "SKILL.md must be located at the root of the skill directory."

        content = skill_md.read_text(encoding="utf-8")
        assert content.startswith("---"), "SKILL.md must start with YAML frontmatter."
        parts = content.split("---", 2)
        assert len(parts) >= 3, "Frontmatter must be enclosed between '---' delimiters."

        frontmatter = yaml.safe_load(parts[1])
        assert isinstance(frontmatter, dict), "Frontmatter must parse into a YAML dictionary."
        assert "name" in frontmatter, "Missing required 'name' field in frontmatter."
        assert "description" in frontmatter, "Missing required 'description' field in frontmatter."
        assert frontmatter["name"] == UNIT1_DIR.name, (
            f"Skill name '{frontmatter['name']}' must match directory name '{UNIT1_DIR.name}'."
        )

    def test_real_dataset_validation_cli_execution(self):
        script = str(UNIT1_DIR / "scripts" / "validate_dataset.py")
        clean_csv = str(UNIT1_DIR / "test_data" / "clean_sample.csv")

        proc = subprocess.run([PY_EXE, script, clean_csv], capture_output=True, text=True)
        assert proc.returncode == 0, f"Validation script failed with stderr: {proc.stderr}"

        output = json.loads(proc.stdout)
        assert output["status"] == "PASS"
        assert output["metadata"]["rows"] == 3
        assert len(output["errors"]) == 0

    def test_flawed_dataset_rejection(self):
        script = str(UNIT1_DIR / "scripts" / "validate_dataset.py")
        flawed_csv = str(UNIT1_DIR / "test_data" / "flawed_sample.csv")

        proc = subprocess.run([PY_EXE, script, flawed_csv], capture_output=True, text=True)
        assert proc.returncode == 0  # Warnings do not cause non-zero exit code
        output = json.loads(proc.stdout)
        assert output["status"] == "WARNING"
        assert len(output["warnings"]) >= 3


# ==============================================================================
# 2. UNIT 2: Live MCP Server Connection & Tool Invocations
# ==============================================================================
class TestUnit2Integration:
    """Verifies actual execution of FastMCP / MCPServer tools."""

    def test_live_tool_invocations(self):
        sys.path.insert(0, str(UNIT2_DIR))
        import server

        # 1. Test analyze_text
        sample = "Context engineering teaches agents to structure knowledge for optimal reliability."
        res1 = json.loads(server.analyze_text(sample))
        assert res1["total_words"] == 10
        assert res1["total_characters"] == len(sample)
        assert res1["unique_words"] == 10

        # 2. Test extract_keywords
        res2 = json.loads(server.extract_keywords("Python agents call MCP tools. Agents love Python.", count=2))
        keywords = [item["word"] for item in res2["keywords"]]
        assert "agents" in keywords or "python" in keywords

        # 3. Test check_reading_level
        res3 = json.loads(server.check_reading_level("The cat sat on the mat."))
        assert res3["reading_level"] in ("Elementary School", "Middle School")

        # 4. Test reverse_text
        assert server.reverse_text("MCP") == "PCM"

        # 5. Test detect_sentiment
        res5 = json.loads(server.detect_sentiment("This clean and reliable code is great!"))
        assert res5["sentiment"] == "positive"
        assert res5["score"] > 0



# ==============================================================================
# 3. UNIT 3: Plugin Bundle & Cross-Platform Packaging
# ==============================================================================
class TestUnit3Integration:
    """Verifies that the plugin bundle correctly packages skills and MCP links."""

    def test_plugin_manifest_cross_platform_validity(self):
        claude_manifest = json.loads((UNIT3_DIR / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        assert claude_manifest["name"] == "text-processor-plugin"

        codex_manifest = json.loads((UNIT3_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        assert codex_manifest["name"] == "text-processor-plugin"
        assert len(codex_manifest["skills"]) == 3

    def test_mcp_config_links_to_unit2_server(self):
        mcp_config = json.loads((UNIT3_DIR / ".mcp.json").read_text(encoding="utf-8"))
        server_entry = mcp_config["mcpServers"]["text-processor"]
        assert "args" in server_entry
        target_server = (UNIT3_DIR / server_entry["args"][0]).resolve()
        assert target_server.exists(), f"Target MCP server not found at: {target_server}"


# ==============================================================================
# 4. UNIT 4: Actual Subagent Multi-Agent Orchestration
# ==============================================================================
class TestUnit4Integration:
    """Verifies the multi-agent pipeline orchestration lifecycle."""

    def test_pipeline_execution_and_isolation(self):
        sys.path.insert(0, str(UNIT4_DIR))
        from pipeline_runner import CodeQualityPipeline

        target_file = UNIT4_DIR / "main.py"
        pipeline = CodeQualityPipeline(target_file)

        # Stage 1: Researcher identifies defects
        research = pipeline.run_researcher()
        assert any("N+1" in r for r in research.potential_risks)
        assert any("token" in r.lower() for r in research.potential_risks)

        # Stage 2-4: Parallel Reviewers & Sign-off
        results = pipeline.execute_pipeline()
        assert results["target"] == "main.py"
        assert "security_verdict" in results
        assert "performance_verdict" in results


# ==============================================================================
# 5. UNIT 5: Real Hook Event Delivery & Ingestion
# ==============================================================================
class TestUnit5Integration:
    """Verifies HTTP event ingestion and Gradio monitoring."""

    def test_real_hook_delivery(self):
        sys.path.insert(0, str(UNIT5_DIR))
        from app import api, events

        events.clear()
        client = TestClient(api)

        # Send OpenCode telemetry event
        payload = {
            "platform": "opencode",
            "event": "PreToolUse",
            "tool": "analyze_text",
            "args": "Sample input text for analysis",
        }
        res = client.post("/event", json=payload)
        assert res.status_code == 200
        assert len(events) == 1
        assert events[0]["tool"] == "analyze_text"

        # Health endpoint reports updated count
        health_res = client.get("/health")
        assert health_res.json()["events"] == 1


# ==============================================================================
# 6. UNIT 6: Nano Harness Security Audit & Execution Boundaries
# ==============================================================================
class TestUnit6SecurityAudit:
    """Rigorous security testing of Nano Harness execution boundaries."""

    def test_path_traversal_attack_blocked(self, tmp_path):
        sys.path.insert(0, str(UNIT6_DIR))
        from nano_harness import NanoHarness

        harness = NanoHarness(workspace=tmp_path, allow_write=False)

        # Test ../ traversal
        with pytest.raises(PermissionError):
            harness.safe_path("../../../etc/passwd")

        # Test absolute path escape
        with pytest.raises(PermissionError):
            harness.safe_path("C:/Windows/System32/calc.exe")

    def test_disallowed_shell_commands_blocked(self, tmp_path):
        from nano_harness import NanoHarness
        harness = NanoHarness(workspace=tmp_path, allow_commands=["echo"])

        with pytest.raises(PermissionError, match="not permitted"):
            harness.exec_cmd(["curl", "http://evil.com"])

        with pytest.raises(PermissionError, match="not permitted"):
            harness.exec_cmd(["python", "-c", "import os; os.system('calc')"])

    def test_arbitrary_file_write_blocked_when_allow_write_false(self, tmp_path):
        from nano_harness import NanoHarness
        harness = NanoHarness(workspace=tmp_path, allow_write=False)

        with pytest.raises(PermissionError, match="write_file disabled"):
            harness.write_file("malicious.bat", "@echo off\nformat C:")

    def test_agent_loop_observation_reflection(self, tmp_path):
        from nano_harness import NanoHarness
        harness = NanoHarness(workspace=tmp_path, allow_write=True)

        # Agent step 1: write a file with print output
        obs1 = harness.step("print(write_file('notes.txt', 'research complete'))")
        assert "Wrote" in obs1

        # Agent step 2: read the file
        obs2 = harness.step("print(read_file('notes.txt'))")
        assert "research complete" in obs2

        # Agent step 3: finish
        obs3 = harness.step("final_answer('Task fully succeeded.')")
        assert harness.done is True
        assert harness.final_result == "Task fully succeeded."
