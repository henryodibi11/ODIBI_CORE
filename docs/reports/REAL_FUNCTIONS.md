# ODIBI CORE - Real Functions Reference

This document lists ALL actual functions available in `odibi_core.functions`.

**Total Functions: 97**

---

## 1. conversion_utils (10 functions)

Utilities for data type conversion and null handling.

- `cast_column` - Cast column to specific data type
- `detect_engine` - Detect DataFrame engine (pandas/spark)
- `extract_numbers` - Extract numeric values from strings
- `fill_null` - Fill null values with strategy
- `map_values` - Map values using dictionary
- `normalize_nulls` - Standardize null representations
- `one_hot_encode` - One-hot encode categorical columns
- `parse_json` - Parse JSON strings into columns
- `to_boolean` - Convert to boolean type
- `to_numeric` - Convert to numeric type

---

## 2. data_ops (10 functions)

Core data manipulation operations.

- `deduplicate` - Remove duplicate rows
- `detect_engine` - Detect DataFrame engine
- `filter_rows` - Filter rows by condition
- `group_and_aggregate` - Group and aggregate data
- `pivot_table` - Create pivot tables
- `rename_columns` - Rename DataFrame columns
- `safe_join` - Join with error handling
- `select_columns` - Select specific columns
- `sort_data` - Sort DataFrame
- `unpivot` - Unpivot (melt) DataFrame

---

## 3. datetime_utils (10 functions)

Date and time manipulation utilities.

- `add_time_delta` - Add time offset to datetime
- `calculate_age` - Calculate age from date of birth
- `date_diff` - Calculate difference between dates
- `detect_engine` - Detect DataFrame engine
- `extract_date_parts` - Extract year/month/day components
- `format_datetime` - Format datetime to string
- `get_current_timestamp` - Get current timestamp
- `is_weekend` - Check if date is weekend
- `to_datetime` - Convert to datetime type
- `truncate_datetime` - Truncate datetime to unit

---

## 4. math_utils (14 functions)

Mathematical operations and statistical functions.

- `calculate_cumulative_sum` - Calculate cumulative sum
- `calculate_moving_average` - Calculate rolling average
- `calculate_percent_change` - Calculate percentage change
- `calculate_percentile` - Calculate percentile values
- `calculate_z_score` - Calculate z-scores
- `clip_values` - Clip values to range
- `detect_engine` - Detect DataFrame engine
- `normalize_min_max` - Min-max normalization
- `outlier_detection_iqr` - Detect outliers using IQR
- `rolling_zscore` - Rolling window z-score
- `round_numeric` - Round numeric values
- `safe_divide` - Division with zero handling
- `safe_log` - Logarithm with zero handling
- `safe_sqrt` - Square root with negative handling

---

## 5. psychro_utils (5 functions)

Psychrometric calculations for HVAC systems.

- `dew_point` - Calculate dew point temperature
- `enthalpy_moist_air` - Calculate moist air enthalpy
- `humidity_ratio` - Calculate humidity ratio
- `relative_humidity` - Calculate relative humidity
- `wet_bulb_temperature` - Calculate wet bulb temperature

---

## 6. reliability_utils (8 functions)

Reliability engineering calculations.

- `availability_index` - Calculate availability index
- `expected_failures` - Calculate expected failures
- `failure_rate` - Calculate failure rate
- `mean_time_between_failures` - Calculate MTBF
- `mission_reliability` - Calculate mission reliability
- `mttr` - Calculate mean time to repair
- `reliability_at_time` - Calculate reliability at time
- `weibull_reliability` - Weibull reliability model

---

## 7. string_utils (13 functions)

String manipulation utilities.

- `concat_strings` - Concatenate string columns
- `detect_engine` - Detect DataFrame engine
- `pad_string` - Pad string to length
- `regex_extract` - Extract using regex pattern
- `regex_replace` - Replace using regex pattern
- `replace_substring` - Replace substring
- `split_string` - Split string by delimiter
- `standardize_column_names` - Standardize column names
- `string_length` - Get string length
- `to_lowercase` - Convert to lowercase
- `to_titlecase` - Convert to title case
- `to_uppercase` - Convert to uppercase
- `trim_whitespace` - Remove whitespace

---

## 8. thermo_utils (10 functions)

Thermodynamic calculations for power systems.

- `btu_lb_to_kj_kg` - Convert BTU/lb to kJ/kg
- `fahrenheit_to_kelvin` - Convert °F to K
- `feedwater_enthalpy_btu_lb` - Calculate feedwater enthalpy
- `kelvin_to_fahrenheit` - Convert K to °F
- `kj_kg_to_btu_lb` - Convert kJ/kg to BTU/lb
- `mpa_to_psia` - Convert MPa to psia
- `psia_to_mpa` - Convert psia to MPa
- `saturation_pressure` - Calculate saturation pressure
- `saturation_temperature` - Calculate saturation temperature
- `steam_enthalpy_btu_lb` - Calculate steam enthalpy

---

## 9. unit_conversion (6 functions)

Unit conversion utilities for engineering data.

- `convert_density` - Convert density units
- `convert_energy` - Convert energy units
- `convert_flow` - Convert flow rate units
- `convert_power` - Convert power units
- `convert_pressure` - Convert pressure units
- `convert_temperature` - Convert temperature units

---

## 10. validation_utils (11 functions)

Data quality validation utilities.

- `check_missing_data` - Check for missing values
- `check_schema_match` - Validate schema match
- `detect_engine` - Detect DataFrame engine
- `find_duplicates` - Find duplicate rows
- `generate_data_quality_report` - Generate DQ report
- `get_column_stats` - Get column statistics
- `get_schema` - Get DataFrame schema
- `get_value_counts` - Get value frequency counts
- `validate_not_null` - Validate no nulls
- `validate_range` - Validate value ranges
- `validate_unique` - Validate uniqueness

---

## Usage Examples

```python
from odibi_core.functions import data_ops, math_utils, validation_utils

# Deduplicate data
clean_df = data_ops.deduplicate(df, subset=['id'])

# Calculate z-scores
normalized_df = math_utils.calculate_z_score(df, column='temperature')

# Validate data quality
report = validation_utils.generate_data_quality_report(df)
```

---

## Function Mapping (Old → New)

**DEPRECATED/FAKE** → **USE INSTEAD**

- `handle_nulls` → `conversion_utils.fill_null`
- `coalesce` → `conversion_utils.fill_null` (with strategy='coalesce')
- `apply_transformation` → Use specific function directly
- `filter_data` → `data_ops.filter_rows`
- `clean_string` → `string_utils.trim_whitespace`
- `normalize_text` → `string_utils.to_lowercase` + `string_utils.trim_whitespace`
- `extract_pattern` → `string_utils.regex_extract`
- `split_and_trim` → `string_utils.split_string` + `string_utils.trim_whitespace`
- `concatenate_with_separator` → `string_utils.concat_strings`
- `calculate_percentage` → `math_utils.calculate_percent_change`
- `moving_average` → `math_utils.calculate_moving_average`
- `exponential_smoothing` → `math_utils.calculate_moving_average` (with weighted window)
- `parse_datetime` → `datetime_utils.to_datetime`
- `calculate_duration` → `datetime_utils.date_diff`
- `is_business_day` → `datetime_utils.is_weekend` (inverse)

---

**Last Updated**: 2025-11-02  
**Generated by**: Comprehensive Audit Script
