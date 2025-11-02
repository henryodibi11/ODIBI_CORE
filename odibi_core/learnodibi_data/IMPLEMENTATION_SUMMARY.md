# LearnODIBI Data Module - Implementation Summary

## Overview
Successfully created the `learnodibi_data` module for ODIBI CORE that generates synthetic demo datasets for teaching and demonstration purposes.

## Created Files

### Core Module Files
1. **`__init__.py`** - Module exports and documentation
2. **`data_generator.py`** - Dataset generation functions (373 lines)
   - `generate_energy_demo()` - 1000 rows of industrial energy data
   - `generate_weather_demo()` - 1095 rows of weather data (365 days × 3 locations)
   - `generate_maintenance_demo()` - 100 maintenance records
   - `generate_all_datasets()` - Generate all datasets at once

3. **`datasets.py`** - Dataset loader with caching (179 lines)
   - `get_dataset()` - Load dataset with auto-generation
   - `list_datasets()` - List available datasets
   - `get_dataset_info()` - Get dataset metadata
   - `clear_cache()` - Clear in-memory cache
   - In-memory caching for performance

### Supporting Files
4. **`datasets/.gitkeep`** - Placeholder for datasets directory
5. **`README.md`** - Complete module documentation with examples
6. **`tests/test_learnodibi_data.py`** - Comprehensive test suite (26 tests)
7. **`examples/learnodibi_data_demo.py`** - Interactive demo script

## Datasets Generated

### 1. Energy Demo (`energy_demo.csv`)
- **Size**: 1000 rows × 7 columns (~116 KB)
- **Columns**: timestamp, facility_id, temperature_f, pressure_psi, flow_rate_gpm, power_kw, efficiency_pct
- **Features**:
  - 3 facilities (PLANT_A, PLANT_B, PLANT_C)
  - Hourly data over ~42 days
  - Realistic patterns (daily temperature cycles, correlated metrics)
  - **Quality issues**: ~10% null values, ~5% outliers (intentional for teaching)
  
### 2. Weather Demo (`weather_demo.csv`)
- **Size**: 1095 rows × 6 columns (~54 KB)
- **Columns**: date, location, temp_celsius, humidity_pct, pressure_mb, wind_speed_kph
- **Features**:
  - 3 locations matching energy facilities
  - 365 days of daily data
  - Seasonal temperature patterns (sinusoidal)
  - Realistic correlations (temperature ↔ humidity)

### 3. Maintenance Demo (`maintenance_demo.csv`)
- **Size**: 100 rows × 5 columns (~4 KB)
- **Columns**: equipment_id, maintenance_date, status, cost, downtime_hours
- **Features**:
  - 15-20 unique equipment pieces
  - Status distribution: 60% COMPLETED, 30% SCHEDULED, 10% OVERDUE
  - Realistic cost distribution ($500-$50,000, log-normal)
  - Downtime correlated with cost (0-48 hours)

## Key Features

### ✅ Deterministic & Reproducible
- All datasets use seed=42 by default
- Same parameters always generate identical data
- Perfect for testing and teaching

### ✅ Realistic Data
- Industry-appropriate value ranges
- Temporal patterns (daily, seasonal)
- Correlated metrics (flow ↔ power, temp ↔ efficiency)
- Log-normal distributions for costs

### ✅ Teaching-Friendly
- Intentional quality issues (nulls, outliers)
- Multiple facilities/locations for joins
- Time series data for trend analysis
- Different data types (numeric, categorical, datetime)

### ✅ Performance Optimized
- In-memory caching for repeated access
- Lazy generation (only when needed)
- CSV storage for persistence
- Fast load times (<1 second)

### ✅ Developer-Friendly API
```python
# Simple API
from odibi_core.learnodibi_data import get_dataset, list_datasets

datasets = list_datasets()  # ['energy_demo', 'maintenance_demo', 'weather_demo']
df = get_dataset("energy_demo")  # Auto-generates if needed
```

## Test Coverage

**26 tests, 100% passing**

### Test Categories:
- **Data Generators** (14 tests)
  - Shape validation
  - Column validation
  - Data quality (nulls, ranges)
  - Reproducibility
  - Custom parameters

- **Dataset Loader** (10 tests)
  - Loading all datasets
  - Error handling
  - Caching behavior
  - Metadata retrieval

- **Bulk Operations** (2 tests)
  - Generate all datasets
  - Overwrite behavior

## Usage Examples

### Basic Usage
```python
from odibi_core.learnodibi_data import get_dataset

# Load energy dataset
df = get_dataset("energy_demo")
print(df.shape)  # (1000, 7)
print(df.head())
```

### Generate All Datasets
```python
from odibi_core.learnodibi_data import generate_all_datasets

# Generate to custom directory
paths = generate_all_datasets(output_dir="data/demo", overwrite=True)
# Generated energy_demo: data/demo/energy_demo.csv (1000 rows)
# Generated weather_demo: data/demo/weather_demo.csv (1095 rows)
# Generated maintenance_demo: data/demo/maintenance_demo.csv (100 rows)
```

### Custom Generation
```python
from odibi_core.learnodibi_data import generate_energy_demo

# Custom parameters
df = generate_energy_demo(
    num_rows=500,
    facilities=["FACTORY_1", "FACTORY_2"],
    seed=123
)
```

