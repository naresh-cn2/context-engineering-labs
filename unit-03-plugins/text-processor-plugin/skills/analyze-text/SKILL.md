---
name: "analyze-text"
description: "Analyze text statistics including character count, word count, sentence count, average lengths, and unique vocabulary. Use when evaluating prose complexity or computing text metrics."
license: "MIT"
compatibility: "Requires text-processor MCP server"
metadata:
  author: "nares"
  version: "1.0.0"
---

# Analyze Text Skill

Use the `analyze_text` tool from the text-processor MCP server to compute comprehensive text statistics.

## When to Use

Use this skill when the user asks about:
- Text statistics, character counts, or word counts
- Sentence counts and average word or sentence length
- Vocabulary diversity and readability metrics

## How to Use

1. Call the `analyze_text` tool passing the complete target text as input.
2. The tool returns a JSON object with:
   - `total_characters`: Full character length
   - `characters_without_spaces`: Length excluding whitespace
   - `total_words`: Word count
   - `total_sentences`: Sentence count
   - `average_word_length`: Mean characters per word
   - `average_sentence_length`: Mean words per sentence
   - `unique_words`: Number of distinct vocabulary terms
3. Interpret the metrics in clear prose:
   - High unique word ratio denotes rich, diverse vocabulary.
   - Long average sentence length denotes syntactically complex prose.

