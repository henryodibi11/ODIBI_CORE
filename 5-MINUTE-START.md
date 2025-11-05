# ⚡ Your First ODIBI Pipeline in 5 Minutes

**Goal**: Get a working pipeline running in 5 minutes or less!

**No theory, just copy-paste-run!** 🚀

---

## Step 1: Install (30 seconds)

```bash
pip install odibi-core pandas
```

Wait for it to finish... ✅

---

## Step 2: Create Sample Data (30 seconds)

Copy this into a file called `create_data.py`:

```python
import pandas as pd

# Create sample CSV
data = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'amount': [100.50, 250.75, 80.00, 420.00, 150.25],
    'country': ['USA', 'UK', 'Canada', 'USA', 'Australia']
})

data.to_csv('customers.csv', index=False)
print("✅ Created customers.csv")
```

Run it:
```bash
python create_data.py
```

You should see: `✅ Created customers.csv`

---

## Step 3: Your First Pipeline! (2 minutes)

Copy this into a file called `my_first_pipeline.py`:

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.core.node import Step

# Define what the pipeline should do
steps = [
    # Step 1: Read the CSV file
    Step(
        layer="ingest",
        name="read_customers",
        type="config_op",
        engine="pandas",
        value="customers.csv",
        params={"source_type": "csv"},
        outputs={"data": "raw_customers"}
    ),
    
    # Step 2: Filter for high-value customers (amount > 100)
    Step(
        layer="transform",
        name="filter_high_value",
        type="sql",
        engine="pandas",
        value="SELECT * FROM data WHERE amount > 100",
        inputs={"data": "raw_customers"},
        outputs={"data": "high_value_customers"}
    ),
    
    # Step 3: Save as Parquet
    Step(
        layer="store",
        name="save_output",
        type="config_op",
        engine="pandas",
        value="high_value_customers.parquet",
        params={"format": "parquet"},
        inputs={"data": "high_value_customers"}
    )
]

# Create the orchestrator (the boss that runs everything)
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True  # Track what happens
)

# Execute the pipeline!
print("\n🚀 Running pipeline...\n")
result = orchestrator.execute()

# Check results
if result['success']:
    print(f"\n✅ SUCCESS! Pipeline completed!")
    print(f"   Steps executed: {result['nodes_executed']}")
    print(f"   Output saved to: high_value_customers.parquet")
else:
    print(f"\n❌ Pipeline failed!")
    print(f"   Failed steps: {result.get('failed_nodes', [])}")
```

Run it:
```bash
python my_first_pipeline.py
```

---

## What Just Happened? (Visual)

```
customers.csv (5 customers)
      ↓
   [READ]
      ↓
  All 5 customers loaded
      ↓
  [FILTER] amount > 100
      ↓
  4 customers remain (Alice, Bob, Diana, Eve)
      ↓
   [SAVE]
      ↓
high_value_customers.parquet ✅
```

---

## Verify It Worked (1 minute)

Copy this into `check_output.py`:

```python
import pandas as pd

# Read the result
df = pd.read_parquet('high_value_customers.parquet')

print("\n📊 High-Value Customers:")
print(df)
print(f"\n✅ Found {len(df)} high-value customers")
```

Run it:
```bash
python check_output.py
```

You should see:
```
📊 High-Value Customers:
   customer_id     name  amount    country
0            1    Alice  100.50        USA
1            2      Bob  250.75         UK
2            4    Diana  420.00        USA
3            5      Eve  150.25  Australia

✅ Found 4 high-value customers
```

---

## 🎉 Congratulations!

You just built a complete data pipeline with:
- ✅ Data ingestion (reading CSV)
- ✅ Transformation (SQL filtering)
- ✅ Data storage (writing Parquet)
- ✅ Automatic tracking
- ✅ Error handling

**Time taken**: ~5 minutes ⚡

---

## What's Next? (Choose Your Path)

### Path 1: Make It Better
Add more transforms! Try this step between "filter" and "save":

```python
Step(
    layer="transform",
    name="add_category",
    type="sql",
    engine="pandas",
    value="""
        SELECT *,
            CASE
                WHEN amount > 300 THEN 'VIP'
                WHEN amount > 150 THEN 'Premium'
                ELSE 'Standard'
            END as category
        FROM data
    """,
    inputs={"data": "high_value_customers"},
    outputs={"data": "categorized_customers"}
)
```

Don't forget to update the save step to use `categorized_customers`!

---

### Path 2: Add Reliability
Make your pipeline production-ready:

```python
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True,
    enable_checkpoints=True,  # ← Save progress
    max_retries=3,            # ← Retry on errors
    retry_delay=5             # ← Wait 5 seconds between retries
)
```

---

### Path 3: Try Azure Cloud
Want to read/write from Azure?

**→ Go to**: [examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb](examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb)

---

### Path 4: Scale to Spark
Got big data (> 10 GB)?

Just change one line:
```python
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",  # ← Changed from "pandas" to "spark"
    ...
)
```

**Everything else stays the same!** 🤯

---

### Path 5: Learn More Concepts
**→ Go to**: [docs/guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md](docs/guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md)

---

## Quick Reference Card

### Basic Pipeline Template
```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.core.node import Step

