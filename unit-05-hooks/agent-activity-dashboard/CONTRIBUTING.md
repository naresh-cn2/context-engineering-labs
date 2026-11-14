# Contributing to Agent Activity Dashboard

We welcome contributions to expand telemetry adapters, enhance web visualizations, or add alerting capabilities!

## Development Guidelines

1. **Adding Platform Integrations**:
   - Ensure new hook adapters implement fail-soft design principles: agent execution must never block if the telemetry endpoint is offline.
2. **Backend Enhancements**:
   - Keep `app.py` dependency-minimal (FastAPI, Uvicorn).
   - Maintain the circular memory buffer constraint to prevent memory leaks during long-running tasks.
3. **Testing**:
   - Run the automated test suite:
     ```bash
     pytest tests/ -v
     ```
   - All tests must pass before submitting pull requests.
