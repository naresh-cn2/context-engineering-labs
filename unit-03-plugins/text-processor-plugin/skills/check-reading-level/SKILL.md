---
name: "check-reading-level"
description: "Estimate text reading difficulty and Flesch-Kincaid Grade Level. Use when assessing audience appropriateness, readability, or educational grading."
license: "MIT"
compatibility: "Requires text-processor MCP server"
metadata:
  author: "nares"
  version: "1.0.0"
---

# Check Reading Level Skill

Use the `check_reading_level` tool from the text-processor MCP server to evaluate reading accessibility and grade difficulty.

## When to Use

Use this skill when the user asks:
- "Is this text beginner-friendly?"
- "What is the reading level or grade level of this passage?"
- "How difficult is this documentation to read?"

## How to Use

1. Call `check_reading_level` with the target text.
2. The tool returns:
   - `grade_level`: Numeric Flesch-Kincaid score (e.g. 8.2)
   - `reading_level`: Category ("Elementary School", "Middle School", "High School", "College/Academic")
3. Compare the score against target audience expectations and recommend simplifications if the reading level exceeds user needs.

