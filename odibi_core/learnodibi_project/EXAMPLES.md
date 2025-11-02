# ODIBI CORE Learn Project - Usage Examples

## Example 1: Basic Pipeline Execution

```python
from odibi_core.learnodibi_project import DemoPipeline

# Create pipeline instance
pipeline = DemoPipeline()

# Run full pipeline
result = pipeline.run_full()

# Access datasets
energy_weather = result.data_map['silver_energy_weather']
efficiency = result.data_map['gold_efficiency_report']

print(f"Energy-Weather joined data: {len(energy_weather)} rows")
print(f"Efficiency report: {len(efficiency)} facilities")
```

## Example 2: Layer-by-Layer Execution

```python
from odibi_core.learnodibi_project import DemoPipeline

pipeline = DemoPipeline()

# Bronze: Ingestion only
bronze = pipeline.run_bronze()
print(f"Bronze datasets: {list(bronze.data_map.keys())}")

# Silver: Ingestion + Transformation
silver = pipeline.run_silver()
energy_cleaned = silver.data_map['silver_energy']
print(f"Cleaned energy records: {len(energy_cleaned)}")

# Gold: Full pipeline with aggregations
gold = pipeline.run_gold()
summary = gold.data_map['gold_daily_summary']
print(f"Facilities summarized: {len(summary)}")
```

## Example 3: Configuration Inspection

```python
from odibi_core.learnodibi_project import get_pipeline_config

# Get bronze config
bronze_config = get_pipeline_config("bronze")
print(f"Bronze layer has {len(bronze_config)} steps:")
for step in bronze_config:
    print(f"  - {step['name']}: {step['type']}")

# Get full config
full_config = get_pipeline_config("full")
print(f"\nFull pipeline has {len(full_config)} steps")

# Inspect specific step
energy_step = bronze_config[0]
print(f"\nFirst step details:")
print(f"  Name: {energy_step['name']}")
print(f"  Layer: {energy_step['layer']}")
print(f"  Type: {energy_step['type']}")
print(f"  Engine: {energy_step['engine']}")
print(f"  Output: {energy_step['outputs']}")
```

## Example 4: Custom Engine (Spark)

```python
from odibi_core.learnodibi_project import DemoPipeline

# Use Spark engine for distributed processing
pipeline = DemoPipeline(engine="spark")

# Run pipeline
result = pipeline.run_full()

# Datasets are now Spark DataFrames
energy_df = result.data_map['silver_energy']
print(f"Type: {type(energy_df)}")  # pyspark.sql.DataFrame
```

## Example 5: Disable Tracking

```python
from odibi_core.learnodibi_project import DemoPipeline

# Run without tracker (faster for testing)
pipeline = DemoPipeline(enable_tracking=False)
result = pipeline.run_gold()

# No tracker logs created
```

## Example 6: Custom Output Directory

```python
from odibi_core.learnodibi_project import DemoPipeline

# Save outputs to custom directory
pipeline = DemoPipeline(output_dir="C:/my_outputs")
result = pipeline.run_full()

# Files saved to C:/my_outputs/
```

## Example 7: Pipeline Description

```python
from odibi_core.learnodibi_project import DemoPipeline

pipeline = DemoPipeline()

# Print full pipeline architecture
print(pipeline.describe())
```

Output:
```
ODIBI CORE Demo Pipeline - Medallion Architecture
==================================================

BRONZE LAYER (Ingestion)
  • read_energy_data      → bronze_energy
  • read_weather_data     → bronze_weather
  • read_maintenance_data → bronze_maintenance

SILVER LAYER (Transformation)
  • clean_energy_data         → silver_energy
  • join_energy_weather       → silver_energy_weather
  • clean_maintenance_data    → silver_maintenance

GOLD LAYER (Aggregation)
  • aggregate_daily_by_facility    → gold_daily_summary
  • calculate_efficiency_metrics   → gold_efficiency_report
  • analyze_maintenance_costs      → gold_maintenance_costs

PUBLISH LAYER (Output)
  • save_daily_summary       → gold_daily_summary.parquet
  • save_efficiency_report   → gold_efficiency_report.json
  • save_maintenance_costs   → gold_maintenance_costs.csv
```

