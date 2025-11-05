# ODIBI CORE v1.0 - Engineering Plan (Phase Zero)

**Author**: AMP AI Engineering Agent  
**Date**: 2025-11-01  
**Status**: Phase Zero - Architectural Planning  
**Thread**: T-72900eef-bee0-467e-8f40-f70d9a480543

---

## 1. ARCHITECTURE SUMMARY

### 1.1 Mission Statement

ODIBI CORE v1.0 is a **Node-centric, engine-agnostic, config-driven data engineering framework** designed to unify Spark and Pandas execution under a single abstraction layer. It enables data engineers to define pipelines declaratively via configuration (SQL tables or JSON), execute them on either engine with guaranteed behavioral parity, and capture complete execution lineage with truth-preserving snapshots.

The framework's primary goal is to **decouple pipeline logic from execution context**, allowing the same transformation to run on:
- **Pandas** (local development, small datasets, rapid iteration)
- **Spark** (production, distributed processing, cloud-native workloads)

This eliminates the Spark-specific lock-in present in v2 while maintaining compatibility with existing v2 pipelines.

### 1.2 Design Intent

**Core Philosophy:**
1. **Node is Law** - Every operation (connect, ingest, store, transform, publish) is modeled as a discrete `Node` with inputs, outputs, and deterministic behavior
2. **Config Drives All** - Pipelines are data, not code; stored in SQL tables/JSON for versioning, auditing, and dynamic modification
3. **Engine Agnostic** - Node logic is pure; engine-specific code is isolated in `EngineContext` implementations
4. **Truth Preserving** - Every Node execution logs before/after state, schema diffs, row counts, and timing for debugging and compliance
5. **Composable & Replaceable** - Nodes can run independently, be swapped, or replayed without affecting the DAG
6. **Self-Improving** - Execution metadata enables AMP to analyze failures, validate parity, and suggest optimizations

**Why This Matters:**
- v2 requires Databricks/Spark for all operations → v1 enables local Pandas development
- v2 embeds logic in Python classes → v1 externalizes to config tables
- v2 lacks execution snapshots → v1 captures full lineage for audit trails
- v2 couples transformations to engine → v1 enables Spark↔Pandas parity testing

### 1.3 Node Model Application Across Layers

The framework defines **5 canonical Node types** corresponding to data engineering stages:

| Node Type | Layer | Purpose | Example |
|-----------|-------|---------|---------|
| **ConnectNode** | `connect` | Establish database/API/storage connections | PostgreSQL connection with secrets |
| **IngestNode** | `ingest` | Read raw data from sources | Read CSV from ADLS or local file |
| **StoreNode** | `store` | Persist data to Bronze layer | Write Parquet to medallion storage |
| **TransformNode** | `transform` | Apply Silver/Gold logic | Calculate boiler efficiency metrics |
| **PublishNode** | `publish` | Export to downstream systems | Write to Delta Lake or API endpoint |

**Node Execution Flow:**
```
Config → ConfigLoader → Orchestrator → DAG Builder → Node Execution → Tracker → Story
```

Each Node:
- Receives a `data_map` (dict of logical name → DataFrame)
- Reads from `inputs` (references to `data_map` keys)
- Executes engine-specific logic via `EngineContext`
- Writes to `outputs` (new entries in `data_map`)
- Logs pre/post snapshots to `Tracker`
- Updates `NodeState` (PENDING → SUCCESS/FAILED)

**Key Insight:** By standardizing on this contract, new Node types can be registered dynamically without modifying core framework code.

---

## 2. PHASE-BY-PHASE IMPLEMENTATION PLAN

### Phase 1: Foundation & Scaffolding (Week 1)

**Objective:** Establish project structure, base classes, and testing infrastructure

**Deliverables:**
1. **Repo Scaffold**
   - Create `odibi_core/` directory structure per spec
   - Setup `pyproject.toml` with dependencies (pandas, pyspark, duckdb, iapws, pytest)
   - Configure `pytest.ini` with test discovery patterns
   - Initialize git repo with `.gitignore` (exclude `*.db`, `*.parquet`, `__pycache__`)

2. **Base Abstractions**
   - `core/node.py`: `NodeBase` abstract class with `run()` method
   - `core/node.py`: `NodeState` enum (PENDING, SUCCESS, FAILED, RETRY)
   - `core/events.py`: Event emitter for pipeline hooks (on_start, on_complete, on_error)
   - `core/tracker.py`: Stub implementation for snapshot logging

3. **Engine Context Contracts**
   - `engine/base_context.py`: `EngineContext` ABC with abstract methods
   - `engine/pandas_context.py`: Stub implementation (DuckDB + Pandas)
   - `engine/spark_context.py`: Stub implementation (PySpark session management)

4. **Testing Harness**
   - `tests/conftest.py`: Shared fixtures (sample DataFrames, mock configs)
   - `tests/test_node_base.py`: Verify NodeState transitions
   - `tests/test_engine_contracts.py`: Ensure both engines implement required methods

**Success Criteria:**
- All base classes importable without errors
- `pytest` runs with 0 failures (tests may be minimal stubs)
- Directory structure matches spec exactly

---

### Phase 2: Engine Contexts (Week 2)

**Objective:** Fully implement Pandas and Spark engine contexts with parity

**Deliverables:**

