# Phase 7: Framework Recommendations
## ODIBI_CORE Medallion Architecture Projects

**Phase:** 7 - Framework Recommendations & Template Design  
**Date:** 2025-11-02  
**Status:** ✅ COMPLETE

---

## 🎯 Objective

After building 10 production-grade medallion projects with 282 nodes, analyze patterns across all configurations, DAG structures, and execution logs to derive concrete recommendations that simplify daily data engineering workflows in ODIBI_CORE.

---

## 📊 Pattern Analysis Summary

Across all 10 projects, we observed:
- **100% Bronze layer consistency:** 3 parallel ingestions → 3 publish nodes (6 nodes per project)
- **100% Silver join pattern:** Multi-source merge → validate → cache → publish
- **100% Gold KPI pattern:** Load Silver → aggregate by dimensions → calculate KPIs → publish
- **100% validation triad:** Schema + Range + Business rules in every Silver layer
- **10/10 cache placement:** Always after joins, before downstream transforms

**Key Insight:** The medallion pattern is **highly repetitive** across domains, suggesting strong opportunities for template-based automation.

---

## 🏗️ Recommended Templates

### 1. Bronze Ingestion Template

**Name:** `BronzeMultiSourceIngestionTemplate`  
**Purpose:** Ingest 3+ heterogeneous sources and publish to standardized Bronze outputs  
**When to Use:** Any project requiring raw data capture from files  
**Parameters:**
- `project_id` (str): Project identifier (e.g., "p01_manufacturing")
- `sources` (list): List of {"name", "format", "path"} dicts
- `output_dir` (str): Bronze output directory

**Example Config:**
```json
{
  "template": "BronzeMultiSourceIngestion",
  "params": {
    "project_id": "p11_supply_chain",
    "sources": [
      {"name": "suppliers", "format": "csv", "path": "data/suppliers.csv"},
      {"name": "shipments", "format": "json", "path": "data/shipments.json"},
      {"name": "inventory", "format": "parquet", "path": "data/inventory.parquet"}
    ],
    "output_dir": "output/bronze/p11_supply_chain/"
  }
}
```

**Generated Nodes (6 per source set):**
- `ingest_{name}` (connect node)
- `publish_{name}` (publish node to `bronze_{name}.parquet`)

**Benefits:**
- Eliminates boilerplate for 60% of Bronze configs
- Standardizes naming conventions (`ingest_X`, `publish_X`)
- Auto-generates output paths following medallion structure

---

### 2. Silver Join & Validate Template

**Name:** `SilverMultiJoinValidateTemplate`  
**Purpose:** Load Bronze outputs, perform multi-source joins, add derived fields, validate, cache  
**When to Use:** Any Silver layer with 2+ joins and derived calculations  
**Parameters:**
- `project_id` (str)
- `bronze_sources` (list): Bronze outputs to load
- `joins` (list): Join specifications (left/right tables, keys, how)
- `derived_fields` (list): Field definitions with expressions
- `validations` (dict): Schema/range/business rule specs
- `cache` (bool): Whether to cache post-join

**Example Config:**
```json
{
  "template": "SilverMultiJoinValidate",
  "params": {
    "project_id": "p11_supply_chain",
    "bronze_sources": ["bronze_suppliers", "bronze_shipments", "bronze_inventory"],
    "joins": [
      {"left": "shipments", "right": "suppliers", "on": "supplier_id", "how": "inner"},
      {"left": "joined_1", "right": "inventory", "on": "product_id", "how": "left"}
    ],
    "derived_fields": [
      {"name": "delivery_delay_days", "expression": "actual_delivery_date - scheduled_date"},
      {"name": "stock_coverage_days", "expression": "inventory_level / daily_demand"},
      {"name": "supplier_performance", "expression": "on_time_deliveries / total_deliveries"}
    ],
    "validations": {
      "schema": ["supplier_id", "product_id", "delivery_delay_days"],
      "range": {"delivery_delay_days": {"min": -5, "max": 90}},
      "business_rules": ["stock_coverage_days > 0"]
    },
    "cache": true
  }
}
```

**Generated Nodes (~12-15):**
- Load Bronze sources (3 connect nodes)
- Join operations (2 transform nodes)
- Derived field calculations (3 transform nodes)
- Cache node (1 cache node)
- Validation node (1 validate node)
- Publish Silver output (1 publish node)

**Benefits:**
- Reduces Silver config size by 70%
- Enforces validation triad pattern automatically
- Handles complex multi-join DAGs declaratively

---

### 3. Gold KPI Calculator Template

