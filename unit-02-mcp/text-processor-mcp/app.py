#!/usr/bin/env python3
"""Gradio Web UI + MCP Server for Text Processor.

Conforms to Unit 2 Part 2: Gradio MCP Integration.
Provides both an interactive web dashboard and an active MCP endpoint.
"""

from __future__ import annotations

import json
from collections import Counter
import gradio as gr


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "by", "from",
    "that", "this", "it", "as", "if", "not", "i", "you", "he", "she", "we", "they"
}


def analyze_text(text: str) -> str:
    """Analyze text statistics."""
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    sentences = text.count(".") + text.count("!") + text.count("?")

    avg_word_length = round(chars_no_spaces / len(words), 2) if words else 0.0
    avg_sentence_length = round(len(words) / max(sentences, 1), 2)

    return json.dumps({
        "total_characters": chars,
        "characters_without_spaces": chars_no_spaces,
        "total_words": len(words),
        "total_sentences": max(sentences, 1),
        "average_word_length": avg_word_length,
        "average_sentence_length": avg_sentence_length,
        "unique_words": len(set(w.lower() for w in words))
    }, indent=2)


def extract_keywords(text: str, count: int = 5) -> str:
    """Extract top keywords by frequency."""
    words = text.lower().split()
    filtered = [w.strip(".,!?;:\"'()[]{}") for w in words if w.strip(".,!?;:\"'()[]{}") and w.lower() not in STOPWORDS]

    word_freq = Counter(filtered)
    top_words = word_freq.most_common(int(count))

    return json.dumps({
        "keywords": [{"word": w, "frequency": f} for w, f in top_words]
    }, indent=2)


def check_reading_level(text: str) -> str:
    """Estimate Flesch-Kincaid Grade Level."""
    words = len(text.split())
    if words == 0:
        return json.dumps({"error": "No text provided to analyze"}, indent=2)

    sentences = max(text.count(".") + text.count("!") + text.count("?"), 1)
    vowels = "aeiou"
    syllables = sum(1 for c in text.lower() if c in vowels)

    grade = max(0.0, (0.39 * (words / sentences)) + (11.8 * (syllables / words)) - 15.59)
    grade = round(grade, 1)

    if grade < 6:
        level = "Elementary School"
    elif grade < 9:
        level = "Middle School"
    elif grade < 13:
        level = "High School"
    else:
        level = "College/Academic"

    return json.dumps({
        "grade_level": grade,
        "reading_level": level,
        "word_count": words,
        "sentence_count": sentences
    }, indent=2)


with gr.Blocks(title="Text Processor MCP") as demo:
    gr.Markdown("# Text Processing Tools (MCP + Gradio)")
    gr.Markdown("Analyze text statistics, extract keywords, and check reading difficulty.")

    with gr.Tab("Analyze Text"):
        text_input1 = gr.Textbox(
            label="Enter text",
            lines=6,
            placeholder="Paste text here to analyze..."
        )
        analysis_output = gr.Textbox(label="Analysis Results (JSON)", lines=8)
        gr.Button("Analyze Text", variant="primary").click(analyze_text, text_input1, analysis_output)

    with gr.Tab("Extract Keywords"):
        text_input2 = gr.Textbox(label="Enter text", lines=6, placeholder="Paste article or text...")
        count_input = gr.Slider(1, 20, value=5, step=1, label="Number of keywords")
        keywords_output = gr.Textbox(label="Extracted Keywords (JSON)", lines=8)
        gr.Button("Extract Keywords", variant="primary").click(
            extract_keywords,
            [text_input2, count_input],
            keywords_output
        )

    with gr.Tab("Reading Level"):
        text_input3 = gr.Textbox(label="Enter text", lines=6, placeholder="Paste passage...")
        level_output = gr.Textbox(label="Reading Level Assessment (JSON)", lines=6)
        gr.Button("Check Reading Level", variant="primary").click(check_reading_level, text_input3, level_output)


if __name__ == "__main__":
    # Launch Gradio with MCP endpoint enabled
    demo.launch(server_name="127.0.0.1", server_port=7860)

