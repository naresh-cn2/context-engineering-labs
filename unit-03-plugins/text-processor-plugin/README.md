# Text Processor Plugin (`text-processor-plugin`)

Official practical implementation for **Unit 3: Plugins — Bundling for Distribution** of the Hugging Face Context Engineering Course.

## Architecture

This plugin bundles **Agent Skills**, **MCP Server Connectivity**, and an **OpenCode Plugin Module** into a single redistributable unit:

```
text-processor-plugin/
├── .claude-plugin/
│   └── plugin.json             # Manifest for Claude Code & cross-agent registries
├── .codex-plugin/
│   └── plugin.json             # Codex manifest configuration
├── .opencode/
│   └── plugins/
│       └── text-processor-plugin.js # Code-first plugin module for OpenCode
├── .mcp.json                   # MCP server connection spec
├── package.json                # NPM / Git package manifest for OpenCode runtime loading
├── skills/
│   ├── analyze-text/
│   │   └── SKILL.md            # Skill: Text statistics & complexity
│   ├── extract-keywords/
│   │   └── SKILL.md            # Skill: Frequency & topic extraction
│   └── check-reading-level/
│       └── SKILL.md            # Skill: Flesch-Kincaid grade evaluation
├── README.md                   # Plugin documentation
└── tests/
    └── test_plugin.py          # Automated verification test suite
```

## Cross-Platform Distribution

1. **Manifest-first platforms** (Claude Code, Codex):
   - Claude Code discovers `.claude-plugin/plugin.json`.
   - OpenAI Codex discovers `.codex-plugin/plugin.json`.
   - Both load the three bundled Agent Skills from `skills/`.

2. **Code-first platforms** (OpenCode v2.2.6+):
   - OpenCode requires plugins to be packaged as npm or Git package specifiers exporting a default object with `{ id, setup }`.
   - The plugin entrypoint `.opencode/plugins/text-processor-plugin.js` exports:
     ```javascript
     export const TextProcessorPlugin = {
       id: "text-processor-plugin",
       setup: async (ctx) => { ... }
     };
     export default TextProcessorPlugin;
     ```
   - When registered, OpenCode intercepts tool executions and logs lifecycle telemetry.

3. **MCP Provider**:
   - `.mcp.json` references the `text-processor-mcp` server from Unit 2.

## Reproducible Installation in OpenCode

OpenCode v2.2.6 rejects relative directory paths (`opencode plugin add ./folder`) and requires an npm package name or a Git package specifier pointing to a repository containing `package.json`.

### 1. Install via Git Package Specifier
```bash
opencode plugin add git+file://C:/Users/nares/workspace/context-engineering-labs
```

### 2. Configure via opencode.json
Add the plugin specifier to your workspace or global `opencode.json`:
```json
{
  "plugins": [
    "git+file://C:/Users/nares/workspace/context-engineering-labs"
  ]
}
```

### 3. Verify Active Runtime Status
Inspect loaded plugins via the OpenCode API:
```bash
opencode api GET /api/plugin
```

Expected verification output:
```json
{
  "id": "text-processor-plugin",
  "source": {
    "type": "package",
    "target": "git+file://C:/Users/nares/workspace/context-engineering-labs"
  },
  "features": {
    "server": true
  },
  "state": {
    "status": "active"
  }
}
```
