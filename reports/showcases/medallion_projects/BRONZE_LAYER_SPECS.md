# Phase 1: Bronze Layer Specifications
## ODIBI_CORE Medallion Architecture Projects

**Phase:** 1 - Bronze Layer (Raw Ingestion)  
**Date:** 2025-11-02  
**Status:** ✅ COMPLETE

---

## 🎯 Objective

Define ingestion layer for all 10 medallion projects with 3+ heterogeneous data sources each. Generate sample data and ODIBI_CORE configs for Bronze layer ingestion.

---

## 📊 Bronze Layer Architecture

**Purpose:** Raw data ingestion with minimal transformation  
**Pattern:** Source → Connect node → Publish node → Bronze storage  
**File Formats:** CSV, JSON, Parquet  
**Node Types:** `connect` (ingestion), `publish` (save to Bronze)

---

## 📁 Project Specifications

### P01: Manufacturing Yield & Downtime KPI System

**Data Sources:**
1. **machine_sensors.csv** (200 rows)
   - Schema: timestamp, machine_id, temperature, pressure, vibration, production_count, status
   - Refresh: Hourly
   - Format: CSV

2. **production_logs.json** (100 rows)
   - Schema: batch_id, machine_id, product_type, start_time, end_time, units_produced, units_defective, shift
   - Refresh: Per batch
   - Format: JSON

3. **maintenance_records.parquet** (50 rows)
   - Schema: maintenance_id, machine_id, maintenance_date, maintenance_type, downtime_hours, cost
   - Refresh: Daily
   - Format: Parquet

**Bronze Outputs:**
- `bronze_machine_sensors.parquet`
- `bronze_production_logs.parquet`
- `bronze_maintenance_records.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P02: Financial Transactions Reconciliation

**Data Sources:**
1. **transactions.csv** (500 rows)
   - Schema: transaction_id, account_id, timestamp, amount, currency, transaction_type, merchant_id
   - Refresh: Real-time
   - Format: CSV

2. **accounts.json** (100 rows)
   - Schema: account_id, customer_name, account_type, balance, credit_limit, risk_tier
   - Refresh: Daily
   - Format: JSON

3. **risk_ratings.parquet** (100 rows)
   - Schema: account_id, credit_score, fraud_score, days_delinquent, risk_updated_date
   - Refresh: Weekly
   - Format: Parquet

**Bronze Outputs:**
- `bronze_transactions.parquet`
- `bronze_accounts.parquet`
- `bronze_risk_ratings.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P03: IoT Sensor Reliability & Maintenance Prediction

**Data Sources:**
1. **sensor_telemetry.csv** (300 rows)
   - Schema: timestamp, sensor_id, temperature, humidity, battery_level, signal_strength, status
   - Refresh: 30-minute intervals
   - Format: CSV

2. **maintenance_logs.json** (40 rows)
   - Schema: maintenance_id, sensor_id, maintenance_date, issue_type, resolution_time_hours, cost
   - Refresh: As-needed
   - Format: JSON

3. **weather_data.parquet** (30 rows)
   - Schema: date, location, avg_temperature, precipitation_mm, wind_speed_kph
   - Refresh: Daily
   - Format: Parquet

**Bronze Outputs:**
- `bronze_sensor_telemetry.parquet`
- `bronze_maintenance_logs.parquet`
- `bronze_weather_data.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P04: Retail Demand Forecast & Promotion Effectiveness

**Data Sources:**
1. **sales_transactions.csv** (400 rows)
   - Schema: transaction_id, timestamp, store_id, product_id, quantity, price, discount_applied
   - Refresh: Real-time
   - Format: CSV

2. **inventory_levels.json** (50 rows)
   - Schema: product_id, product_name, category, current_stock, reorder_point, supplier_id
   - Refresh: Daily
   - Format: JSON

3. **promotional_campaigns.parquet** (20 rows)
   - Schema: campaign_id, start_date, end_date, product_id, discount_rate, marketing_spend
   - Refresh: Weekly
   - Format: Parquet

**Bronze Outputs:**
- `bronze_sales_transactions.parquet`
- `bronze_inventory_levels.parquet`
- `bronze_promotional_campaigns.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P05: Healthcare Appointment Analytics

**Data Sources:**
1. **appointment_records.csv** (300 rows)
   - Schema: appointment_id, patient_id, doctor_id, scheduled_time, actual_start_time, appointment_type, status
   - Refresh: Hourly
   - Format: CSV

2. **patient_demographics.json** (100 rows)
   - Schema: patient_id, age, gender, insurance_type, chronic_conditions, risk_score
   - Refresh: Daily
   - Format: JSON

3. **clinic_capacity.parquet** (30 rows)
   - Schema: date, doctor_id, available_slots, booked_slots, avg_appointment_duration_min
   - Refresh: Daily
   - Format: Parquet

**Bronze Outputs:**
- `bronze_appointment_records.parquet`
- `bronze_patient_demographics.parquet`
- `bronze_clinic_capacity.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P06: Energy Efficiency & Weather Normalization

**Data Sources:**
1. **meter_readings.csv** (720 rows)
   - Schema: timestamp, meter_id, kwh_consumed, power_factor, voltage
   - Refresh: Hourly
   - Format: CSV

2. **weather_data.json** (30 rows)
   - Schema: date, location, avg_temperature_c, heating_degree_days, cooling_degree_days
   - Refresh: Daily
   - Format: JSON

3. **building_metadata.parquet** (20 rows)
   - Schema: meter_id, building_type, square_footage, year_built, hvac_system
   - Refresh: Static
   - Format: Parquet

**Bronze Outputs:**
- `bronze_meter_readings.parquet`
- `bronze_weather_data.parquet`
- `bronze_building_metadata.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P07: Logistics Fleet Tracking & Delivery SLA