1. **PandasEngineContext** (`engine/pandas_context.py`)
   - `__init__(secrets=None)`: Store secrets callable/dict
   - `connect(**kwargs)`: No-op for Pandas (returns self)
   - `read(source, **kwargs)`: Support CSV, Parquet, SQLite, DuckDB SQL
   - `write(df, target, **kwargs)`: Write to Parquet, CSV, SQLite
   - `execute_sql(query, **kwargs)`: Use DuckDB to query DataFrames
   - `register_temp(name, df)`: Register Pandas DF in DuckDB context
   - `get_secret(key)`: Resolve from secrets dict/callable
   - Helper: `collect_sample(df, n=5)`: Return head(n)

2. **SparkEngineContext** (`engine/spark_context.py`)
   - `__init__(secrets=None, spark_config=None)`: Initialize SparkSession
   - `connect(**kwargs)`: Setup Azure storage account keys if secrets provided
   - `read(source, **kwargs)`: Support Parquet, Delta, JDBC, CSV
   - `write(df, target, **kwargs)`: Write to Delta/Parquet with mode overwrite/append
   - `execute_sql(query, **kwargs)`: Use `spark.sql(query)`
   - `register_temp(name, df)`: Call `df.createOrReplaceTempView(name)`
   - `get_secret(key)`: Resolve from secrets (e.g., `dbutils.secrets.get()` in Databricks)
   - Helper: `collect_sample(df, n=5)`: Return `df.limit(n).toPandas()`

3. **Parity Tests**
   - `tests/test_engine_parity.py`:
     - Create identical DataFrame in both engines
     - Write to temp storage
     - Read back and compare row counts
     - Execute SQL query and validate results match
     - Test temp table registration

**Success Criteria:**
- Both engines can read/write Parquet files
- Both engines execute SQL queries returning identical results
- Secret injection works for both dict and callable patterns
- `collect_sample()` returns Pandas DataFrame in both cases

---

### Phase 3: Config Loader & Validation (Week 3)

**Objective:** Load pipeline definitions from SQL/JSON and validate correctness

**Deliverables:**

1. **ConfigLoader** (`core/config_loader.py`)
   - `load(source_uri)`: Detect source type (SQLite, JSON, CSV)
   - Parse into `Step` dataclass with fields:
     ```python
     @dataclass
     class Step:
         layer: str  # connect, ingest, store, transform, publish
         name: str
         type: str   # sql, function, config_op, api
         engine: str # pandas, spark
         value: str  # SQL text or function reference
         params: dict
         inputs: dict  # logical_name -> dataset_key
         outputs: dict # logical_name -> dataset_key
         metadata: dict
     ```
   - Support SQLite schema from AGENTS.md (ingestion_source_config, transformation_config)
   - Support JSON array format for version control

2. **Config Validation** (`core/config_validator.py`)
   - `validate_config(steps: List[Step])`:
     - Ensure all `output` keys are unique across steps
     - Detect circular dependencies (build dependency graph, check for cycles)
     - Verify `inputs` reference previously defined `outputs`
     - Validate layer ordering (Connect before Ingest, Ingest before Transform)
     - Check engine is valid (pandas/spark)
     - Validate step types (sql, function, etc.)

3. **Tests**
   - `tests/test_config_loader.py`:
     - Load valid config from SQLite
     - Load valid config from JSON
     - Handle missing files gracefully
   - `tests/test_config_validator.py`:
     - Detect duplicate outputs
     - Detect circular dependency
     - Catch undefined inputs

**Success Criteria:**
- Can load 59-source Energy Efficiency config from `odibi_config_local.db`
- Validation detects all error types with clear messages
- Config loaded in <100ms for 100-step pipeline

---

### Phase 4: Core Nodes Implementation (Week 4)

**Objective:** Implement all 5 canonical Node types

**Deliverables:**

1. **ConnectNode** (`nodes/connect_node.py`)
   - Initialize connection via `context.connect(**params)`
   - Store connection metadata in tracker
   - No data_map inputs/outputs (side-effect only)

2. **IngestNode** (`nodes/ingest_node.py`)
   - Read data: `df = context.read(step.value, **step.params)`
   - Write to data_map: `data_map[step.outputs['data']] = df`
   - Log row count and schema

3. **StoreNode** (`nodes/store_node.py`)
   - Read from data_map: `df = data_map[step.inputs['data']]`
   - Write to storage: `context.write(df, step.value, **step.params)`
   - Log write location and row count

4. **TransformNode** (`nodes/transform_node.py`)
   - Support two modes:
     - **SQL Transform**: Register inputs as temp tables, execute SQL, capture result
     - **Function Transform**: Import Python function from registry, call with inputs
   - Example SQL: `SELECT * FROM bronze WHERE efficiency > 80`
   - Example function: `functions.thermo.steam.calc_enthalpy`

5. **PublishNode** (`nodes/publish_node.py`)
   - Similar to StoreNode but targets external systems
   - Could write to Delta, API endpoint, or database

6. **Node Registry** (`nodes/__init__.py`)
   - `NODE_REGISTRY = {'connect': ConnectNode, 'ingest': IngestNode, ...}`
   - `register_node(name)` decorator for extensibility

7. **Tests**
   - `tests/nodes/test_ingest_node.py`: Verify read from CSV
   - `tests/nodes/test_transform_node.py`: Test SQL and function transforms
   - `tests/nodes/test_store_node.py`: Verify write to Parquet

**Success Criteria:**
- All 5 Nodes execute successfully on both Pandas and Spark
- SQL transforms produce identical results on both engines
- Function transforms import and execute correctly
- Nodes update NodeState properly

---

### Phase 5: Orchestrator & DAG Execution (Week 5)

**Objective:** Build pipeline DAG and execute Nodes in dependency order

**Deliverables:**

