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
- **Manifest-first platforms** (Claude Code, Codex): Discover `plugin.json` and load skills from `skills/`.
- **Code-first platforms** (OpenCode): Discover lifecycle hooks from `.opencode/plugins/`.
- **MCP Provider**: References the `text-processor-mcp` server from Unit 2.