**Data Sources:**
1. **gps_telemetry.csv** (400 rows)
   - Schema: timestamp, vehicle_id, latitude, longitude, speed_kph, fuel_level_pct
   - Refresh: 15-minute intervals
   - Format: CSV

2. **delivery_records.json** (150 rows)
   - Schema: delivery_id, vehicle_id, customer_id, scheduled_time, actual_delivery_time, delivery_status, distance_km
   - Refresh: Real-time
   - Format: JSON

3. **traffic_data.parquet** (168 rows)
   - Schema: timestamp, route_id, congestion_level, avg_speed_kph, incidents
   - Refresh: Hourly
   - Format: Parquet

**Bronze Outputs:**
- `bronze_gps_telemetry.parquet`
- `bronze_delivery_records.parquet`
- `bronze_traffic_data.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P08: Marketing Attribution & Conversion Funnel

**Data Sources:**
1. **ad_impressions.csv** (1000 rows)
   - Schema: impression_id, timestamp, campaign_id, ad_id, user_id, platform, cost
   - Refresh: Real-time
   - Format: CSV

2. **clicks_conversions.json** (200 rows)
   - Schema: click_id, impression_id, user_id, click_timestamp, conversion, conversion_value
   - Refresh: Real-time
   - Format: JSON

3. **customer_journey.parquet** (300 rows)
   - Schema: user_id, session_id, touchpoint_sequence, first_touch, last_touch, converted
   - Refresh: Daily
   - Format: Parquet

**Bronze Outputs:**
- `bronze_ad_impressions.parquet`
- `bronze_clicks_conversions.parquet`
- `bronze_customer_journey.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P09: Education Outcome Correlation

**Data Sources:**
1. **student_grades.csv** (500 rows)
   - Schema: student_id, course_id, semester, grade, grade_points, credits
   - Refresh: End of semester
   - Format: CSV

2. **attendance_records.json** (150 rows)
   - Schema: student_id, semester, classes_attended, classes_total, attendance_rate
   - Refresh: Weekly
   - Format: JSON

3. **student_demographics.parquet** (150 rows)
   - Schema: student_id, age, gender, major, enrollment_year, financial_aid
   - Refresh: Semester
   - Format: Parquet

**Bronze Outputs:**
- `bronze_student_grades.parquet`
- `bronze_attendance_records.parquet`
- `bronze_student_demographics.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

### P10: SaaS Usage Reporting & Tenant KPIs

**Data Sources:**
1. **user_events.csv** (800 rows)
   - Schema: event_id, timestamp, user_id, tenant_id, event_type, feature_name, session_duration_sec
   - Refresh: Real-time
   - Format: CSV

2. **subscription_data.json** (20 rows)
   - Schema: tenant_id, subscription_tier, start_date, mrr, user_count, status
   - Refresh: Daily
   - Format: JSON

3. **feature_flags.parquet** (60 rows)
   - Schema: tenant_id, feature_name, enabled, enabled_date
   - Refresh: Real-time
   - Format: Parquet

**Bronze Outputs:**
- `bronze_user_events.parquet`
- `bronze_subscription_data.parquet`
- `bronze_feature_flags.parquet`

**Total Nodes:** 6 (3 connect + 3 publish)

---

## 📊 Summary Statistics

| Project | Data Sources | Total Rows | Formats | Bronze Nodes |
|---------|-------------|-----------|---------|--------------|
| P01 Manufacturing | 3 | 350 | CSV, JSON, Parquet | 6 |
| P02 Financial | 3 | 700 | CSV, JSON, Parquet | 6 |
| P03 IoT Sensors | 3 | 370 | CSV, JSON, Parquet | 6 |
| P04 Retail | 3 | 470 | CSV, JSON, Parquet | 6 |
| P05 Healthcare | 3 | 430 | CSV, JSON, Parquet | 6 |
| P06 Energy | 3 | 770 | CSV, JSON, Parquet | 6 |
| P07 Logistics | 3 | 718 | CSV, JSON, Parquet | 6 |
| P08 Marketing | 3 | 1500 | CSV, JSON, Parquet | 6 |
| P09 Education | 3 | 800 | CSV, JSON, Parquet | 6 |
| P10 SaaS | 3 | 880 | CSV, JSON, Parquet | 6 |
| **TOTAL** | **30** | **6,988** | **All 3 formats** | **60** |

---

## ✅ Acceptance Criteria Met

- [x] Each project has ≥3 distinct source systems
- [x] All source formats covered (CSV, JSON, Parquet)
- [x] Sample data generated and validated
- [x] Bronze layer preserves raw data with minimal transformation
- [x] Total of 60 Bronze layer nodes across 10 projects

---

## 🚀 Next Steps

**Phase 2: Silver Layer** - Define transformation, join, validation, and enrichment logic

**Deliverable:** `SILVER_LAYER_SPECS.md`

---

*Generated by ODIBI_CORE Medallion Project System*  
*Phase: 1 - Bronze Layer | Status: COMPLETE*