steps = [
    Step(layer="ingest", name="read", type="config_op", engine="pandas",
         value="input.csv", outputs={"data": "raw"}),
    
    Step(layer="transform", name="process", type="sql", engine="pandas",
         value="SELECT * FROM data WHERE ...",
         inputs={"data": "raw"}, outputs={"data": "processed"}),
    
    Step(layer="store", name="save", type="config_op", engine="pandas",
         value="output.parquet", inputs={"data": "processed"})
]

orchestrator = Orchestrator(steps=steps, engine_type="pandas")
result = orchestrator.execute()
```

---

### Common Step Types

| What You Want | Step Type | Example Value |
|---------------|-----------|---------------|
| Read file | `type="config_op"` | `value="data.csv"` |
| SQL transform | `type="sql"` | `value="SELECT * FROM data WHERE x > 10"` |
| Python function | `type="function"` | `value="my_module.my_function"` |
| Save file | `type="config_op"` | `value="output.parquet"` |

---

### Supported File Formats

| Format | Read | Write | Best For |
|--------|------|-------|----------|
| **CSV** | ✅ | ✅ | Simple data, humans reading |
| **Parquet** | ✅ | ✅ | Large data, analytics (RECOMMENDED) |
| **JSON** | ✅ | ✅ | APIs, semi-structured |
| **Delta** | ✅ | ✅ | Production, ACID transactions |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'odibi_core'"
**Fix**: Run `pip install odibi-core`

---

### "FileNotFoundError: customers.csv"
**Fix**: Run `create_data.py` first to create the CSV file

---

### "KeyError: 'data'"
**Fix**: Check that `outputs` in one step matches `inputs` in the next:
```python
Step(..., outputs={"data": "my_data"}),  # Output name
Step(..., inputs={"data": "my_data"}),   # Must match!
```

---

### Pipeline runs but no output file
**Fix**: Check the `value` in your store step:
```python
Step(layer="store", name="save", value="output.parquet", ...)
```
File will be created in the same directory you run the script from.

---

## 🎯 Challenge: Modify the Pipeline

Try these modifications:

### Challenge 1: Different Filter
Change the filter to find customers from USA only:
```python
value="SELECT * FROM data WHERE country = 'USA'"
```

### Challenge 2: Multiple Filters
Combine filters:
```python
value="SELECT * FROM data WHERE amount > 100 AND country = 'USA'"
```

### Challenge 3: Add Calculations
```python
value="""
    SELECT *,
        amount * 0.10 as commission,
        amount * 1.20 as amount_with_tax
    FROM data
"""
```

### Challenge 4: Aggregations
```python
value="""
    SELECT country,
        COUNT(*) as customer_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount
    FROM data
    GROUP BY country
"""
```

---

## 📚 Learn More

- **Next Guide**: [START_HERE.md](START_HERE.md) - Choose your learning path
- **Visual Guide**: [docs/guides/ODIBI_CORE_VISUAL_GUIDE.md](docs/guides/ODIBI_CORE_VISUAL_GUIDE.md)
- **Azure Cloud**: [examples/azure_notebooks/AZURE_NOTEBOOKS_README.md](examples/azure_notebooks/AZURE_NOTEBOOKS_README.md)
- **All Levels**: [docs/ODIBI_CORE_MASTERY_INDEX.md](docs/ODIBI_CORE_MASTERY_INDEX.md)

---

**You're ready to build real pipelines!** 🚀

Any questions? Check [START_HERE.md](START_HERE.md) for more help!
