# ODIBI CORE Learn Project

**A complete Bronze → Silver → Gold pipeline demonstration using ODIBI CORE v1.0**

This module showcases the medallion architecture pattern with config-driven data pipelines for energy facility analytics.

---

## 📋 Overview

The demo pipeline processes energy facility data through three layers:

### **Bronze Layer** (Ingestion)
Raw data ingestion from source systems:
- `energy_demo.csv` → `bronze_energy` (energy consumption records)
- `weather_demo.csv` → `bronze_weather` (weather data for correlation)
- `maintenance_demo.csv` → `bronze_maintenance` (maintenance records and costs)

### **Silver Layer** (Transformation)
Data cleaning, validation, and enrichment:
- `clean_energy_data` → `silver_energy` (remove nulls, filter outliers 0-10K kWh)
- `join_energy_weather` → `silver_energy_weather` (inner join on facility + date)
- `clean_maintenance_data` → `silver_maintenance` (remove null/negative costs)

### **Gold Layer** (Aggregation)
Business metrics and KPIs:
- `aggregate_daily_by_facility` → `gold_daily_summary` (facility-level aggregation)
- `calculate_efficiency_metrics` → `gold_efficiency_report` (efficiency ratios)
- `analyze_maintenance_costs` → `gold_maintenance_costs` (cost analysis)

### **Publish Layer** (Output)
Save results to multiple formats:
- `gold_daily_summary.parquet` (Parquet format)
- `gold_efficiency_report.json` (JSON with indent)
- `gold_maintenance_costs.csv` (CSV export)

---

## 🚀 Quick Start

```python
from odibi_core.learnodibi_project import DemoPipeline

# Create pipeline instance
pipeline = DemoPipeline()

# Run full pipeline (Bronze → Silver → Gold → Publish)
result = pipeline.run_full()

# Check outputs
print(result.summary())
print(f"Datasets: {list(result.data_map.keys())}")
```

---

## 📊 Layer-by-Layer Execution

```python
from odibi_core.learnodibi_project import DemoPipeline

pipeline = DemoPipeline()

# Run Bronze layer only (ingestion)
result = pipeline.run_bronze()
# Produces: bronze_energy, bronze_weather, bronze_maintenance

# Run Bronze + Silver (ingestion + transformation)
result = pipeline.run_silver()
# Produces: bronze_* + silver_energy, silver_energy_weather, silver_maintenance

# Run Bronze + Silver + Gold (full aggregation)
result = pipeline.run_gold()
# Produces: all bronze/silver + gold_daily_summary, gold_efficiency_report, gold_maintenance_costs

# Run complete pipeline with publishing
result = pipeline.run_full()
# Produces: all datasets + saves outputs to files
```

---

## 🔍 Configuration Inspection

```python
from odibi_core.learnodibi_project import get_pipeline_config

# Get bronze layer configuration
config = get_pipeline_config("bronze")
print(f"Bronze has {len(config)} steps")

# Inspect step details
for step in config:
    print(f"{step['name']}: {step['layer']} → {step['outputs']}")

# Available configs: "bronze", "silver", "gold", "full"
```

---

## 🛠️ Custom Engine

```python
from odibi_core.learnodibi_project import DemoPipeline

# Use Spark engine instead of Pandas
pipeline = DemoPipeline(engine="spark")
result = pipeline.run_full()

# Disable tracking
pipeline = DemoPipeline(enable_tracking=False)

# Custom output directory
pipeline = DemoPipeline(output_dir="/path/to/output")
```

---

## 📁 File Structure

```
learnodibi_project/
├── __init__.py                      # Module exports
├── demo_pipeline.py                 # DemoPipeline class
├── bronze_config.json               # Bronze layer config (3 steps)
├── silver_config.json               # Bronze + Silver (6 steps)
├── gold_config.json                 # Bronze + Silver + Gold (9 steps)
├── full_pipeline_config.json        # Complete pipeline (12 steps)
├── README.md                        # This file
├── data/                            # Sample data
│   ├── energy_demo.csv              # Energy consumption records
│   ├── weather_demo.csv             # Weather data
│   └── maintenance_demo.csv         # Maintenance records
└── output/                          # Pipeline outputs
    ├── gold_daily_summary.parquet
    ├── gold_efficiency_report.json
    ├── gold_maintenance_costs.csv
    └── tracker_logs/                # Lineage and metrics
```

---

## 📖 Configuration Format

Each config step follows the ODIBI CORE format:

```json
{
  "layer": "transform",
  "name": "clean_energy_data",
  "type": "sql",
  "engine": "pandas",
  "value": "SELECT * FROM data WHERE consumption_kwh IS NOT NULL AND consumption_kwh > 0",
  "params": {},
  "inputs": {"data": "bronze_energy"},
  "outputs": {"data": "silver_energy"},
  "metadata": {
    "description": "Clean and validate energy data",
    "quality_rules": ["no_nulls", "range_check"]
  }
}
```

