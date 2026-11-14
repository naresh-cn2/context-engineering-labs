# Contributing to Text Processor MCP

Thank you for your interest in contributing to Text Processor MCP!

## Development Guidelines

1. **Python Environment**: Python 3.10+ is required. Recommended: 3.12.
2. **Virtual Environment**:
   ```bash
   cd course-workspace/unit2-mcp/text-processor-mcp
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Adding New Tools**:
   - Register new functions in `server/text_processor_server.py` using `@mcp.tool()`.
   - Provide explicit type annotations and docstrings for automatic JSON schema generation.
   - Maintain pure Python or lightweight dependencies to keep cold start latency minimal.
4. **Testing**:
   - Add unit tests in `tests/test_server.py`.
   - Run tests:
     ```bash
     pytest tests/ -v
     ```
5. **Code Style**:
   - Follow PEP 8 standards and ensure logging only writes to `sys.stderr` to avoid corrupting `stdio` JSON-RPC frames.
