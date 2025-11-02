# Story Explanations System - ODIBI CORE v1.0

**Modernized from Energy Efficiency v2 Step Explanations**

---

## Overview

The Story Explanations system allows you to add rich, human-readable narratives to each pipeline step. These explanations appear in the generated HTML stories, providing context for what each step does, why it exists, and how it works.

**Inspired by**: Energy Efficiency v2's `metadata/Step Explanations` folder

**Modernizations**:
- ✅ Multiple format support (JSON, Markdown, Python dict)
- ✅ Structured data model (Purpose, Details, Formulas, Result)
- ✅ Auto-rendering in HTML stories
- ✅ Markdown → HTML conversion
- ✅ Backward compatible (works without explanations)

---

## V2 Example (Original Pattern)

**From `Energy Efficiency/metadata/Step Explanations/Argo/argo_boilers.py`:**

```python
step_explanations = [
    dedent("""\
    **Purpose:**
    Calculate saturated steam and feedwater enthalpy using IAPWS-97 standard.

    **Details:**
    - Converts steam pressure from psig → psia → MPa
    - Models steam as saturated vapor (x = 1)
    - Returns enthalpies in imperial units (BTU/lb)

    **Added Columns:**
    - `Boiler_Steam_h` → Saturated steam enthalpy (BTU/lb)
    - `Boiler_Feedwater_h` → Saturated feedwater enthalpy (BTU/lb)

    **Result:**
    Provides thermodynamic properties required for energy balance calculations.
    """),
]
```

**Pattern identified:**
- **Purpose** - What the step does
- **Details** - How it works (bullet points)
- **Added Columns** - Schema changes
- **Formulas** (sometimes) - Calculations
- **Result** - Expected outcome

---

## V1 Implementation (Modernized)

### Format Options

#### Option 1: JSON File (Recommended)

**File: `explanations.json`**

```json
[
  {
    "step_name": "calc_boiler_enthalpy",
    "purpose": "Calculate saturated steam and feedwater enthalpy using IAPWS-97 standard.",
    "details": [
      "Converts steam pressure from psig → psia → MPa: `(P_psig + 14.7) × 0.00689476`",
      "Converts feedwater temperature from °F → K: `(T_F − 32) × 5/9 + 273.15`",
      "Models steam as saturated vapor (x = 1)",
      "Models feedwater as saturated liquid (x = 0)",
      "Returns enthalpies in imperial units (BTU/lb)"
    ],
    "formulas": {
      "Steam Enthalpy": "IAPWS97(P=P_mpa, x=1).h × 0.429922614",
      "Feedwater Enthalpy": "IAPWS97(P=P_mpa, T=T_kelvin, x=0).h × 0.429922614"
    },
    "added_columns": ["Boiler_Steam_h", "Boiler_Feedwater_h"],
    "result": "Provides thermodynamic properties required for energy balance and efficiency calculations."
  },
  {
    "step_name": "calc_boiler_efficiency",
    "purpose": "Calculate boiler thermal efficiency using standardized energy balance.",
    "details": [
      "Calculates blowdown percentage",
      "Computes efficiency based on LHV and HHV",
      "Quantifies energy loss vs target",
      "Tracks total fuel consumption"
    ],
    "formulas": {
      "Blowdown %": "((Feed_Flow − Steam_Flow) ÷ Feed_Flow) × 100",
      "Efficiency (LHV)": "((Steam_Flow × h_steam) − (Feed_Flow × h_feed)) ÷ (Fuel_Flow × LHV) × 100",
      "Energy Loss": "(Energy_Output ÷ Efficiency) − (Energy_Output ÷ Target_Efficiency)"
    },
    "result": "Generates comprehensive boiler energy KPIs quantifying thermal performance."
  }
]
```

#### Option 2: Python Dict (Inline)

**In config metadata:**