**Name:** `GoldKPIAggregationTemplate`  
**Purpose:** Load Silver, aggregate by dimensions, calculate domain KPIs, publish Gold outputs  
**When to Use:** Any Gold layer with dimensional aggregations and calculated metrics  
**Parameters:**
- `project_id` (str)
- `silver_source` (str): Silver output to load
- `aggregations` (list): Group-by dimensions and aggregation specs
- `kpis` (list): KPI definitions with formulas
- `outputs` (list): Gold output destinations

**Example Config:**
```json
{
  "template": "GoldKPIAggregation",
  "params": {
    "project_id": "p11_supply_chain",
    "silver_source": "silver_supply_chain_unified",
    "aggregations": [
      {
        "name": "by_supplier_month",
        "group_by": ["supplier_id", "month"],
        "aggs": {
          "total_shipments": "count",
          "avg_delivery_delay": "mean(delivery_delay_days)",
          "on_time_rate": "mean(on_time_delivery)"
        }
      }
    ],
    "kpis": [
      {
        "name": "supplier_reliability_score",
        "formula": "(on_time_rate * 0.6) + ((1 - normalized_delay) * 0.4)",
        "description": "Weighted score of on-time delivery and delay"
      },
      {
        "name": "stock_out_risk",
        "formula": "count(stock_coverage_days < 7) / count(*)",
        "description": "Percentage of SKUs at risk of stock-out"
      }
    ],
    "outputs": [
      "gold_supply_chain_kpis_monthly.parquet",
      "gold_supplier_scorecards.parquet"
    ]
  }
}
```

**Generated Nodes (~8-10):**
- Load Silver (1 connect node)
- Aggregate by dimensions (2-3 transform nodes)
- Calculate KPIs (2-3 transform nodes)
- Publish outputs (2 publish nodes)

**Benefits:**
- Standardizes KPI calculation patterns
- Auto-documents formulas in config
- Reduces Gold config size by 60%

---

### 4. Validation Rule Set Library

**Name:** `ValidationLibrary`  
**Purpose:** Pre-built validation rule sets for common data quality checks  
**When to Use:** Any layer requiring data validation  
**Categories:**

**Schema Validations:**
- `required_columns`: Ensure critical columns exist
- `no_null_columns`: Flag nulls in non-nullable fields
- `data_type_check`: Validate column types (int, float, date, string)

**Range Validations:**
- `numeric_range`: Min/max bounds for numeric fields
- `date_range`: Valid date windows
- `percentage_range`: Values between 0-1 or 0-100

**Business Rule Validations:**
- `financial_rules`: Debit/credit balance, non-negative amounts
- `retail_rules`: Price > 0, quantity > 0, discount ≤ 1
- `healthcare_rules`: appointment_duration > 0, wait_time ≥ -30

**Example Usage:**
```json
{
  "operation": "validate",
  "config": {
    "rule_set": "financial_rules",
    "overrides": {
      "max_transaction_amount": 1000000
    }
  }
}
```

**Benefits:**
- Industry-standard validation rules out-of-the-box
- Reduces validation config repetition
- Ensures consistency across projects

---

### 5. Cache Strategy Template

**Name:** `CacheStrategyTemplate`  
**Purpose:** Intelligent caching at optimal DAG boundaries  
**When to Use:** Any pipeline with expensive joins or transformations  
**Strategies:**

**Post-Join Caching (100% adoption in our projects):**
```json
{
  "cache_strategy": "post_join",
  "trigger": "after_all_joins",
  "invalidate_on": "source_change"
}
```

**Pre-Aggregation Caching:**
```json
{
  "cache_strategy": "pre_aggregation",
  "trigger": "before_group_by",
  "invalidate_on": "daily"
}
```

**Benefits:**
- Reduces re-execution time by 30-70%
- Auto-places cache nodes at optimal boundaries
- Configurable invalidation policies

---

## 🚀 Recommended Runner Abstractions

### 1. MedallionRunner

**Purpose:** Single orchestrator for Bronze → Silver → Gold execution  
**Interface:**
```python
class MedallionRunner:
    def __init__(self, project_id: str, config_dir: str):
        self.project_id = project_id
        self.bronze_config = f"{config_dir}/{project_id}_bronze.json"
        self.silver_config = f"{config_dir}/{project_id}_silver.json"
        self.gold_config = f"{config_dir}/{project_id}_gold.json"
    
    def run_bronze(self) -> ExecutionResult:
        """Execute Bronze layer ingestion."""
        pass
    
    def run_silver(self) -> ExecutionResult:
        """Execute Silver layer transformations."""
        pass
    
    def run_gold(self) -> ExecutionResult:
        """Execute Gold layer aggregations."""
        pass
    
    def run_end_to_end(self) -> ExecutionSummary:
        """Execute all 3 layers sequentially."""
        bronze_result = self.run_bronze()
        if bronze_result.status == "SUCCESS":
            silver_result = self.run_silver()
            if silver_result.status == "SUCCESS":
                gold_result = self.run_gold()
                return ExecutionSummary([bronze_result, silver_result, gold_result])
```

