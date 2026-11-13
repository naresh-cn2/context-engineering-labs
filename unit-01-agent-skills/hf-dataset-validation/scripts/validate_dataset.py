#!/usr/bin/env python3
"""Automated dataset validation engine for Hugging Face and ML workflows.

Conforms to the Hugging Face Context Engineering Course: Unit 1 Specification.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd


def load_dataset(filepath: str | Path) -> tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
    """Loads a dataset file into a pandas DataFrame based on file extension.

    Returns:
        tuple: (DataFrame or None, detected format, error message if any)
    """
    path = Path(filepath)
    if not path.exists():
        return None, None, f"File not found: {filepath}"

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
            return df, "csv", None
        elif suffix in (".parquet", ".pq"):
            df = pd.read_parquet(path)
            return df, "parquet", None
        elif suffix in (".json", ".jsonl"):
            # Try reading line-delimited first, fallback to standard JSON
            try:
                df = pd.read_json(path, lines=True)
            except Exception:
                df = pd.read_json(path)
            return df, "json", None
        elif suffix == ".arrow":
            import pyarrow as pa
            with open(path, "rb") as f:
                reader = pa.ipc.open_stream(f)
                df = reader.read_all().to_pandas()
            return df, "arrow", None
        else:
            return None, "unsupported", f"Unsupported file extension: '{suffix}'. Supported: .csv, .parquet, .json, .jsonl, .arrow"
    except Exception as e:
        return None, suffix.lstrip("."), f"Failed to parse file: {str(e)}"


def validate_dataset(
    filepath: str | Path,
    required_columns: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Inspects a dataset file for schema conformity, format validity, and data quality issues.

    Args:
        filepath: Path to the dataset file.
        required_columns: Set of column names that must be present. Defaults to {'text', 'label'}.

    Returns:
        dict: Structured evaluation report containing status, errors, warnings, and metadata.
    """
    if required_columns is None:
        required_columns = {"text", "label"}

    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {
        "filepath": str(filepath),
        "rows": 0,
        "columns": [],
        "dtypes": {},
        "memory_mb": 0.0,
    }

    df, file_format, load_error = load_dataset(filepath)

    if load_error:
        errors.append(load_error)
        return {
            "status": "FAIL",
            "format": file_format or "unknown",
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata,
        }

    assert df is not None

    metadata["format"] = file_format
    metadata["rows"] = int(len(df))
    metadata["columns"] = list(df.columns)
    metadata["dtypes"] = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
    metadata["memory_mb"] = round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 3)

    if len(df) == 0:
        errors.append("Dataset contains 0 rows (empty dataset).")

    # Schema Validation
    actual_columns = set(df.columns)
    missing_columns = required_columns - actual_columns
    if missing_columns:
        errors.append(f"Missing required columns: {sorted(list(missing_columns))}")

    # Data Quality: Missing values
    missing_series = df.isna().sum()
    missing_dict = {col: int(count) for col, count in missing_series.items() if count > 0}
    if missing_dict:
        total_missing = sum(missing_dict.values())
        warnings.append(f"Found {total_missing} missing (NaN/null) values across {len(missing_dict)} columns.")
        metadata["missing_values"] = missing_dict

    # Data Quality: Duplicates
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        pct = round((dup_count / len(df)) * 100, 2) if len(df) > 0 else 0
        warnings.append(f"Found {dup_count} duplicate rows ({pct}% of dataset).")
        metadata["duplicate_rows"] = dup_count

    # Data Quality: Empty whitespace strings in text / object columns
    object_cols = df.select_dtypes(include=["object", "string"]).columns
    empty_strings_dict: Dict[str, int] = {}
    for col in object_cols:
        # Check non-null entries that strip to empty
        non_null_mask = df[col].notna()
        empty_count = int((df.loc[non_null_mask, col].astype(str).str.strip() == "").sum())
        if empty_count > 0:
            empty_strings_dict[col] = empty_count

    if empty_strings_dict:
        total_empty = sum(empty_strings_dict.values())
        warnings.append(f"Found {total_empty} empty/whitespace-only strings in columns: {list(empty_strings_dict.keys())}.")
        metadata["empty_strings"] = empty_strings_dict

    status = "FAIL" if errors else ("WARNING" if warnings else "PASS")

    return {
        "status": status,
        "format": file_format,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python validate_dataset.py <filepath> [--required-cols col1,col2...]")
        sys.exit(1)

    filepath = sys.argv[1]
    required_cols: Optional[Set[str]] = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--required-cols":
        required_cols = set(sys.argv[3].split(","))

    report = validate_dataset(filepath, required_columns=required_cols)
    print(json.dumps(report, indent=2))

    if report["errors"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