## Example 8: Data Quality Verification

```python
from odibi_core.learnodibi_project import DemoPipeline

pipeline = DemoPipeline()

# Run silver layer
result = pipeline.run_silver()

# Verify data quality rules applied
silver_energy = result.data_map['silver_energy']

# Check: No nulls in consumption
assert silver_energy['consumption_kwh'].notna().all(), "Found null values!"

# Check: All positive values
assert (silver_energy['consumption_kwh'] > 0).all(), "Found non-positive values!"

# Check: Within range (0-10,000 kWh)
assert (silver_energy['consumption_kwh'] < 10000).all(), "Found outliers!"

print("✓ All quality checks passed")
```

## Example 9: Analyzing Gold Metrics

```python
from odibi_core.learnodibi_project import DemoPipeline
import pandas as pd

pipeline = DemoPipeline()
result = pipeline.run_gold()

# Get efficiency report
efficiency = result.data_map['gold_efficiency_report']

# Find most efficient facility
most_efficient = efficiency.nsmallest(1, 'efficiency_kwh_per_day')
print(f"Most efficient facility:")
print(most_efficient)

# Get maintenance costs
maintenance = result.data_map['gold_maintenance_costs']

# Find highest maintenance facility
highest_cost = maintenance.nlargest(1, 'total_maintenance_cost_usd')
print(f"\nHighest maintenance costs:")
print(highest_cost)

# Calculate total metrics
total_consumption = efficiency['total_consumption_kwh'].sum()
total_maintenance = maintenance['total_maintenance_cost_usd'].sum()
print(f"\nTotal consumption: {total_consumption:.2f} kWh")
print(f"Total maintenance cost: ${total_maintenance:.2f}")
```

## Example 10: Reading Output Files

```python
import pandas as pd
from pathlib import Path

output_dir = Path("odibi_core/learnodibi_project/output")

# Read Parquet
daily_summary = pd.read_parquet(output_dir / "gold_daily_summary.parquet")
print(f"Daily summary: {len(daily_summary)} facilities")
print(daily_summary)

# Read JSON
efficiency = pd.read_json(output_dir / "gold_efficiency_report.json")
print(f"\nEfficiency report: {len(efficiency)} facilities")
print(efficiency)

# Read CSV
maintenance = pd.read_csv(output_dir / "gold_maintenance_costs.csv")
print(f"\nMaintenance costs: {len(maintenance)} facilities")
print(maintenance)
```

## Example 11: Direct SDK Usage

```python
from odibi_core.sdk import ODIBI

# Run bronze config directly
ODIBI.run(
    config_path="odibi_core/learnodibi_project/bronze_config.json",
    engine="pandas"
)

# Validate config
ODIBI.validate(
    config_path="odibi_core/learnodibi_project/full_pipeline_config.json"
)
```

## Example 12: Pipeline from Config

```python
from odibi_core.sdk import Pipeline

# Load from config
pipeline = Pipeline.from_config(
    "odibi_core/learnodibi_project/gold_config.json"
)

# Configure
pipeline.set_engine("pandas")
pipeline.set_max_workers(4)

# Execute
result = pipeline.execute()

# Access data
efficiency = result.data_map['gold_efficiency_report']
print(efficiency.head())
```

## Example 13: Custom Transformation

```python
from odibi_core.learnodibi_project import get_pipeline_config
from odibi_core.sdk import Pipeline
import json

# Load silver config
config = get_pipeline_config("silver")

# Add custom step
custom_step = {
    "layer": "transform",
    "name": "calculate_cost_per_kwh",
    "type": "sql",
    "engine": "pandas",
    "value": """
        SELECT 
            m.facility_id,
            SUM(m.cost_usd) as total_cost,
            SUM(e.consumption_kwh) as total_kwh,
            SUM(m.cost_usd) / SUM(e.consumption_kwh) as cost_per_kwh
        FROM maintenance m
        INNER JOIN energy e ON m.facility_id = e.facility_id
        GROUP BY m.facility_id
    """,
    "inputs": {"maintenance": "silver_maintenance", "energy": "silver_energy"},
    "outputs": {"data": "cost_analysis"},
    "metadata": {"description": "Calculate cost per kWh"}
}

config.append(custom_step)

# Save modified config
with open("custom_config.json", "w") as f:
    json.dump(config, f, indent=2)

# Run modified pipeline
pipeline = Pipeline.from_config("custom_config.json")
result = pipeline.execute()
print(result.data_map['cost_analysis'])
```

