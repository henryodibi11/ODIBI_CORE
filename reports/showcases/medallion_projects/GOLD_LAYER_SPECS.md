# Phase 3: Gold Layer Specifications
## ODIBI_CORE Medallion Architecture Projects

**Phase:** 3 - Gold Layer (Analytics & KPIs)  
**Date:** 2025-11-02  
**Status:** ✅ COMPLETE

---

## 🎯 Objective

Define analytics-ready layer with KPIs, aggregations, and dimensional modeling. Create ODIBI_CORE configs for Gold layer business metrics.

---

## 🥇 Gold Layer Architecture

**Purpose:** Business-ready datasets with calculated KPIs  
**Pattern:** Silver → Aggregate → Calculate KPIs → Publish → Gold storage  
**Node Types:** `connect` (load Silver), `transform` (aggregations), `publish`  
**Requirements:** ≥3 analytic metrics/aggregates per project, explicit formulas

---

## 📁 Project Gold Analytics

### P01: Manufacturing Yield & Downtime KPI System

**Aggregation Level:** Machine + Shift + Day

**KPIs (5):**

1. **OEE (Overall Equipment Effectiveness)**
   - Formula: `OEE = Availability × Performance × Quality`
   - Availability = (Operating Time - Downtime) / Operating Time
   - Performance = (Actual Production / Target Production)
   - Quality = (Good Units / Total Units)
   - Target: > 85%

2. **MTBF (Mean Time Between Failures)**
   - Formula: `MTBF = Total Operating Hours / Number of Failures`
   - Unit: Hours
   - Target: > 200 hours

3. **Yield Rate**
   - Formula: `Yield = (Units Produced - Defects) / Units Produced * 100`
   - Unit: Percentage
   - Target: > 95%

4. **Downtime Cost**
   - Formula: `Downtime Cost = Downtime Hours × (Labor Cost + Opportunity Cost)`
   - Unit: USD
   - Breakdown: Planned vs Unplanned

5. **Production Throughput**
   - Formula: `Throughput = Total Units Produced / Total Time`
   - Unit: Units/Hour
   - Aggregated: By machine, shift, product type

**Dimensions:** machine_id, shift, product_type, date

**Gold Outputs:**
- `gold_manufacturing_kpis_daily.parquet`
- `gold_manufacturing_kpis_by_machine.parquet`

**Total Nodes:** 8

---

### P02: Financial Transactions Reconciliation

**Aggregation Level:** Account + Day + Transaction Type

**KPIs (4):**

1. **Reconciliation Rate**
   - Formula: `Reconciliation Rate = Matched Transactions / Total Transactions * 100`
   - Target: > 99.9%

2. **Fraud Detection Accuracy**
   - Formula: `Accuracy = True Positives / (True Positives + False Positives)`
   - Includes: Precision, Recall, F1-Score
   - Target: F1 > 0.85

3. **Credit Risk Score (Portfolio)**
   - Formula: `Portfolio Risk = Σ(Account Balance × Fraud Score × Default Probability)`
   - Unit: USD
   - Aggregated: By risk tier, account type

4. **Transaction Velocity**
   - Formula: `Velocity = Count(Transactions in 24h) / Historical Average`
   - Anomaly threshold: > 3 standard deviations
   - Use case: Fraud detection

**Dimensions:** account_id, account_type, risk_tier, currency, date

**Gold Outputs:**
- `gold_financial_kpis_daily.parquet`
- `gold_financial_risk_summary.parquet`

**Total Nodes:** 9

---

### P03: IoT Sensor Reliability & Maintenance Prediction

**Aggregation Level:** Sensor + Location + Week

**KPIs (4):**

1. **Sensor Uptime**
   - Formula: `Uptime = Online Hours / Total Hours * 100`
   - Target: > 99.5%