1. **Orchestrator** (`core/orchestrator.py`)
   ```python
   class Orchestrator:
       def __init__(self, steps, context, tracker, events):
           self.steps = steps
           self.context = context
           self.tracker = tracker
           self.events = events
           self.data_map = {}
       
       def build_dag(self):
           # Create dependency graph from inputs/outputs
           # Topological sort for execution order
       
       def run(self):
           # For each step in topological order:
           #   1. Instantiate Node from registry
           #   2. Call node.run(data_map)
           #   3. Update tracker
           #   4. Emit events
   ```

2. **DAG Builder** (part of Orchestrator)
   - Parse `inputs` and `outputs` to build directed graph
   - Detect cycles using DFS
   - Return execution order via topological sort

3. **Lineage Export** (`core/lineage.py`)
   - After pipeline completes, export JSON:
     ```json
     {
       "pipeline_id": "energy_efficiency_bronze",
       "steps": [
         {"name": "ingest_boiler_data", "inputs": [], "outputs": ["raw_boiler"], "duration_ms": 45},
         {"name": "transform_silver", "inputs": ["raw_boiler"], "outputs": ["silver_boiler"], "duration_ms": 120}
       ],
       "total_duration_ms": 165
     }
     ```

4. **Tests**
   - `tests/test_orchestrator.py`:
     - Execute 3-step linear pipeline
     - Execute branching pipeline (1 ingest → 2 transforms)
     - Detect circular dependency
     - Verify data_map propagates correctly

**Success Criteria:**
- 10-step pipeline executes in correct order
- Circular dependencies caught before execution
- Lineage JSON validates against schema
- Execution time tracked per-step

---

### Phase 6: Tracker & Story Generation (Week 6)

**Objective:** Capture execution metadata and generate HTML reports

**Deliverables:**

1. **Tracker Implementation** (`core/tracker.py`)
   - `snapshot(name, df, context)`:
     - Call `context.collect_sample(df, n=10)` to get Pandas DF
     - Extract schema: `[(col, dtype) for col, dtype in df.dtypes.items()]`
     - Compute row count (Pandas: `len(df)`, Spark: `df.count()`)
     - Store timestamp
   - `log_diff(before_snapshot, after_snapshot)`:
     - Compare schemas (added/removed/changed columns)
     - Compare row counts (delta)
   - `get_stats()`: Return all tracked metrics

2. **Story Generator** (`story/generator.py`)
   - `generate_step_story(step_name, tracker_data)`:
     - Create HTML card with:
       - Step name and duration
       - Input/output row counts
       - Schema before/after table
       - Sample data table (first 5 rows)
       - Execution timestamp
   - `generate_pipeline_story(all_steps)`:
     - Create HTML dashboard with all step cards
     - Add DAG visualization (Mermaid or D3.js)
     - Summary statistics (total duration, rows processed)

3. **Tests**
   - `tests/test_tracker.py`:
     - Verify snapshot captures schema
     - Test Pandas and Spark snapshots produce same structure
   - `tests/test_story_generator.py`:
     - Generate HTML and validate structure
     - Check all expected sections present

**Success Criteria:**
- Tracker captures snapshots for both engines
- HTML story renders correctly in browser
- Story includes DAG visualization
- Schema diffs highlight changes

---

### Phase 7: Function Library (Week 7)

**Objective:** Implement domain-specific pure functions for Energy Efficiency

**Deliverables:**

1. **Thermodynamic Functions** (`functions/thermo/steam.py`)
   - `steam_enthalpy_btu_lb(pressure_psia, temp_f)`: Use IAPWS97
   - `feedwater_enthalpy_btu_lb(temp_f)`: Approximation formula
   - Lazy import IAPWS97 with version check

2. **Psychrometric Functions** (`functions/psychro/air.py`)
   - Future placeholder for air property calculations

3. **Unit Conversions** (`functions/physics/units.py`)
   - `convert_pressure(value, from_unit, to_unit)`: Support psig, bar, kPa
   - `convert_temperature(value, from_unit, to_unit)`: Support F, C, K
   - `convert_flow(value, from_unit, to_unit)`: Support CFH, lb/hr, kg/s

4. **Safe Math Ops** (`functions/math/safe_ops.py`)
   - `safe_divide(a, b, default=0)`: Return default if b==0
   - `safe_log(x, default=None)`: Handle x<=0

5. **Function Registry** (`functions/registry.py`)
   - `FUNCTION_REGISTRY = {'thermo.steam_enthalpy': steam_enthalpy_btu_lb, ...}`
   - `resolve_function(name)`: Import and return function by dotted path
   - Used by TransformNode for function-type transforms

6. **Tests**
   - `tests/functions/test_steam.py`: Validate enthalpy calculations
   - `tests/functions/test_units.py`: Test conversion accuracy

**Success Criteria:**
- All functions return correct values (compare to v2)
- Lazy imports work (no import errors if IAPWS97 missing)
- Registry can resolve functions by string path

---

### Phase 8: I/O Readers & Writers (Week 8)

**Objective:** Standardize data I/O across engines

**Deliverables:**

1. **Readers** (`io/readers.py`)
   - Abstract: `BaseReader(EngineContext)`
   - `CsvReader`: Pandas uses `pd.read_csv()`, Spark uses `spark.read.csv()`
   - `ParquetReader`: Both support native Parquet
   - `SqlReader`: Execute query and return DataFrame
   - `DeltaReader`: Spark-only (Pandas reads as Parquet)

