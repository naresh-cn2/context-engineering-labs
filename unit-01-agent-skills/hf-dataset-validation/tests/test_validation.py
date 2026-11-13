"""Automated test suite for hf-dataset-validation skill."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

# Resolve paths
SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
TEST_DATA_DIR = SKILL_ROOT / "test_data"
SKILL_MD = SKILL_ROOT / "SKILL.md"

sys.path.insert(0, str(SCRIPTS_DIR))
from validate_dataset import validate_dataset
from generate_report import generate_report


class TestSkillSpecification:
    """Verifies compliance with the Agent Skills Specification (agentskills.io)."""

    def test_skill_md_exists(self):
        assert SKILL_MD.exists(), "SKILL.md must be located at the root of the skill directory."

    def test_skill_frontmatter_schema(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert content.startswith("---"), "SKILL.md must start with YAML frontmatter."
        parts = content.split("---", 2)
        assert len(parts) >= 3, "Frontmatter must be enclosed between '---' delimiters."

        frontmatter = yaml.safe_load(parts[1])
        assert isinstance(frontmatter, dict), "Frontmatter must parse into a YAML dictionary."

        # Required fields per Agent Skills Spec
        assert "name" in frontmatter, "Missing required 'name' field in frontmatter."
        assert "description" in frontmatter, "Missing required 'description' field in frontmatter."

        # Field validation
        name = frontmatter["name"]
        assert name == SKILL_ROOT.name, f"Skill name '{name}' must match directory name '{SKILL_ROOT.name}'."
        assert len(name) <= 64, "Skill name must not exceed 64 characters."
        assert "--" not in name, "Skill name must not contain consecutive hyphens."

        description = frontmatter["description"]
        assert len(description) <= 1024, "Skill description must not exceed 1024 characters."
        assert len(description) >= 20, "Skill description must be adequately descriptive."


class TestDatasetValidationEngine:
    """Verifies dataset validation logic and edge cases."""

    def test_clean_sample(self):
        clean_file = TEST_DATA_DIR / "clean_sample.csv"
        result = validate_dataset(clean_file)

        assert result["status"] == "PASS"
        assert result["format"] == "csv"
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
        assert result["metadata"]["rows"] == 3
        assert set(result["metadata"]["columns"]) == {"text", "label", "split"}

    def test_flawed_sample(self):
        flawed_file = TEST_DATA_DIR / "flawed_sample.csv"
        result = validate_dataset(flawed_file)

        assert result["status"] == "WARNING"
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) > 0

        # Verify duplicate detection
        assert result["metadata"]["duplicate_rows"] == 1

        # Verify missing value detection
        assert "missing_values" in result["metadata"]
        assert result["metadata"]["missing_values"].get("text", 0) >= 1

        # Verify empty string detection
        assert "empty_strings" in result["metadata"]
        assert result["metadata"]["empty_strings"].get("text", 0) >= 1

    def test_invalid_schema(self):
        invalid_file = TEST_DATA_DIR / "invalid_schema.csv"
        result = validate_dataset(invalid_file)

        assert result["status"] == "FAIL"
        assert len(result["errors"]) > 0
        assert any("Missing required columns" in err for err in result["errors"])

    def test_nonexistent_file(self):
        fake_file = TEST_DATA_DIR / "nonexistent_file_xyz.csv"
        result = validate_dataset(fake_file)

        assert result["status"] == "FAIL"
        assert any("File not found" in err for err in result["errors"])

    def test_json_format(self):
        json_file = TEST_DATA_DIR / "sample.json"
        result = validate_dataset(json_file)

        assert result["status"] == "PASS"
        assert result["format"] == "json"
        assert result["metadata"]["rows"] == 2

    def test_generate_report(self):
        clean_file = TEST_DATA_DIR / "clean_sample.csv"
        report_output = generate_report(clean_file)

        assert "HUGGING FACE DATASET VALIDATION REPORT" in report_output
        assert "Overall Status:   PASS" in report_output
        assert "DATASET DIMENSIONS & MEMORY:" in report_output
        assert "REMEDIATION RECOMMENDATIONS:" in report_output


class TestCLIExecution:
    """Verifies command-line execution and exit codes."""

    def test_cli_clean_pass(self):
        clean_file = str(TEST_DATA_DIR / "clean_sample.csv")
        cmd = [sys.executable, str(SCRIPTS_DIR / "validate_dataset.py"), clean_file]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        assert proc.returncode == 0, f"Expected exit code 0, got {proc.returncode} with stderr: {proc.stderr}"
        output = json.loads(proc.stdout)
        assert output["status"] == "PASS"

    def test_cli_failure_exit_code(self):
        invalid_file = str(TEST_DATA_DIR / "invalid_schema.csv")
        cmd = [sys.executable, str(SCRIPTS_DIR / "validate_dataset.py"), invalid_file]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        assert proc.returncode == 1, f"Expected exit code 1 for schema error, got {proc.returncode}"
        output = json.loads(proc.stdout)
        assert output["status"] == "FAIL"