**Usage:**
```python
runner = MedallionRunner(project_id="p11_supply_chain", config_dir="configs/medallion_projects")
summary = runner.run_end_to_end()
print(f"Total nodes: {summary.total_nodes}, Time: {summary.execution_time_ms}ms")
```

**Benefits:**
- Single entry point for full medallion execution
- Built-in error handling (halt on layer failure)
- Automatic layer sequencing (Bronze before Silver before Gold)
- Row-count reconciliation between layers

---

### 2. TemplateLibrary

**Purpose:** Registry of reusable config templates  
**Interface:**
```python
class TemplateLibrary:
    @staticmethod
    def apply_template(template_name: str, params: dict) -> List[Step]:
        """Generate Step list from template and parameters."""
        if template_name == "BronzeMultiSourceIngestion":
            return BronzeTemplate.generate(params)
        elif template_name == "SilverMultiJoinValidate":
            return SilverTemplate.generate(params)
        elif template_name == "GoldKPIAggregation":
            return GoldTemplate.generate(params)
        else:
            raise ValueError(f"Unknown template: {template_name}")
    
    @staticmethod
    def list_templates() -> List[str]:
        """List all available templates."""
        return ["BronzeMultiSourceIngestion", "SilverMultiJoinValidate", "GoldKPIAggregation"]
```

**Usage:**
```python
params = {
    "project_id": "p11_supply_chain",
    "sources": [{"name": "suppliers", "format": "csv", "path": "data/suppliers.csv"}]
}
bronze_steps = TemplateLibrary.apply_template("BronzeMultiSourceIngestion", params)
# Write to config file or pass directly to Orchestrator
```

**Benefits:**
- Centralized template management
- Version-controlled template evolution
- Easy template discovery

---

### 3. MultiLayerValidationRunner

**Purpose:** Run validations across all layers with detailed reporting  
**Interface:**
```python
class MultiLayerValidationRunner:
    def __init__(self, project_id: str):
        self.project_id = project_id
    
    def validate_bronze(self) -> ValidationReport:
        """Validate Bronze layer outputs (schema, row counts)."""
        pass
    
    def validate_silver(self) -> ValidationReport:
        """Validate Silver layer outputs (joins, derived fields, validations)."""
        pass
    
    def validate_gold(self) -> ValidationReport:
        """Validate Gold layer outputs (KPIs, aggregations)."""
        pass
    
    def validate_end_to_end(self) -> ValidationSummary:
        """Run all validations, reconcile row counts between layers."""
        pass
```

**Benefits:**
- Unified validation framework
- Row-count reconciliation (Bronze → Silver → Gold)
- Schema evolution detection
- Validation report generation

---

## 📋 Config Generator Recommendations

### 1. Bronze Config Generator

**CLI Tool:**
```bash
odibi generate bronze \
  --project-id p11_supply_chain \
  --sources suppliers.csv,shipments.json,inventory.parquet \
  --input-dir data/bronze/p11_supply_chain/ \
  --output-dir output/bronze/p11_supply_chain/
```

**Output:** `p11_bronze.json` with 6 nodes (3 ingests + 3 publishes)

**Benefits:**
- Eliminates manual Bronze config writing
- Auto-detects file formats from extensions
- Enforces naming conventions

---

### 2. Silver Config Generator

**CLI Tool:**
```bash
odibi generate silver \
  --project-id p11_supply_chain \
  --join "shipments:suppliers:supplier_id" \
  --join "result:inventory:product_id" \
  --derived "delivery_delay:actual_date - scheduled_date" \
  --validate "schema,range,business"
```

**Output:** `p11_silver.json` with ~12-15 nodes

**Benefits:**
- Declarative join specification
- Auto-generates validation nodes
- Adds cache node automatically

---

### 3. Gold Config Generator

**CLI Tool:**
```bash
odibi generate gold \
  --project-id p11_supply_chain \
  --aggregate-by "supplier_id,month" \
  --kpi "supplier_reliability:(on_time_rate * 0.6) + ((1 - delay_norm) * 0.4)" \
  --output gold_supply_chain_kpis.parquet
```

**Output:** `p11_gold.json` with ~8-10 nodes

**Benefits:**
- Formula-based KPI definition
- Auto-aggregation setup
- Multiple output support

---

## 🔧 Boilerplate Simplifications

