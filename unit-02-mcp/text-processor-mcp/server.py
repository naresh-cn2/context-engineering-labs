#!/usr/bin/env python3
"""Text Processor MCP Server.

Implements the Model Context Protocol (MCP) server for text analysis tools,
conforming to Unit 2 of the Hugging Face Context Engineering Course.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List

# Compatibility layer: supports both mcp 2.x (MCPServer) and mcp 1.x (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.fastmcp import FastMCP  # type: ignore

# Common English stopwords for keyword filtering
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "by", "from",
    "that", "this", "it", "as", "if", "not", "i", "you", "he", "she", "we", "they"
}

mcp = FastMCP("text-processor")


@mcp.tool()
def analyze_text(text: str) -> str:
    """Analyze text and compute detailed statistical metrics.

    Args:
        text: The input text to analyze.

    Returns:
        JSON string containing character counts, word counts, sentence counts,
        average word length, average sentence length, and vocabulary uniqueness.
    """
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    sentences = text.count(".") + text.count("!") + text.count("?")

    avg_word_length = round(chars_no_spaces / len(words), 2) if words else 0.0
    avg_sentence_length = round(len(words) / max(sentences, 1), 2)
    unique_words_count = len(set(word.lower() for word in words))

    results = {
        "total_characters": chars,
        "characters_without_spaces": chars_no_spaces,
        "total_words": len(words),
        "total_sentences": max(sentences, 1),
        "average_word_length": avg_word_length,
        "average_sentence_length": avg_sentence_length,
        "unique_words": unique_words_count,
    }
    return json.dumps(results, indent=2)


@mcp.tool()
def extract_keywords(text: str, count: int = 5) -> str:
    """Extract prominent keywords by frequency from the input text, omitting stopwords.

    Args:
        text: The input text to extract keywords from.
        count: Maximum number of top keywords to return (default: 5).

    Returns:
        JSON string containing list of keyword objects with their frequencies.
    """
    words = text.lower().split()
    filtered = [w.strip(".,!?;:\"'()[]{}") for w in words if w.strip(".,!?;:\"'()[]{}") and w.lower() not in STOPWORDS]

    word_freq = Counter(filtered)
    top_words = word_freq.most_common(count)

    results = {
        "keywords": [{"word": w, "frequency": f} for w, f in top_words]
    }
    return json.dumps(results, indent=2)


@mcp.tool()
def check_reading_level(text: str) -> str:
    """Estimate the reading difficulty level and Flesch-Kincaid Grade Level.

    Args:
        text: The input text to evaluate.

    Returns:
        JSON string containing estimated grade level score and categorical reading level.
    """
    words = len(text.split())
    if words == 0:
        return json.dumps({"error": "No text provided to analyze"}, indent=2)

    sentences = max(text.count(".") + text.count("!") + text.count("?"), 1)
    vowels = "aeiou"
    syllables = sum(1 for c in text.lower() if c in vowels)

    # Flesch-Kincaid Grade Level formula
    grade = (0.39 * (words / sentences)) + (11.8 * (syllables / words)) - 15.59
    grade = max(0.0, round(grade, 1))

    if grade < 6:
        level = "Elementary School"
    elif grade < 9:
        level = "Middle School"
    elif grade < 13:
        level = "High School"
    else:
        level = "College/Academic"

    results = {
        "grade_level": grade,
        "reading_level": level,
        "word_count": words,
        "sentence_count": sentences,
    }
    return json.dumps(results, indent=2)


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse the characters in the given string.

    Args:
        text: The input text.

    Returns:
        Reversed string.
    """
    return text[::-1]


@mcp.tool()
def detect_sentiment(text: str) -> str:
    """Analyze basic emotional sentiment polarity of the text.

    Args:
        text: The input text.

    Returns:
        JSON string with detected sentiment (positive, negative, neutral) and score.
    """
    positive_words = {"good", "great", "excellent", "awesome", "fantastic", "clean", "reliable", "best", "fast", "love"}
    negative_words = {"bad", "terrible", "poor", "broken", "slow", "defect", "error", "fail", "hate", "issue"}

    words = [w.strip(".,!?;:\"'").lower() for w in text.split()]
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)

    if pos_count > neg_count:
        sentiment = "positive"
        score = round(pos_count / max(len(words), 1), 2)
    elif neg_count > pos_count:
        sentiment = "negative"
        score = round(-neg_count / max(len(words), 1), 2)
    else:
        sentiment = "neutral"
        score = 0.0

    return json.dumps({
        "sentiment": sentiment,
        "score": score,
        "positive_indicators": pos_count,
        "negative_indicators": neg_count
    }, indent=2)


if __name__ == "__main__":
    mcp.run()