```python
explanations = {
    "filter_high_value": {
        "purpose": "Filter dataset to include only high-value items.",
        "details": ["Executes SQL: SELECT * FROM data WHERE value > 100"],
        "result": "Produces filtered dataset with 60% of original rows."
    }
}

# Pass to tracker
story_path = tracker.export_to_story(explanations=explanations)
```

#### Option 3: Markdown Files (Per-Step)

**Directory structure:**
```
explanations/
├── calc_boiler_enthalpy.md
├── calc_efficiency.md
└── filter_data.md
```

**File: `explanations/calc_efficiency.md`:**
```markdown
**Purpose:**
Calculate boiler thermal efficiency using standardized energy balance.

**Details:**
- Uses IAPWS-97 for enthalpy calculations
- Accounts for blowdown losses
- Compares against target efficiency

**Result:**
Generates comprehensive boiler energy KPIs.
```

**Load:**
```python
loader = ExplanationLoader()
explanations = loader.load("explanations/")  # Directory
```

---

## Usage in ODIBI CORE

### Basic Usage

```python
from odibi_core.core import Tracker
from odibi_core.story import ExplanationLoader

# Execute pipeline
tracker = Tracker()
# ... run pipeline ...

# Load explanations
loader = ExplanationLoader()
explanations = loader.load("project/explanations.json")

# Generate story with explanations
story_path = tracker.export_to_story(explanations=explanations)
```

### In Demo Pipeline

```python
# Load config
steps = ConfigLoader().load("pipeline.json")

# Load explanations
explanations = ExplanationLoader().load("explanations.json")

# Execute
orchestrator.run()

# Generate story with explanations
tracker.export_to_story(explanations=explanations)
```

---

## Explanation Structure

### StepExplanation Class

```python
class StepExplanation:
    step_name: str           # Links to step name in config
    purpose: str             # What the step does
    details: List[str]       # How it works (bullet points)
    formulas: Dict[str, str] # Calculations (optional)
    added_columns: List[str] # Schema changes (optional)
    result: str              # Expected outcome
    notes: List[str]         # Additional notes (optional)
```

### Rendering in HTML Stories

**Each step card includes:**

1. **Existing sections** (always shown):
   - Step metadata (name, layer, status, duration)
   - Before snapshot (collapsible)
   - After snapshot (default open)
   - Schema changes (if any)

2. **NEW: Step Explanation** (if available):
   - Yellow background with orange left border
   - Purpose section
   - Details (bullet list)
   - Formulas table (if provided)
   - Added columns list (if provided)
   - Result summary
   - Notes (if any)

