# Contributing to Text Processor Plugin

We welcome contributions to expand skills, enhance hooks, or support additional agent runtimes!

## Development Guidelines

1. **Adding a Skill**:
   - Create a subfolder under `skills/<skill-name>/`.
   - Add `SKILL.md` with YAML frontmatter (`name` matching folder, `description` concise and imperative).
   - Update `.codex-plugin/plugin.json` to include the new skill name.
2. **Hook Modifications**:
   - Edit `.opencode/plugins/text-processor-plugin.js`.
   - Ensure all calls to `ctx` methods are defensive with optional chaining (`?.`).
3. **Testing**:
   - Run the automated test suite:
     ```bash
     pytest tests/ -v
     ```
   - Ensure all tests pass before submitting changes.
