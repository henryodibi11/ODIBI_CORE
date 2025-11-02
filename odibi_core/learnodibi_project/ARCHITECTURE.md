# Learn ODIBI Project - Architecture Documentation

## Overview

The `learnodibi_project` module demonstrates a production-grade data pipeline using the **Medallion Architecture** pattern (Bronze → Silver → Gold) implemented with ODIBI CORE v1.0.

---

## Architectural Layers

### 🥉 Bronze Layer: Raw Data Ingestion

**Purpose**: Ingest raw data from source systems with minimal transformation

**Steps**:
1. `read_energy_data` - Ingest energy consumption metrics
2. `read_weather_data` - Ingest weather observations
3. `read_maintenance_data` - Ingest maintenance records

**Outputs**:
- `bronze_energy` - Raw energy consumption data
- `bronze_weather` - Raw weather data
- `bronze_maintenance` - Raw maintenance records

**Characteristics**:
- ✅ Preserves original data structure
- ✅ No filtering or validation
- ✅ Includes nulls and outliers
- ✅ Direct CSV ingestion

---

### 🥈 Silver Layer: Cleaned and Enriched Data

**Purpose**: Apply data quality rules, clean data, and join sources

**Steps**:
1. `clean_energy_data` - Remove nulls, filter outliers (0-10,000 kWh)
2. `join_energy_weather` - Join energy with weather on facility + date
3. `clean_maintenance_data` - Remove null/negative costs

**Outputs**:
- `silver_energy` - Cleaned energy data
- `silver_energy_weather` - Energy enriched with weather context
- `silver_maintenance` - Validated maintenance records

**Quality Rules**:
- ✅ No null values in key columns
- ✅ Range validation (0-10,000 kWh)
- ✅ Non-negative costs
- ✅ Inner joins ensure data consistency

**SQL Example (Clean Energy)**:
```sql
SELECT * FROM data 
WHERE consumption_kwh IS NOT NULL 
  AND consumption_kwh > 0 
  AND consumption_kwh < 10000 
ORDER BY facility_id, date
```

---

### 🥇 Gold Layer: Business Aggregations and KPIs

**Purpose**: Calculate business metrics, KPIs, and aggregations for reporting

**Steps**:
1. `aggregate_daily_by_facility` - Facility-level daily summaries
2. `calculate_efficiency_metrics` - Efficiency ratios and KPIs
3. `analyze_maintenance_costs` - Maintenance cost analysis

**Outputs**:
- `gold_daily_summary` - Aggregated metrics per facility
- `gold_efficiency_report` - Efficiency KPIs
- `gold_maintenance_costs` - Cost analysis by facility

**Metrics**:
- ✅ Total/average consumption
- ✅ Peak demand
- ✅ Efficiency ratios (kWh per day)
- ✅ Demand efficiency ratio
- ✅ Maintenance costs (total, average, max)

**SQL Example (Efficiency)**:
```sql
SELECT 
  facility_id,
  total_consumption_kwh,
  avg_daily_consumption_kwh,
  max_peak_demand_kw,
  CAST(total_consumption_kwh AS FLOAT) / NULLIF(total_days, 0) as efficiency_kwh_per_day,
  CAST(max_peak_demand_kw AS FLOAT) / NULLIF(avg_daily_consumption_kwh, 0) as demand_efficiency_ratio
FROM data 
ORDER BY efficiency_kwh_per_day DESC
```

---

### 📤 Publish Layer: Output Files

**Purpose**: Save gold datasets to multiple formats for consumption

**Steps**:
1. `save_daily_summary` - Save to Parquet (columnar format)
2. `save_efficiency_report` - Save to JSON (readable format)
3. `save_maintenance_costs` - Save to CSV (universal format)

**Outputs**:
- `gold_daily_summary.parquet` - Optimized for analytics
- `gold_efficiency_report.json` - Human-readable with indentation
- `gold_maintenance_costs.csv` - Excel-compatible

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      BRONZE LAYER                           │
│                    (Raw Ingestion)                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│bronze_energy │    │bronze_weather│    │bronze_maint  │
│(18 rows)     │    │(18 rows)     │    │(8 rows)      │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
┌─────────────────────────────────────────────────────────────┐
│                      SILVER LAYER                           │
│              (Cleaning & Enrichment)                        │
└─────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│silver_energy │◄───┤silver_energy_│    │silver_maint  │
│(15 rows)     │    │weather       │    │(6 rows)      │
│              │    │(15 rows)     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
┌─────────────────────────────────────────────────────────────┐
│                       GOLD LAYER                            │
│               (Aggregation & KPIs)                          │
└─────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│gold_daily_   │◄───┤gold_efficiency│   │gold_maint_   │
│summary       │    │report        │    │costs         │
│(3 facilities)│    │(3 facilities)│    │(3 facilities)│
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
┌─────────────────────────────────────────────────────────────┐
│                     PUBLISH LAYER                           │
│                  (File Output)                              │
└─────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
  [.parquet]            [.json]                [.csv]
