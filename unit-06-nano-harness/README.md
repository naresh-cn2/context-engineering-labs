# Nano Harness (`nano_harness`)

Official practical implementation for **Unit 6 (Bonus): Nano Harness — Build Your Own Agent** of the Hugging Face Context Engineering Course.

## Architecture & Principles

`nano_harness` is a minimal, code-first autonomous agent harness demonstrating how code agents function under the hood:

```
[System Prompt + Task]
         │
         ▼
   Call LLM (Deterministic low-temperature output)
         │
         ▼
   Extract Executable Python
         │
         ▼
   Sandboxed Execution Environment
   ├── Path Confinement (safe_path: strictly inside workspace)
   ├── Command Allowlist (allow_commands: only pre-approved shell binaries)
   ├── Write Gating (allow_write flag)
   └── Output Truncation (max_chars buffer management)
         │
         ├─── if final_answer(result) ───► Task Complete!
         │
         └─── Observation / Error ────────► Feeds back into History -> Next Step
```

## Available Tools

- `list_dir(path='.')`: Lists workspace directory contents safely.
- `read_file(path, max_chars=4000)`: Reads file contents with context bounds.
- `write_file(path, content)`: Writes to file only when writes are explicitly enabled.
- `exec_cmd(args)`: Runs allowlisted shell commands.
- `web_fetch(url, max_bytes=10000)`: Fetches web page content with size limit.
- `hf_search(query, resource_type='models', limit=5)`: Searches Hugging Face Hub.
- `final_answer(value)`: Signals task completion.

## Verification

```bash
python -m pytest tests/test_nano_harness.py -v
```

