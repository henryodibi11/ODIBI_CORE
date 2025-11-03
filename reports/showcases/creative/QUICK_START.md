# 🚀 Quick Start - ODIBI_CORE Creative Showcase Stories

## 📖 View the Stories (1 Minute)

### Step 1: Open the Index
Click here to open in your browser:
**[SHOWCASE_STORIES_INDEX.html](file:///D:/projects/odibi_core/resources/output/creative_showcases/SHOWCASE_STORIES_INDEX.html)**

### Step 2: Browse Showcases
- See 100 showcase cards organized by complexity
- Each card shows: Showcase #, complexity badge, description
- Click "View Story →" on any showcase

### Step 3: Explore a Story
Each HTML story shows:
- **Pipeline overview** (name, domain, execution time)
- **Step-by-step cards** (one per transformation)
- **Before/After snapshots** (schema + sample data)
- **Schema diffs** (columns added/removed)
- **Row deltas** (data volume changes)

---

## 🎯 Recommended Showcases

### Start Here (Simple)
- **#001 - Credit Card Fraud Detection** (Finance, 6 steps)
- **#006 - Urban Air Quality Monitor** (IoT, 4 steps)
- **#014 - Patient Wait-Time Optimizer** (Healthcare, 5 steps)

### Next (Medium Complexity)
- **#050 - Wildlife Migration Tracker** (Environmental, 8 steps with validation)
- **#034 - Clinical Trial Data Pipeline** (Healthcare, 7 steps with caching)
- **#042 - Customer Churn Predictor** (Retail, 9 steps)

### Advanced (Full Features)
- **#087 - Smart Factory Sensor Analytics** (IoT, 8 steps, Branching DAG)
- **#093 - Vaccination Campaign Tracker** (Healthcare, 10 steps, Linear DAG)
- **#099 - Credit Card Fraud Detection** (Finance, 10 steps with error injection)

---

## 📊 What You'll See in Each Story

### Header Section
```
ODIBI CORE Pipeline Story
Pipeline ID: showcase_050
Start Time: 2025-11-02 21:03:06
Duration: 33.59ms

TOTAL STEPS: 8 | SUCCESS: 8 | FAILED: 0 | SUCCESS RATE: 100.0%
```

### Step Card Example
```
Step: merge_sources_3
Layer: silver | Duration: 1.00ms | Status: ✅ success

Before Snapshot (100 rows, 2 columns)
┌──────┬─────────┐
│ id   │ value   │
├──────┼─────────┤
│ 1    │ 45.32   │
│ 2    │ 78.91   │
└──────┴─────────┘

After Snapshot (100 rows, 3 columns)
┌──────┬─────────┬──────────────┐
│ id   │ value   │ merged_field │
├──────┼─────────┼──────────────┤
│ 1    │ 45.32   │ X            │
│ 2    │ 78.91   │ Y            │
└──────┴─────────┴──────────────┘

Schema Changes: +1 column added (merged_field)
Row Delta: 0 (no rows added/removed)
```

---

## 🔄 Auto-Scaling Index

The index **automatically updates** when you run showcases:

### Generate More Showcases
```bash
cd D:/projects/odibi_core
python scripts/creative_showcase_executor.py
```

The index will auto-refresh with all new stories!

### Scale to 200 Showcases
1. Update generator to create 200 configs
2. Run executor
3. Index auto-generates with 200 cards
4. No manual updates needed!

---

## 📁 File Locations

### HTML Stories
```
D:/projects/odibi_core/resources/output/creative_showcases/
├── showcase_001_story/
│   └── story_run_*.html
├── showcase_002_story/
│   └── story_run_*.html
...
└── showcase_100_story/
    └── story_run_*.html
```

### Stories Index
```
D:/projects/odibi_core/resources/output/creative_showcases/SHOWCASE_STORIES_INDEX.html
```

### Markdown Reports
```
D:/projects/odibi_core/reports/showcases/creative/
├── CREATIVE_SHOWCASE_001.md
├── CREATIVE_SHOWCASE_002.md
...
└── CREATIVE_SHOWCASE_100.md
```

---

## 🎓 Learning Path

### For Beginners
1. Open the **stories index**
2. Start with **Simple showcases** (#001-020)
3. See how data flows through basic ETL
4. Notice schema changes in transformations

### For Data Engineers
1. Compare **DAG topologies** (Linear vs Branching vs Parallel)
2. Study **validation steps** (how rows get filtered)
3. Observe **caching impact** (passthrough vs computation)
4. Review **merge operations** (multi-source ingestion)

### For Framework Developers
1. Examine **Tracker snapshots** (how lineage is preserved)
2. Study **event firing patterns** (when each lifecycle event occurs)
3. Review **schema diff logic** (how column changes are detected)
4. Understand **DAG execution order** (topological sorting)

---

## 🐛 Troubleshooting

**Q: Stories show 0 steps?**  
A: Run the latest executor version - old stories were empty, new ones have data

**Q: Index doesn't show my showcase?**  
A: Index auto-generates after executor finishes. Re-run if needed:
```bash
python scripts/generate_story_index.py
```

**Q: Story HTML won't open?**  
A: Use file:// URLs or double-click from File Explorer

**Q: Want to customize stories?**  
A: Edit `odibi_core/story/story_generator.py` for HTML template

---

## 💡 Pro Tips

1. **Compare Complexity Levels** - Open showcase #001 (simple) vs #087 (advanced) side-by-side
2. **Study Schema Evolution** - Look for steps that add columns (transforms) vs remove rows (validation)
3. **Track Data Flow** - Follow sample data values through the pipeline
4. **Learn DAG Patterns** - Compare Linear (#006) vs Branching (#087) vs Parallel (#050)
5. **Use for Documentation** - Share HTML stories with stakeholders to explain pipelines

---

## 📞 Support

- **Documentation**: [HOW_TO_VIEW_STORIES.md](HOW_TO_VIEW_STORIES.md)
- **Features**: [FEATURES_CHECKLIST.md](FEATURES_CHECKLIST.md)
- **Delivery Summary**: [FINAL_DELIVERY_SUMMARY.md](FINAL_DELIVERY_SUMMARY.md)
- **Main Index**: [INDEX.md](INDEX.md)

---

**You're all set! Open the stories index and start exploring.** 🎨

[→ Open Stories Index](file:///D:/projects/odibi_core/resources/output/creative_showcases/SHOWCASE_STORIES_INDEX.html)
