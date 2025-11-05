"""
Domain Knowledge Base for Advanced Showcase Generation
========================================================
Provides rich, domain-specific context for realistic data engineering scenarios.
"""

DOMAIN_KNOWLEDGE = {
    "Finance": {
        "entities": ["accounts", "trades", "transactions", "portfolios", "positions", "counterparties", "instruments"],
        "kpis": ["VaR", "PnL", "trade_volume", "settlement_lag", "counterparty_risk", "margin_utilization", "execution_quality"],
        "typical_sources": ["FIX protocol streams", "clearing house CSVs", "reference data APIs", "risk system DB tables"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["dedupe_by_trade_id", "standardize_timestamps_to_utc", "calculate_pnl", "aggregate_by_book", "scd2_instrument_ref", "validate_notional_range"],
        "windows": {"intraday_risk": "15min", "eod_positions": "1d", "weekly_var": "7d"},
        "constraints": {"pii": False, "sox_compliant": True, "latency_sla": "5min"},
        "phrases": {
            "problem": ["Trading desk reports settlement lags", "Risk team needs real-time VaR", "Regulatory reporting requires complete audit trail"],
            "design": ["fan-in merge ensures all counterparty feeds synchronized", "SCD2 on instruments preserves historical pricing", "parallel ingestion of FIX and clearing house"],
            "trade_off": ["Window = 15min balances latency vs late-arriving trades", "Caching PnL aggregates reduces query load 40%", "Validation catches notional outliers before downstream"]
        }
    },
    
    "Manufacturing": {
        "entities": ["equipment", "production_runs", "quality_inspections", "maintenance_logs", "inventory", "work_orders", "defects"],
        "kpis": ["OEE", "MTBF", "MTTR", "yield_rate", "defect_ppm", "downtime_hours", "inventory_turns"],
        "typical_sources": ["PLC sensor streams", "MES databases", "ERP exports", "QA system APIs"],
        "formats": ["CSV", "PARQUET", "JSON", "AVRO"],
        "transforms_common": ["window_agg_5min", "outlier_detection_zscore", "equipment_scd2", "join_work_order_to_runs", "calculate_oee", "categorize_defects"],
        "windows": {"sensor_aggregation": "5min", "shift_rollup": "8h", "weekly_yield": "7d"},
        "constraints": {"real_time_plc": True, "high_cardinality_equipment": True, "late_arrivals_common": True},
        "phrases": {
            "problem": ["OEE trending down on Line 3", "Quality defects spiking in welding", "Predictive maintenance needs failure patterns"],
            "design": ["5-min sensor windows aggregate PLC streams before join", "Equipment SCD2 tracks configuration changes affecting yield", "Outlier detection flags anomalies for review"],
            "trade_off": ["Late data tolerance = 2min trade-off coverage vs latency", "Caching hourly OEE reduces recalculation overhead", "Partitioning by line_id enables parallel processing"]
        }
    },
    
    "IoT": {
        "entities": ["devices", "sensors", "events", "telemetry", "firmware_versions", "device_metadata", "alerts"],
        "kpis": ["device_uptime", "message_latency", "firmware_adoption", "anomaly_rate", "battery_life", "connectivity_ratio"],
        "typical_sources": ["MQTT streams", "device shadow tables", "firmware catalog APIs", "alert webhooks"],
        "formats": ["JSON", "AVRO", "PARQUET"],
        "transforms_common": ["dedupe_by_device_ts", "validate_schema_versions", "geohash_location", "window_agg_1min", "flag_stale_devices", "join_device_metadata"],
        "windows": {"realtime_alerts": "1min", "device_health": "1h", "weekly_summary": "7d"},
        "constraints": {"high_volume_streams": True, "late_arrivals": True, "schema_drift": True},
        "phrases": {
            "problem": ["Fleet uptime dropped to 92%", "Firmware v2.1 rollout shows instability", "Anomaly detection needs low-latency processing"],
            "design": ["1-min tumbling windows aggregate telemetry streams", "Schema validation handles drift from firmware versions", "Geohashing enables spatial queries"],
            "trade_off": ["Deduplication by device+timestamp prevents double-counting", "Caching device metadata reduces join overhead", "Watermark = 2min handles most late arrivals"]
        }
    },
    
    "Logistics": {
        "entities": ["shipments", "routes", "carriers", "facilities", "orders", "tracking_events", "exceptions"],
        "kpis": ["on_time_percentage", "eta_accuracy", "cost_per_mile", "dwell_time", "damage_rate", "carrier_performance"],
        "typical_sources": ["EDI 214 feeds", "TMS database", "GPS tracking APIs", "WMS exports"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["standardize_edi_timestamps", "join_tracking_to_orders", "calculate_dwell", "classify_exceptions", "scd2_facility_dim", "geo_distance"],
        "windows": {"realtime_tracking": "15min", "daily_performance": "1d", "carrier_scorecard": "30d"},
        "constraints": {"edi_schema_drift": True, "timezone_complexity": True, "late_updates": True},
        "phrases": {
            "problem": ["Carrier OTP degraded 8% this quarter", "ETA prediction accuracy at 67%", "Exception handling needs automated triage"],
            "design": ["Fan-in conformance merges EDI vendors with standardized timestamps", "SCD2 on facilities preserves relocations affecting routes", "Dwell time calculated from timestamp deltas"],
            "trade_off": ["15-min snaps balance real-time needs vs API costs", "Window = 7d for dwell captures seasonal patterns", "Partitioning by carrier enables parallel scorecards"]
        }
    },
    
    "Retail": {
        "entities": ["transactions", "products", "customers", "stores", "inventory", "promotions", "returns"],
        "kpis": ["basket_size", "conversion_rate", "inventory_turnover", "promo_lift", "customer_ltv", "return_rate"],
        "typical_sources": ["POS systems", "e-commerce clickstreams", "inventory DBs", "loyalty program APIs"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["sessionize_clicks", "basket_analysis", "product_scd2", "promo_attribution", "cohort_segmentation", "rfm_scoring"],
        "windows": {"realtime_inventory": "5min", "daily_sales": "1d", "monthly_cohorts": "30d"},
        "constraints": {"high_seasonality": True, "multi_channel": True, "customer_pii": True},
        "phrases": {
            "problem": ["Promo attribution unclear across channels", "Inventory sync lagging 20 mins", "Customer segments need real-time refresh"],
            "design": ["Sessionization groups clicks into shopping journeys", "SCD2 on products preserves pricing/category history", "RFM scoring identifies VIP customers"],
            "trade_off": ["5-min inventory snaps vs 1-min trade-off accuracy vs cost", "30d cohort window balances retention signal vs recency", "Caching product dims reduces join overhead 35%"]
        }
    },
    
    "Healthcare": {
        "entities": ["admissions", "claims", "patients", "providers", "medications", "lab_results", "diagnoses"],
        "kpis": ["length_of_stay", "readmission_rate", "claim_denial_rate", "cost_per_encounter", "time_to_treatment"],
        "typical_sources": ["HL7 feeds", "claims processing DBs", "EHR exports", "pharmacy systems"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["parse_hl7", "dedupe_claims", "provider_scd2", "calculate_los", "diagnosis_grouper", "validate_hipaa"],
        "windows": {"admit_tracking": "1h", "daily_census": "1d", "monthly_outcomes": "30d"},
        "constraints": {"hipaa_compliant": True, "pii_heavy": True, "schema_complex": True},
        "phrases": {
            "problem": ["Readmission rate 18% vs 12% benchmark", "Claim denial up 3% this month", "LOS trending higher for cardiac cases"],
            "design": ["HL7 parser normalizes admission events", "SCD2 on providers tracks facility/specialty changes", "Diagnosis grouper rolls up to DRG codes"],
            "trade_off": ["HIPAA validation blocks non-compliant rows before gold layer", "30d window for outcomes balances clinical significance vs timeliness", "Partitioning by facility enables parallel census"]
        }
    },
    
    "Energy": {
        "entities": ["meters", "readings", "outages", "transformers", "circuits", "substations", "demand_forecasts"],
        "kpis": ["load_factor", "peak_demand", "outage_minutes", "voltage_variance", "forecast_accuracy", "transmission_loss"],
        "typical_sources": ["AMI meter streams", "SCADA systems", "weather APIs", "GIS databases"],
        "formats": ["CSV", "JSON", "PARQUET", "AVRO"],
        "transforms_common": ["aggregate_15min", "outlier_voltage", "join_weather", "forecast_demand", "calculate_load_factor", "detect_outages"],
        "windows": {"realtime_monitoring": "1min", "hourly_demand": "1h", "daily_forecasts": "1d"},
        "constraints": {"high_frequency": True, "weather_dependent": True, "geospatial": True},
        "phrases": {
            "problem": ["Peak demand forecast off by 12%", "Voltage variance spiking in grid sector 4", "Outage detection lagging 8 mins"],
            "design": ["15-min AMI aggregation aligns with ISO billing intervals", "Weather join enriches demand forecasts", "Outlier detection flags voltage anomalies"],
            "trade_off": ["1-min outage detection vs 5-min trade-off latency vs false positives", "Load factor = peak/avg over 24h window", "GIS partitioning enables spatial queries"]
        }
    },
    
    "Media": {
        "entities": ["impressions", "clicks", "users", "campaigns", "creatives", "publishers", "conversions"],
        "kpis": ["CTR", "viewability", "completion_rate", "cpm", "ROAS", "attribution_lift"],
        "typical_sources": ["ad server logs", "bid stream data", "attribution APIs", "CRM databases"],
        "formats": ["JSON", "PARQUET", "AVRO"],
        "transforms_common": ["dedupe_impressions", "sessionize_clicks", "multi_touch_attribution", "viewability_scoring", "fraud_detection", "cohort_analysis"],
        "windows": {"realtime_bidding": "100ms", "hourly_performance": "1h", "campaign_lifetime": "30d"},
        "constraints": {"high_qps": True, "fraud_risk": True, "multi_touch_complex": True},
        "phrases": {
            "problem": ["CTR down 15% week-over-week", "Fraud rate spiking on mobile inventory", "Attribution model needs multi-touch support"],
            "design": ["Sessionization groups user journey across publishers", "Multi-touch attribution distributes credit by position", "Fraud detection flags bot-like patterns"],
            "trade_off": ["100ms window for RTB vs hourly for analytics", "30d attribution window vs 7d trade-off completeness vs recency", "Dedup by impression_id prevents double-counting"]
        }
    },
    
    "Education": {
        "entities": ["enrollments", "courses", "students", "instructors", "assessments", "attendance", "graduations"],
        "kpis": ["enrollment_rate", "completion_rate", "graduation_rate", "attendance_avg", "gpa_distribution", "instructor_rating"],
        "typical_sources": ["SIS databases", "LMS exports", "assessment systems", "attendance trackers"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["calculate_gpa", "aggregate_attendance", "cohort_tracking", "course_scd2", "predict_risk", "join_demographics"],
        "windows": {"weekly_attendance": "7d", "semester_performance": "16w", "cohort_graduation": "4y"},
        "constraints": {"ferpa_compliant": True, "student_pii": True, "long_windows": True},
        "phrases": {
            "problem": ["Completion rate 68% vs 75% target", "At-risk students identified too late", "Graduation tracking needs cohort-based analysis"],
            "design": ["Cohort tracking follows students from enrollment to graduation", "SCD2 on courses preserves curriculum changes", "Attendance aggregation flags at-risk students"],
            "trade_off": ["Weekly attendance snaps balance timeliness vs stability", "GPA calculation uses cumulative vs semester-only", "4-year cohort window tracks traditional degree path"]
        }
    },
    
    "PublicData": {
        "entities": ["census_tracts", "permits", "violations", "311_requests", "weather_stations", "traffic_sensors", "budgets"],
        "kpis": ["response_time_311", "permit_approval_days", "violation_resolution_rate", "budget_variance", "service_coverage"],
        "typical_sources": ["open data portals", "city APIs", "weather services", "GIS databases"],
        "formats": ["CSV", "JSON", "PARQUET"],
        "transforms_common": ["geohash_location", "join_census_demographics", "calculate_response_time", "aggregate_by_district", "detect_anomalies", "budget_variance"],
        "windows": {"daily_311": "1d", "monthly_permits": "30d", "annual_budget": "365d"},
        "constraints": {"public_facing": True, "geospatial_heavy": True, "data_quality_variable": True},
        "phrases": {
            "problem": ["311 response time up 18% in District 5", "Permit backlog at 45 days vs 30 day target", "Budget variance analysis needs trend detection"],
            "design": ["Geohashing enables spatial joins with census tracts", "Response time calculated from request→resolution timestamps", "District aggregation rolls up metrics by boundary"],
            "trade_off": ["Daily 311 snaps vs real-time trade-off reporting lag vs stability", "Census join enriches with demographics for equity analysis", "Anomaly detection flags unusual patterns"]
        }
    }
}


def get_domain_context(domain: str) -> dict:
    """Get rich domain context for scenario generation."""
    return DOMAIN_KNOWLEDGE.get(domain, DOMAIN_KNOWLEDGE["PublicData"])


def get_all_domains() -> list:
    """Get list of all available domains."""
    return list(DOMAIN_KNOWLEDGE.keys())


def sample_scenario_elements(domain: str, seed: int = None) -> dict:
    """Sample realistic scenario elements for a domain."""
    import random
    if seed is not None:
        random.seed(seed)
    
    ctx = get_domain_context(domain)
    
    return {
        "domain": domain,
        "entities": random.sample(ctx["entities"], min(3, len(ctx["entities"]))),
        "kpis": random.sample(ctx["kpis"], min(2, len(ctx["kpis"]))),
        "sources": random.sample(ctx["typical_sources"], min(2, len(ctx["typical_sources"]))),
        "formats": random.sample(ctx["formats"], min(2, len(ctx["formats"]))),
        "transforms": random.sample(ctx["transforms_common"], min(4, len(ctx["transforms_common"]))),
        "window": random.choice(list(ctx["windows"].values())),
        "problem": random.choice(ctx["phrases"]["problem"]),
        "design_rationale": random.choice(ctx["phrases"]["design"]),
        "trade_off": random.choice(ctx["phrases"]["trade_off"])
    }