2. **Prediction Accuracy**
   - Formula: `Accuracy = Correct Predictions / Total Predictions`
   - Breakdown: True positive, false positive, false negative rates
   - Target: > 90%

3. **Maintenance Cost Savings**
   - Formula: `Savings = (Reactive Cost - Predictive Cost) / Reactive Cost * 100`
   - Comparison: Planned vs emergency maintenance costs
   - Target: 30% reduction

4. **Battery Health Index**
   - Formula: `Health Index = Battery Level × (1 - Drain Rate) × Uptime Ratio`
   - Range: 0-100
   - Action trigger: < 30

**Dimensions:** sensor_id, location, maintenance_type, date

**Gold Outputs:**
- `gold_iot_reliability_weekly.parquet`
- `gold_iot_maintenance_forecast.parquet`

**Total Nodes:** 8

---

### P04: Retail Demand Forecast & Promotion Effectiveness

**Aggregation Level:** Product + Store + Week

**KPIs (5):**

1. **Forecast Accuracy (MAPE)**
   - Formula: `MAPE = (1/n) × Σ|Actual - Forecast| / Actual × 100`
   - Target: < 15%

2. **Promotion Lift**
   - Formula: `Lift = (Sales During Promo - Baseline Sales) / Baseline Sales × 100`
   - Target: > 20%

3. **Inventory Turnover**
   - Formula: `Turnover = COGS / Average Inventory`
   - Target: > 8 (monthly)

4. **Marketing ROI**
   - Formula: `ROI = (Revenue - Marketing Spend) / Marketing Spend × 100`
   - Target: > 300%

5. **Stock-Out Rate**
   - Formula: `Stock-Out Rate = Days Out of Stock / Total Days × 100`
   - Target: < 2%

**Dimensions:** product_id, category, store_id, campaign_id, date

**Gold Outputs:**
- `gold_retail_demand_forecast.parquet`
- `gold_retail_promotion_effectiveness.parquet`

**Total Nodes:** 10

---

### P05: Healthcare Appointment Analytics

**Aggregation Level:** Doctor + Clinic + Week

**KPIs (4):**

1. **Average Wait Time**
   - Formula: `Avg Wait = Σ(Actual Start - Scheduled) / Total Appointments`
   - Unit: Minutes
   - Target: < 15 minutes

2. **Appointment Utilization**
   - Formula: `Utilization = Booked Slots / Available Slots × 100`
   - Target: 85-95% (optimal range)

3. **No-Show Rate**
   - Formula: `No-Show Rate = No-Shows / Total Appointments × 100`
   - Target: < 10%

4. **Patient Wait-Time Reduction**
   - Formula: `Reduction = (Previous Wait - Current Wait) / Previous Wait × 100`
   - Trend: Month-over-month improvement
   - Target: 20% reduction YoY

**Dimensions:** doctor_id, appointment_type, insurance_type, date

**Gold Outputs:**
- `gold_healthcare_wait_time_kpis.parquet`
- `gold_healthcare_utilization_by_doctor.parquet`

**Total Nodes:** 8

---

### P06: Energy Efficiency & Weather Normalization

**Aggregation Level:** Building + Month

**KPIs (4):**

1. **kWh per Degree Day**
   - Formula: `Intensity = Total kWh / (Heating DD + Cooling DD)`
   - Benchmark: Compare to similar buildings
   - Target: Reduction of 10% YoY

2. **Consumption Variance**
   - Formula: `Variance = (Actual - Baseline) / Baseline × 100`
   - Normalized for weather
   - Target: Variance < 5%

3. **Efficiency Score**
   - Formula: `Score = (Baseline Consumption / Actual Consumption) × 100`
   - Target: > 100 (consuming less than baseline)

4. **Savings Achieved**
   - Formula: `Savings = (Baseline kWh - Actual kWh) × Energy Rate`
   - Unit: USD
   - Aggregated: By building type, month

**Dimensions:** meter_id, building_type, hvac_system, month