**Appearance:**
```
┌─────────────────────────────────────────┐
│ filter_high_value                       │
│ Layer: transform | Status: success      │
├─────────────────────────────────────────┤
│ ▶ Before Snapshot                       │
│ ▼ After Snapshot                        │
│   Row Count: 6 | Columns: 5             │
│   [Sample data table]                   │
│ ▼ Schema Changes                        │
│   Delta Rows: -4                        │
│ ▼ Step Explanation          [NEW]       │
│  ┌──────────────────────────────────┐   │
│  │ Purpose: Filter high-value items │   │
│  │ Details: - SQL WHERE value > 100 │   │
│  │ Result: 6 rows remaining         │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Energy Efficiency Examples (Adapted for v1)

### Example 1: Boiler Enthalpy Calculation

```json
{
  "step_name": "calc_boiler_enthalpy",
  "purpose": "Calculate saturated steam and feedwater enthalpy using IAPWS-97 industrial formulation for water properties.",
  "details": [
    "Converts steam pressure from psig → psia → MPa: `(P_psig + 14.7) × 0.00689476`",
    "Converts feedwater temperature from °F → K: `(T_F − 32) × 5/9 + 273.15`",
    "Models steam as saturated vapor using IAPWS97(P=P_mpa, x=1)",
    "Models feedwater as saturated liquid using IAPWS97(P=P_mpa, T=T_kelvin, x=0)",
    "Converts kJ/kg → BTU/lb: multiply by 0.429922614"
  ],
  "formulas": {
    "Steam Enthalpy": "IAPWS97(P=P_mpa, x=1).h × 0.429922614",
    "Feedwater Enthalpy": "IAPWS97(P=P_mpa, T=T_kelvin, x=0).h × 0.429922614"
  },
  "added_columns": ["Boiler_Steam_h", "Boiler_Feedwater_h"],
  "result": "Provides thermodynamic properties (h_steam, h_feedwater in BTU/lb) required for energy balance and efficiency calculations."
}
```

### Example 2: Efficiency Calculation

```json
{
  "step_name": "calc_boiler_energy_metrics",
  "purpose": "Calculate boiler thermal efficiency, blowdown, energy loss, and total fuel consumption using standardized energy balance.",
  "details": [
    "**Blowdown %**: Portion of feedwater purged to maintain water chemistry",
    "**Efficiency (LHV)**: Based on Lower Heating Value (combustion products exit as vapor)",
    "**Efficiency (HHV)**: Based on Higher Heating Value (includes latent heat)",
    "**Energy Loss**: Excess fuel consumed relative to design target",
    "**Energy Consumption**: Total fuel energy input to boiler"
  ],
  "formulas": {
    "Blowdown %": "((Feed_Flow − Steam_Flow) ÷ Feed_Flow) × 100",
    "Efficiency (LHV)": "((Steam_Flow × h_steam) − (Feed_Flow × h_feed)) ÷ (Fuel_Flow × LHV) × 100",
    "Efficiency (HHV)": "((Steam_Flow × h_steam) − (Feed_Flow × h_feed)) ÷ (Fuel_Flow × HHV) × 100",
    "Energy Loss": "((Steam_Flow × h_steam) ÷ Efficiency) − ((Steam_Flow × h_steam) ÷ Target_Efficiency)"
  },
  "added_columns": ["Blowdown %", "Efficiency (LHV)", "Efficiency (HHV)", "Energy Loss", "Energy Consumption"],
  "result": "Generates comprehensive boiler energy KPIs quantifying thermal performance and identifying efficiency gaps against target benchmarks."
}
```

### Example 3: Gold Layer Union

```json
{
  "step_name": "combine_all_boilers",
  "purpose": "Consolidate all boiler energy efficiency data across three plants into a unified Gold-layer dataset.",
  "details": [
    "Performs SQL UNION of 4 boiler Silver tables from Argo, Cedar Rapids, and Winston Salem",
    "Filters data to exclude current-day records: `WHERE Time_Stamp < current_date()`",
    "Combines thermal efficiency metrics (HHV/LHV), fuel consumption, steam production",
    "Maintains standardized schema for cross-plant analytics"
  ],
  "result": "Generates `combined_boilers` Gold table enabling enterprise-wide boiler performance benchmarking and thermal efficiency analysis."
}
```

---

## How It Works

### 1. Author Explanations

Create `explanations.json` with step narratives:

```json
[
  {"step_name": "step1", "purpose": "...", "details": [...]},
  {"step_name": "step2", "purpose": "...", "formulas": {...}}
]
```

### 2. Load Explanations

```python
from odibi_core.story import ExplanationLoader

loader = ExplanationLoader()
explanations = loader.load("explanations.json")
```

### 3. Generate Story with Explanations

```python
# Automatic (via tracker)
tracker.export_to_story(explanations=explanations)

# Manual
from odibi_core.story import StoryGenerator

generator = StoryGenerator(explanations=explanations)
story_path = generator.save_story(lineage)
```

### 4. View HTML Story

Open `stories/story_*.html` in browser - explanations appear in each step card!

---

## Markdown Support

### Basic Markdown

**Supported syntax:**
- `**bold**` → **bold**
- `` `code` `` → `code`
- `- list item` → • list item
- Tables (if markdown library installed)

**Example:**
```markdown
**Purpose:**
Calculate efficiency using `IAPWS-97` standard.

