# 🎨 ODIBI_CORE Creative Showcase Suite

## 🚀 Quick Access

**[→ Open Stories Index](file:///D:/projects/odibi_core/resources/output/creative_showcases/SHOWCASE_STORIES_INDEX.html)** - Browse all 100 interactive HTML stories

---

## ✅ What This Suite Demonstrates

### 💎 ODIBI_CORE's Unique Features

1. **🎯 Native DAG Orchestration** - No Airflow, no Prefect - pure Python dependency resolution
2. **🔍 Truth-Preserving Lineage** - Every transformation tracked with before/after snapshots
3. **🏅 Medallion-First Architecture** - Bronze→Silver→Gold layering built into the framework
4. **⚡ Event-Driven Observability** - Real-time lifecycle hooks without external monitoring
5. **🧩 Config-Driven Pipelines** - Entire DAG defined in JSON/SQL, zero hardcoding
6. **📊 Auto-Generated Stories** - HTML visualizations showing exactly what happened

### 📊 Coverage

- ✅ **100 showcases** across 10 domains
- ✅ **6 DAG topologies** (Linear, Branching, Parallel, Conditional, Diamond, Cascade)
- ✅ **3 complexity levels** (Simple: 20, Medium: 50, Advanced: 30)
- ✅ **100 HTML stories** with real data transformations
- ✅ **Auto-scaling index** that always links to latest stories

---

## 📚 Documentation

### For Users
- **[QUICK_START.md](QUICK_START.md)** - Get started in 1 minute
- **[HOW_TO_VIEW_STORIES.md](HOW_TO_VIEW_STORIES.md)** - Complete usage guide

### For Developers
- **[FEATURES_CHECKLIST.md](FEATURES_CHECKLIST.md)** - All validated features
- **[FINAL_DELIVERY_SUMMARY.md](FINAL_DELIVERY_SUMMARY.md)** - Technical delivery summary
- **[../../scripts/CREATIVE_SHOWCASE_README.md](../../scripts/CREATIVE_SHOWCASE_README.md)** - Implementation details

---

## 🔄 Auto-Scaling Index

The stories index **automatically** uses the most recent story for each showcase:

```python
# Finds the newest HTML file by modification time
html_file = max(html_files, key=lambda f: f.stat().st_mtime)
```

**Benefits:**
- ✅ Always shows latest execution results
- ✅ Works if you re-run showcases
- ✅ Scales to unlimited showcases
- ✅ No manual maintenance required

---

## 📁 File Structure

```
odibi_core/
├── scripts/
│   ├── creative_showcase_generator.py    # Phase 1: Generate 100 configs
│   ├── creative_showcase_executor.py     # Phase 2: Execute + auto-index
│   ├── creative_showcase_master.py       # Run all phases
│   └── generate_story_index.py           # Standalone index generator
├── resources/
│   ├── configs/creative_showcases/
│   │   ├── creative_showcase_001.json - 100.json
│   │   ├── creative_showcase_001_metadata.json - 100_metadata.json
│   │   └── creative_showcases.db
│   └── output/creative_showcases/
│       ├── showcase_001_story/
│       │   └── story_run_*.html (newest used by index)
│       ├── showcase_002_story/
│       ...
│       ├── showcase_100_story/
│       └── SHOWCASE_STORIES_INDEX.html (auto-generated)
└── reports/showcases/creative/
    ├── CREATIVE_SHOWCASE_001.md - 100.md
    ├── CREATIVE_MASTER_SUMMARY.md
    ├── CREATIVE_SHOWCASE_SUMMARY.md
    ├── CREATIVE_FILE_ATLAS.md
    └── This README.md
```

---

## 🎯 What Each Showcase Shows

### Markdown Reports (.md)
- 💎 What makes ODIBI_CORE unique
- 📖 Story (backstory + data goal)
- 🏗️ Pipeline architecture
- 🏅 Medallion walkthrough (Bronze/Silver/Gold)
- 🔬 Component spotlight (concrete examples)
- 📊 Execution metrics
- 🧠 "What ODIBI_CORE learned" reflection

### HTML Stories (.html)
- **Header**: Pipeline name, execution time, success rate
- **Step Cards**: One per transformation with:
  - Before snapshot (schema + sample rows)
  - After snapshot (schema + sample rows)
  - Schema diff (columns added/removed)
  - Row delta (data volume changes)
  - Execution timing

---

## 🏆 Total Deliverables

| Artifact Type | Count | Description |
|---------------|-------|-------------|
| **Scripts** | 4 | Generator, executor, master, index |
| **HTML Stories** | 100 | Interactive visualizations |
| **Markdown Reports** | 104 | 100 showcases + 4 summaries |
| **JSON Configs** | 200 | 100 steps + 100 metadata |
| **SQL Database** | 1 | All configs in structured format |
| **Documentation** | 8 | Usage guides + summaries |
| **Stories Index** | 1 | Auto-scaling gallery (always latest) |

---

## 🚀 Run Commands

### Execute All 100 Showcases
```bash
cd D:/projects/odibi_core
python scripts/creative_showcase_executor.py
# Index auto-generates with latest stories!
```

### Regenerate Index Only
```bash
python scripts/generate_story_index.py
# Scans for newest story in each folder
```

### Full Suite (All 4 Phases)
```bash
python scripts/creative_showcase_master.py
```

---

## ✅ Key Improvements

### Latest Update: Auto-Latest Stories
- Index now **always** links to the most recent story file
- Handles multiple runs gracefully
- No stale links

### Previous Updates
- Added "What Makes ODIBI_CORE Unique" section
- Added Medallion Architecture Walkthrough
- Added Component Spotlight with concrete examples
- Populated stories with real data transformations
- Auto-generated stories index

---

**Start exploring:** [Open Stories Index](file:///D:/projects/odibi_core/resources/output/creative_showcases/SHOWCASE_STORIES_INDEX.html)
