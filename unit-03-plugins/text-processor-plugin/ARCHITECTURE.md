# Architecture & Technical Design: Text Processor Plugin

## Overview

Text Processor Plugin is a cross-agent plugin distribution unifying Agent Skills, Model Context Protocol (MCP) server bindings, and runtime lifecycle hooks.

```mermaid
flowchart TD
    subgraph Package["Plugin Distribution Package"]
        ManifestClaude[".claude-plugin/plugin.json"]
        ManifestCodex[".codex-plugin/plugin.json"]
        Pkg[package.json]
        MCP[".mcp.json"]
        Skills["skills/* (analyze-text, extract-keywords, check-reading-level)"]
        Hook[".opencode/plugins/text-processor-plugin.js"]
    end

    subgraph Runtimes["Supported Agent Harnesses"]
        OC["OpenCode v2.2.6+"]
        CC["Claude Code"]
        CX["Codex CLI"]
    end

    OC -->|Reads| Pkg
    OC -->|Loads| Hook
    OC -->|Discovers| Skills
    CC -->|Reads| ManifestClaude
    CC -->|Discovers| Skills
    CX -->|Reads| ManifestCodex
    CX -->|Discovers| Skills
    OC & CC & CX -->|Configures| MCP
```

## Directory Structure Specification

- `.claude-plugin/plugin.json`: Standard metadata file for Anthropic Claude Code plugin discovery.
- `.codex-plugin/plugin.json`: Metadata and skill manifest for OpenAI Codex CLI environments.
- `package.json`: Node.js ES module declaration exposing the plugin setup entrypoint.
- `.mcp.json`: Auto-configuration file declaring the `text-processor` MCP server.
- `skills/`: Standard agent skills following the open Agent Skills specification (YAML frontmatter + Markdown instructions).
- `.opencode/plugins/text-processor-plugin.js`: Code-first hook export returning `{ id, setup }`.

## Runtime Hook Lifecycle

The JavaScript plugin module implements OpenCode's plugin API:
```javascript
export const TextProcessorPlugin = {
  id: "text-processor-plugin",
  setup: async (ctx) => {
    // 1. Log initialization
    // 2. Register custom command /text-stats
    // 3. Return lifecycle listeners ("tool.execute.before")
  }
};
```
