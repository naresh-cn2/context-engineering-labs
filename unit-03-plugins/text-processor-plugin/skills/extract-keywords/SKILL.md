---
name: "extract-keywords"
description: "Extract the most important words and topics from text based on frequency analysis. Use when finding keywords, summarizing key topics, or indexing documents."
license: "MIT"
compatibility: "Requires text-processor MCP server"
metadata:
  author: "nares"
  version: "1.0.0"
---

# Extract Keywords Skill

Use the `extract_keywords` tool from the text-processor MCP server to discover high-frequency domain keywords.

## When to Use

Use this skill when the user asks for:
- Main keywords, key phrases, or salient terms
- Topic extraction or thematic overview
- Content tagging or summarization keywords

## How to Use

1. Call the `extract_keywords` tool with the text and optional `count` (default: 5).
2. The tool removes standard English stopwords and returns:
   - `keywords`: Array of `{ "word": <string>, "frequency": <int> }`
3. Group related keywords into themes and present them clearly to the user with supporting frequencies.

