#!/usr/bin/env python3
"""Nano Harness: A Minimal Code-First Autonomous Agent Loop.

Conforms to Unit 6 (Bonus) of the Hugging Face Context Engineering Course.
Demonstrates:
- Code-first interaction (LLM outputs executable Python)
- Tool-boundary sandboxing (path confinement, command allowlists, write flags)
- Context budgeting (hard character limits)
- Step-limited loop with observation reflection
- Extended tools: web_fetch and hf_search
"""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


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

    def safe_path(self, path_str: str | Path) -> Path:
        """Enforces path confinement: all paths must resolve inside workspace."""
        p = (self.workspace / Path(path_str)).resolve()
        if not str(p).startswith(str(self.workspace)):
            raise PermissionError(f"Access denied: path '{path_str}' escapes workspace root.")
        return p

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
            raise NotADirectoryError(f"Not a directory: {p}")
        return sorted([x.name + ("/" if x.is_dir() else "") for x in p.iterdir()])

    def read_file(self, path: str, max_chars: int = 4000) -> str:
        """Reads text from a file with size truncation."""
        p = self.safe_path(path)
        content = p.read_text(encoding="utf-8", errors="replace")
        return self.clip(content, min(max_chars, self.max_chars))

    def write_file(self, path: str, content: str) -> str:
        """Writes content to a file, gated by allow_write flag."""
        if not self.allow_write:
            raise PermissionError("write_file disabled: allow_write is set to False.")
        p = self.safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(content), encoding="utf-8")
        return f"Wrote {len(str(content))} bytes to {path}"

    def exec_cmd(self, args: List[str]) -> str:
        """Executes shell command strictly if executable is in allow_commands."""
        if not args or args[0] not in self.allow_commands:
            raise PermissionError(f"Command '{args[0] if args else ''}' is not permitted by allowlist.")
        proc = subprocess.run(args, capture_output=True, timeout=self.timeout_s, text=True, cwd=self.workspace)
        parts = []
        if proc.stdout:
            parts.append(f"stdout:\n{proc.stdout}")
        if proc.stderr:
            parts.append(f"stderr:\n{proc.stderr}")
        output = "\n\n".join(parts) or f"(exit code {proc.returncode} with no output)"
        return self.clip(output)

    # ---------- Extended Tool Implementations (Unit 6 Hands-On) ----------

    def web_fetch(self, url: str, max_bytes: int = 10000) -> str:
        """Fetches web page content with size limit and timeout."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NanoHarness/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout_s) as response:
                content = response.read(max_bytes + 1)
                truncated = len(content) > max_bytes
                if truncated:
                    content = content[:max_bytes]
                text = content.decode("utf-8", errors="replace")
                return text + ("\n...[truncated]" if truncated else "")
        except urllib.error.URLError as e:
            return f"Error: Failed to fetch {url}: {e}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"

    def hf_search(self, query: str, resource_type: str = "models", limit: int = 5) -> List[Dict[str, Any]] | str:
        """Searches the Hugging Face Hub using public/authenticated API."""
        try:
            url = f"https://huggingface.co/api/{resource_type}?search={query}&limit={limit}"
            headers = {"User-Agent": "NanoHarness/1.0"}
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
                        "description": (item.get("description") or "")[:200]
                    })
                return results
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"

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
        """Executes a single turn of Python code in the sandbox environment."""
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
                obs.append(f"stdout:\n{self.clip(stdout_text)}")
            if stderr_text:
                obs.append(f"stderr:\n{self.clip(stderr_text)}")
            return "\n\n".join(obs) or "Executed successfully (no output)"

        except PermissionError as e:
            return f"Error: PermissionError: {str(e)}"
        except FileNotFoundError as e:
            return f"Error: FileNotFoundError: {str(e)}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"