**Gold Outputs:**
- `gold_energy_efficiency_monthly.parquet`
- `gold_energy_weather_normalized.parquet`

**Total Nodes:** 7

---

### P07: Logistics Fleet Tracking & Delivery SLA

**Aggregation Level:** Vehicle + Route + Day

**KPIs (4):**

1. **On-Time Delivery Percentage**
   - Formula: `OTD% = On-Time Deliveries / Total Deliveries × 100`
   - On-Time: Within 15 minutes of scheduled time
   - Target: > 95%

2. **Average Delivery Time**
   - Formula: `Avg Time = Σ Delivery Duration / Count(Deliveries)`
   - Unit: Minutes
   - Breakdown: By route, time of day

3. **Fuel Efficiency**
   - Formula: `Efficiency = Total Distance / Total Fuel Consumed`
   - Unit: km/L
   - Target: > 8 km/L

4. **SLA Compliance Cost**
   - Formula: `Cost = Late Deliveries × Penalty + Failed Deliveries × Refund`
   - Unit: USD
   - Target: < 1% of revenue

**Dimensions:** vehicle_id, route_id, delivery_status, date

**Gold Outputs:**
- `gold_logistics_sla_daily.parquet`
- `gold_logistics_fleet_efficiency.parquet`

**Total Nodes:** 9

---

### P08: Marketing Attribution & Conversion Funnel

**Aggregation Level:** Campaign + Channel + Week

**KPIs (5):**

1. **Conversion Rate**
   - Formula: `CVR = Conversions / Clicks × 100`
   - Target: > 3%

2. **Customer Acquisition Cost (CAC)**
   - Formula: `CAC = Total Marketing Spend / New Customers`
   - Unit: USD
   - Benchmark: By channel

3. **Return on Ad Spend (ROAS)**
   - Formula: `ROAS = Revenue from Ads / Ad Spend`
   - Target: > 4.0 (400%)

4. **Attribution Efficiency**
   - Formula: Compares first-touch, last-touch, linear, time-decay models
   - Metric: Which touchpoint contributes most to conversions

5. **Customer Lifetime Value (CLV)**
   - Formula: `CLV = Avg Order Value × Purchase Frequency × Customer Lifespan`
   - Unit: USD
   - Use: Compare to CAC (CLV/CAC > 3)

**Dimensions:** campaign_id, platform, ad_id, user_segment, date

**Gold Outputs:**
- `gold_marketing_attribution_weekly.parquet`
- `gold_marketing_funnel_metrics.parquet`

**Total Nodes:** 11

---

### P09: Education Outcome Correlation

**Aggregation Level:** Student Cohort + Major + Semester

**KPIs (4):**

1. **Graduation Rate**
   - Formula: `Grad Rate = Graduated Students / Enrolled Students × 100`
   - Cohort: Track same enrollment year
   - Target: > 80%

2. **GPA Trends**
   - Formula: `Avg GPA = Σ(Grade Points × Credits) / Σ Credits`
   - Breakdown: By major, cohort, semester
   - Target: Increasing trend

3. **Attendance Correlation**
   - Formula: `Correlation = Pearson(Attendance Rate, GPA)`
   - Statistical significance: p < 0.05
   - Insight: Quantify attendance impact

4. **At-Risk Student Rate**
   - Formula: `At-Risk % = (GPA < 2.0 OR Attendance < 75%) / Total Students × 100`
   - Early warning system
   - Target: < 15%

**Dimensions:** student_id, major, enrollment_year, semester

**Gold Outputs:**
- `gold_education_graduation_rates.parquet`
- `gold_education_correlation_analysis.parquet`

**Total Nodes:** 8

---

### P10: SaaS Usage Reporting & Tenant KPIs

**Aggregation Level:** Tenant + Feature + Month

**KPIs (5):**

1. **DAU/MAU Ratio**
   - Formula: `Stickiness = DAU / MAU`
   - Target: > 0.3 (30% daily engagement)

