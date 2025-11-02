# ODB-CORE Studio - User Guide 📖

**Version**: 1.1.0  
**Status**: Ready to Use ✅

---

## 🚀 Quick Start

### 1. Launch the Studio
```cmd
cd d:\projects\odibi_core
python -m streamlit run odibi_core\learnodibi_ui\app.py
```

### 2. Access in Browser
Open: http://localhost:8501

### 3. Explore!
Navigate using the sidebar menu.

---

## 📚 Page-by-Page Guide

### 🏠 Home Page

**What You'll See**:
- Welcome message and feature overview
- Quick Start guide (click to expand)
- Navigation instructions

**What to Do**:
- Read the overview
- Click on page links in sidebar to navigate

---

### 🎓 Page 1: Core Concepts

**Purpose**: Learn the 5 fundamental node types

**How to Use**:
1. Click on each node tab (ConnectNode, IngestNode, etc.)
2. Read the description and example use case
3. See the code example
4. Click **"💡 Try It"** button to run it
5. View the simulated output

**Try This**:
- Click "Try It" on **IngestNode** → See a 100-row DataFrame appear
- Click "Try It" on **TransformNode** → See before/after transformation
- Click **"▶️ Run Complete Pipeline"** at bottom → Watch progress bar

**Expected Behavior**:
- Buttons respond immediately
- Sample data appears in tables
- Progress bars animate
- Metrics update

---

### 🔍 Page 2: Functions Explorer

**Purpose**: Discover and test 100+ built-in functions

**How to Use**:

**Step 1 - Browse Functions**:
1. Go to **"Browse Functions"** tab
2. Expand a category (e.g., "Math Utilities")
3. Click on a function button (e.g., **"🔧 safe_divide"**)
4. Page will reload

**Step 2 - Test Function**:
1. Switch to **"Function Tester"** tab (manually)
2. You'll see the selected function's interactive tester
3. Enter input values
4. Click **"▶️ Run"** button
5. See results and metrics

**Available Interactive Testers**:
- ✅ **safe_divide** - Division with default value
- ✅ **clean_string** - Text cleaning operations
- ✅ **convert_temperature** - C/F/K conversions
- ✅ **calculate_percentage** - Part/whole with progress bar
- ✅ **moving_average** - Visual chart with adjustable window
- ✅ **parse_datetime** - Date string parsing
- ✅ **validate_range** - Range validation with progress

**Tips**:
- Use the search box to find functions quickly
- Filter by category in sidebar
- Functions without testers show "coming soon" message

**Expected Behavior**:
- Click function → Page reloads → selected_function stored
- Switch to Tester tab → See interactive form
- Enter values → Click Run → See results immediately

---

### 💻 Page 3: SDK Examples

**Purpose**: Learn from real, runnable code examples

**How to Use**:
1. Select a category from sidebar:
   - Getting Started (Beginner)
   - Data Transformation (Intermediate)
   - Advanced Patterns (Advanced)
   - Real-World Use Cases (Advanced)

2. Expand an example (click the expander)

3. Read the description

4. Review the code

5. Click **"▶️ Run Example"**

6. View the output:
   - DataFrames show in tables
   - JSON shows in pretty format
   - Console output displays

7. Click **"📥 Download Results"** if available

**Try These**:
- **Basic Pipeline** → See simple 3-row transformation
- **Data Cleaning** → See before/after cleaning
- **ETL Pipeline** → See Bronze→Silver→Gold layers
- **Data Quality Checks** → See quality report

**Expected Behavior**:
- Code executes without errors
- Results display immediately
- Download generates CSV file
- Metrics show execution time

---

### ⚡ Page 4: Demo Project (Main Attraction!)

**Purpose**: Run a complete medallion architecture pipeline

**The Pipeline**:
- **Bronze**: Ingest raw sensor/energy data
- **Silver**: Clean, validate, and enrich data
- **Gold**: Aggregate and create analytics

**How to Use**:

**Bronze Layer**:
1. Adjust number of rows slider
2. Toggle quality options (nulls, outliers)
3. Click **"📥 Ingest Data"**
4. See data preview and metrics
5. Click **"📥 Download Bronze Data"** if desired
6. Click **"🔄 Reset Bronze"** to start over

**Silver Layer** (requires Bronze first):
1. Select transformation options:
   - Handle null values
   - Remove outliers
   - Validate ranges
   - Add derived columns
2. Click **"⚙️ Transform Data"**
3. See before/after comparison
4. View metrics and charts
5. Download if desired

