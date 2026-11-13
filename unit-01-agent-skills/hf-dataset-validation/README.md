# Hugging Face Dataset Validation Skill (`hf-dataset-validation`)

Compliant implementation for **Unit 1: Agent Skills** of the Hugging Face Context Engineering Course, built strictly according to the **[Agent Skills Specification](https://agentskills.io)**.

## Architecture

```
hf-dataset-validation/
├── SKILL.md                          # Standardized specification frontmatter + instructions
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Python & test artifact rules
├── README.md                         # Architecture & usage documentation
├── scripts/
│   ├── validate_dataset.py           # Core validation engine (JSON output & CLI exit codes)
│   └── generate_report.py            # Formatted human-readable report generator
├── references/
│   └── examples.md                   # CLI & Python programmatic reference
├── assets/
│   └── validation-template.txt       # Report layout template
├── test_data/
│   ├── clean_sample.csv              # Valid baseline dataset
│   ├── flawed_sample.csv             # Dataset with nulls, duplicates, empty strings
│   ├── invalid_schema.csv            # Missing required columns
│   └── sample.json                   # Valid JSON format dataset
└── tests/
    └── test_validation.py            # Automated pytest test suite
```

## Features

1. **Multi-Format Parsing**: Automatically identifies and reads CSV, Parquet, JSON, and Arrow datasets.
2. **Schema Enforcement**: Validates required columns (defaulting to `text` and `label`) and reports missing columns as critical errors.
3. **Data Quality Diagnostics**: Identifies null/missing values, duplicate rows, and whitespace-only strings.
4. **Agent Integration**: Standardized frontmatter enables progressive disclosure in OpenCode, Claude Code, and Codex.
5. **Dual Output Modalities**: Structured machine-readable JSON for automated pipelines and clean ASCII reports for human inspection.

## Verification & Testing

To run the full automated verification test suite:
```bash
python -m pytest tests/test_validation.py -v
```

