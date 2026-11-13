"""Automated test suite for Nano Harness (Unit 6)."""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

import sys
HARNESS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_DIR))

from nano_harness import NanoHarness


@pytest.fixture
def test_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "hello.txt").write_text("Hello World from Nano Harness!", encoding="utf-8")
        harness = NanoHarness(workspace=tmp_path, allow_write=False)
        yield harness, tmp_path


class TestNanoHarnessSandboxing:
    """Verifies security boundaries and constraints."""

    def test_safe_path_confinement(self, test_env):
        harness, tmp_path = test_env

        # Allowed path
        safe = harness.safe_path("hello.txt")
        assert safe == tmp_path / "hello.txt"

        # Traversal attempt
        with pytest.raises(PermissionError, match="escapes workspace root"):
            harness.safe_path("../../windows/system32")

    def test_write_gating_disabled(self, test_env):
        harness, _ = test_env
        assert harness.allow_write is False

        with pytest.raises(PermissionError, match="write_file disabled"):
            harness.write_file("new_file.txt", "data")

    def test_write_gating_enabled(self, test_env):
        _, tmp_path = test_env
        harness_writer = NanoHarness(workspace=tmp_path, allow_write=True)

        res = harness_writer.write_file("output.txt", "payload123")
        assert "Wrote 10 bytes" in res
        assert (tmp_path / "output.txt").read_text(encoding="utf-8") == "payload123"

    def test_command_allowlist(self, test_env):
        harness, _ = test_env
        with pytest.raises(PermissionError, match="not permitted"):
            harness.exec_cmd(["rm", "-rf", "/"])

    def test_output_clipping(self, test_env):
        harness, _ = test_env
        harness.max_chars = 50
        long_text = "a" * 100
        clipped = harness.clip(long_text)
        assert len(clipped) < 100
        assert "Output truncated" in clipped


class TestNanoHarnessExecution:
    """Verifies step execution and agent tool interactions."""

    def test_step_list_and_read(self, test_env):
        harness, _ = test_env

        code = (
            "files = list_dir('.')\n"
            "print('Found:', files)\n"
            "content = read_file('hello.txt')\n"
            "print('Content:', content)\n"
        )
        obs = harness.step(code)
        assert "hello.txt" in obs
        assert "Hello World from Nano Harness!" in obs
        assert harness.done is False

    def test_step_final_answer(self, test_env):
        harness, _ = test_env

        code = "final_answer({'status': 'complete', 'files_processed': 1})"
        obs = harness.step(code)
        assert harness.done is True
        assert harness.final_result == {"status": "complete", "files_processed": 1}
        assert "Final answer:" in obs

    def test_python_fence_extraction(self):
        fenced_code = "Here is the code:\n```python\nprint('hello')\n```\nDone."
        extracted = NanoHarness.extract_python(fenced_code)
        assert extracted == "print('hello')"

    def test_extended_tools_interface(self, test_env):
        harness, _ = test_env
        # Test web_fetch error handling with invalid host
        result = harness.web_fetch("http://invalid-nonexistent-domain-xyz123.org", max_bytes=100)
        assert "Error:" in result

