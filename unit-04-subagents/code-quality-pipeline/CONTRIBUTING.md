# Contributing to Code Quality Multi-Agent Pipeline

We welcome contributions to add new agent personas, implement additional review topologies, or improve model integrations!

## Development Guidelines

1. **Adding a New Agent Persona**:
   - Create a Claude agent definition under `.claude/agents/<agent-name>.md` with YAML frontmatter.
   - Create a corresponding Codex agent definition under `.codex/agents/<agent-name>.toml`.
   - If the agent is a reviewer or auditor, adhere strictly to the **Principle of Least Privilege**: do not grant `Write` or `Edit` tools.
2. **Adding Orchestration Patterns**:
   - Extend `CodeQualityPipeline` in `pipeline_runner.py`.
   - Maintain compatibility for both `simulated` mode and `live` mode.
3. **Running Tests**:
   - Run the complete unit test suite:
     ```bash
     pytest tests/ -v
     ```
   - All tests must pass before submitting a pull request.
