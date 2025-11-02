# Functions Demo

This demo showcases the ODIBI CORE functions module with realistic data cleaning and transformation workflows.

## Quick Start

```bash
# 1. Generate synthetic data
python generate_data.py

# 2. Run demo pipeline (Pandas + Spark)
python demo_pipeline.py
```

## Datasets

- **users.csv** (100 rows) - User profiles with demographics
- **orders.csv** (200 rows) - Order transactions
- **messy_data.csv** (50 rows) - Intentionally messy data for cleaning
- **timeseries.csv** (100 rows) - Time series with trend and seasonality

## Demo Pipeline

The demo pipeline demonstrates:

1. **Data Quality** - Initial validation and reporting
2. **String Cleaning** - Standardize names, trim whitespace, case conversion
3. **Type Conversion** - Boolean coercion, datetime parsing, numeric casting
4. **Null Handling** - Normalize null representations, fill missing values
5. **Date Features** - Extract year, month, day
6. **Mathematical Operations** - Z-scores, min-max normalization
7. **Metadata Tracking** - Add run IDs and timestamps
8. **Validation** - Final quality checks
9. **Parity Verification** - Compare Pandas vs Spark results

## Functions Showcased

### data_ops
- `safe_join()` - Graceful joins with schema handling
- `filter_rows()` - SQL-style filtering
- `group_and_aggregate()` - Unified aggregations

### string_utils
- `standardize_column_names()` - snake_case, camelCase, etc.
- `trim_whitespace()` - Remove leading/trailing spaces
- `to_lowercase()` - Case conversion

### conversion_utils
- `to_boolean()` - Flexible boolean coercion
- `to_numeric()` - Safe numeric conversion
- `normalize_nulls()` - Handle various null representations

### datetime_utils
- `to_datetime()` - Parse date strings
- `extract_date_parts()` - Extract year/month/day
- `date_diff()` - Calculate time differences

### math_utils
- `calculate_z_score()` - Statistical normalization
- `normalize_min_max()` - Range scaling
- `safe_divide()` - Division with zero handling

### validation_utils
- `generate_data_quality_report()` - Comprehensive DQ report
- `check_missing_data()` - Missing value analysis
- `validate_not_null()` - Null checks

### helpers
- `add_metadata_columns()` - Pipeline tracking
- `compare_results()` - Parity verification
- `collect_sample()` - Quick data inspection

## Expected Output

```
🐼 PANDAS PIPELINE
============================================================
1. Loaded messy data: 50 rows, 6 columns
2. Initial data quality:
   - Missing data in Notes: 10 rows
   - Duplicate count: 0
3. Cleaning strings...
   ✓ Standardized column names
4. Converting types...
   ✓ Converted status_flag to boolean
   ✓ Parsed created_date to datetime
...
✅ PANDAS PIPELINE COMPLETE

⚡ SPARK PIPELINE
============================================================
[Similar output for Spark]
...
✅ SPARK PIPELINE COMPLETE

PARITY VERIFICATION
============================================================
✅ Both engines produced identical results!
```

## Notes

- Spark pipeline skips gracefully if PySpark not installed
- All functions are engine-agnostic (same API for Pandas/Spark)
- Demo uses minimal dependencies (pandas, numpy, pyspark optional)