### Check Dataset Info
```python
from odibi_core.learnodibi_data import get_dataset_info

info = get_dataset_info("energy_demo")
print(info)
# {'name': 'energy_demo', 'file_exists': True, 
#  'file_path': '...', 'cached': True, 'file_size_bytes': 119211}
```

## Demo Script Output

Run `python examples/learnodibi_data_demo.py` for a comprehensive overview:

```
======================================================================
ODIBI CORE - LearnODIBI Data Demo
======================================================================

1. Available Datasets
----------------------------------------------------------------------
   1. energy_demo
   2. maintenance_demo
   3. weather_demo

2. Dataset Overview
----------------------------------------------------------------------
[Shows sample data, shapes, and columns for each dataset]

3. Energy Dataset Quality Analysis
----------------------------------------------------------------------
[Analyzes nulls, outliers, summary statistics]

4. Weather Dataset Seasonal Patterns
----------------------------------------------------------------------
[Shows temperature patterns by location]

5. Maintenance Dataset Analysis
----------------------------------------------------------------------
[Analyzes status distribution, costs, downtime]
```

## Teaching Use Cases

### 1. Data Validation Practice
- Detect null values (~10% in energy data)
- Find outliers using IQR or z-scores
- Validate data types and ranges

### 2. Data Cleaning
- Fill nulls with forward fill, mean, or interpolation
- Remove or cap outliers
- Standardize categorical values

### 3. Time Series Analysis
- Hourly/daily patterns
- Trend analysis
- Seasonal decomposition

### 4. Multi-table Joins
- Join energy + weather on date/location
- Analyze weather impact on energy efficiency
- Cross-reference with maintenance records

### 5. Aggregations
- Group by facility/equipment
- Calculate summary statistics
- Build reporting tables

### 6. Visualization
- Time series plots
- Distribution histograms
- Correlation heatmaps
- Seasonal patterns

## Code Quality

### ✅ Type Hints
All functions have complete type hints for better IDE support:
```python
def generate_energy_demo(
    num_rows: int = 1000,
    facilities: list = None,
    seed: int = 42
) -> pd.DataFrame:
```

### ✅ Comprehensive Docstrings
Google-style docstrings with Args, Returns, and Examples:
```python
"""
Generate synthetic energy dataset with realistic industrial metrics.

Args:
    num_rows: Number of rows to generate (default: 1000)
    facilities: List of facility IDs (default: ["PLANT_A", "PLANT_B", "PLANT_C"])
    seed: Random seed for reproducibility (default: 42)

Returns:
    DataFrame with columns: timestamp, facility_id, temperature_f, ...

Example:
    >>> df = generate_energy_demo(num_rows=100)
    >>> df.shape
    (100, 7)
"""
```

### ✅ Error Handling
Clear error messages for invalid inputs:
```python
if name not in _AVAILABLE_DATASETS:
    available = ', '.join(list_datasets())
    raise ValueError(
        f"Unknown dataset: '{name}'. Available datasets: {available}"
    )
```

### ✅ Performance
- Efficient numpy/pandas operations
- In-memory caching
- Lazy CSV generation
- Vectorized calculations

## File Structure
```
odibi_core/learnodibi_data/
├── __init__.py                    # Module exports
├── data_generator.py              # Dataset generation functions
├── datasets.py                    # Dataset loader with caching
├── README.md                      # Complete documentation
├── IMPLEMENTATION_SUMMARY.md      # This file
└── datasets/                      # Generated CSV files
    ├── .gitkeep
    ├── energy_demo.csv           # 1000 rows, ~116 KB
    ├── weather_demo.csv          # 1095 rows, ~54 KB
    └── maintenance_demo.csv      # 100 rows, ~4 KB

tests/
└── test_learnodibi_data.py       # 26 tests, 100% passing

examples/
└── learnodibi_data_demo.py       # Interactive demo script
```

## Dependencies
- **pandas**: DataFrame operations
- **numpy**: Random number generation, numerical operations

Both are already included in ODIBI CORE's base requirements.

## Integration with ODIBI CORE

This module integrates seamlessly with ODIBI CORE's node-based architecture:

```python
from odibi_core.learnodibi_data import get_dataset
from odibi_core.nodes import ReadNode, TransformNode

# Load demo data
energy_df = get_dataset("energy_demo")

# Use in ODIBI CORE nodes
read_node = ReadNode(data=energy_df)
transform_node = TransformNode(...)
```

## Future Enhancements (Optional)

Potential additions for future versions:
1. More datasets (sales, inventory, customer, IoT sensor)
2. Configurable quality issues (% nulls, outlier types)
3. Time series anomalies (sudden spikes, drift)
4. Spark DataFrame support
5. Export to other formats (Parquet, JSON)
6. Data profiling reports
7. Interactive Jupyter notebooks

## Verification

All functionality verified:
- ✅ 26/26 tests passing
- ✅ All datasets generated successfully
- ✅ Demo script runs without errors
- ✅ No linting or type checking errors
- ✅ Documentation complete
- ✅ Examples working

## Summary

The `learnodibi_data` module is production-ready and provides:
- 3 realistic synthetic datasets
- Simple, intuitive API
- Deterministic, reproducible data
- Comprehensive tests (100% passing)
- Complete documentation
- Teaching-friendly features
- Seamless ODIBI CORE integration

Users can now easily access demo data for learning ODIBI CORE without needing external data sources or complex setup.