2. **Writers** (`io/writers.py`)
   - Abstract: `BaseWriter(EngineContext)`
   - `ParquetWriter`: Both write native Parquet
   - `DeltaWriter`: Spark native, Pandas converts to Parquet
   - `CsvWriter`: Both support CSV export

3. **Integration**
   - IngestNode uses Readers
   - StoreNode/PublishNode use Writers
   - Engine context handles engine-specific API calls

4. **Tests**
   - `tests/io/test_readers.py`: Read CSV in both engines, compare
   - `tests/io/test_writers.py`: Write Parquet, read back, validate

**Success Criteria:**
- Both engines read/write identical file formats
- Delta Lake handled gracefully (Spark native, Pandas as Parquet)
- Large files (>1GB) handled without memory overflow (test chunking)

---

### Phase 9: Parity Testing Framework (Week 9)

**Objective:** Automated Spark↔Pandas validation

**Deliverables:**

1. **Parity Test Runner** (`tests/parity/test_runner.py`)
   ```python
   def run_parity_test(config_path, test_data_path):
       # Load config
       # Execute pipeline with PandasEngineContext
       # Execute pipeline with SparkEngineContext
       # Compare outputs:
       #   - Row counts
       #   - Schemas
       #   - Sample row values (sorted for determinism)
       # Return ParityReport
   ```

2. **ParityReport** (`tests/parity/report.py`)
   - Compare row counts (must match exactly)
   - Compare schemas (column names, types)
   - Compare sample data (first 100 rows after sorting)
   - Compute percentage difference for numeric columns
   - Generate HTML report with pass/fail per step

3. **Example Test**
   - `tests/parity/test_energy_efficiency.py`:
     - Run Bronze ingestion in both engines
     - Run Silver transformation in both engines
     - Validate efficiency calculations match within 0.01%

4. **CI Integration**
   - Add GitHub Actions workflow
   - Run parity tests on every PR
   - Fail if row counts differ or schema mismatch

**Success Criteria:**
- Energy Efficiency pipeline passes parity test
- Report clearly shows which steps differ
- Runs in <5 minutes for full pipeline

---

### Phase 10: Documentation & Examples (Week 10)

**Objective:** Comprehensive docs for users and AMP

**Deliverables:**

1. **README.md**
   - Quick Start (install, run demo)
   - Architecture overview
   - Config schema reference
   - Engine comparison table

2. **LearnODIBI_Guide_v1.md**
   - Node model explanation
   - Step-by-step pipeline building
   - Example: Build 3-step bronze pipeline
   - Example: Add custom function to registry

3. **API Reference** (`docs/api_reference.md`)
   - All public classes and methods
   - Config schema with examples
   - Node contracts

4. **Migration Guide** (`docs/migration_from_v2.md`)
   - Map v2 concepts to v1 Nodes
   - Convert v2 transformation to config
   - Parity checklist

5. **Example Pipeline** (`examples/run_energy_efficiency_demo.py`)
   - Load config from SQLite
   - Execute with Pandas engine
   - Generate HTML story
   - Print summary stats

6. **Story Visuals**
   - Run demo and capture screenshots
   - Embed in LearnODIBI_Guide.md

**Success Criteria:**
- User can run demo in <5 minutes
- All code examples execute without errors
- AMP can read docs and answer user questions

---

## 3. CRITICAL ANALYSIS & REFINEMENTS

### 3.1 Architectural Strengths

| Strength | Rationale |
|----------|-----------|
| **Engine Abstraction** | Clean separation allows adding new engines (Polars, DuckDB-native) without touching Nodes |
| **Config-Driven** | Pipelines become data, enabling version control, A/B testing, and dynamic modification |
| **Node Model** | Composability enables unit testing individual steps, replay on failure, and incremental development |
| **Tracker** | Truth-preserving snapshots critical for debugging, compliance, and AMP self-improvement |
| **Function Library** | Pure functions decoupled from engines enable reuse in non-pipeline contexts (e.g., batch calculators) |

### 3.2 Identified Weaknesses & Proposed Fixes

#### Weakness 1: Spark Lazy Evaluation Handling

**Issue:** Spec mentions using `.toPandas()` for snapshots but doesn't address:
- When to call `.cache()` to avoid re-computation
- How to handle wide transformations that don't fit in memory

**Proposed Fix:**
- Add `SparkEngineContext.cache_checkpoint(df, name)` method
- Tracker snapshots trigger checkpoint automatically after expensive operations
- Add config flag `checkpoint_strategy: auto | manual | never`

#### Weakness 2: Schema Evolution Not Addressed

**Issue:** Config defines static schemas, but real data sources add/remove columns

**Proposed Fix:**
- Add `SchemaValidator` class in `core/schema_validator.py`
- Support three modes:
  - `strict`: Fail on schema mismatch
  - `warn`: Log warning, proceed
  - `auto`: Add new columns, fill missing with null
- Store schema versions in tracker for lineage

#### Weakness 3: Error Recovery Strategy Missing

**Issue:** Spec defines `NodeState.RETRY` but no retry logic

**Proposed Fix:**
- Add `retry_config` to Step:
  ```python
  retry_config = {
      'max_attempts': 3,
      'backoff_seconds': [10, 60, 300],
      'retry_on': ['NetworkError', 'TimeoutError']
  }
  ```
- Orchestrator implements retry loop with exponential backoff
- Tracker logs all retry attempts for analysis

#### Weakness 4: Parallel Execution Not Specified

**Issue:** Orchestrator executes sequentially, but independent branches could run in parallel

**Proposed Fix:**
- Add `execution_mode` parameter to Orchestrator:
  - `sequential`: Current behavior
  - `parallel`: Use `ThreadPoolExecutor` for independent subgraphs