**Gold Layer** (requires Silver):
1. Select aggregation options:
   - Daily summary
   - By sensor/facility
   - Statistical aggregates
2. Click **"📊 Aggregate Data"**
3. See aggregated results
4. View summary metrics

**Analytics Tab**:
1. Run all layers (Bronze → Silver → Gold)
2. View combined visualizations:
   - Trend charts
   - Distribution plots
   - Correlation heatmaps
3. See pipeline summary metrics

**Expected Behavior**:
- Each layer builds on previous
- Data persists in session
- Visualizations update automatically
- Downloads work for each layer

---

### 📖 Page 5: Documentation

**Purpose**: Browse ODIBI CORE documentation

**How to Use**:
1. See table of contents on left
2. Click a document to view
3. Use search box to filter files
4. Read markdown with syntax highlighting

**Expected Behavior**:
- Markdown renders correctly
- Code blocks syntax-highlighted
- Search filters document list
- Navigation smooth

---

## 🎨 Theme & Styling

**Color Scheme**:
- **Gold (#F5B400)**: Primary actions, headers, highlights
- **Teal (#00796B)**: Secondary actions, subheaders
- **Dark (#1E1E1E)**: Background (easy on eyes)
- **White (#FFFFFF)**: Text (high contrast)

**Visual Cues**:
- 🥉 **Bronze**: Brown/copper color
- 🥈 **Silver**: Gray/silver color
- 🥇 **Gold**: Yellow/gold color
- ✅ **Success**: Green
- ❌ **Error**: Red
- ⚠️ **Warning**: Orange
- ℹ️ **Info**: Blue

---

## ⌨️ Keyboard Shortcuts

While the app is running:
- **R** - Rerun the current page
- **C** - Clear cache
- **Ctrl+C** (in terminal) - Stop the server

---

## 🆘 Troubleshooting

### Issue: Functions don't respond when clicked
**Solution**: 
- Make sure you're clicking the function button in "Browse Functions" tab
- After clicking, manually switch to "Function Tester" tab
- The page will show the selected function's tester

### Issue: SDK examples throw errors
**Solution**:
- All examples should work now with pd and np imported
- If you see import errors, the fix is applied
- Try refreshing the browser (Ctrl+Shift+R)

### Issue: Demo Project doesn't show data
**Solution**:
- Make sure to click the action buttons ("Ingest Data", "Transform Data", etc.)
- Bronze must run before Silver
- Silver must run before Gold
- Check the status indicators at top (✅ = complete, ⏸️ = pending)

### Issue: Visualizations don't render
**Solution**:
- Make sure plotly is installed: `pip install plotly`
- Charts require data - run the pipeline first
- If still not showing, check browser console for errors

### Issue: Page shows errors on load
**Solution**:
- Clear Streamlit cache (press 'C' in the app)
- Restart the server (Ctrl+C, then relaunch)
- Hard refresh browser (Ctrl+Shift+R)

---

## 📊 Expected Performance

| Operation | Expected Time |
|-----------|---------------|
| Page load | < 1 second |
| Function test | < 100ms |
| SDK example execution | < 500ms |
| Bronze ingestion (1000 rows) | < 200ms |
| Silver transformation | < 300ms |
| Gold aggregation | < 400ms |
| Chart rendering | < 500ms |

---

## 💡 Tips for Best Experience

1. **Start with Core Concepts** - Understand the fundamentals
2. **Use Function Tester** - Play with parameters to learn
3. **Run SDK Examples** - See patterns and best practices
4. **Run Full Demo** - Bronze → Silver → Gold → Analytics
5. **Download Results** - Take data with you for analysis
6. **Check Metrics** - Learn about performance
7. **Read Documentation** - Dive deeper into topics

---

## 📞 Support

**Documentation**:
- [ALL_UI_FIXES_COMPLETE.md](ALL_UI_FIXES_COMPLETE.md) - Fix summary
- [STUDIO_LAUNCH_GUIDE.md](STUDIO_LAUNCH_GUIDE.md) - Launch guide
- [PHASE_10_COMPLETE.md](PHASE_10_COMPLETE.md) - Phase 10 details

**Verification**:
- Run: `python diagnose_studio.py`
- Run: `python test_all_ui_features.py`

**Still have issues?**
- Check [UI_FIX_REPORT.md](UI_FIX_REPORT.md) for detailed fixes
- All issues have been resolved - if you see errors, try cache clear

---

**Enjoy learning with ODB-CORE Studio!** 🎉
