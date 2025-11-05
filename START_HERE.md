# 🚀 START HERE - ODIBI Core for Complete Beginners

**Welcome!** This guide assumes you have **ZERO** experience with ODIBI Core. We'll get you building pipelines in minutes using visuals and simple steps.

---

## 🎯 What is ODIBI Core in One Picture?

```
┌─────────────────────────────────────────────────────────────┐
│  YOU: "Read this CSV, clean it, save as Parquet"           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  ODIBI CORE: Handles everything automatically               │
│  ✅ Reading data                                            │
│  ✅ Running transformations                                 │
│  ✅ Tracking what happened                                  │
│  ✅ Retrying on failures                                    │
│  ✅ Saving checkpoints                                      │
│  ✅ Writing output                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT: Clean data pipeline that runs on Pandas OR Spark  │
└─────────────────────────────────────────────────────────────┘
```

**In simple words**: ODIBI Core is like a smart assistant that builds data pipelines for you.

---

## 🏃 Three Ways to Learn (Pick One!)

### Option 1: Interactive Learning (RECOMMENDED for Beginners) 🌟
**Best if**: You want to learn by doing with instant feedback

```bash
# 1. Install
pip install odibi-core

# 2. Launch interactive UI
python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"

# 3. Click "Guided Learning" → Start with Phase 1
```

**What you get**: Interactive code that runs in your browser, step-by-step lessons, instant results

---

### Option 2: Quick 5-Minute Pipeline (For the Impatient) ⚡
**Best if**: You want to see results NOW

👉 **[Go to 5-MINUTE-START.md](5-MINUTE-START.md)**

**What you get**: Copy-paste code that creates your first pipeline immediately

---

### Option 3: Read Visual Guides (For Visual Learners) 📖
**Best if**: You prefer reading with lots of diagrams

👉 **[Go to docs/guides/ODIBI_CORE_VISUAL_GUIDE.md](docs/guides/ODIBI_CORE_VISUAL_GUIDE.md)**

**What you get**: Diagrams, flowcharts, and explanations

---

## 🗺️ Learning Path (Visual Decision Tree)

```
START: What do you want to do?
│
├─ "I want to understand the basics first"
│  └─▶ Read: docs/guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md (15 min)
│     Then: docs/guides/ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md (30 min)
│
├─ "I want to use Azure cloud storage"
│  └─▶ Go to: examples/azure_notebooks/AZURE_NOTEBOOKS_README.md
│     Then: Open Notebook_01_Azure_Basic_Setup.ipynb
│
├─ "I want to build production pipelines"
│  └─▶ Read: docs/ODIBI_CORE_MASTERY_INDEX.md
│     Then: Follow the 8-level learning path
│
├─ "I just want example code NOW"
│  └─▶ Go to: examples/
│     Try: phase9_sdk_demo.py
│
└─ "I'm confused, just tell me what to do!"
   └─▶ Run: python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"
      Click "Guided Learning" and follow along!
```

---

## 📊 What Can ODIBI Core Do? (Visual Examples)

### Example 1: Simple Data Pipeline
```
INPUT (CSV file)  →  CLEAN (SQL filter)  →  OUTPUT (Parquet)
     ↓                      ↓                      ↓
  1000 rows          →   800 rows clean    →  Saved to disk
```

**Your code**:
```python
Step(layer="ingest", name="read", value="data.csv"),
Step(layer="transform", name="clean", value="SELECT * FROM data WHERE valid=true"),
Step(layer="store", name="save", value="output.parquet")
```

**ODIBI Core handles**: Reading, executing SQL, writing, tracking, errors ✅

---

### Example 2: Cloud Pipeline (Azure)
```
AZURE BLOB          →  TRANSFORM         →  AZURE BLOB
(Bronze/raw data)      (Clean + Validate)    (Silver/clean data)
     ↓                      ↓                      ↓
Raw customer CSV    →  Remove duplicates  →  Clean Parquet
1M rows                  →  950K rows        →  Partitioned by country
```

**Your code**: Just specify Azure paths, ODIBI Core handles cloud auth, reading, writing ✅

---