**Details:**
- Convert pressure: `P_mpa = (P_psig + 14.7) × 0.00689476`
- Calculate enthalpy: `h = IAPWS97(P, T).h`

**Result:**
Adds `Boiler_Steam_h` column in BTU/lb.
```

### Formula Tables

**Markdown table:**
```markdown
| Column | Formula |
|--------|---------|
| `Efficiency` | `(output / input) × 100` |
| `Blowdown %` | `((feed - steam) / feed) × 100` |
```

**Renders as:**
| Column | Formula |
|--------|---------|
| `Efficiency` | `(output / input) × 100` |
| `Blowdown %` | `((feed - steam) / feed) × 100` |

---

## Authoring Best Practices

### Pattern from Energy Efficiency

**Good explanation structure:**

1. **Purpose** (1 sentence) - What and why
2. **Details** (3-5 bullets) - How it works
3. **Formulas** (if calculations) - Exact formulas
4. **Added Columns** (if schema changes) - New columns
5. **Result** (1 sentence) - Expected outcome

### Example Template

```json
{
  "step_name": "your_step_name",
  "purpose": "[One sentence: what this step does]",
  "details": [
    "[Bullet 1: key operation]",
    "[Bullet 2: important detail]",
    "[Bullet 3: technical note]"
  ],
  "formulas": {
    "Column_Name": "[formula or calculation]"
  },
  "added_columns": ["new_col1", "new_col2"],
  "result": "[One sentence: what you get]"
}
```

### Writing Tips

**Do:**
- ✅ Use technical precision (exact column names, formulas)
- ✅ Include units (BTU/lb, psig, °F)
- ✅ Explain conversions (°F → K)
- ✅ List added/removed columns
- ✅ Keep purpose to 1-2 sentences

**Don't:**
- ❌ Write novels (keep details to 3-7 bullets)
- ❌ Repeat what's obvious from code
- ❌ Use jargon without explanation
- ❌ Forget units on formulas

---

## Integration with Config

### Inline in Config Metadata

```json
{
  "layer": "transform",
  "name": "calc_efficiency",
  "type": "function",
  "value": "thermo.boiler_efficiency",
  "metadata": {
    "explanation": {
      "purpose": "Calculate boiler efficiency using energy balance",
      "formulas": {"Efficiency": "(output / input) × 100"}
    }
  }
}
```

**Then:**
```python
# Extract from config metadata
explanations = {}
for step in steps:
    if "explanation" in step.metadata:
        explanations[step.name] = step.metadata["explanation"]

tracker.export_to_story(explanations=explanations)
```

---

## Backward Compatibility

### Without Explanations

```python
# Works exactly as before
tracker.export_to_story()
# Generates story with snapshots, no explanations
```

### With Explanations

```python
# Enhanced story
tracker.export_to_story(explanations=explanations)
# Generates story WITH explanations in yellow boxes
```

**No breaking changes** - explanations are purely additive.

---

## Advanced: Auto-Generated Explanations

### Concept (Future Enhancement)

**Use AMP to generate draft explanations:**

```python
# Analyze SQL
sql = "SELECT category, AVG(value) as avg_value FROM data GROUP BY category"