## Example 14: Event Monitoring

```python
from odibi_core.learnodibi_project import DemoPipeline
from odibi_core.core import EventEmitter

# Custom event handler
def on_step_complete(step, duration_ms):
    print(f"✓ Step '{step.name}' completed in {duration_ms:.2f}ms")
    
def on_step_error(step, error):
    print(f"✗ Step '{step.name}' failed: {error}")

# Create pipeline with events
pipeline = DemoPipeline()

# Note: Direct event attachment requires modifying demo_pipeline.py
# This example shows the pattern for custom implementations
```

## Example 15: Testing Individual Layers

```python
from odibi_core.learnodibi_project import DemoPipeline
import pytest

def test_bronze_layer():
    """Test bronze layer ingestion."""
    pipeline = DemoPipeline()
    result = pipeline.run_bronze()
    
    # Check all bronze datasets exist
    assert 'bronze_energy' in result.data_map
    assert 'bronze_weather' in result.data_map
    assert 'bronze_maintenance' in result.data_map
    
    # Check data loaded
    assert len(result.data_map['bronze_energy']) > 0

def test_silver_layer():
    """Test silver layer transformations."""
    pipeline = DemoPipeline()
    result = pipeline.run_silver()
    
    # Check silver datasets exist
    assert 'silver_energy' in result.data_map
    assert 'silver_energy_weather' in result.data_map
    
    # Verify data quality
    energy = result.data_map['silver_energy']
    assert energy['consumption_kwh'].notna().all()
    assert (energy['consumption_kwh'] > 0).all()

def test_gold_layer():
    """Test gold layer aggregations."""
    pipeline = DemoPipeline()
    result = pipeline.run_gold()
    
    # Check gold datasets exist
    assert 'gold_daily_summary' in result.data_map
    assert 'gold_efficiency_report' in result.data_map
    
    # Verify metrics calculated
    efficiency = result.data_map['gold_efficiency_report']
    assert 'efficiency_kwh_per_day' in efficiency.columns
    assert len(efficiency) == 3  # 3 facilities

if __name__ == "__main__":
    test_bronze_layer()
    test_silver_layer()
    test_gold_layer()
    print("All tests passed!")
```

---

## Running the Demo Script

```bash
# Run the complete demo
python -m odibi_core.learnodibi_project.run_demo

# Or directly
cd odibi_core/learnodibi_project
python run_demo.py
```

---

## Common Patterns

### Pattern 1: Incremental Development
```python
# Start with bronze
pipeline = DemoPipeline()
bronze = pipeline.run_bronze()

# Add silver transformations
silver = pipeline.run_silver()

# Add gold aggregations
gold = pipeline.run_gold()

# Publish when ready
full = pipeline.run_full()
```

### Pattern 2: Data Exploration
```python
pipeline = DemoPipeline()
result = pipeline.run_gold()

# Explore datasets
for name, df in result.data_map.items():
    if name.startswith('gold_'):
        print(f"\n{name}:")
        print(df.head())
        print(f"Shape: {df.shape}")
```

### Pattern 3: Quality Assurance
```python
pipeline = DemoPipeline()
result = pipeline.run_silver()

for name, df in result.data_map.items():
    if name.startswith('silver_'):
        print(f"\n{name} Quality Report:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Nulls: {df.isnull().sum().sum()}")
        print(f"  Duplicates: {df.duplicated().sum()}")
```

---

These examples cover the most common use cases for the Learn ODIBI Project module. Experiment with them to understand the medallion architecture pattern and ODIBI CORE's config-driven approach!