### Example 3: Production Pipeline with Reliability
```
READ DATA  →  TRANSFORM  →  CHECKPOINT ✓  →  AGGREGATE  →  SAVE
   ↓             ↓              ↓               ↓            ↓
 If fails?   If fails?      Saved state!    If fails?    If fails?
   ↓             ↓              ↓               ↓            ↓
 RETRY 3x    RETRY 3x     ← Resume here!    RETRY 3x    RETRY 3x
```

**ODIBI Core handles**: Automatic retries, checkpoints, resume on failure ✅

---

## 🎨 Key Concepts (Visual)

### 1. Five Types of Building Blocks (Nodes)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   CONNECT    │  │   INGEST     │  │  TRANSFORM   │  │    STORE     │  │   PUBLISH    │
│              │  │              │  │              │  │              │  │              │
│ Setup        │  │ Read data    │  │ Clean/       │  │ Save to      │  │ Export to    │
│ connections  │  │ from sources │  │ transform    │  │ disk/lake    │  │ external     │
│              │  │              │  │              │  │              │  │              │
│ Example:     │  │ Example:     │  │ Example:     │  │ Example:     │  │ Example:     │
│ Connect to   │  │ Read CSV     │  │ Filter rows  │  │ Write        │  │ Send to API  │
│ PostgreSQL   │  │ Query DB     │  │ Add columns  │  │ Parquet      │  │ Publish      │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**You snap these blocks together like LEGO!**

---

### 2. Two Execution Engines (Pick Based on Data Size)

```
┌─────────────────────────────────────────────────────────┐
│                   YOUR DATA SIZE                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Small data (< 10 GB)?                                 │
│  └─▶ Use PANDAS engine                                 │
│      ✅ Fast                                            │
│      ✅ Runs on laptop                                  │
│      ✅ Simple setup                                    │
│                                                         │
│  Large data (> 10 GB)?                                 │
│  └─▶ Use SPARK engine                                  │
│      ✅ Distributed                                     │
│      ✅ Scales to terabytes                            │
│      ✅ Runs on clusters                               │
│                                                         │
│  🎯 BEST PART: Same code works on both!                │
└─────────────────────────────────────────────────────────┘
```

---

### 3. Medallion Architecture (Bronze → Silver → Gold)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   BRONZE    │      │   SILVER    │      │    GOLD     │
│             │      │             │      │             │
│ Raw data    │  →   │ Cleaned     │  →   │ Business    │
│ As-is from  │      │ Validated   │      │ Aggregated  │
│ source      │      │ Standardized│      │ Ready for   │
│             │      │             │      │ analysis    │
├─────────────┤      ├─────────────┤      ├─────────────┤
│ Example:    │      │ Example:    │      │ Example:    │
│ Raw CSV     │      │ Duplicates  │      │ Customer    │
│ with        │      │ removed     │      │ totals by   │
│ duplicates  │      │ Null values │      │ country     │
│ and errors  │      │ handled     │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
```

**ODIBI Core makes this pattern easy!**

---

## 🛠️ Installation (Super Simple)

### Option 1: Standard Install
```bash
pip install odibi-core
```

### Option 2: With Azure Support
```bash
pip install odibi-core
pip install azure-storage-file-datalake azure-identity
```

### Option 3: Development Install
```bash
git clone https://github.com/yourusername/odibi_core.git
cd odibi_core
pip install -e .
```

**Test it worked**:
```python
python -c "from odibi_core import __version__; print(f'✅ ODIBI Core {__version__} installed!')"
```

---

## 📚 Documentation Map (Where to Go Next)

### For Complete Beginners
```
1. START_HERE.md ← YOU ARE HERE!
2. 5-MINUTE-START.md (your first pipeline)
3. docs/guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md (concepts)
4. docs/guides/ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md (build stuff)
5. examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb (hands-on)
```

### For Azure Users
```
1. examples/azure_notebooks/AZURE_NOTEBOOKS_README.md
2. Notebook_01_Azure_Basic_Setup.ipynb (30 min)
3. Notebook_02_Azure_Medallion_Pipeline.ipynb (45 min)
4. Notebook_03_Azure_Databricks_Spark.ipynb (advanced)
```

### For Visual Learners
```
1. docs/guides/ODIBI_CORE_VISUAL_GUIDE.md (diagrams!)
2. docs/AZURE_INTEGRATION_INDEX.md (visual index)
3. Interactive UI: `python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"`
```

### Complete Mastery Path
```
1. docs/ODIBI_CORE_MASTERY_INDEX.md (overview)
2. Level 1 → Level 8 guides (progressive learning)
3. docs/guides/ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md (production)
```

---

## ❓ Common Questions

### "Which guide should I read first?"
**Answer**: If you're brand new, run the interactive UI:
```bash
python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"
```
Click "Guided Learning" → Phase 1. It teaches you step-by-step!

---

### "I just want example code"
**Answer**: Look in `examples/`:
- `phase9_sdk_demo.py` - Simple examples
- `azure_notebooks/` - Azure examples (Jupyter notebooks)
- `functions_demo/` - Custom functions

---

### "What if I get stuck?"
**Answer**:
1. Check troubleshooting in the guides
2. Look at examples that work
3. Use the interactive UI (it has built-in help)

---

### "Do I need to know Python well?"
**Answer**: Basic Python is enough! If you can read this, you're good:
```python
data = {"name": "Alice", "age": 30}
print(data["name"])
```

---

### "Can I use this in production?"
**Answer**: YES! ODIBI Core includes:
- ✅ Retry logic
- ✅ Checkpoints
- ✅ Lineage tracking
- ✅ Event monitoring
- ✅ Cloud integration

See: `docs/guides/ODIBI_CORE_LEVEL_4_RELIABILITY.md`

---

## 🎯 Next Steps (Choose Your Adventure!)

### Path A: "I want to build something NOW"
```bash
# Copy this to a file called my_first_pipeline.py
from odibi_core.orchestrator import Orchestrator
from odibi_core.core.node import Step

