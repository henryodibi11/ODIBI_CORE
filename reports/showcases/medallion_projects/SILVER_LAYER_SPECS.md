# Phase 2: Silver Layer Specifications
## ODIBI_CORE Medallion Architecture Projects

**Phase:** 2 - Silver Layer (Transformation & Quality)  
**Date:** 2025-11-02  
**Status:** ✅ COMPLETE

---

## 🎯 Objective

Define transformation layer with multi-source joins, derived fields, validations, and caching. Create ODIBI_CORE configs for Silver layer processing.

---

## 🥈 Silver Layer Architecture

**Purpose:** Clean, conform, and enrich Bronze data  
**Pattern:** Bronze → Transform → Join → Validate → Cache → Silver storage  
**Node Types:** `connect` (load Bronze), `transform`, `validate`, `cache`, `publish`  
**Requirements:** ≥2 joins, ≥4 derived fields, ≥1 validation per project

---

## 📁 Project Silver Transformations

### P01: Manufacturing Yield & Downtime KPI System

**Joins:**
1. **Machine Sensors ⋈ Production Logs** (on machine_id)
2. **Combined ⋈ Maintenance Records** (on machine_id)

**Derived Fields (6):**
- `oee_score` = (production_count / target_count) * quality_rate * availability_rate
- `yield_rate` = (units_produced - units_defective) / units_produced
- `downtime_ratio` = downtime_hours / total_hours
- `avg_temperature` = rolling_mean(temperature, window=10)
- `production_efficiency` = units_produced / production_time_hours
- `maintenance_cost_per_unit` = maintenance_cost / units_produced

**Validations:**
- Schema check (required columns exist)
- Range validation (temperature 0-150, pressure 0-200)
- Business rule: yield_rate must be between 0 and 1

**Cache:** After join, before validation

**Silver Outputs:**
- `silver_manufacturing_unified.parquet`

**Total Nodes:** 12 (3 connect + 3 transform + 2 join + 1 validate + 1 cache + 2 publish)

---

### P02: Financial Transactions Reconciliation

**Joins:**
1. **Transactions ⋈ Accounts** (on account_id)
2. **Combined ⋈ Risk Ratings** (on account_id)

**Derived Fields (5):**
- `reconciled_balance` = previous_balance + transaction_amount
- `credit_utilization` = balance / credit_limit
- `risk_adjusted_exposure` = balance * (fraud_score / 100)
- `transaction_velocity` = count(transactions) / time_window_days
- `fraud_flag` = fraud_score > 75 AND transaction_velocity > 10

**Validations:**
- Schema check
- Range validation (fraud_score 0-100, credit_score 300-850)
- Business rule: credit_utilization must be ≤ 1.0
- Cross-source consistency: all account_ids in transactions exist in accounts

**Cache:** After joins, before aggregations

**Silver Outputs:**
- `silver_financial_reconciled.parquet`

**Total Nodes:** 13

---

### P03: IoT Sensor Reliability & Maintenance Prediction

**Joins:**
1. **Sensor Telemetry ⋈ Maintenance Logs** (on sensor_id)
2. **Combined ⋈ Weather Data** (on date extracted from timestamp)

**Derived Fields (6):**
- `uptime_ratio` = count(status='online') / total_readings
- `battery_drain_rate` = diff(battery_level) / diff(timestamp)
- `failure_prediction_score` = f(battery_level, signal_strength, uptime_ratio)
- `weather_impact_score` = correlation(sensor_failures, precipitation)
- `mtbf_days` = days_between_maintenance_events
- `maintenance_cost_per_day` = total_maintenance_cost / days_operational

**Validations:**
- Schema check
- Range validation (battery_level 0-100, signal_strength -90 to -30)
- Business rule: uptime_ratio must be > 0.90 for production sensors

**Cache:** After weather join

**Silver Outputs:**
- `silver_iot_reliability.parquet`

**Total Nodes:** 14

---

### P04: Retail Demand Forecast & Promotion Effectiveness

**Joins:**
1. **Sales Transactions ⋈ Inventory Levels** (on product_id)
2. **Combined ⋈ Promotional Campaigns** (on product_id + date range)