**Fields:**
- `layer`: Pipeline layer (ingest, transform, aggregate, publish)
- `name`: Unique step identifier
- `type`: Operation type (config_op for read/write, sql for transformations)
- `engine`: Execution engine (pandas or spark)
- `value`: File path (config_op) or SQL query (sql)
- `params`: Additional parameters (e.g., orient, index)
- `inputs`: Named input datasets (keys match SQL table names)
- `outputs`: Named output datasets
- `metadata`: Documentation and lineage info

---

## 🎯 Use Cases Demonstrated

1. **Config-Driven Pipelines**: JSON configs define complete workflows
2. **Medallion Architecture**: Bronze/Silver/Gold pattern for data lakes
3. **SQL Transformations**: Use SQL with Pandas/Spark engines
4. **Data Quality**: Null checks, range validation, outlier filtering
5. **Multi-Source Ingestion**: Read from multiple CSV files
6. **Data Enrichment**: Join energy with weather context
7. **Business Aggregations**: Facility-level KPIs and metrics
8. **Multiple Outputs**: Parquet, JSON, CSV formats
9. **Lineage Tracking**: Tracker captures snapshots and timing
10. **Event Monitoring**: Listen to step completion events

---

## 💡 Sample Data

**Energy Data** (`energy_demo.csv`):
- 18 records across 3 facilities
- Includes nulls and outliers for testing Silver layer cleaning
- Columns: facility_id, date, consumption_kwh, peak_demand_kw

**Weather Data** (`weather_demo.csv`):
- 18 records matching energy data
- Columns: facility_id, date, temperature_avg, humidity_pct

**Maintenance Data** (`maintenance_demo.csv`):
- 8 maintenance records
- Includes null and negative costs for testing
- Columns: facility_id, maintenance_date, maintenance_type, cost_usd

---

## 📈 Expected Outputs

After running `pipeline.run_full()`:

**gold_daily_summary.parquet:**
```
facility_id | total_days | total_consumption_kwh | avg_daily_consumption_kwh | max_peak_demand_kw | avg_temperature
FAC001      | 5          | 6502.5                | 1300.5                    | 145.2              | 19.7
FAC002      | 5          | 11102.5               | 2220.5                    | 235.0              | 19.7
FAC003      | 5          | 4537.5                | 907.5                     | 94.0               | 19.7
```

**gold_efficiency_report.json:**
```json
[
  {
    "facility_id": "FAC002",
    "efficiency_kwh_per_day": 2220.5,
    "demand_efficiency_ratio": 0.106
  },
  ...
]
```

**gold_maintenance_costs.csv:**
```
facility_id,maintenance_count,total_maintenance_cost_usd,avg_maintenance_cost_usd,max_maintenance_cost_usd
FAC001,2,1650.50,825.25,1200.50
FAC002,2,800.75,400.38,520.00
FAC003,2,1270.25,635.13,890.25
```

---

## 🧪 Testing the Pipeline

```python
# Test Bronze layer
pipeline = DemoPipeline()
result = pipeline.run_bronze()
assert 'bronze_energy' in result.data_map
assert 'bronze_weather' in result.data_map
assert 'bronze_maintenance' in result.data_map

# Test Silver layer
result = pipeline.run_silver()
silver_df = result.data_map['silver_energy']
assert silver_df['consumption_kwh'].notna().all()  # No nulls
assert (silver_df['consumption_kwh'] > 0).all()    # All positive
assert (silver_df['consumption_kwh'] < 10000).all() # Within range

# Test Gold layer
result = pipeline.run_gold()
efficiency_df = result.data_map['gold_efficiency_report']
assert 'efficiency_kwh_per_day' in efficiency_df.columns
assert 'demand_efficiency_ratio' in efficiency_df.columns
```

---

## 🔗 Pipeline Description

```python
pipeline = DemoPipeline()
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

---

## 🎓 Learning Objectives

By studying this module, you'll learn:

1. ✅ How to structure medallion architecture pipelines
2. ✅ How to write ODIBI CORE JSON configurations
3. ✅ How to use SQL transformations with Pandas/Spark
4. ✅ How to implement data quality rules
5. ✅ How to join multiple data sources
6. ✅ How to calculate business metrics and KPIs
7. ✅ How to save outputs in multiple formats
8. ✅ How to track pipeline lineage and metrics
9. ✅ How to build reusable pipeline classes
10. ✅ How to test data pipelines layer by layer

---

## 📚 Next Steps

1. **Customize Configs**: Modify JSON configs to add new transformations
2. **Add Layers**: Extend with additional Silver or Gold steps
3. **New Data Sources**: Add more CSV files and ingestion steps
4. **Spark Engine**: Test with `engine="spark"` for distributed processing
5. **Quality Checks**: Add schema validation and data quality assertions
6. **Scheduling**: Integrate with ODIBI CORE scheduler for automation
7. **Cloud Storage**: Modify paths to read/write from Azure/S3
8. **Monitoring**: Add custom event listeners for alerting
9. **Explanations**: Create showcase explanations for HTML story export
10. **Testing**: Write pytest tests for each pipeline layer

---

## 🤝 Contributing

This module is a learning resource. Feel free to:
- Add new sample datasets
- Create additional transformation examples
- Enhance documentation
- Submit improvements

---

## 📄 License

Part of ODIBI CORE v1.0 - Open for educational and commercial use.
