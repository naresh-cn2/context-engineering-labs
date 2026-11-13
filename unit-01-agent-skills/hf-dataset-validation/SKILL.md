---
name: "hf-dataset-validation"
description: "Validate Hugging Face datasets for schema conformity, formats (CSV, Parquet, JSON, Arrow), and data quality defects. Use when validating, inspecting, or checking datasets before model training, publishing, or sharing."
license: "MIT"
compatibility: "Python 3.8+, requires pandas, datasets, pyarrow"
metadata:
  author: "nares"
  version: "1.0.0"
  created: "2026-11-13"
  framework: "Agent Skills Specification v1"
allowed-tools: "Python(scripts/*) Bash(python:*)"
---

# Hugging Face Dataset Validation Skill

## Overview

This skill provides an automated, rigorous validation pipeline for datasets destined for the Hugging Face Hub or machine learning workflows. It empowers agents to inspect and verify:
- **Format Compliance**: Support for CSV, Parquet, JSON, and Arrow formats.
- **Schema Conformity**: Verification of required columns (`text`, `label`, `split`), column counts, and consistent data types.
- **Data Quality Assurance**: Detection of missing values (`null`/`NaN`), full-row duplicates, whitespace-only empty strings, and outlier distribution.
- **Resource Footprint**: Row counts, column counts, and memory usage profiling.

## Prerequisites Checklist

- [x] Python 3.8+ runtime accessible
- [x] Dependencies installed: `pandas>=1.3.0`, `datasets>=2.0.0`, `numpy>=1.20.0`, `pyarrow>=14.0.0`
- [x] Target dataset file available locally

## Step-by-Step Execution Guide

### 1. Identify File Format
Inspect the file extension to route to the correct parsing engine:
```bash
python scripts/validate_dataset.py <path/to/dataset_file>
```

Supported extensions: `.csv`, `.parquet`, `.json`, `.jsonl`, `.arrow`.

### 2. Run Automated Quality Checks
The validation script returns a structured JSON evaluation:
- `status`: `"PASS"`, `"WARNING"`, or `"FAIL"`
- `errors`: Critical issues that halt publication (missing file, invalid schema, unparseable format, empty dataset)
- `warnings`: Data quality defects (duplicate records, missing values, empty strings)
- `metadata`: Exact counts of rows, columns, data types, memory footprint, and quality counts

Exit code policy:
- `0`: Dataset is valid or has non-blocking quality warnings.
- `1`: Blocking errors detected (missing file or invalid schema).

### 3. Generate Human-Readable Validation Report
To produce an ASCII summary report suitable for inclusion in dataset cards and documentation:
```bash
python scripts/generate_report.py <path/to/dataset_file>
```

### 4. Remediation Guidelines
- **Missing Required Columns**: Add missing columns (e.g. `split` default to `"train"`, `label` mapped to integer or categorical string).
- **Duplicate Rows**: Deduplicate rows using `df.drop_duplicates()`.
- **Empty Strings**: Clean object columns with `df[col] = df[col].replace(r'^\s*$', None, regex=True)` and decide on imputation or dropping.
- **Missing Values**: Impute or drop based on split integrity.

## Supporting Resources

- [Usage Examples & Code Reference](references/examples.md)
- [Validation Report Template](assets/validation-template.txt)
- [Validation Engine Implementation](scripts/validate_dataset.py)
- [Report Generator Implementation](scripts/generate_report.py)