- DAG builder identifies parallel-safe subgraphs
- Pandas parallelism limited by GIL (use multiprocessing for CPU-bound tasks)
- Spark parallelism handled natively

#### Weakness 5: Secrets Management Overly Simplistic

**Issue:** Spec says "framework does not manage secrets" but production needs key rotation, audit logging

**Proposed Refinement:**
- Add `SecretProvider` interface:
  ```python
  class SecretProvider(ABC):
      @abstractmethod
      def get_secret(self, key: str) -> str: pass
      def log_access(self, key: str): pass  # Audit trail
  ```
- Implementations: `DictSecretProvider`, `DbusecretsProvider`, `AzureKeyVaultProvider`
- Tracker logs which secrets were accessed (key names only, not values)

#### Weakness 6: Function Versioning Not Addressed

**Issue:** If `steam_enthalpy()` formula changes, old pipelines may produce different results

**Proposed Fix:**
- Add `version` field to function registry:
  ```python
  FUNCTION_REGISTRY = {
      'thermo.steam_enthalpy': {'v1.0': steam_enthalpy_v1, 'v1.1': steam_enthalpy_v1_1}
  }
  ```
- Config specifies function version: `value: "thermo.steam_enthalpy@v1.0"`
- Default to latest if no version specified

#### Weakness 7: Memory Management for Large DataFrames

**Issue:** Pandas `collect_sample()` on 1TB Spark DataFrame will OOM

**Proposed Fix:**
- Add intelligent sampling in SparkEngineContext:
  ```python
  def collect_sample(self, df, n=5):
      row_count = df.count()
      if row_count < 10000:
          return df.limit(n).toPandas()
      else:
          # Stratified sample for large datasets
          return df.sample(fraction=n/row_count).limit(n).toPandas()
  ```

---

## 4. PARITY AND VALIDATION STRATEGY

### 4.1 What Parity Means

**Definition:** Spark and Pandas engines produce identical results for the same config, within acceptable tolerance.

**Scope:**
- **Exact Match**: Row counts, column names, column order
- **Type Match**: Data types (with known mappings: Spark `DoubleType` ↔ Pandas `float64`)
- **Value Match**: Numeric values within 0.01% tolerance (floating-point precision)
- **Order Invariant**: Row order may differ (sort before comparing)

**Out of Scope:**
- Performance parity (Spark expected to be faster on >10M rows)
- Memory usage parity
- Execution plan parity

### 4.2 Parity Test Levels

#### Level 1: Unit Parity (Per Node)

Test each Node type in isolation:
```python
def test_ingest_node_parity():
    # Setup
    csv_path = "tests/data/sample.csv"
    
    # Pandas execution
    pandas_ctx = PandasEngineContext()
    pandas_node = IngestNode(step, pandas_ctx, tracker, events)
    pandas_df = pandas_node.run({})['output']
    
    # Spark execution
    spark_ctx = SparkEngineContext()
    spark_node = IngestNode(step, spark_ctx, tracker, events)
    spark_df = spark_node.run({})['output'].toPandas()
    
    # Compare
    assert pandas_df.shape == spark_df.shape
    assert list(pandas_df.columns) == list(spark_df.columns)
```

#### Level 2: Pipeline Parity (End-to-End)

Run full config on both engines:
```python
def test_energy_efficiency_bronze_parity():
    config = load_config("bronze_only.json")
    
    # Run on Pandas
    pandas_results = Orchestrator(config, PandasEngineContext(), ...).run()
    
    # Run on Spark
    spark_results = Orchestrator(config, SparkEngineContext(), ...).run()
    
    # Compare all outputs
    for key in pandas_results.data_map.keys():
        compare_dataframes(pandas_results[key], spark_results[key].toPandas())
```

#### Level 3: SQL Parity (DuckDB vs Spark SQL)

Validate SQL transforms produce identical results:
```python
def test_sql_transform_parity():
    query = "SELECT asset, AVG(efficiency) as avg_eff FROM bronze GROUP BY asset"
    
    # Pandas (DuckDB)
    pandas_ctx.register_temp("bronze", bronze_df)
    pandas_result = pandas_ctx.execute_sql(query)
    
    # Spark
    spark_ctx.register_temp("bronze", bronze_spark_df)
    spark_result = spark_ctx.execute_sql(query).toPandas()
    
    # Compare (sorted by asset for determinism)
    pd.testing.assert_frame_equal(
        pandas_result.sort_values('asset').reset_index(drop=True),
        spark_result.sort_values('asset').reset_index(drop=True),
        atol=0.0001
    )
```

#### Level 4: Function Parity (Pure Functions)

Ensure functions produce same output regardless of engine:
```python
def test_steam_enthalpy_parity():
    # Test on scalar values
    pressure, temp = 150.0, 600.0
    result = steam_enthalpy_btu_lb(pressure, temp)
    assert 1200 < result < 1400  # Expected range
    
    # Test vectorized (Pandas)
    df = pd.DataFrame({'P': [150, 160, 170], 'T': [600, 610, 620]})
    df['h'] = df.apply(lambda r: steam_enthalpy_btu_lb(r.P, r.T), axis=1)
    
    # Test Spark UDF
    spark_udf = F.udf(steam_enthalpy_btu_lb, DoubleType())
    spark_df = spark.createDataFrame(df[['P', 'T']])
    spark_df = spark_df.withColumn('h', spark_udf('P', 'T'))
    
    # Compare
    assert df['h'].tolist() == spark_df.toPandas()['h'].tolist()
```