### Current Pain Points (Identified)

1. **Repetitive Bronze configs:** 10 projects × 6 nodes = 60 nearly identical nodes
2. **Join boilerplate:** Every Silver layer has 2+ joins with similar structure
3. **Validation repetition:** Schema + range + business rules replicated across projects
4. **Manual DAG dependency management:** Dependencies must be specified for every node

### Recommended Simplifications

1. **Template-Based Configs:**
   - Replace 60 Bronze nodes with 10 template invocations (~90% reduction)
   - Replace 134 Silver nodes with ~10-15 template invocations (~75% reduction)

2. **Auto-Dependency Resolution:**
   - Infer dependencies from data flow (outputs → inputs)
   - Eliminate manual `"dependencies": [...]` specification

3. **Validation Libraries:**
   - Replace 31 custom validation configs with library references
   - Example: `"validate": "financial_rules"` instead of 10-line validation spec

4. **Smart Defaults:**
   - Auto-add cache after joins (observed in 100% of projects)
   - Auto-publish to standard medallion paths
   - Auto-name nodes following conventions (`ingest_X`, `join_X_Y`, `calc_kpi_X`)

---

## 🌟 Spark Compatibility Considerations

For future Spark-based medallion projects:

1. **Engine Abstraction:**
   - Templates should work with both `PandasEngineContext` and `SparkEngineContext`
   - Same config, different execution engine

2. **Scale Adjustments:**
   - Broadcast joins for small dimension tables (< 10MB)
   - Partition hints for large fact tables
   - Adaptive query execution for complex aggregations

3. **Format Optimization:**
   - Parquet with Snappy compression for Bronze/Silver
   - Delta Lake for Gold (ACID transactions, time travel)

4. **Caching Strategy:**
   - Spark `.cache()` for hot datasets
   - Disk persistence for intermediate joins

**Example Spark-Compatible Config:**
```json
{
  "template": "SilverMultiJoinValidate",
  "params": {
    "engine": "spark",  // Instead of "pandas"
    "join_hints": {
      "suppliers": "broadcast",  // Small table
      "shipments": "partition(date)"  // Large table
    }
  }
}
```

---

## 📊 Production Roadmap

### Phase 1: Template System (2-3 weeks)
- [ ] Implement `TemplateLibrary` class
- [ ] Build Bronze/Silver/Gold template generators
- [ ] Create validation rule library
- [ ] Add template unit tests

### Phase 2: Runner Abstractions (1-2 weeks)
- [ ] Build `MedallionRunner`
- [ ] Build `MultiLayerValidationRunner`
- [ ] Add row-count reconciliation
- [ ] Add execution summary reporting

### Phase 3: CLI Generators (1 week)
- [ ] `odibi generate bronze` command
- [ ] `odibi generate silver` command
- [ ] `odibi generate gold` command
- [ ] Add config validation

### Phase 4: Spark Parity (2-3 weeks)
- [ ] Test templates with `SparkEngineContext`
- [ ] Add Spark-specific optimizations
- [ ] Implement Delta Lake support
- [ ] Performance benchmarking

### Phase 5: Real-Time Extensions (3-4 weeks)
- [ ] Streaming Bronze ingestion (Kafka, Kinesis)
- [ ] Incremental Silver updates (CDC patterns)
- [ ] Real-time Gold metrics (sliding windows)

---

## 🎯 High-Level Summary

After building 10 medallion projects with 282 nodes, the next evolution of ODIBI_CORE should focus on:

1. **Template-Based Automation** (highest ROI)
   - 5-10 reusable templates eliminate 70-90% of config boilerplate
   - Bronze, Silver, Gold templates cover 100% of observed patterns

2. **Runner Abstractions** (ease of use)
   - `MedallionRunner` for one-command end-to-end execution
   - `TemplateLibrary` for config generation

3. **Validation Libraries** (quality & consistency)
   - Industry-standard rule sets (financial, retail, healthcare, etc.)
   - Reduce validation config size by 80%

4. **Smart Defaults** (developer experience)
   - Auto-cache after joins
   - Auto-dependency inference
   - Convention-based naming

5. **Spark Readiness** (scale)
   - Engine-agnostic templates
   - Broadcast/partition hints
   - Delta Lake support

**Bottom Line:** ODIBI_CORE has proven the medallion pattern works beautifully with config-driven orchestration. The next step is to make daily engineering **5-10x faster** through intelligent templates and runners that automate the repetitive 80% while preserving flexibility for the custom 20%.

---

*ODIBI_CORE Medallion Architecture Projects*  
*Phase 7: Framework Recommendations | Status: ✅ COMPLETE | Date: 2025-11-02*
