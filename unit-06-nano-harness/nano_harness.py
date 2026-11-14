#!/usr/bin/env python3
"""Nano Harness: A Hardened Code-First Autonomous Agent Sandbox.

Conforms to Unit 6 (Bonus) of the Hugging Face Context Engineering Course.
Demonstrates:
- Code-first interaction (LLM outputs executable Python)
- Multi-layer tool sandboxing:
  * Strict path confinement with symlink and traversal protection
  * Hardened command execution with allowlisting and shell injection defense
  * Write gating with protection for sensitive project files
  * Web fetching with protocol filtering and SSRF/private IP protection
  * Context budgeting (hard character limits)
  * Sanitized error handling preventing host path leakage
- Step-limited loop with observation reflection
- Extended tools: web_fetch and hf_search
"""

from __future__ import annotations

import io
import ipaddress
import json
import os
import re
import shlex
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

# Restricted file and directory patterns forbidden from writes
RESTRICTED_WRITE_PATTERNS = {".git", ".env", ".ssh", ".gnupg", "id_rsa"}

# Shell metacharacters forbidden in exec_cmd arguments
FORBIDDEN_SHELL_CHARS = {";", "&&", "||", "|", ">", "<", "`", "$(", "${", "\n", "\r"}


class NanoHarness:
    def __init__(
        self,
        workspace: str | Path,
        model: str = "zai-org/GLM-5.1",
        allow_write: bool = False,
        allow_commands: Optional[List[str]] = None,
        max_chars: int = 8000,
        timeout_s: int = 30,
        max_steps: int = 50,
        api_key: Optional[str] = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.model = model
        self.allow_write = allow_write
        self.allow_commands = allow_commands or ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]
        self.max_chars = max_chars
        self.timeout_s = timeout_s
        self.max_steps = max_steps
        self.api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "")

        self.done = False
        self.final_result: Any = None
        self.messages: List[Dict[str, str]] = []

    def sanitize_error(self, message: str) -> str:
        """Sanitizes error messages to prevent internal host path or username leakage."""
        clean = str(message).replace(str(self.workspace), "<workspace>")
        home = str(Path.home())
        if home:
            clean = clean.replace(home, "<home>")
        return clean

    def safe_path(self, path_str: str | Path) -> Path:
        """Enforces strict path confinement within workspace root.

        Defends against:
        - Relative traversals (../ and ..\\)
        - Absolute path escapes
        - URL-encoded path traversal sequences (%2e%2e)
        - Null byte injection
        - Symlink traversal escapes
        """
        raw = str(path_str)
        if "\0" in raw:
            raise PermissionError("Access denied: null byte in path.")

        # Decode any percent-encoded characters
        decoded = urllib.parse.unquote(raw)

        candidate = Path(decoded)
        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (self.workspace / candidate).resolve()

        # Enforce strict relative containment
        try:
            resolved.relative_to(self.workspace)
        except ValueError:
            raise PermissionError(f"Access denied: path '{path_str}' escapes workspace root.")

        # If path exists as a symlink, verify symlink target is also contained
        try:
            if candidate.is_symlink():
                target = candidate.resolve()
                target.relative_to(self.workspace)
        except (ValueError, OSError):
            raise PermissionError(f"Access denied: symlink '{path_str}' points outside workspace.")

        return resolved

    def clip(self, text: Any, limit: Optional[int] = None) -> str:
        """Truncates text to prevent context overflow."""
        s = "" if text is None else str(text)
        cap = limit or self.max_chars
        if len(s) > cap:
            return s[:cap] + f"\n... [Output truncated to {cap} characters]"
        return s

    # ---------- Core Tool Implementations ----------

    def list_dir(self, path: str = ".") -> List[str]:
        """Lists directory contents safely within workspace."""
        p = self.safe_path(path)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.sanitize_error(str(p))}")
        return sorted([x.name + ("/" if x.is_dir() else "") for x in p.iterdir()])

    def read_file(self, path: str, max_chars: int = 4000) -> str:
        """Reads text from a file with size truncation."""
        p = self.safe_path(path)
        content = p.read_text(encoding="utf-8", errors="replace")
        return self.clip(content, min(max_chars, self.max_chars))

    def write_file(self, path: str, content: str) -> str:
        """Writes content to a file, gated by allow_write flag and file restrictions."""
        if not self.allow_write:
            raise PermissionError("write_file disabled: allow_write is set to False.")

        p = self.safe_path(path)

        # Check for sensitive file restrictions
        for part in p.parts:
            if part in RESTRICTED_WRITE_PATTERNS or part.startswith(".git"):
                raise PermissionError(f"Access denied: mutating restricted path part '{part}' is forbidden.")

        # Check write permissions on existing read-only file
        if p.exists() and not os.access(p, os.W_OK):
            raise PermissionError(f"Access denied: file '{p.name}' is read-only.")

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(content), encoding="utf-8")
        return f"Wrote {len(str(content))} bytes to {path}"

    def exec_cmd(self, args: List[str] | str) -> str:
        """Executes shell command with strict allowlisting and injection defense."""
        if isinstance(args, str):
            cmd_list = shlex.split(args)
        elif isinstance(args, list):
            cmd_list = args
        else:
            raise TypeError("exec_cmd expects a list of strings or command string.")

        if not cmd_list:
            raise PermissionError("Command is empty.")

        binary = cmd_list[0]

        # Prevent directory traversal in binary path (e.g. /bin/sh or ../../cmd.exe)
        binary_base = Path(binary).name
        if "/" in binary or "\\" in binary:
            raise PermissionError(f"Explicit binary paths forbidden. Use allowed command name directly: {binary}")

        if binary_base not in self.allow_commands:
            raise PermissionError(f"Command '{binary_base}' is not permitted by allowlist.")

        # Defense against shell chaining and injection inside argument strings
        full_line = " ".join(cmd_list)
        for char in FORBIDDEN_SHELL_CHARS:
            if char in full_line:
                raise PermissionError(f"Command chaining or shell metacharacter '{char}' is strictly forbidden.")

        proc = subprocess.run(
            cmd_list,
            shell=False,
            capture_output=True,
            timeout=self.timeout_s,
            text=True,
            cwd=self.workspace,
        )
        parts = []
        if proc.stdout:
            parts.append(f"stdout:\n{proc.stdout}")
        if proc.stderr:
            parts.append(f"stderr:\n{proc.stderr}")
        output = "\n\n".join(parts) or f"(exit code {proc.returncode} with no output)"
        return self.clip(self.sanitize_error(output))

    # ---------- Extended Tool Implementations (SSRF Protection) ----------

    def _is_private_or_restricted_host(self, hostname: str) -> bool:
        """Evaluates whether a host is private, loopback, or cloud metadata."""
        if not hostname:
            return True

        lower_host = hostname.lower()
        if lower_host in {"localhost", "127.0.0.1", "::1", "metadata.google.internal"}:
            return True

        # Check IP literal or resolve DNS
        try:
            ip = ipaddress.ip_address(hostname)
            return (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            )
        except ValueError:
            pass

        # Resolve hostname to check underlying IP
        try:
            addrs = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addrs:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if (
                    ip.is_private
                    or ip.is_loopback
                    or ip.is_link_local
                    or ip.is_reserved
                    or ip.is_multicast
                ):
                    return True
        except Exception:
            return False

        return False

    def web_fetch(self, url: str, max_bytes: int = 10000) -> str:
        """Fetches web page content with scheme restrictions, SSRF defense, and size limits."""
        parsed = urllib.parse.urlparse(url)

        # Enforce scheme: only http and https allowed
        if parsed.scheme.lower() not in {"http", "https"}:
            return f"Error: Forbidden URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname or ""
        if self._is_private_or_restricted_host(hostname):
            return f"Error: SSRF protection: URL targets restricted or private host '{hostname}'."

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NanoHarness/2.0"})
            with urllib.request.urlopen(req, timeout=self.timeout_s) as response:
                content = response.read(max_bytes + 1)
                truncated = len(content) > max_bytes
                if truncated:
                    content = content[:max_bytes]
                text = content.decode("utf-8", errors="replace")
                return text + ("\n...[truncated]" if truncated else "")
        except urllib.error.URLError as e:
            return f"Error: Failed to fetch URL: {self.sanitize_error(str(e))}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {self.sanitize_error(str(e))}"

    def hf_search(self, query: str, resource_type: str = "models", limit: int = 5) -> List[Dict[str, Any]] | str:
        """Searches the Hugging Face Hub using public/authenticated API."""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://huggingface.co/api/{resource_type}?search={encoded_query}&limit={limit}"
            headers = {"User-Agent": "NanoHarness/2.0"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout_s) as response:
                data = json.loads(response.read().decode("utf-8"))
                results = []
                for item in data[:limit]:
                    results.append({
                        "id": item.get("id"),
                        "downloads": item.get("downloads", 0),
                        "description": (item.get("description") or "")[:200],
                    })
                return results
        except Exception as e:
            return f"Error: {type(e).__name__}: {self.sanitize_error(str(e))}"

    def final_answer(self, value: Any) -> Any:
        """Signals task completion."""
        self.done = True
        self.final_result = value
        return value

    # ---------- Execution & Parser Logic ----------

    @staticmethod
    def extract_python(content: str) -> str:
        """Extracts executable python from markdown fences or raw code."""
        fenced = re.search(r"```(?:python)?\s*\n(.*?)\n```", content, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()
        return content.strip()

    def step(self, code_str: str) -> str:
        """Executes a single turn of Python code in the sandboxed namespace."""
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        exec_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
            },
            "list_dir": self.list_dir,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "exec_cmd": self.exec_cmd,
            "web_fetch": self.web_fetch,
            "hf_search": self.hf_search,
            "final_answer": self.final_answer,
        }

        try:
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                exec(code_str, exec_globals)

            stdout_text = stdout_buf.getvalue().strip()
            stderr_text = stderr_buf.getvalue().strip()

            if self.done:
                return f"Final answer: {self.clip(self.final_result)}"

            obs = []
            if stdout_text:
                obs.append(f"stdout:\n{self.clip(self.sanitize_error(stdout_text))}")
            if stderr_text:
                obs.append(f"stderr:\n{self.clip(self.sanitize_error(stderr_text))}")
            return "\n\n".join(obs) or "Executed successfully (no output)"

        except PermissionError as e:
            return f"Error: PermissionError: {self.sanitize_error(str(e))}"
        except FileNotFoundError as e:
            return f"Error: FileNotFoundError: {self.sanitize_error(str(e))}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {self.sanitize_error(str(e))}"
