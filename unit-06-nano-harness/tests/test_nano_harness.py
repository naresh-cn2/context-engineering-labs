"""Automated test suite and security regression tests for Nano Harness (Unit 6)."""

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

    def test_path_traversal_variations(self, test_env):
        harness, _ = test_env

        # Absolute path outside root
        with pytest.raises(PermissionError, match="escapes workspace root"):
            harness.safe_path("C:/Windows/System32/drivers/etc/hosts")

        # Percent-encoded traversal sequence (%2e%2e)
        with pytest.raises(PermissionError, match="escapes workspace root"):
            harness.safe_path("%2e%2e/%2e%2e/etc/passwd")

        # Null byte injection
        with pytest.raises(PermissionError, match="null byte in path"):
            harness.safe_path("hello.txt\0/../../shadow")

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

    def test_write_restricted_files_forbidden(self, test_env):
        _, tmp_path = test_env
        harness_writer = NanoHarness(workspace=tmp_path, allow_write=True)

        with pytest.raises(PermissionError, match="mutating restricted path part"):
            harness_writer.write_file(".git/config", "malicious_config")

        with pytest.raises(PermissionError, match="mutating restricted path part"):
            harness_writer.write_file(".env", "SECRET=stolen")

    def test_command_allowlist(self, test_env):
        harness, _ = test_env
        with pytest.raises(PermissionError, match="not permitted"):
            harness.exec_cmd(["rm", "-rf", "/"])

    def test_command_injection_defense(self, test_env):
        harness, _ = test_env

        # Command chaining attempts
        with pytest.raises(PermissionError, match="strictly forbidden"):
            harness.exec_cmd(["echo", "hello", "&&", "cat", "hello.txt"])

        with pytest.raises(PermissionError, match="strictly forbidden"):
            harness.exec_cmd("echo hello; rm -rf /")

        with pytest.raises(PermissionError, match="strictly forbidden"):
            harness.exec_cmd("echo $(whoami)")

        with pytest.raises(PermissionError, match="strictly forbidden"):
            harness.exec_cmd(["echo", "hello", "|", "rg", "h"])

    def test_explicit_binary_path_forbidden(self, test_env):
        harness, _ = test_env
        with pytest.raises(PermissionError, match="Explicit binary paths forbidden"):
            harness.exec_cmd(["/bin/ls", "."])

        with pytest.raises(PermissionError, match="Explicit binary paths forbidden"):
            harness.exec_cmd(["C:\\Windows\\System32\\cmd.exe", "/c", "dir"])

    def test_output_clipping(self, test_env):
        harness, _ = test_env
        harness.max_chars = 50
        long_text = "a" * 100
        clipped = harness.clip(long_text)
        assert len(clipped) < 100
        assert "Output truncated" in clipped


class TestNetworkSandboxing:
    """Verifies URL scheme restrictions and SSRF defenses."""

    def test_forbidden_url_schemes(self, test_env):
        harness, _ = test_env

        # File scheme
        res = harness.web_fetch("file:///etc/passwd")
        assert "Error: Forbidden URL scheme" in res

        # Gopher / FTP schemes
        res_ftp = harness.web_fetch("ftp://ftp.example.com/test")
        assert "Error: Forbidden URL scheme" in res_ftp

    def test_ssrf_private_ip_blocking(self, test_env):
        harness, _ = test_env

        # Cloud metadata IP
        res_metadata = harness.web_fetch("http://169.254.169.254/latest/meta-data")
        assert "SSRF protection" in res_metadata

        # Localhost loopback IP
        res_loopback = harness.web_fetch("http://127.0.0.1:8000/event")
        assert "SSRF protection" in res_loopback

        # Localhost name
        res_localhost = harness.web_fetch("http://localhost:8080/admin")
        assert "SSRF protection" in res_localhost

        # Private 10.x.x.x network
        res_private = harness.web_fetch("http://10.0.0.1/status")
        assert "SSRF protection" in res_private


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

    def test_sanitized_error_handling(self, test_env):
        harness, tmp_path = test_env
        obs = harness.step("read_file('missing_file.txt')")
        assert "FileNotFoundError" in obs
        # Workspace root absolute path must be redacted
        assert str(tmp_path) not in obs
