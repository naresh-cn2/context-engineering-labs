#!/usr/bin/env python3
"""Generate human-readable dataset quality reports.

Conforms to the Hugging Face Context Engineering Course: Unit 1 Specification.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Set

import pandas as pd

# Allow relative import of validate_dataset from same scripts folder
sys.path.insert(0, str(Path(__file__).parent))
from validate_dataset import validate_dataset


def generate_report(filepath: str | Path, required_columns: Optional[Set[str]] = None) -> str:
    """Generates an ASCII-formatted validation report summarizing dataset health.

    Args:
        filepath: Path to dataset file.
        required_columns: Expected columns.

    Returns:
        str: Formatted report text.
    """
    res = validate_dataset(filepath, required_columns=required_columns)
    meta = res["metadata"]

    lines = []
    lines.append("=" * 68)
    lines.append("          HUGGING FACE DATASET VALIDATION REPORT")
    lines.append("=" * 68)
    lines.append(f"Target File:      {filepath}")
    lines.append(f"Detected Format:  {res.get('format', 'unknown').upper()}")
    lines.append(f"Overall Status:   {res['status']}")
    lines.append("-" * 68)

    if res["errors"]:
        lines.append("CRITICAL BLOCKING ERRORS:")
        for err in res["errors"]:
            lines.append(f"  [X] {err}")
        lines.append("-" * 68)

    # Basic stats
    lines.append("DATASET DIMENSIONS & MEMORY:")
    lines.append(f"  Total Rows:     {meta.get('rows', 0):,}")
    lines.append(f"  Total Columns:  {len(meta.get('columns', []))}")
    lines.append(f"  Memory Footprint: {meta.get('memory_mb', 0.0):.3f} MB")
    lines.append("")

    # Columns
    dtypes = meta.get("dtypes", {})
    if dtypes:
        lines.append("COLUMN SCHEMA SPECIFICATION:")
        for col, dtype in dtypes.items():
            lines.append(f"  - {col:<24} {dtype}")
        lines.append("")

    # Data Quality
    lines.append("DATA QUALITY DIAGNOSTICS:")
    if res["warnings"]:
        for warn in res["warnings"]:
            lines.append(f"  [!] {warn}")
    else:
        lines.append("  [OK] No duplicate rows, missing values, or empty strings detected.")
    lines.append("")

    # Recommendations
    lines.append("REMEDIATION RECOMMENDATIONS:")
    if res["status"] == "FAIL":
        lines.append("  1. Resolve critical blocking errors before publishing or training.")
        if any("Missing required columns" in e for e in res["errors"]):
            lines.append("     - Ensure standard Hugging Face columns ('text', 'label') are present.")
    elif res["status"] == "WARNING":
        lines.append("  1. Review flagged warnings. Consider running deduplication or imputation.")
        lines.append("  2. Add a comprehensive dataset card (`README.md`) detailing splits and source.")
        lines.append("  3. Specify an open license (e.g., MIT, Apache-2.0, CC-BY-4.0).")
    else:
        lines.append("  1. Dataset passes all checks. Ready for Hugging Face Hub upload or training pipeline.")
        lines.append("  2. Pair with a complete README.md / dataset card metadata header.")

    lines.append("=" * 68)
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    report_text = generate_report(filepath)
    print(report_text)


if __name__ == "__main__":
    main()