# AMP infers:
explanation = {
    "purpose": "Calculate average value by category",
    "details": ["Groups data by category column", "Computes AVG aggregation"],
    "added_columns": ["avg_value"],
    "result": "One row per category with average value"
}
```

**Benefit**: Jumpstart explanation authoring, human edits for precision.

---

## Examples from Energy Efficiency (Modernized)

### Pivot Operation

```json
{
  "step_name": "pivot_historian_data",
  "purpose": "Convert long-format historian data into wide-format structure for KPI calculations.",
  "details": [
    "Groups by Time_Stamp, Plant, and Asset",
    "Pivots Description column values into individual measurement columns",
    "Aggregates values using first() function per timestamp",
    "Produces one consolidated record per hour"
  ],
  "result": "Wide-format dataset ready for IAPWS-97 enthalpy calculations and constant joins."
}
```

### Unpivot Operation

```json
{
  "step_name": "unpivot_calculated_kpis",
  "purpose": "Convert wide-format calculated KPIs into standardized long format.",
  "details": [
    "Unpivots all calculated columns into Description / Value pairs",
    "Preserves identifier columns: Time_Stamp, Plant, Asset",
    "Ensures schema compatibility with Silver-layer data model"
  ],
  "result": "Normalized long-format dataset ready for final enrichment and unit conversion."
}
```

### Gold Layer Consolidation

```json
{
  "step_name": "combine_all_plants",
  "purpose": "Consolidate energy efficiency data across all plants into unified Gold-layer dataset.",
  "details": [
    "Performs SQL UNION of Silver tables from Argo, Cedar Rapids, Winston Salem, NKC plants",
    "Filters to exclude current-day incomplete records",
    "Maintains standardized schema for cross-plant comparisons",
    "Enables enterprise-wide performance benchmarking"
  ],
  "result": "Generates `combined_all_assets` Gold table for executive dashboards and efficiency analysis."
}
```

---

## Visual Result

### HTML Story with Explanations

**Step card now includes:**

```html
<div class="step-card success">
    <h2>calc_boiler_enthalpy</h2>
    <div class="step-meta">...</div>
    
    <!-- Snapshots -->
    <details>...</details>
    
    <!-- NEW: Explanation -->
    <details open>
        <summary><strong>Step Explanation</strong></summary>
        <div class="explanation">
            <p><strong>Purpose:</strong></p>
            <p>Calculate saturated steam and feedwater enthalpy using IAPWS-97.</p>
            
            <p><strong>Details:</strong></p>
            <ul>
                <li>Converts steam pressure from psig → psia → MPa</li>
                <li>Models steam as saturated vapor (x = 1)</li>
                <li>Returns enthalpies in BTU/lb</li>
            </ul>
            
            <p><strong>Formulas:</strong></p>
            <table>
                <tr><th>Column</th><th>Formula</th></tr>
                <tr><td>Steam Enthalpy</td><td>IAPWS97(P, x=1).h × 0.429</td></tr>
            </table>
            
            <p><strong>Result:</strong></p>
            <p>Provides thermodynamic properties for energy balance.</p>
        </div>
    </details>
</div>
```

**Visual styling:**
- Yellow background (#fef3c7)
- Orange left border (#f59e0b)
- Clear sectioning (Purpose, Details, Result)
- Formatted code blocks and formulas

---

## Summary

### What We Achieved

**Ported from v2:**
- ✅ Purpose/Details/Result pattern
- ✅ Formula documentation
- ✅ Technical precision
- ✅ Bullet-point details

**Modernizations:**
- ✅ JSON format (v2 used Python strings)
- ✅ Multiple format support (JSON, Markdown, dict)
- ✅ Auto-rendering in HTML
- ✅ Markdown → HTML conversion
- ✅ Backward compatible

**Benefits:**
- ✅ Self-documenting pipelines
- ✅ Knowledge preservation
- ✅ Onboarding new engineers
- ✅ Audit trail with context
- ✅ AMP can read and understand pipelines

---

## Next Steps

### For Your Energy Efficiency Project

1. **Convert v2 explanations to JSON:**
   ```bash
   # Extract from argo_boilers.py step_explanations list
   # Save as argo_boilers_explanations.json
   ```

2. **Load in ODIBI CORE:**
   ```python
   explanations = ExplanationLoader().load("metadata/argo_boilers_explanations.json")
   tracker.export_to_story(explanations=explanations)
   ```

3. **View enhanced stories:**
   - Open `stories/story_*.html`
   - See your domain knowledge preserved!

---

**Story Explanations System: Complete!** 📖✨

Makes ODIBI CORE pipelines **self-documenting** with rich narratives inspired by your Energy Efficiency v2 best practices!
