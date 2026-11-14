# Contributing to HF Dataset Validation Skill

Contributions to improve dataset parsing performance, add quality metrics, or support additional serialization formats are welcome!

## Development Setup

1. Clone or navigate to the repository:
   ```bash
   cd course-workspace/unit1-skills/hf-dataset-validation
   ```
2. Activate your virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Code Guidelines

- Adhere to PEP 8 standards with type annotations on all function signatures.
- Keep CLI argument parsing in `scripts/validate_dataset.py` compatible with standard Unix flags.
- Do not add third-party dependencies unless strictly required.
- Maintain 100% backward compatibility with the `SKILL.md` specification.

## Running Tests

Before submitting changes, ensure all tests pass:
```bash
python -m pytest tests/test_validation.py -v
```