### 4.3 Automated Parity CI

**GitHub Actions Workflow:**
```yaml
name: Parity Tests
on: [pull_request]
jobs:
  parity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -e .[test]
      - name: Run parity tests
        run: pytest tests/parity/ -v --tb=short
      - name: Generate parity report
        run: python tests/parity/generate_report.py
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: parity-report
          path: parity_report.html
```

### 4.4 Known Parity Challenges

| Challenge | Mitigation |
|-----------|------------|
| **Floating-point precision** | Use `atol=0.0001` in comparisons |
| **Datetime timezones** | Normalize all timestamps to UTC |
| **String case sensitivity** | DuckDB is case-insensitive for column names, Spark isn't → use exact casing |
| **NULL handling** | DuckDB treats empty string ≠ NULL, Spark may differ → explicit `fillna()` |
| **Aggregation order** | Always sort results before comparing |

---

## 5. TESTING AND QUALITY PLAN

### 5.1 Test Pyramid

```
         /\
        /E2E\         10 tests  - Full pipeline parity tests
       /------\
      /Integr.\      30 tests  - Multi-node workflows
     /----------\
    / Unit Tests \   100 tests - Individual functions/classes
   /--------------\
```

### 5.2 Test Categories

#### 5.2.1 Unit Tests (100 tests)

**Core (`tests/core/`):**
- `test_node.py`: NodeBase state transitions, abstract methods
- `test_config_loader.py`: Load from SQLite/JSON/CSV, error handling
- `test_config_validator.py`: Duplicate detection, cycle detection, input validation
- `test_orchestrator.py`: DAG building, topological sort
- `test_tracker.py`: Snapshot capture, diff calculation

**Nodes (`tests/nodes/`):**
- `test_connect_node.py`: Connection initialization
- `test_ingest_node.py`: Read CSV/Parquet/SQL
- `test_store_node.py`: Write Parquet/CSV
- `test_transform_node.py`: SQL and function transforms
- `test_publish_node.py`: External writes

**Engine (`tests/engine/`):**
- `test_pandas_context.py`: All EngineContext methods
- `test_spark_context.py`: All EngineContext methods
- `test_engine_parity.py`: Same operations on both engines

**Functions (`tests/functions/`):**
- `test_steam.py`: Enthalpy calculations (compare to IAPWS97 reference)
- `test_units.py`: Conversion accuracy (use known values)
- `test_safe_ops.py`: Division by zero, log(0) handling

**I/O (`tests/io/`):**
- `test_readers.py`: Read from all supported formats
- `test_writers.py`: Write to all supported formats

#### 5.2.2 Integration Tests (30 tests)

**Multi-Node Workflows (`tests/integration/`):**
- `test_bronze_pipeline.py`: Ingest → Store
- `test_silver_pipeline.py`: Ingest → Transform → Store
- `test_branching_pipeline.py`: 1 ingest → 2 parallel transforms
- `test_error_handling.py`: Missing file, invalid SQL, function error

**Config-Driven (`tests/integration/`):**
- `test_energy_efficiency_bronze.py`: Full bronze layer (59 sources)
- `test_energy_efficiency_silver.py`: Full silver layer (51 transforms)

#### 5.2.3 End-to-End Tests (10 tests)

**Parity (`tests/parity/`):**
- `test_bronze_parity.py`: Full bronze layer Pandas vs Spark
- `test_silver_parity.py`: Full silver layer Pandas vs Spark
- `test_sql_parity.py`: Complex SQL queries
- `test_function_parity.py`: All registered functions

**Performance (`tests/performance/`):**
- `test_pandas_performance.py`: Verify >10k records/sec for 1M rows
- `test_spark_performance.py`: Verify 10M rows processed in <5min

### 5.3 Quality Gates

**Pre-Commit:**
- `black` formatting enforced
- `mypy` type checking passes
- No `print()` statements in core code (use logging)

**PR Merge Criteria:**
- All unit tests pass
- Code coverage >85%
- At least 1 integration test added for new features
- Docstrings present for all public methods

**Release Criteria:**
- All parity tests pass
- Performance benchmarks meet targets
- Documentation updated
- Migration guide from v2 completed

### 5.4 Test Data Management

**Fixtures (`tests/fixtures/`):**
- `sample_bronze.csv`: 100 rows of boiler data
- `sample_tags.csv`: 8 tag definitions
- `sample_hhv.csv`: Heating value lookup
- `sample_config.json`: 5-step pipeline config

**Generators (`tests/generators/`):**
- `generate_test_data.py`: Create synthetic time-series data
- `generate_config.py`: Programmatically build test configs

**Cleanup:**
- All tests use temporary directories (`tmpdir` fixture)
- Spark tests stop SparkSession in teardown
- No test artifacts committed to git

---

## 6. DOCUMENTATION AND TEACHING PLAN

### 6.1 Documentation Structure

```
docs/
  README.md                      # Quick start, install
  architecture.md                # Node model, engine abstraction
  config_reference.md            # All config fields with examples
  api_reference.md               # Auto-generated from docstrings
  migration_from_v2.md           # v2 → v1 mapping
  LearnODIBI_v1_Guide.md         # Tutorial with examples
  troubleshooting.md             # Common errors and fixes
  contributing.md                # How to add custom Nodes/functions
```

### 6.2 Teaching Approach (LearnODIBI_v1_Guide.md)

**Chapter 1: Understanding Nodes**
- What is a Node? (visual diagram)
- The 5 canonical Node types
- Example: Dissect an IngestNode execution
- Exercise: Write a custom TransformNode

