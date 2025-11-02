# LearnODIBI Data - Synthetic Demo Datasets

The `learnodibi_data` module provides synthetic datasets for teaching and demonstrating ODIBI CORE capabilities. All datasets are deterministic (reproducible) and include intentional quality issues for practicing data validation and cleaning.

## Quick Start

```python
from odibi_core.learnodibi_data import get_dataset, list_datasets

# List available datasets
datasets = list_datasets()
# ['energy_demo', 'maintenance_demo', 'weather_demo']

# Load a dataset (auto-generates if needed)
energy_df = get_dataset("energy_demo")
print(energy_df.shape)  # (1000, 7)
```

## Available Datasets

### 1. Energy Demo (`energy_demo`)
Industrial energy monitoring data with quality issues for teaching data validation.

**Size**: 1000 rows × 7 columns  
**Columns**:
- `timestamp`: Hourly timestamps (~42 days)
- `facility_id`: Plant identifier (PLANT_A, PLANT_B, PLANT_C)
- `temperature_f`: Temperature in Fahrenheit
- `pressure_psi`: Pressure in PSI
- `flow_rate_gpm`: Flow rate in GPM
- `power_kw`: Power consumption in kW
- `efficiency_pct`: Efficiency percentage

**Quality Issues**:
- ~10% null values across numeric columns
- ~5% outliers for teaching anomaly detection

**Use Cases**:
- Data validation and cleaning
- Time series analysis
- Multi-facility aggregation
- Quality control monitoring

```python
df = get_dataset("energy_demo")
print(df.head())
```

### 2. Weather Demo (`weather_demo`)
Daily weather data with realistic seasonal patterns.

**Size**: 1095 rows × 6 columns (365 days × 3 locations)  
**Columns**:
- `date`: Daily date
- `location`: Location name (matches facilities)
- `temp_celsius`: Temperature in Celsius
- `humidity_pct`: Humidity percentage
- `pressure_mb`: Atmospheric pressure in millibars
- `wind_speed_kph`: Wind speed in km/h

**Features**:
- Seasonal temperature patterns (sinusoidal)
- Location-specific variations
- Realistic correlations (temp ↔ humidity)

**Use Cases**:
- Joining with energy data
- Seasonal pattern analysis
- Weather impact studies

```python
df = get_dataset("weather_demo")
print(df.groupby('location')['temp_celsius'].mean())
```

### 3. Maintenance Demo (`maintenance_demo`)
Equipment maintenance records with costs and downtime.

**Size**: 100 rows × 5 columns  
**Columns**:
- `equipment_id`: Equipment identifier (EQ_001, EQ_002, ...)
- `maintenance_date`: Date of maintenance
- `status`: SCHEDULED, COMPLETED, OVERDUE
- `cost`: Maintenance cost ($500-$50,000)
- `downtime_hours`: Equipment downtime (0-48 hours)

**Distribution**:
- 60% COMPLETED
- 30% SCHEDULED
- 10% OVERDUE

**Features**:
- Log-normal cost distribution (realistic)
- Downtime correlated with cost
- 15-20 unique equipment pieces

**Use Cases**:
- Maintenance tracking and reporting
- Cost analysis
- Downtime optimization
- Status-based filtering

```python
df = get_dataset("maintenance_demo")
print(df.groupby('status')['cost'].agg(['count', 'mean', 'sum']))
```

## API Reference

### `get_dataset(name, use_cache=True, regenerate=False)`
Load a dataset by name, generating if needed.

**Parameters**:
- `name` (str): Dataset name ('energy_demo', 'weather_demo', 'maintenance_demo')
- `use_cache` (bool): Use in-memory cache for faster access (default: True)
- `regenerate` (bool): Force regeneration even if file exists (default: False)

**Returns**: pandas.DataFrame

**Example**:
```python
df = get_dataset("energy_demo")
df = get_dataset("weather_demo", use_cache=False)
df = get_dataset("maintenance_demo", regenerate=True)
```

### `list_datasets()`
Get list of available datasets.

