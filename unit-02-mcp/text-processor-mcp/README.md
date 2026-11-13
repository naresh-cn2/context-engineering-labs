# Text Processor MCP Server (`text-processor-mcp`)

Official practical implementation for **Unit 2: Model Context Protocol (MCP)** of the Hugging Face Context Engineering Course.

## Architecture & Capabilities

The server implements the Model Context Protocol (MCP) using the official SDK, exposing text analysis tools over `stdio` for local code agents, as well as a Gradio web application for interactive browser usage.

### Exposed Tools

1. **`analyze_text(text: str) -> str`**:
   Computes word count, character count, sentence count, average word length, average sentence length, and vocabulary uniqueness.
2. **`extract_keywords(text: str, count: int = 5) -> str`**:
   Filters English stopwords and returns the most prominent keywords by frequency.
3. **`check_reading_level(text: str) -> str`**:
   Calculates the Flesch-Kincaid Grade Level and categorizes readability (Elementary, Middle School, High School, College/Academic).
4. **`reverse_text(text: str) -> str`**:
   Reverses the characters in the input string.
5. **`detect_sentiment(text: str) -> str`**:
   Evaluates text polarity score and emotional valence (positive, negative, neutral).

## Project Structure

```
text-processor-mcp/
├── server.py              # FastMCP / MCPServer definition and tool registrations
├── app.py                 # Gradio Web UI with embedded MCP server
├── requirements.txt       # Dependencies: mcp, gradio, pytest
├── README.md              # Architectural documentation
└── tests/
    └── test_text_processor.py # 9 automated unit and registration tests
```

## Running & Testing

### Automated Test Suite
```bash
python -m pytest tests/test_text_processor.py -v
```

### Launch Interactive Web UI
```bash
python app.py
```
Visit `http://localhost:7860` for the Gradio interface.

### OpenCode Integration
Configured in `opencode.json`:
```json
{
  "mcp": {
    "text-processor": {
      "type": "local",
      "command": [
        "path/to/.venv/Scripts/python.exe",
        "path/to/server.py"
      ]
    }
  }
}
```
Status verification:
```bash
opencode mcp list
# Output: ✓ text-processor  connected
```