**Chapter 2: Config-Driven Pipelines**
- Why config vs code?
- Config schema walkthrough
- Example: Define a 3-step pipeline in JSON
- Exercise: Convert a Python script to config

**Chapter 3: Engine Abstraction**
- What is an EngineContext?
- When to use Pandas vs Spark
- Example: Run same pipeline on both engines
- Exercise: Add a new engine (DuckDB-native)

**Chapter 4: Transformation Patterns**
- SQL transforms (filtering, aggregation, joins)
- Function transforms (custom calculations)
- Pivot-calculate-unpivot pattern
- Example: Energy efficiency boiler metrics
- Exercise: Build a silver layer transform

**Chapter 5: Debugging with Tracker**
- How snapshots work
- Reading the HTML story
- Identifying data quality issues
- Example: Debug a failing transform
- Exercise: Find schema drift in a pipeline

**Chapter 6: Production Deployment**
- Secrets management best practices
- Error handling and retry logic
- Monitoring and alerting
- Example: Deploy to Databricks
- Exercise: Setup CI/CD with GitHub Actions

### 6.3 Visual Aids

**Generated Automatically:**
1. **DAG Diagrams** - Mermaid graphs from config
2. **Story HTML** - Execution reports with sample data
3. **Schema Evolution** - Side-by-side before/after tables

**Static Diagrams (created by AMP):**
1. **Node Lifecycle** - State transitions flowchart
2. **Engine Architecture** - Layered diagram showing abstraction
3. **Config Flow** - From SQLite → ConfigLoader → Orchestrator → Nodes

### 6.4 API Reference (Auto-Generated)

Use `pdoc` or `sphinx` to generate from docstrings:
```bash
pdoc --html --output-dir docs/api odibi_core
```

**Required Docstring Quality:**
- All public classes: Purpose, example usage
- All public methods: Args (with types), Returns, Raises
- All config fields: Description, example value, validation rules

### 6.5 Example Projects

**Example 1: Simple Bronze Pipeline**
```python
# examples/simple_bronze.py
config = {
    "steps": [
        {"layer": "ingest", "name": "read_csv", "type": "config_op", 
         "engine": "pandas", "value": "data/sample.csv", 
         "outputs": {"data": "raw_data"}},
        {"layer": "store", "name": "write_parquet", "type": "config_op",
         "engine": "pandas", "value": "output/bronze.parquet",
         "inputs": {"data": "raw_data"}}
    ]
}
orchestrator = Orchestrator(config, PandasEngineContext(), tracker, events)
orchestrator.run()
```

**Example 2: SQL Transform**
```python
# examples/sql_transform.py
config = {
    "steps": [
        {"layer": "ingest", "name": "read_bronze", ...},
        {"layer": "transform", "name": "filter_high_efficiency", 
         "type": "sql", "engine": "pandas",
         "value": "SELECT * FROM bronze WHERE efficiency > 80",
         "inputs": {"bronze": "raw_data"}, 
         "outputs": {"data": "filtered_data"}},
        {"layer": "store", "name": "write_silver", ...}
    ]
}
```

**Example 3: Function Transform**
```python
# examples/function_transform.py
config = {
    "steps": [
        {"layer": "transform", "name": "calc_enthalpy", 
         "type": "function", "engine": "pandas",
         "value": "thermo.steam.calc_enthalpy",
         "inputs": {"data": "raw_data"}, 
         "outputs": {"data": "enriched_data"},
         "params": {"pressure_col": "P", "temp_col": "T", "output_col": "h"}}
    ]
}
```

### 6.6 AMP Self-Improvement

**How AMP Uses Documentation:**
1. Reads `LearnODIBI_v1_Guide.md` to answer user questions
2. Consults `troubleshooting.md` when errors occur
3. Uses `api_reference.md` to suggest correct function signatures
4. Reads execution stories to identify data quality issues

**Feedback Loop:**
- User encounters error → AMP reads story + logs → Suggests fix
- AMP notices repeated pattern → Proposes adding to `troubleshooting.md`
- User asks "how do I..." → AMP drafts tutorial section

---

## 7. RISKS AND MITIGATIONS