**Returns**: List[str]

**Example**:
```python
datasets = list_datasets()
# ['energy_demo', 'maintenance_demo', 'weather_demo']
```

### `generate_all_datasets(output_dir=None, overwrite=False)`
Generate all datasets and save to CSV files.

**Parameters**:
- `output_dir` (str): Directory to save CSVs (default: module's datasets/ dir)
- `overwrite` (bool): Overwrite existing files (default: False)

**Returns**: Dict[str, str] - Mapping of dataset names to file paths

**Example**:
```python
paths = generate_all_datasets()
paths = generate_all_datasets(output_dir="data/demo", overwrite=True)
```

### `get_dataset_info(name)`
Get metadata about a dataset without loading it.

**Parameters**:
- `name` (str): Dataset name

**Returns**: dict with keys: name, file_exists, file_path, cached, file_size_bytes

**Example**:
```python
info = get_dataset_info("energy_demo")
print(f"Cached: {info['cached']}, Size: {info['file_size_bytes']} bytes")
```

### `clear_cache()`
Clear the in-memory dataset cache.

**Example**:
```python
clear_cache()  # Free memory or force reload
```

## Generator Functions

For advanced use, you can directly call generator functions:

```python
from odibi_core.learnodibi_data import (
    generate_energy_demo,
    generate_weather_demo,
    generate_maintenance_demo
)

# Custom parameters
energy_df = generate_energy_demo(
    num_rows=500,
    facilities=["FACTORY_1", "FACTORY_2"],
    seed=123
)

weather_df = generate_weather_demo(
    num_days=180,
    locations=["SITE_A", "SITE_B"],
    seed=456
)

maint_df = generate_maintenance_demo(
    num_records=50,
    equipment_prefix="PUMP",
    seed=789
)
```

## Data Storage

Generated datasets are stored as CSV files in:
```
odibi_core/learnodibi_data/datasets/
├── energy_demo.csv
├── weather_demo.csv
└── maintenance_demo.csv
```

Files are auto-generated on first use and cached for subsequent loads.

## Reproducibility

All datasets use a default random seed of `42` for reproducibility. The same parameters will always generate identical data:

```python
df1 = get_dataset("energy_demo")
df2 = get_dataset("energy_demo")
# df1 and df2 are identical
```

## Teaching Use Cases

### Data Validation Practice
```python
df = get_dataset("energy_demo")

# Find null values
nulls = df.isnull().sum()
print(nulls[nulls > 0])

# Detect outliers using IQR
Q1 = df['power_kw'].quantile(0.25)
Q3 = df['power_kw'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['power_kw'] < Q1 - 1.5*IQR) | (df['power_kw'] > Q3 + 1.5*IQR)]
```

### Data Cleaning
```python
# Fill nulls with forward fill
df_clean = df.fillna(method='ffill')

# Remove outliers
df_clean = df[df['temperature_f'].between(170, 230)]
```

### Time Series Analysis
```python
df = get_dataset("energy_demo")
df['hour'] = df['timestamp'].dt.hour
hourly_avg = df.groupby('hour')['power_kw'].mean()
```

### Multi-table Joins
```python
energy = get_dataset("energy_demo")
weather = get_dataset("weather_demo")

# Join on date and location
energy['date'] = energy['timestamp'].dt.date
energy['location'] = energy['facility_id'].map({
    'PLANT_A': 'PLANT_A_LOCATION',
    'PLANT_B': 'PLANT_B_LOCATION',
    'PLANT_C': 'PLANT_C_LOCATION'
})

combined = energy.merge(weather, on=['date', 'location'])
```

## Demo Script

Run the included demo script to see all datasets:

```bash
python examples/learnodibi_data_demo.py
```

This will:
- List all available datasets
- Show sample data from each dataset
- Analyze data quality issues
- Display summary statistics
- Demonstrate seasonal patterns
- Show maintenance cost/downtime analysis

## Requirements

- pandas
- numpy

These are already included in ODIBI CORE's dependencies.
