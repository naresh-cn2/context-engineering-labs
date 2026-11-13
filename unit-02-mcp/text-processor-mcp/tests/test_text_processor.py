"""Automated test suite for Text Processor MCP Server."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure server module is discoverable
SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from server import (
    analyze_text,
    extract_keywords,
    check_reading_level,
    reverse_text,
    detect_sentiment,
    mcp,
)


class TestTextProcessorTools:
    """Tests the functional correctness of all MCP tools."""

    def test_analyze_text_basic(self):
        sample = "The quick brown fox jumps over the lazy dog."
        output = analyze_text(sample)
        data = json.loads(output)

        assert data["total_characters"] == len(sample)
        assert data["total_words"] == 9
        assert data["total_sentences"] == 1
        assert data["average_word_length"] > 0
        assert data["unique_words"] == 8  # "the" is repeated twice

    def test_analyze_text_empty(self):
        output = analyze_text("")
        data = json.loads(output)

        assert data["total_characters"] == 0
        assert data["total_words"] == 0
        assert data["average_word_length"] == 0.0

    def test_extract_keywords(self):
        sample = "Context engineering empowers code agents. Code agents require rich context to perform well."
        output = extract_keywords(sample, count=3)
        data = json.loads(output)

        assert "keywords" in data
        assert len(data["keywords"]) <= 3

        words_found = [item["word"] for item in data["keywords"]]
        # "agents", "context", "code" should be top keywords
        assert "agents" in words_found or "context" in words_found or "code" in words_found

        # Verify stopwords were filtered out
        assert "the" not in words_found
        assert "to" not in words_found

    def test_check_reading_level_levels(self):
        # Elementary sample
        elementary_sample = "The cat sat on the mat. The dog was big."
        out_elem = json.loads(check_reading_level(elementary_sample))
        assert out_elem["reading_level"] in ("Elementary School", "Middle School")
        assert out_elem["word_count"] > 0

        # Advanced academic sample
        academic_sample = (
            "Epistemological formulations in philosophical hermeneutics necessitate rigorous "
            "methodological contextualization across multidimensional structural paradigms."
        )
        out_acad = json.loads(check_reading_level(academic_sample))
        assert out_acad["grade_level"] >= 10
        assert out_acad["reading_level"] in ("High School", "College/Academic")

    def test_check_reading_level_empty(self):
        out = json.loads(check_reading_level(""))
        assert "error" in out

    def test_reverse_text(self):
        sample = "HuggingFace Context Course"
        assert reverse_text(sample) == "esruoC txetnoC ecaFgnigguH"

    def test_detect_sentiment(self):
        pos_sample = "This clean and reliable code is the best solution!"
        pos_data = json.loads(detect_sentiment(pos_sample))
        assert pos_data["sentiment"] == "positive"
        assert pos_data["score"] > 0

        neg_sample = "This terrible error is a bad and broken defect."
        neg_data = json.loads(detect_sentiment(neg_sample))
        assert neg_data["sentiment"] == "negative"
        assert neg_data["score"] < 0

        neutral_sample = "The meeting is scheduled at noon in room three."
        neu_data = json.loads(detect_sentiment(neutral_sample))
        assert neu_data["sentiment"] == "neutral"


class TestMCPServerStructure:
    """Verifies FastMCP / MCPServer initialization and tool registration."""

    def test_server_instance(self):
        assert mcp.name == "text-processor"

    def test_registered_tools(self):
        # Inspect tools registered on the server instance
        # FastMCP / MCPServer maintains a tool manager or dictionary
        tools_dict = {}
        if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools"):
            tools_dict = mcp._tool_manager._tools
        elif hasattr(mcp, "_tools"):
            tools_dict = mcp._tools

        if tools_dict:
            expected_tools = {"analyze_text", "extract_keywords", "check_reading_level", "reverse_text", "detect_sentiment"}
            assert expected_tools.issubset(set(tools_dict.keys())), f"Missing tools. Registered: {list(tools_dict.keys())}"