**Derived Fields (7):**
- `revenue` = quantity * price * (1 - discount_applied)
- `promotion_lift` = (sales_during_promo - baseline_sales) / baseline_sales
- `inventory_turnover` = sales_quantity / current_stock
- `stock_out_risk` = current_stock < reorder_point
- `days_of_supply` = current_stock / avg_daily_sales
- `marketing_roi` = (revenue_during_campaign - marketing_spend) / marketing_spend
- `demand_forecast_7d` = trend + seasonality component

**Validations:**
- Schema check
- Range validation (discount_applied 0-1, quantity > 0)
- Business rule: revenue must be positive

**Cache:** After inventory join

**Silver Outputs:**
- `silver_retail_demand.parquet`

**Total Nodes:** 15

---

### P05: Healthcare Appointment Analytics

**Joins:**
1. **Appointment Records ⋈ Patient Demographics** (on patient_id)
2. **Combined ⋈ Clinic Capacity** (on doctor_id + date)

**Derived Fields (6):**
- `wait_time_minutes` = diff(scheduled_time, actual_start_time)
- `utilization_rate` = booked_slots / available_slots
- `no_show_rate` = count(status='no-show') / total_appointments
- `avg_wait_by_appointment_type` = group_mean(wait_time, appointment_type)
- `patient_complexity_score` = chronic_conditions * risk_score
- `on_time_performance` = count(wait_time <= 15) / total_appointments

**Validations:**
- Schema check
- Range validation (wait_time >= -30, utilization_rate 0-1.5)
- Business rule: appointment_duration must be > 0

**Cache:** After patient demographics join

**Silver Outputs:**
- `silver_healthcare_appointments.parquet`

**Total Nodes:** 13

---

### P06: Energy Efficiency & Weather Normalization

**Joins:**
1. **Meter Readings ⋈ Building Metadata** (on meter_id)
2. **Combined ⋈ Weather Data** (on date extracted from timestamp)

**Derived Fields (5):**
- `kwh_per_sqft` = kwh_consumed / square_footage
- `weather_normalized_consumption` = kwh_consumed / (1 + heating_degree_days + cooling_degree_days)
- `efficiency_score` = baseline_consumption / actual_consumption
- `variance_from_baseline` = (actual - baseline) / baseline
- `savings_potential` = (current_consumption - efficient_consumption) * energy_rate

**Validations:**
- Schema check
- Range validation (kwh_consumed >= 0, power_factor 0-1)
- Business rule: efficiency_score must be > 0

**Cache:** After weather join

**Silver Outputs:**
- `silver_energy_normalized.parquet`

**Total Nodes:** 12

---

### P07: Logistics Fleet Tracking & Delivery SLA

**Joins:**
1. **GPS Telemetry ⋈ Delivery Records** (on vehicle_id + time range)
2. **Combined ⋈ Traffic Data** (on route_id derived from GPS)

**Derived Fields (6):**
- `delivery_delay_minutes` = diff(scheduled_time, actual_delivery_time)
- `on_time_delivery` = delivery_delay_minutes <= 15
- `fuel_efficiency_kpl` = distance_km / fuel_consumed
- `avg_speed_kph` = distance_km / duration_hours
- `traffic_impact_score` = correlation(delivery_delay, congestion_level)
- `sla_compliance_rate` = count(on_time_delivery) / total_deliveries

**Validations:**
- Schema check
- Range validation (speed_kph 0-120, fuel_level 0-100)
- Business rule: distance_km must be > 0

**Cache:** After delivery join

**Silver Outputs:**
- `silver_logistics_sla.parquet`

**Total Nodes:** 14

---

### P08: Marketing Attribution & Conversion Funnel

**Joins:**
1. **Ad Impressions ⋈ Clicks/Conversions** (on impression_id)
2. **Combined ⋈ Customer Journey** (on user_id)

