# ODIBI_CORE Dual-Mode Showcase Suite
## Configuration Examples & Demonstrations

**Purpose:** Educational demonstrations of ODIBI_CORE's dual-mode configuration architecture (JSON vs SQL)

---

## Quick Start

### Run Showcase #1 (Fully Validated)
```bash
cd D:/projects/odibi_core
python scripts/showcase_01_runner.py
```

**What it does:**
- Loads bookstore sales and inventory data
- Executes 8-step pipeline in both JSON and SQL modes
- Compares results (100% match expected)
- Generates comparison report

---

## Files in This Directory

### Configuration Files
- `showcase_01.json` - Global Bookstore Analytics (✅ Validated)
- `showcase_02.json` - Smart Home Sensor Data Pipeline
- `showcase_03.json` - Movie Recommendation Data Flow
- `showcase_04.json` - Financial Transactions Audit
- `showcase_05.json` - Social Media Sentiment Dashboard
- `showcase_06.json` - City Weather & Air Quality Data Merger
- `showcase_07.json` - Healthcare Patient Wait-Time Analysis
- `showcase_08.json` - E-Commerce Returns Monitor
- `showcase_09.json` - Transportation Fleet Tracker
- `showcase_10.json` - Education Outcome Correlation Study

### Database
- `showcase_configs.db` - SQLite database containing SQL-mode configs
- `showcase_db_init.sql` - Database schema definition

---

## Configuration Format Examples

### JSON Config Structure
```json
{
  "layer": "silver",
  "name": "calculate_revenue",
  "type": "transform",
  "engine": "pandas",
  "value": {
    "operation": "add_column",
    "column_name": "revenue",
    "expression": "price * quantity_sold"
  },
  "params": {},
  "inputs": ["bookstore_sales"],
  "outputs": ["sales_with_revenue"],
  "metadata": {
    "description": "Calculate total revenue per book sale"
  }
}
```

### SQL Config Structure
```sql
INSERT INTO showcase_config 
(showcase_id, showcase_name, layer, step_name, step_type, engine, value, inputs, outputs, metadata)
VALUES 
(1, 'Global Bookstore Analytics', 'silver', 'calculate_revenue', 'transform', 'pandas',
 '{"operation": "add_column", "column_name": "revenue", "expression": "price * quantity_sold"}',
 '["bookstore_sales"]', '["sales_with_revenue"]', 
 '{"description": "Calculate total revenue per book sale"}');
```

---

## Sample Data Locations

All sample data files are in: `../../data/showcases/`

**Showcase #1:**
- `bookstore_sales.csv` (15 rows)
- `bookstore_inventory.csv` (15 rows)

**Showcase #2:**
- `sensor_readings.csv` (50 rows)
- `device_metadata.csv` (15 rows)

**Showcases #3-10:**
- `data_X_1.csv` (20 rows each - placeholder data)

---

## Output Locations

- **JSON Mode Outputs:** `../../output/showcases/json_mode/showcase_XX/`
- **SQL Mode Outputs:** `../../output/showcases/sql_mode/showcase_XX/`

---

## Reports

All comparison reports are in: `../../../reports/showcases/`

- `SHOWCASE_01_GLOBAL_BOOKSTORE_ANALYTICS_COMPARE.md` (✅ Complete)
- `SHOWCASE_DUALMODE_SUMMARY.md` (Master summary)

---

## Showcase Themes

| ID | Name | Theme | Status |
|----|------|-------|--------|
| 1 | Global Bookstore Analytics | Retail Analytics | ✅ Validated |
| 2 | Smart Home Sensor Data | IoT Analytics | ⏳ Config Ready |
| 3 | Movie Recommendation | Content Analytics | ⏳ Config Ready |
| 4 | Financial Transactions | Finance & Compliance | ⏳ Config Ready |
| 5 | Social Media Sentiment | Social Analytics | ⏳ Config Ready |
| 6 | Weather & Air Quality | Environmental Data | ⏳ Config Ready |
| 7 | Patient Wait-Time | Healthcare Operations | ⏳ Config Ready |
| 8 | E-Commerce Returns | Retail Operations | ⏳ Config Ready |
| 9 | Fleet Tracker | Logistics | ⏳ Config Ready |
| 10 | Education Outcomes | Education Analytics | ⏳ Config Ready |

---

## Educational Value

Each showcase demonstrates:
- ✅ **Bronze/Silver/Gold Medallion Architecture**
- ✅ **JSON vs SQL Configuration Parity**
- ✅ **Pandas Engine Capabilities**
- ✅ **Data Lineage Tracking**
- ✅ **Performance Metrics**

---

## Key Learnings

### For Data Engineers
- **Flexibility:** Choose JSON (git-friendly) or SQL (governance-focused) based on team needs
- **Validation:** Dual-mode execution is a powerful testing strategy
- **Performance:** Configuration source has negligible impact on runtime

### For Framework Developers
- **Abstraction:** Config normalization enables multi-source support
- **Extensibility:** Adding YAML/Parquet/API sources requires minimal code changes
- **Testing:** Side-by-side execution validates implementation correctness

---

## Next Steps

1. **Run Showcase #1** to see dual-mode execution in action
2. **Review generated report** to understand comparison methodology
3. **Explore JSON configs** to learn pipeline structure
4. **Query SQL database** to see alternative config storage
5. **Customize data files** to test with your own datasets

---

*Part of ODIBI_CORE Dual-Mode Demonstration Project (ODB-1)*  
*Author: Henry Odibi*
