"""
Mini-Projects - Hands-on capstone exercises for each phase
"""

MINI_PROJECTS = {
    "phase1": {
        "title": "Build a Simple CSV Pipeline",
        "phase": "Phase 1",
        "difficulty": "Beginner",
        "duration": "30-45 minutes",
        "description": "Create your first end-to-end data pipeline using the 5 canonical nodes",
        "objectives": [
            "Connect to a local CSV file",
            "Read data into a DataFrame",
            "Apply basic transformation",
            "Store results to a new CSV",
            "Verify the output"
        ],
        "instructions": """
## 🎯 Project Goal

Build a complete pipeline that:
1. Reads sales data from CSV
2. Adds a "profit" column (revenue - cost)
3. Saves the result to a new file

## 📋 Step-by-Step Guide

### Step 1: Create Sample Data
Create a file `sales_data.csv` with this content:
```csv
product,revenue,cost
Widget A,100,60
Widget B,200,120
Widget C,150,90
```

### Step 2: Write the Pipeline
Use ConnectNode, IngestNode, TransformNode, and StoreNode

### Step 3: Run and Verify
Check that `sales_with_profit.csv` was created with the profit column

## ✅ Success Criteria
- Pipeline runs without errors
- Output file contains "profit" column
- Profit = revenue - cost for all rows
        """,
        "starter_code": """'''
Mini-Project: Simple CSV Pipeline
'''

from odibi_core.nodes import ConnectNode, IngestNode, TransformNode, StoreNode

# TODO: Step 1 - Connect to sales_data.csv

# TODO: Step 2 - Read data with IngestNode

# TODO: Step 3 - Add profit column with TransformNode

# TODO: Step 4 - Save to sales_with_profit.csv

# TODO: Step 5 - Print success message
""",
        "solution": """'''
Mini-Project: Simple CSV Pipeline - SOLUTION
'''

from odibi_core.nodes import ConnectNode, IngestNode, TransformNode, StoreNode

# Step 1: Connect
conn = ConnectNode(source="sales_data.csv", source_type="csv")
print("✅ Connected to sales_data.csv")

# Step 2: Read data
ingest = IngestNode(connection=conn)
df = ingest.read()
print(f"✅ Loaded {len(df)} rows")

# Step 3: Transform - Add profit column
def add_profit(df):
    df['profit'] = df['revenue'] - df['cost']
    return df

transform = TransformNode(transformation_func=add_profit)
df = transform.apply(df)
print("✅ Added profit column")

# Step 4: Store
store = StoreNode(target="sales_with_profit.csv", target_type="csv")
store.write(df)
print("✅ Saved to sales_with_profit.csv")

# Step 5: Verify
print("\\nFinal Data:")
print(df)
"""
    },
    
    "phase2": {
        "title": "Dual-Engine Calculator",
        "phase": "Phase 2",
        "difficulty": "Intermediate",
        "duration": "45-60 minutes",
        "description": "Build a function that works on both Pandas and Spark DataFrames",
        "objectives": [
            "Write engine-agnostic code",
            "Test with Pandas DataFrame",
            "Test with Spark DataFrame",
            "Compare results for parity",
            "Handle edge cases (nulls, zeros)"
        ],
        "instructions": """
## 🎯 Project Goal

Create a `calculate_roi()` function that:
- Works on both Pandas and Spark
- Calculates ROI = (revenue - cost) / cost
- Handles division by zero
- Returns new DataFrame with roi column

## 📋 Requirements

```python
def calculate_roi(df, revenue_col, cost_col, result_col="roi"):
    # Should work for both engines!
    pass
```

## ✅ Success Criteria
- Function works with Pandas DataFrame
- Function works with Spark DataFrame
- Handles cost = 0 gracefully
- Both engines produce identical results
        """,
        "starter_code": """from odibi_core.functions import detect_engine
import pandas as pd
import numpy as np

def calculate_roi(df, revenue_col, cost_col, result_col="roi"):
    engine = detect_engine(df)
    
    if engine == "pandas":
        # TODO: Pandas implementation
        pass
    else:
        # TODO: Spark implementation
        pass
    
    return df

# Test with Pandas
df_pandas = pd.DataFrame({
    'revenue': [100, 200, 150],
    'cost': [50, 0, 75]  # Note: one zero!
})

result = calculate_roi(df_pandas, 'revenue', 'cost')
print(result)
""",
        "solution": """from odibi_core.functions import detect_engine
import pandas as pd
import numpy as np

def calculate_roi(df, revenue_col, cost_col, result_col="roi"):
    engine = detect_engine(df)
    
    if engine == "pandas":
        # Pandas: Use np.where for safe division
        df[result_col] = np.where(
            df[cost_col] != 0,
            (df[revenue_col] - df[cost_col]) / df[cost_col],
            0.0  # Fill value when cost is zero
        )
    else:
        # Spark: Use F.when for safe division
        from pyspark.sql import functions as F
        df = df.withColumn(
            result_col,
            F.when(
                F.col(cost_col) != 0,
                (F.col(revenue_col) - F.col(cost_col)) / F.col(cost_col)
            ).otherwise(0.0)
        )
    
    return df

# Test with Pandas
df_pandas = pd.DataFrame({
    'revenue': [100, 200, 150],
    'cost': [50, 0, 75]
})

result = calculate_roi(df_pandas, 'revenue', 'cost')
print(result)
# Expected ROI: [1.0, 0.0, 1.0] ✅
"""
    },
    
    "phase3": {
        "title": "Config-Driven Bronze Pipeline",
        "phase": "Phase 3",
        "difficulty": "Intermediate",
        "duration": "60-90 minutes",
        "description": "Build a pipeline that reads all settings from configuration files",
        "objectives": [
            "Design a pipeline config schema",
            "Load config from JSON",
            "Build pipeline dynamically from config",
            "Execute Bronze layer ingestion",
            "Log metadata to config database"
        ],
        "instructions": """
## 🎯 Project Goal

Create a Bronze layer pipeline that:
- Reads configuration from `bronze_config.json`
- Ingests multiple source files
- Saves to Bronze layer with metadata
- Logs execution details

## 📋 Config Schema

```json
{
  "pipeline_name": "bronze_ingestion",
  "sources": [
    {"name": "customers", "path": "raw/customers.csv", "type": "csv"},
    {"name": "orders", "path": "raw/orders.csv", "type": "csv"}
  ],
  "target_dir": "data/bronze",
  "metadata_db": "pipeline_metadata.db"
}
```

## ✅ Success Criteria
- Reads all sources from config
- Saves each to Bronze layer
- Creates metadata table
- Handles missing files gracefully
        """,
        "starter_code": """import json
from odibi_core.nodes import ConnectNode, IngestNode, StoreNode
from odibi_core.config import MetadataManager

# TODO: Load bronze_config.json

# TODO: For each source in config:
#   - Create ConnectNode
#   - IngestNode to read
#   - StoreNode to Bronze layer
#   - Log to metadata

# TODO: Print summary
""",
        "solution": """import json
from pathlib import Path
from odibi_core.nodes import ConnectNode, IngestNode, StoreNode
from odibi_core.config import MetadataManager

# Load config
with open("bronze_config.json") as f:
    config = json.load(f)

# Initialize metadata manager
metadata = MetadataManager(config["metadata_db"])

# Process each source
for source in config["sources"]:
    print(f"\\n📥 Processing: {source['name']}")
    
    try:
        # Connect
        conn = ConnectNode(source=source['path'], source_type=source['type'])
        
        # Ingest
        ingest = IngestNode(connection=conn)
        df = ingest.read()
        print(f"  ✅ Loaded {len(df)} rows")
        
        # Store to Bronze
        target_path = f"{config['target_dir']}/{source['name']}.parquet"
        store = StoreNode(target=target_path, format="parquet")
        store.write(df)
        print(f"  ✅ Saved to {target_path}")
        
        # Log metadata
        metadata.log_execution(
            pipeline=config["pipeline_name"],
            source=source['name'],
            rows=len(df),
            status="success"
        )
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        metadata.log_execution(
            pipeline=config["pipeline_name"],
            source=source['name'],
            status="failed",
            error=str(e)
        )

print("\\n🎉 Bronze ingestion complete!")
"""
    },
    
    "capstone": {
        "title": "Full Medallion Pipeline with Observability",
        "phase": "Capstone",
        "difficulty": "Advanced",
        "duration": "3-4 hours",
        "description": "Build a complete Bronze→Silver→Gold pipeline with config, logging, and monitoring",
        "objectives": [
            "Design end-to-end medallion architecture",
            "Implement Bronze (ingestion) layer",
            "Implement Silver (transformation) layer",
            "Implement Gold (aggregation) layer",
            "Add comprehensive logging",
            "Create DAG visualization",
            "Generate execution report"
        ],
        "instructions": """
## 🎯 Capstone Project

Build a **complete data engineering pipeline** that demonstrates everything you've learned!

## 🏗️ Project Structure

```
my_capstone_pipeline/
├── configs/
│   ├── bronze_config.json
│   ├── silver_config.json
│   └── gold_config.json
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── logs/
├── run_pipeline.py
└── README.md
```

## 📊 Pipeline Flow

**Bronze Layer:**
- Ingest 3 data sources (customers, orders, products)
- Validate data exists
- Save as Parquet files
- Log metadata

**Silver Layer:**
- Clean and validate Bronze data
- Join customers + orders
- Apply business rules
- Handle nulls and duplicates
- Save to Silver layer

**Gold Layer:**
- Aggregate by customer
- Calculate KPIs (total revenue, avg order value)
- Create reporting table
- Save to Gold layer

## ✅ Success Criteria
- All 3 layers execute successfully
- Config-driven (no hardcoded paths)
- Dual-engine compatible
- Comprehensive logging
- DAG visualization generated
- Execution report produced

## 🎓 You'll Demonstrate:
✅ All 5 canonical nodes  
✅ Medallion architecture  
✅ Config-driven development  
✅ Dual-engine support  
✅ Error handling  
✅ Logging & monitoring  
✅ Best practices  

**This is your graduation project!** 🏆
        """,
        "starter_code": """'''
Capstone Project: Full Medallion Pipeline
'''

# TODO: Import required modules

# TODO: Load configurations

# TODO: BRONZE LAYER
#   - Ingest all sources
#   - Save to bronze/

# TODO: SILVER LAYER  
#   - Read from bronze/
#   - Clean and transform
#   - Save to silver/

# TODO: GOLD LAYER
#   - Read from silver/
#   - Aggregate and calculate KPIs
#   - Save to gold/

# TODO: Generate report
""",
        "solution": "# Solution provided in separate capstone_solution.py file (200+ lines)"
    }
}


def get_mini_project(phase_key: str):
    """Get mini-project for a phase"""
    return MINI_PROJECTS.get(phase_key)


def get_capstone_project():
    """Get the capstone project"""
    return MINI_PROJECTS.get("capstone")