```

---

## Configuration Architecture

### Config Structure

Each config file contains an array of steps following this schema:

```json
{
  "layer": "transform | ingest | aggregate | publish",
  "name": "unique_step_identifier",
  "type": "sql | config_op",
  "engine": "pandas | spark",
  "value": "SQL query | file path",
  "params": {},
  "inputs": {"alias": "dataset_name"},
  "outputs": {"alias": "dataset_name"},
  "metadata": {}
}
```

### Config Files

1. **bronze_config.json** (3 steps)
   - Ingestion only
   - Produces: bronze_energy, bronze_weather, bronze_maintenance

2. **silver_config.json** (6 steps)
   - Bronze + Silver
   - Produces: bronze_* + silver_*

3. **gold_config.json** (9 steps)
   - Bronze + Silver + Gold
   - Produces: bronze_* + silver_* + gold_*

4. **full_pipeline_config.json** (12 steps)
   - All layers + Publishing
   - Produces: All datasets + output files

---

## Class Architecture

### DemoPipeline Class

```python
class DemoPipeline:
    """Main pipeline orchestration class."""
    
    def __init__(engine, enable_tracking, output_dir):
        """Initialize pipeline with configuration."""
        
    def run_bronze() -> PipelineResult:
        """Execute Bronze layer only."""
        
    def run_silver() -> PipelineResult:
        """Execute Bronze + Silver layers."""
        
    def run_gold() -> PipelineResult:
        """Execute Bronze + Silver + Gold layers."""
        
    def run_full() -> PipelineResult:
        """Execute complete pipeline with publishing."""
        
    def _run_config(config_path, layer_name) -> PipelineResult:
        """Internal: Execute pipeline from config file."""
        
    def get_config(layer) -> Dict:
        """Get configuration for specific layer."""
        
    def describe() -> str:
        """Get pipeline architecture description."""
```

### Module Functions

```python
def get_pipeline_config(layer: str) -> Dict[str, Any]:
    """
    Public API to retrieve pipeline configuration.
    
    Args:
        layer: "bronze", "silver", "gold", or "full"
        
    Returns:
        JSON config as dictionary
    """