**Derived Fields (7):**
- `ctr` = clicks / impressions
- `conversion_rate` = conversions / clicks
- `cac` = total_ad_cost / conversions
- `roas` = conversion_value / ad_cost
- `time_to_conversion` = diff(first_touch, conversion_timestamp)
- `attribution_weight` = position_based_weight(touchpoint_sequence)
- `journey_length` = count(touchpoints)

**Validations:**
- Schema check
- Range validation (ctr 0-1, conversion_rate 0-1)
- Business rule: roas should be > 1.0 for profitable campaigns

**Cache:** After customer journey join

**Silver Outputs:**
- `silver_marketing_attribution.parquet`

**Total Nodes:** 16

---

### P09: Education Outcome Correlation

**Joins:**
1. **Student Grades ⋈ Attendance Records** (on student_id + semester)
2. **Combined ⋈ Student Demographics** (on student_id)

**Derived Fields (5):**
- `gpa` = sum(grade_points * credits) / sum(credits)
- `attendance_impact` = correlation(attendance_rate, grade_points)
- `at_risk_flag` = gpa < 2.0 OR attendance_rate < 0.75
- `credits_earned` = sum(credits WHERE grade != 'F')
- `progression_rate` = credits_earned / expected_credits

**Validations:**
- Schema check
- Range validation (grade_points 0-4, attendance_rate 0-1)
- Business rule: credits must be positive

**Cache:** After attendance join

**Silver Outputs:**
- `silver_education_outcomes.parquet`

**Total Nodes:** 12

---

### P10: SaaS Usage Reporting & Tenant KPIs

**Joins:**
1. **User Events ⋈ Subscription Data** (on tenant_id)
2. **Combined ⋈ Feature Flags** (on tenant_id + feature_name)

**Derived Fields (6):**
- `dau` = count(distinct user_id WHERE event_date = today)
- `mau` = count(distinct user_id WHERE event_date >= today - 30)
- `dau_mau_ratio` = dau / mau
- `feature_adoption_rate` = count(users_using_feature) / total_users
- `churn_risk_score` = f(dau_mau_ratio, last_login_days, usage_trend)
- `avg_session_duration` = mean(session_duration_sec)

**Validations:**
- Schema check
- Range validation (session_duration > 0, mau >= dau)
- Business rule: subscription_tier must match feature access

**Cache:** After feature flags join

**Silver Outputs:**
- `silver_saas_usage.parquet`

**Total Nodes:** 13

---

## 📊 Summary Statistics

| Project | Joins | Derived Fields | Validations | Cache Nodes | Silver Nodes |
|---------|-------|----------------|-------------|-------------|--------------|
| P01 Manufacturing | 2 | 6 | 3 | 1 | 12 |
| P02 Financial | 2 | 5 | 4 | 1 | 13 |
| P03 IoT Sensors | 2 | 6 | 3 | 1 | 14 |
| P04 Retail | 2 | 7 | 3 | 1 | 15 |
| P05 Healthcare | 2 | 6 | 3 | 1 | 13 |
| P06 Energy | 2 | 5 | 3 | 1 | 12 |
| P07 Logistics | 2 | 6 | 3 | 1 | 14 |
| P08 Marketing | 2 | 7 | 3 | 1 | 16 |
| P09 Education | 2 | 5 | 3 | 1 | 12 |
| P10 SaaS | 2 | 6 | 3 | 1 | 13 |
| **TOTAL** | **20** | **59** | **31** | **10** | **134** |

---

## ✅ Acceptance Criteria Met

- [x] Each project has ≥2 complex joins
- [x] Each project has ≥4 derived/calculated fields (avg 5.9 per project)
- [x] Each project has ≥1 validation (avg 3.1 per project)
- [x] Each project has ≥1 cache boundary
- [x] Total of 134 Silver layer nodes across 10 projects
- [x] All validations include schema, range, and business rule checks

---

## 🚀 Next Steps

**Phase 3: Gold Layer** - Define analytic aggregations, KPIs, and dimensional modeling

**Deliverable:** `GOLD_LAYER_SPECS.md`

---

*Generated by ODIBI_CORE Medallion Project System*  
*Phase: 2 - Silver Layer | Status: COMPLETE*