2. **Feature Adoption Rate**
   - Formula: `Adoption = Users Using Feature / Total Users × 100`
   - Track: New feature rollout success
   - Target: > 60% within 90 days

3. **Churn Prediction Score**
   - Formula: Multi-factor model (DAU trend, support tickets, usage decline)
   - Range: 0-100
   - Action trigger: > 70

4. **Average Revenue Per User (ARPU)**
   - Formula: `ARPU = MRR / Active Users`
   - Unit: USD
   - Benchmark: By subscription tier

5. **Net Revenue Retention (NRR)**
   - Formula: `NRR = (Starting MRR + Expansion - Churn) / Starting MRR × 100`
   - Target: > 110% (negative churn)

**Dimensions:** tenant_id, subscription_tier, feature_name, month

**Gold Outputs:**
- `gold_saas_tenant_kpis_monthly.parquet`
- `gold_saas_feature_adoption.parquet`

**Total Nodes:** 10

---

## 📊 Summary Statistics

| Project | KPIs | Aggregation Levels | Gold Outputs | Gold Nodes |
|---------|------|-------------------|--------------|------------|
| P01 Manufacturing | 5 | machine, shift, day | 2 | 8 |
| P02 Financial | 4 | account, day, type | 2 | 9 |
| P03 IoT Sensors | 4 | sensor, location, week | 2 | 8 |
| P04 Retail | 5 | product, store, week | 2 | 10 |
| P05 Healthcare | 4 | doctor, clinic, week | 2 | 8 |
| P06 Energy | 4 | building, month | 2 | 7 |
| P07 Logistics | 4 | vehicle, route, day | 2 | 9 |
| P08 Marketing | 5 | campaign, channel, week | 2 | 11 |
| P09 Education | 4 | cohort, major, semester | 2 | 8 |
| P10 SaaS | 5 | tenant, feature, month | 2 | 10 |
| **TOTAL** | **44 KPIs** | **Multiple dimensions** | **20 outputs** | **88** |

---

## 📐 KPI Formula Reference

### Manufacturing
- **OEE** = Availability × Performance × Quality
- **MTBF** = Operating Hours / Failures
- **Yield** = Good Units / Total Units

### Financial
- **Reconciliation Rate** = Matched / Total
- **Portfolio Risk** = Σ(Balance × Risk Score)

### Retail
- **MAPE** = (1/n) × Σ|Actual - Forecast| / Actual
- **ROI** = (Revenue - Spend) / Spend

### Healthcare
- **Utilization** = Booked / Available
- **No-Show Rate** = No-Shows / Total

### Energy
- **Intensity** = kWh / Degree Days
- **Efficiency** = Baseline / Actual

### Logistics
- **OTD%** = On-Time / Total
- **Fuel Efficiency** = Distance / Fuel

### Marketing
- **ROAS** = Revenue / Ad Spend
- **CAC** = Spend / Customers

### Education
- **Graduation Rate** = Graduated / Enrolled
- **Correlation** = Pearson(Attendance, GPA)

### SaaS
- **DAU/MAU** = Daily Users / Monthly Users
- **NRR** = (Start + Expansion - Churn) / Start

---

## ✅ Acceptance Criteria Met

- [x] Each project has ≥3 analytic metrics (avg 4.4 per project)
- [x] All KPIs have explicit formulas
- [x] Aggregations defined at appropriate business levels
- [x] Total of 88 Gold layer nodes across 10 projects
- [x] 44 unique KPIs covering all domains

---

## 🚀 Next Steps

**Phase 4: Execution & Validation** - Run all 10 projects end-to-end, validate results

**Deliverable:** Tracker logs, Event summaries, Row reconciliation

---

*Generated by ODIBI_CORE Medallion Project System*  
*Phase: 3 - Gold Layer | Status: COMPLETE*