steps = [
    Step(layer="ingest", name="read", type="config_op", engine="pandas",
         value="data.csv", outputs={"data": "raw_data"}),
    Step(layer="store", name="save", type="config_op", engine="pandas",
         value="output.parquet", inputs={"data": "raw_data"})
]

orchestrator = Orchestrator(steps=steps, engine_type="pandas")
result = orchestrator.execute()
print(f"✅ Pipeline complete: {result['success']}")
```

Then:
```bash
python my_first_pipeline.py
```

---

### Path B: "I want to understand first"
1. Open: `docs/guides/ODIBI_CORE_VISUAL_GUIDE.md`
2. Read for 10 minutes (lots of pictures!)
3. Then try Path A above

---

### Path C: "I want interactive learning"
```bash
python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"
# Opens in your browser - click and learn!
```

---

## 🎨 Visual Cheat Sheet

### Pipeline Structure
```
┌────────────────────────────────────────────────┐
│ Orchestrator (The Boss)                       │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │ Steps (What to do)                       │ │
│  │  • Read CSV                              │ │
│  │  • Clean data                            │ │
│  │  • Save result                           │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │ Engine (How to do it)                    │ │
│  │  Pandas or Spark                         │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │ Features (Extras)                        │ │
│  │  • Checkpoints ✓                         │ │
│  │  • Retry ✓                               │ │
│  │  │  • Tracking ✓                          │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### Data Flow
```
YOUR CSV FILE  →  [ODIBI CORE]  →  CLEAN PARQUET
                        ↓
                   Tracks everything
                        ↓
                  Saves checkpoints
                        ↓
                  Retries on errors
                        ↓
                   ✅ SUCCESS!
```

---

## 🚀 Ready to Start?

### Absolute Beginner (0 experience)
**→ Go to**: [5-MINUTE-START.md](5-MINUTE-START.md)

### Visual Learner
**→ Go to**: [docs/guides/ODIBI_CORE_VISUAL_GUIDE.md](docs/guides/ODIBI_CORE_VISUAL_GUIDE.md)

### Want Interactive
**→ Run**: `python -c "from odibi_core.learnodibi import launch_ui; launch_ui()"`

### Azure User
**→ Go to**: [examples/azure_notebooks/AZURE_NOTEBOOKS_README.md](examples/azure_notebooks/AZURE_NOTEBOOKS_README.md)

---

**Questions?** All guides have troubleshooting sections!

**Good luck!** 🎉 You've got this! 💪