```

---

## Execution Flow

### 1. Config Loading
```python
loader = ConfigLoader()
steps = loader.load("config.json")
```

### 2. Config Validation
```python
validator = ConfigValidator()
validator.validate_config(steps)  # Checks names, outputs, dependencies
```

### 3. Engine Context Creation
```python
context = create_engine_context("pandas")
context.connect()
```

### 4. Pipeline Orchestration
```python
orchestrator = Orchestrator(steps, context, tracker, events)
result = orchestrator.run()
```

### 5. Result Access
```python
datasets = result.data_map  # Dict of dataset_name -> DataFrame
```

---

## Data Schemas

### Bronze Energy
```
facility_id: str         (e.g., "FAC001")
date: str                (e.g., "2024-01-01")
consumption_kwh: float   (nullable, may contain outliers)
peak_demand_kw: float    (nullable)
```

### Bronze Weather
```
facility_id: str
date: str
temperature_avg: float
humidity_pct: int
```

### Bronze Maintenance
```
facility_id: str
maintenance_date: str
maintenance_type: str    (Preventive, Corrective, Inspection, Emergency)
cost_usd: float          (nullable, may be negative in raw data)
```

### Silver Energy
```
facility_id: str
date: str
consumption_kwh: float   (no nulls, range: 0-10,000)
peak_demand_kw: float    (no nulls)
```

### Silver Energy Weather
```
facility_id: str
date: str
consumption_kwh: float
peak_demand_kw: float
temperature_avg: float
humidity_pct: int
```

### Silver Maintenance
```
facility_id: str
maintenance_date: str
maintenance_type: str
cost_usd: float          (no nulls, >= 0)
```

### Gold Daily Summary
```
facility_id: str
total_days: int
total_consumption_kwh: float
avg_daily_consumption_kwh: float
max_peak_demand_kw: float
avg_temperature: float
```

### Gold Efficiency Report
```
facility_id: str
total_consumption_kwh: float
avg_daily_consumption_kwh: float
max_peak_demand_kw: float
efficiency_kwh_per_day: float
demand_efficiency_ratio: float
```

### Gold Maintenance Costs
```
facility_id: str
maintenance_count: int
total_maintenance_cost_usd: float
avg_maintenance_cost_usd: float
max_maintenance_cost_usd: float
```

---

## Design Patterns

### 1. Medallion Architecture
- **Bronze**: Raw, immutable source data
- **Silver**: Cleaned, validated, joined data
- **Gold**: Aggregated business metrics

### 2. Config-Driven Execution
- Entire pipeline defined in JSON
- No hard-coded transformations
- Easy to version control and modify

### 3. SQL-Based Transformations
- Use SQL for data transformations
- Works with both Pandas and Spark
- Familiar syntax for analysts

### 4. Dependency Resolution
- DAG automatically built from inputs/outputs
- Steps execute in correct order
- Parallel execution where possible

### 5. Data Lineage Tracking
- Tracker captures all transformations
- Schema changes recorded
- Timing metrics collected

---

## Quality Assurance

### Data Quality Rules

**Bronze Layer**:
- ❌ No validation
- ❌ Preserves nulls
- ❌ Includes outliers

**Silver Layer**:
- ✅ Null checks: `WHERE column IS NOT NULL`
- ✅ Range validation: `WHERE value > 0 AND value < 10000`
- ✅ Non-negative: `WHERE cost >= 0`
- ✅ Join validation: Inner joins ensure matching records

**Gold Layer**:
- ✅ Aggregation validation: `GROUP BY` ensures proper grouping
- ✅ Division by zero prevention: `NULLIF(denominator, 0)`
- ✅ Type casting: `CAST(x AS FLOAT)` for calculations

---

## Performance Considerations

### Pandas Engine (Default)
- ✅ In-memory processing
- ✅ Fast for small-medium datasets (< 1M rows)
- ✅ SQL via pandasql library
- ⚠️ Limited by RAM

### Spark Engine (Optional)
- ✅ Distributed processing
- ✅ Handles large datasets (> 1M rows)
- ✅ SQL via Spark SQL
- ✅ Out-of-core processing
- ⚠️ Overhead for small datasets

### Optimization Tips
1. Use Parquet for large datasets
2. Filter early (push down to Bronze/Silver)
3. Partition by facility_id for parallel processing
4. Cache intermediate results if reused
5. Use Spark for > 1M rows

---

## Extension Points

### Add New Data Source
1. Create CSV in `data/`
2. Add ingestion step to bronze_config.json
3. Add cleaning step to silver_config.json
4. Add joins in silver layer

### Add New Transformation
1. Define SQL query
2. Add step to appropriate config
3. Specify inputs/outputs
4. Run validation

### Add New Aggregation
1. Define aggregation SQL
2. Add to gold_config.json
3. Add publish step if needed

### Add New Output Format
1. Add publish step with desired format
2. Specify params (e.g., `{"orient": "records"}`)
3. ODIBI CORE handles format automatically

---

## Testing Strategy

### Unit Tests
```python
def test_bronze_ingestion():
    """Test bronze layer loads all files."""
    
def test_silver_quality():
    """Test silver layer applies quality rules."""
    
def test_gold_aggregations():
    """Test gold layer calculates correct metrics."""
```

### Integration Tests
```python
def test_full_pipeline():
    """Test end-to-end pipeline execution."""
    
def test_output_files():
    """Test files written to correct locations."""
```

### Data Quality Tests
```python
def test_no_nulls():
    """Verify silver data has no nulls."""
    
def test_range_validation():
    """Verify values within expected ranges."""
    
def test_row_counts():
    """Verify expected row counts after filtering."""
```

---

## Best Practices

### Configuration
- ✅ Use descriptive step names
- ✅ Add metadata for documentation
- ✅ Specify all inputs/outputs explicitly
- ✅ Use consistent naming conventions

### SQL Queries
- ✅ Format SQL for readability
- ✅ Use explicit column names (avoid `SELECT *` in production)
- ✅ Add ORDER BY for deterministic results
- ✅ Handle null values explicitly

### Data Quality
- ✅ Define quality rules in metadata
- ✅ Test silver layer thoroughly
- ✅ Document expected ranges
- ✅ Log rejected records

### Performance
- ✅ Filter early, aggregate late
- ✅ Use appropriate engine for data size
- ✅ Enable caching for reused datasets
- ✅ Monitor memory usage

---

## Troubleshooting

### Common Issues

**Issue**: Config validation fails
- **Solution**: Check step names are unique, outputs are unique, inputs exist

**Issue**: SQL query fails
- **Solution**: Check input aliases match config, verify column names

**Issue**: Out of memory
- **Solution**: Use Spark engine or filter data earlier

**Issue**: Output files not created
- **Solution**: Check file paths are valid, directories exist

---

## References

- [ODIBI CORE SDK Documentation](../sdk/__init__.py)
- [ConfigLoader Documentation](../core/config_loader.py)
- [Orchestrator Documentation](../core/dag_executor.py)
- [Medallion Architecture Pattern](https://www.databricks.com/glossary/medallion-architecture)

---

**Last Updated**: 2025-11-02  
**ODIBI CORE Version**: 1.0  
**Module Version**: 1.0
