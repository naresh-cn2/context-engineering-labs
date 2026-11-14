"""Automated test suite for Text Processor Plugin bundle."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class TestPluginBundleStructure:
    """Verifies plugin manifests, bundled skills, and MCP configuration."""

    def test_claude_manifest(self):
        manifest_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        assert manifest_path.exists(), "Missing .claude-plugin/plugin.json manifest."

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data.get("name") == "text-processor-plugin"
        assert "version" in data
        assert "description" in data

    def test_codex_manifest(self):
        manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        assert manifest_path.exists(), "Missing .codex-plugin/plugin.json manifest."

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data.get("name") == "text-processor-plugin"
        assert "skills" in data
        assert len(data["skills"]) == 3

    def test_mcp_configuration(self):
        mcp_path = PLUGIN_ROOT / ".mcp.json"
        assert mcp_path.exists(), "Missing .mcp.json."

        data = json.loads(mcp_path.read_text(encoding="utf-8"))
        assert "mcpServers" in data
        assert "text-processor" in data["mcpServers"]

    def test_bundled_skills(self):
        skills_dir = PLUGIN_ROOT / "skills"
        assert skills_dir.exists()

        expected_skills = ["analyze-text", "extract-keywords", "check-reading-level"]
        for skill_name in expected_skills:
            skill_md = skills_dir / skill_name / "SKILL.md"
            assert skill_md.exists(), f"Missing SKILL.md for {skill_name}"

            content = skill_md.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            assert len(parts) >= 3, f"Skill {skill_name} lacks YAML frontmatter"

            fm = yaml.safe_load(parts[1])
            assert fm.get("name") == skill_name, f"Frontmatter name must match folder: {skill_name}"
            assert "description" in fm, f"Missing description in {skill_name}"

    def test_opencode_plugin_module(self):
        js_module = PLUGIN_ROOT / ".opencode" / "plugins" / "text-processor-plugin.js"
        assert js_module.exists(), "Missing OpenCode plugin module."
        content = js_module.read_text(encoding="utf-8")
        assert "TextProcessorPlugin" in content
        assert "tool.execute.before" in content
        assert "setup:" in content or "setup :" in content, "Plugin must provide setup function"
        assert "id:" in content or 'id: "text-processor-plugin"' in content, "Plugin must provide id"

    def test_package_json_declaration(self):
        pkg_json = PLUGIN_ROOT / "package.json"
        assert pkg_json.exists(), "Missing plugin package.json."
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        assert data.get("name") == "text-processor-plugin"
        assert "main" in data
        assert "exports" in data