### 7.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Spark/Pandas SQL dialect differences** | High | High | Maintain SQL compatibility test suite; use common subset of SQL; flag unsupported syntax early |
| **Floating-point parity failures** | Medium | Medium | Define tolerance levels (0.01%); document known precision limits; add config flag for strict mode |
| **Memory overflow on large datasets** | Medium | High | Implement intelligent sampling; add memory profiling to tracker; document size limits per engine |
| **Dependency conflicts (Spark vs Pandas versions)** | Medium | Medium | Use separate virtual environments for testing; pin major versions; test on multiple Python versions |
| **DuckDB SQL limitations** | Low | Medium | Maintain list of unsupported SQL features; suggest Spark for complex queries; add SQL validation |
| **Circular dependency detection bugs** | Low | High | Exhaustive unit tests; use proven graph algorithm (Kahn's); log DAG for manual inspection |
| **Function versioning conflicts** | Low | Medium | Default to latest; warn if deprecated version used; document version compatibility |

### 7.2 Design Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Node abstraction too rigid** | Medium | High | Design plugin system early; gather user feedback; iterate on contracts before 1.0 freeze |
| **Config becomes too complex** | Medium | Medium | Provide JSON schema validation; create config builder UI (future); examples for all common patterns |
| **Performance overhead of abstraction** | Low | Medium | Benchmark against native Pandas/Spark; optimize hot paths; accept <10% overhead as acceptable |
| **Story generation too slow** | Low | Low | Make story generation optional; limit sample size; parallelize HTML generation |
| **Secrets handling insufficient for enterprise** | Medium | High | Provide plugin interface for vault integrations; document integration with Azure Key Vault, AWS Secrets Manager |

### 7.3 Project Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Scope creep** | High | Medium | Freeze features after Phase 10; create backlog for v1.1; strict PR review |
| **Parity testing too time-consuming** | Medium | Medium | Run parity tests nightly, not on every commit; parallelize test execution; cache test data |
| **Documentation lags behind code** | High | Low | Auto-generate API docs; require docstrings in PR checklist; AMP generates draft docs |
| **Migration from v2 too difficult** | Medium | High | Create automated migration tool; provide side-by-side comparison examples; offer migration consulting |
| **Insufficient user adoption** | Low | High | Engage early users for feedback; create video tutorials; present at conferences |

### 7.4 Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking changes in Spark/Pandas APIs** | Medium | High | Pin minor versions; monitor release notes; maintain compatibility matrix |
| **Config database corruption** | Low | High | Add config validation on load; support JSON backup; implement schema migrations |
| **Story HTML too large for browser** | Low | Low | Limit to 100 steps per story; paginate long pipelines; add "lite" mode |
| **Tracker fills disk** | Medium | Medium | Add retention policy (default 30 days); compress old snapshots; add cleanup job |

---

## 8. SUCCESS METRICS

### 8.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Parity Test Pass Rate** | 100% | Automated CI report |
| **Code Coverage** | >85% | `pytest-cov` report |
| **Type Checking** | 0 mypy errors | Pre-commit hook |
| **Pandas Performance** | >10k rows/sec | Benchmark suite |
| **Spark Performance** | <5min for 10M rows | Benchmark suite |
| **API Stability** | <5% breaking changes per release | Semantic versioning |

### 8.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Docstring Coverage** | 100% public APIs | Custom script |
| **Example Execution** | All examples run successfully | Automated test |
| **Zero Secrets Leaks** | No secrets in logs/stories | Security audit |
| **Error Messages** | User-actionable (not stack traces) | Manual review |

### 8.3 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Migration from v2** | 3 pipelines in first month | Manual tracking |
| **New Pipelines** | 10 pipelines built with v1 | Config database query |
| **AMP Assistance** | AMP successfully builds pipeline from description | User feedback |
| **Community Contributions** | 2 custom Nodes added by users | GitHub PRs |

---

## 9. NEXT STEPS AFTER PHASE ZERO

### 9.1 Immediate Actions

1. **Review this plan with stakeholders**
   - Validate assumptions about parity requirements
   - Confirm priority of Pandas vs Spark features
   - Agree on testing strategy

2. **Setup project infrastructure**
   - Create GitHub repo `odibi_core`
   - Configure issue tracking with phase labels
   - Setup CI/CD pipeline

3. **Refine specifications**
   - Address weaknesses identified in Section 3.2
   - Finalize config schema with examples
   - Lock down Node contract signatures

### 9.2 Phase 1 Kickoff Checklist

- [ ] Repo scaffolded with directory structure
- [ ] `pyproject.toml` created with all dependencies
- [ ] Base classes (`NodeBase`, `EngineContext`) implemented
- [ ] First unit test passes
- [ ] README.md has installation instructions

### 9.3 Open Questions for Stakeholders

1. **Performance Targets**: Are the benchmarks (10k rows/sec Pandas, <5min for 10M rows Spark) realistic given hardware constraints?

2. **Parity Tolerance**: Is 0.01% numeric tolerance acceptable, or do we need exact floating-point match?

3. **Delta Lake Support**: Should Pandas read Delta as Parquet (current plan) or attempt native Delta reader?

4. **Secret Management**: Which vault providers are required for initial release (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)?

5. **Migration Timeline**: When is v2 EOL planned? Should v1 support running v2 configs directly?

6. **Deployment Targets**: Beyond Databricks, which platforms must be supported (AWS EMR, GCP Dataproc, local Jupyter)?

---

## 10. CONCLUSION

ODIBI CORE v1.0 represents a **strategic evolution** from v2's Spark-centric, code-first approach to a **dual-engine, config-driven architecture** that prioritizes:

1. **Developer Experience** - Local Pandas development without Databricks dependency
2. **Operational Visibility** - Truth-preserving snapshots for debugging and compliance
3. **Flexibility** - Plugin system for custom Nodes and engines
4. **AI-Readiness** - Structured lineage and stories enable AMP self-improvement

The 10-phase implementation plan balances **incremental delivery** (each phase produces testable artifacts) with **architectural discipline** (no phase depends on unfinished future work).

**Key Innovations:**
- Node model enables compositional reasoning about pipelines
- Engine abstraction decouples logic from execution context
- Parity testing framework ensures Spark↔Pandas correctness
- Story generation provides immediate feedback for data quality

**Risk Mitigation:**
- Identified 7 architectural weaknesses with concrete fixes
- Defined 3-tier testing pyramid (100 unit, 30 integration, 10 E2E)
- Established quality gates for every phase

**Path to Production:**
- Clear migration guide from v2
- Comprehensive documentation with examples
- Automated parity validation in CI
- Performance benchmarks to ensure scalability

**This plan is ready for stakeholder review and Phase 1 implementation.**

---

**Prepared by**: AMP AI Engineering Agent  
**Review Status**: Awaiting Approval  
**Estimated Implementation**: 10 weeks (1 phase per week)  
**Next Phase**: Phase 1 - Foundation & Scaffolding
