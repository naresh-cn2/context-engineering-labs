# Usage Examples & Technical Reference

## 1. Command-Line Interface (CLI) Usage

### Validate a CSV Dataset
```bash
python scripts/validate_dataset.py test_data/clean_sample.csv
```

**Standard Output (JSON):**
```json
{
  "status": "PASS",
  "format": "csv",
  "errors": [],
  "warnings": [],
  "metadata": {
    "filepath": "test_data/clean_sample.csv",
    "rows": 3,
    "columns": ["text", "label", "split"],
    "dtypes": {
      "text": "object",
      "label": "int64",
      "split": "object"
    },
    "memory_mb": 0.001
  }
}
```

### Validate with Custom Required Columns
```bash
python scripts/validate_dataset.py test_data/custom.parquet --required-cols id,prompt,response
```

### Generate Formatted ASCII Report
```bash
python scripts/generate_report.py test_data/clean_sample.csv
```

---

## 2. Programmatic Python API

You can import and integrate `validate_dataset` directly into your training or preprocessing pipelines:

```python
from pathlib import Path
import sys

# Add scripts directory to path if needed
sys.path.insert(0, "scripts")
from validate_dataset import validate_dataset

# Run validation
result = validate_dataset("data/train.csv", required_columns={"text", "label"})

if result["status"] == "FAIL":
    raise ValueError(f"Dataset validation failed: {result['errors']}")
elif result["status"] == "WARNING":
    print(f"Dataset warnings: {result['warnings']}")
else:
    print("Dataset validated successfully!")
```

