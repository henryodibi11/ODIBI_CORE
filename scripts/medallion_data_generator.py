"""
ODIBI_CORE Medallion Projects - Sample Data Generator
======================================================
Generates deterministic sample datasets for all 10 medallion projects.

Each project gets 3+ data sources in multiple formats (CSV, JSON, Parquet).
Data is small but realistic with proper schemas and relationships.

Author: Henry Odibi
Project: ODIBI_CORE (ODB-1)
"""

import pandas as pd
import json
import random
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Seed for reproducibility
random.seed(42)

class MedallionDataGenerator:
    """Generate sample data for all 10 medallion projects."""
    
    def __init__(self, base_path: str = "D:/projects/odibi_core"):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "resources/data/medallion_projects"
        self.data_path.mkdir(parents=True, exist_ok=True)
    
    def generate_all(self):
        """Generate data for all 10 projects."""
        print("🔧 Generating sample data for 10 medallion projects...\n")
        
        self.generate_p01_manufacturing()
        self.generate_p02_financial()
        self.generate_p03_iot_sensors()
        self.generate_p04_retail()
        self.generate_p05_healthcare()
        self.generate_p06_energy()
        self.generate_p07_logistics()
        self.generate_p08_marketing()
        self.generate_p09_education()
        self.generate_p10_saas()
        
        print("\n✅ All sample data generated successfully!")
    
    def generate_p01_manufacturing(self):
        """P01: Manufacturing Yield & Downtime KPI System"""
        print("📦 P01: Manufacturing...")
        project_dir = self.data_path / "bronze/p01_manufacturing"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Machine sensor data (CSV)
        sensors = []
        for i in range(1, 201):
            sensors.append({
                'timestamp': (datetime(2025, 1, 1) + timedelta(hours=i)).isoformat(),
                'machine_id': f"M{random.randint(1, 5):03d}",
                'temperature': round(random.uniform(60, 90), 2),
                'pressure': round(random.uniform(100, 150), 2),
                'vibration': round(random.uniform(0.1, 2.5), 2),
                'production_count': random.randint(50, 100),
                'status': random.choice(['running', 'running', 'running', 'idle', 'maintenance'])
            })
        pd.DataFrame(sensors).to_csv(project_dir / "machine_sensors.csv", index=False)
        
        # Source 2: Production logs (JSON)
        production = []
        for i in range(1, 101):
            production.append({
                'batch_id': f"B{i:05d}",
                'machine_id': f"M{random.randint(1, 5):03d}",
                'product_type': random.choice(['TypeA', 'TypeB', 'TypeC']),
                'start_time': (datetime(2025, 1, 1) + timedelta(hours=i*2)).isoformat(),
                'end_time': (datetime(2025, 1, 1) + timedelta(hours=i*2 + 1, minutes=random.randint(30, 90))).isoformat(),
                'units_produced': random.randint(80, 120),
                'units_defective': random.randint(0, 10),
                'shift': random.choice(['A', 'B', 'C'])
            })
        with open(project_dir / "production_logs.json", 'w') as f:
            json.dump(production, f, indent=2)
        
        # Source 3: Maintenance records (Parquet)
        maintenance = pd.DataFrame({
            'maintenance_id': [f"MNT{i:04d}" for i in range(1, 51)],
            'machine_id': [f"M{random.randint(1, 5):03d}" for _ in range(50)],
            'maintenance_date': [(datetime(2025, 1, 1) + timedelta(days=random.randint(1, 30))).date() for _ in range(50)],
            'maintenance_type': [random.choice(['preventive', 'corrective', 'emergency']) for _ in range(50)],
            'downtime_hours': [round(random.uniform(0.5, 8), 2) for _ in range(50)],
            'cost': [round(random.uniform(500, 5000), 2) for _ in range(50)]
        })
        maintenance.to_parquet(project_dir / "maintenance_records.parquet", index=False)
        print("  ✅ 3 sources: machine_sensors.csv, production_logs.json, maintenance_records.parquet")
    
    def generate_p02_financial(self):
        """P02: Financial Transactions Reconciliation & Risk Aggregation"""
        print("💰 P02: Financial...")
        project_dir = self.data_path / "bronze/p02_financial"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Transaction logs (CSV)
        transactions = pd.DataFrame({
            'transaction_id': [f"TXN{i:08d}" for i in range(1, 501)],
            'account_id': [f"ACC{random.randint(1, 100):06d}" for _ in range(500)],
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(500)],
            'amount': [round(random.uniform(-5000, 10000), 2) for _ in range(500)],
            'currency': [random.choice(['USD', 'EUR', 'GBP']) for _ in range(500)],
            'transaction_type': [random.choice(['debit', 'credit', 'transfer']) for _ in range(500)],
            'merchant_id': [f"MER{random.randint(1, 50):04d}" for _ in range(500)]
        })
        transactions.to_csv(project_dir / "transactions.csv", index=False)
        
        # Source 2: Account balances (JSON)
        accounts = []
        for i in range(1, 101):
            accounts.append({
                'account_id': f"ACC{i:06d}",
                'customer_name': f"Customer {i}",
                'account_type': random.choice(['checking', 'savings', 'credit']),
                'balance': round(random.uniform(100, 50000), 2),
                'credit_limit': round(random.uniform(5000, 20000), 2) if random.random() > 0.5 else None,
                'risk_tier': random.choice(['low', 'medium', 'high'])
            })
        with open(project_dir / "accounts.json", 'w') as f:
            json.dump(accounts, f, indent=2)
        
        # Source 3: Risk ratings (Parquet)
        risk = pd.DataFrame({
            'account_id': [f"ACC{i:06d}" for i in range(1, 101)],
            'credit_score': [random.randint(550, 850) for _ in range(100)],
            'fraud_score': [round(random.uniform(0, 100), 2) for _ in range(100)],
            'days_delinquent': [random.randint(0, 90) for _ in range(100)],
            'risk_updated_date': [(datetime(2025, 1, 1) + timedelta(days=random.randint(1, 30))).date() for _ in range(100)]
        })
        risk.to_parquet(project_dir / "risk_ratings.parquet", index=False)
        print("  ✅ 3 sources: transactions.csv, accounts.json, risk_ratings.parquet")
    
    def generate_p03_iot_sensors(self):
        """P03: IoT Sensor Reliability & Maintenance Prediction"""
        print("📡 P03: IoT Sensors...")
        project_dir = self.data_path / "bronze/p03_iot_sensors"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Sensor telemetry (CSV)
        telemetry = pd.DataFrame({
            'timestamp': [(datetime(2025, 1, 1) + timedelta(minutes=i*30)).isoformat() for i in range(300)],
            'sensor_id': [f"SEN{random.randint(1, 20):04d}" for _ in range(300)],
            'temperature': [round(random.uniform(-10, 40), 2) for _ in range(300)],
            'humidity': [round(random.uniform(20, 90), 2) for _ in range(300)],
            'battery_level': [round(random.uniform(10, 100), 2) for _ in range(300)],
            'signal_strength': [random.randint(-90, -30) for _ in range(300)],
            'status': [random.choice(['online', 'online', 'online', 'offline', 'warning']) for _ in range(300)]
        })
        telemetry.to_csv(project_dir / "sensor_telemetry.csv", index=False)
        
        # Source 2: Maintenance logs (JSON)
        maintenance = []
        for i in range(1, 41):
            maintenance.append({
                'maintenance_id': f"MAINT{i:04d}",
                'sensor_id': f"SEN{random.randint(1, 20):04d}",
                'maintenance_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(1, 30))).isoformat(),
                'issue_type': random.choice(['battery_replacement', 'calibration', 'hardware_failure', 'connectivity']),
                'resolution_time_hours': round(random.uniform(1, 24), 2),
                'cost': round(random.uniform(50, 500), 2)
            })
        with open(project_dir / "maintenance_logs.json", 'w') as f:
            json.dump(maintenance, f, indent=2)
        
        # Source 3: Weather data (Parquet)
        weather = pd.DataFrame({
            'date': [(datetime(2025, 1, 1) + timedelta(days=i)).date() for i in range(30)],
            'location': ['Location_' + random.choice(['A', 'B', 'C']) for _ in range(30)],
            'avg_temperature': [round(random.uniform(-5, 35), 2) for _ in range(30)],
            'precipitation_mm': [round(random.uniform(0, 50), 2) for _ in range(30)],
            'wind_speed_kph': [round(random.uniform(0, 60), 2) for _ in range(30)]
        })
        weather.to_parquet(project_dir / "weather_data.parquet", index=False)
        print("  ✅ 3 sources: sensor_telemetry.csv, maintenance_logs.json, weather_data.parquet")
    
    def generate_p04_retail(self):
        """P04: Retail Demand Forecast & Promotion Effectiveness"""
        print("🛒 P04: Retail...")
        project_dir = self.data_path / "bronze/p04_retail"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Sales transactions (CSV)
        sales = pd.DataFrame({
            'transaction_id': [f"SALE{i:08d}" for i in range(1, 401)],
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(400)],
            'store_id': [f"STORE{random.randint(1, 10):03d}" for _ in range(400)],
            'product_id': [f"PROD{random.randint(1, 50):04d}" for _ in range(400)],
            'quantity': [random.randint(1, 10) for _ in range(400)],
            'price': [round(random.uniform(5, 200), 2) for _ in range(400)],
            'discount_applied': [random.choice([0, 0, 0, 0.1, 0.15, 0.2]) for _ in range(400)]
        })
        sales.to_csv(project_dir / "sales_transactions.csv", index=False)
        
        # Source 2: Inventory levels (JSON)
        inventory = []
        for i in range(1, 51):
            inventory.append({
                'product_id': f"PROD{i:04d}",
                'product_name': f"Product {i}",
                'category': random.choice(['Electronics', 'Clothing', 'Food', 'Home']),
                'current_stock': random.randint(0, 500),
                'reorder_point': random.randint(50, 100),
                'supplier_id': f"SUP{random.randint(1, 10):03d}"
            })
        with open(project_dir / "inventory_levels.json", 'w') as f:
            json.dump(inventory, f, indent=2)
        
        # Source 3: Promotional campaigns (Parquet)
        promotions = pd.DataFrame({
            'campaign_id': [f"CAMP{i:04d}" for i in range(1, 21)],
            'start_date': [(datetime(2025, 1, 1) + timedelta(days=i*5)).date() for i in range(20)],
            'end_date': [(datetime(2025, 1, 1) + timedelta(days=i*5 + 7)).date() for i in range(20)],
            'product_id': [f"PROD{random.randint(1, 50):04d}" for _ in range(20)],
            'discount_rate': [round(random.uniform(0.1, 0.3), 2) for _ in range(20)],
            'marketing_spend': [round(random.uniform(1000, 10000), 2) for _ in range(20)]
        })
        promotions.to_parquet(project_dir / "promotional_campaigns.parquet", index=False)
        print("  ✅ 3 sources: sales_transactions.csv, inventory_levels.json, promotional_campaigns.parquet")
    
    def generate_p05_healthcare(self):
        """P05: Healthcare Appointment Analytics & Wait-Time Reduction"""
        print("🏥 P05: Healthcare...")
        project_dir = self.data_path / "bronze/p05_healthcare"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Appointment records (CSV)
        appointments = pd.DataFrame({
            'appointment_id': [f"APT{i:08d}" for i in range(1, 301)],
            'patient_id': [f"PAT{random.randint(1, 100):06d}" for _ in range(300)],
            'doctor_id': [f"DOC{random.randint(1, 15):03d}" for _ in range(300)],
            'scheduled_time': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(300)],
            'actual_start_time': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720), minutes=random.randint(-15, 60))).isoformat() for _ in range(300)],
            'appointment_type': [random.choice(['checkup', 'consultation', 'follow-up', 'emergency']) for _ in range(300)],
            'status': [random.choice(['completed', 'completed', 'no-show', 'cancelled']) for _ in range(300)]
        })
        appointments.to_csv(project_dir / "appointment_records.csv", index=False)
        
        # Source 2: Patient demographics (JSON)
        patients = []
        for i in range(1, 101):
            patients.append({
                'patient_id': f"PAT{i:06d}",
                'age': random.randint(1, 90),
                'gender': random.choice(['M', 'F']),
                'insurance_type': random.choice(['private', 'public', 'none']),
                'chronic_conditions': random.randint(0, 3),
                'risk_score': round(random.uniform(0, 100), 2)
            })
        with open(project_dir / "patient_demographics.json", 'w') as f:
            json.dump(patients, f, indent=2)
        
        # Source 3: Clinic capacity (Parquet)
        capacity = pd.DataFrame({
            'date': [(datetime(2025, 1, 1) + timedelta(days=i)).date() for i in range(30)],
            'doctor_id': [f"DOC{random.randint(1, 15):03d}" for _ in range(30)],
            'available_slots': [random.randint(8, 16) for _ in range(30)],
            'booked_slots': [random.randint(5, 16) for _ in range(30)],
            'avg_appointment_duration_min': [random.randint(15, 45) for _ in range(30)]
        })
        capacity.to_parquet(project_dir / "clinic_capacity.parquet", index=False)
        print("  ✅ 3 sources: appointment_records.csv, patient_demographics.json, clinic_capacity.parquet")
    
    def generate_p06_energy(self):
        """P06: Energy Efficiency & Weather Normalization"""
        print("⚡ P06: Energy...")
        project_dir = self.data_path / "bronze/p06_energy"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Meter readings (CSV)
        readings = pd.DataFrame({
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=i)).isoformat() for i in range(720)],
            'meter_id': [f"MTR{random.randint(1, 20):04d}" for _ in range(720)],
            'kwh_consumed': [round(random.uniform(5, 50), 2) for _ in range(720)],
            'power_factor': [round(random.uniform(0.85, 1.0), 2) for _ in range(720)],
            'voltage': [round(random.uniform(220, 240), 2) for _ in range(720)]
        })
        readings.to_csv(project_dir / "meter_readings.csv", index=False)
        
        # Source 2: Weather data (JSON)
        weather = []
        for i in range(30):
            weather.append({
                'date': (datetime(2025, 1, 1) + timedelta(days=i)).date().isoformat(),
                'location': random.choice(['Zone_A', 'Zone_B', 'Zone_C']),
                'avg_temperature_c': round(random.uniform(-5, 35), 2),
                'heating_degree_days': round(random.uniform(0, 20), 2),
                'cooling_degree_days': round(random.uniform(0, 15), 2)
            })
        with open(project_dir / "weather_data.json", 'w') as f:
            json.dump(weather, f, indent=2)
        
        # Source 3: Building metadata (Parquet)
        buildings = pd.DataFrame({
            'meter_id': [f"MTR{i:04d}" for i in range(1, 21)],
            'building_type': [random.choice(['residential', 'commercial', 'industrial']) for _ in range(20)],
            'square_footage': [random.randint(1000, 50000) for _ in range(20)],
            'year_built': [random.randint(1970, 2020) for _ in range(20)],
            'hvac_system': [random.choice(['central', 'split', 'none']) for _ in range(20)]
        })
        buildings.to_parquet(project_dir / "building_metadata.parquet", index=False)
        print("  ✅ 3 sources: meter_readings.csv, weather_data.json, building_metadata.parquet")
    
    def generate_p07_logistics(self):
        """P07: Logistics Fleet Tracking & Delivery SLA Monitoring"""
        print("🚚 P07: Logistics...")
        project_dir = self.data_path / "bronze/p07_logistics"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: GPS telemetry (CSV)
        gps = pd.DataFrame({
            'timestamp': [(datetime(2025, 1, 1) + timedelta(minutes=i*15)).isoformat() for i in range(400)],
            'vehicle_id': [f"VEH{random.randint(1, 25):03d}" for _ in range(400)],
            'latitude': [round(random.uniform(40.0, 41.0), 6) for _ in range(400)],
            'longitude': [round(random.uniform(-74.5, -73.5), 6) for _ in range(400)],
            'speed_kph': [round(random.uniform(0, 80), 2) for _ in range(400)],
            'fuel_level_pct': [round(random.uniform(10, 100), 2) for _ in range(400)]
        })
        gps.to_csv(project_dir / "gps_telemetry.csv", index=False)
        
        # Source 2: Delivery records (JSON)
        deliveries = []
        for i in range(1, 151):
            deliveries.append({
                'delivery_id': f"DEL{i:08d}",
                'vehicle_id': f"VEH{random.randint(1, 25):03d}",
                'customer_id': f"CUST{random.randint(1, 100):05d}",
                'scheduled_time': (datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat(),
                'actual_delivery_time': (datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720), minutes=random.randint(-30, 90))).isoformat(),
                'delivery_status': random.choice(['on-time', 'on-time', 'delayed', 'failed']),
                'distance_km': round(random.uniform(5, 50), 2)
            })
        with open(project_dir / "delivery_records.json", 'w') as f:
            json.dump(deliveries, f, indent=2)
        
        # Source 3: Traffic data (Parquet)
        traffic = pd.DataFrame({
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=i)).isoformat() for i in range(168)],
            'route_id': [f"ROUTE{random.randint(1, 10):02d}" for _ in range(168)],
            'congestion_level': [random.choice(['low', 'medium', 'high']) for _ in range(168)],
            'avg_speed_kph': [round(random.uniform(20, 80), 2) for _ in range(168)],
            'incidents': [random.randint(0, 5) for _ in range(168)]
        })
        traffic.to_parquet(project_dir / "traffic_data.parquet", index=False)
        print("  ✅ 3 sources: gps_telemetry.csv, delivery_records.json, traffic_data.parquet")
    
    def generate_p08_marketing(self):
        """P08: Marketing Attribution & Conversion Funnel"""
        print("📢 P08: Marketing...")
        project_dir = self.data_path / "bronze/p08_marketing"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Ad impressions (CSV)
        impressions = pd.DataFrame({
            'impression_id': [f"IMP{i:010d}" for i in range(1, 1001)],
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(1000)],
            'campaign_id': [f"CAMP{random.randint(1, 20):04d}" for _ in range(1000)],
            'ad_id': [f"AD{random.randint(1, 50):05d}" for _ in range(1000)],
            'user_id': [f"USER{random.randint(1, 200):06d}" for _ in range(1000)],
            'platform': [random.choice(['google', 'facebook', 'instagram', 'twitter']) for _ in range(1000)],
            'cost': [round(random.uniform(0.1, 5), 2) for _ in range(1000)]
        })
        impressions.to_csv(project_dir / "ad_impressions.csv", index=False)
        
        # Source 2: Clicks and conversions (JSON)
        clicks = []
        for i in range(1, 201):
            clicks.append({
                'click_id': f"CLK{i:08d}",
                'impression_id': f"IMP{random.randint(1, 1000):010d}",
                'user_id': f"USER{random.randint(1, 200):06d}",
                'click_timestamp': (datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat(),
                'conversion': random.choice([False, False, False, True]),
                'conversion_value': round(random.uniform(10, 500), 2) if random.random() > 0.7 else None
            })
        with open(project_dir / "clicks_conversions.json", 'w') as f:
            json.dump(clicks, f, indent=2)
        
        # Source 3: Customer journey (Parquet)
        journey = pd.DataFrame({
            'user_id': [f"USER{random.randint(1, 200):06d}" for _ in range(300)],
            'session_id': [f"SES{i:08d}" for i in range(1, 301)],
            'touchpoint_sequence': [','.join([random.choice(['ad', 'email', 'social', 'organic']) for _ in range(random.randint(1, 5))]) for _ in range(300)],
            'first_touch': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(300)],
            'last_touch': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720), minutes=random.randint(10, 1440))).isoformat() for _ in range(300)],
            'converted': [random.choice([True, False]) for _ in range(300)]
        })
        journey.to_parquet(project_dir / "customer_journey.parquet", index=False)
        print("  ✅ 3 sources: ad_impressions.csv, clicks_conversions.json, customer_journey.parquet")
    
    def generate_p09_education(self):
        """P09: Education Outcome Correlation & Cohort Analysis"""
        print("🎓 P09: Education...")
        project_dir = self.data_path / "bronze/p09_education"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Student grades (CSV)
        grades = pd.DataFrame({
            'student_id': [f"STU{random.randint(1, 150):06d}" for _ in range(500)],
            'course_id': [f"COURSE{random.randint(1, 30):03d}" for _ in range(500)],
            'semester': [random.choice(['Fall2024', 'Spring2025']) for _ in range(500)],
            'grade': [random.choice(['A', 'A', 'B', 'B', 'B', 'C', 'C', 'D', 'F']) for _ in range(500)],
            'grade_points': [round(random.uniform(0, 4.0), 2) for _ in range(500)],
            'credits': [random.choice([3, 4]) for _ in range(500)]
        })
        grades.to_csv(project_dir / "student_grades.csv", index=False)
        
        # Source 2: Attendance records (JSON)
        attendance = []
        for i in range(1, 151):
            attendance.append({
                'student_id': f"STU{i:06d}",
                'semester': random.choice(['Fall2024', 'Spring2025']),
                'classes_attended': random.randint(20, 50),
                'classes_total': 50,
                'attendance_rate': round(random.uniform(0.4, 1.0), 2)
            })
        with open(project_dir / "attendance_records.json", 'w') as f:
            json.dump(attendance, f, indent=2)
        
        # Source 3: Demographics and course metadata (Parquet)
        demographics = pd.DataFrame({
            'student_id': [f"STU{i:06d}" for i in range(1, 151)],
            'age': [random.randint(18, 25) for _ in range(150)],
            'gender': [random.choice(['M', 'F', 'Other']) for _ in range(150)],
            'major': [random.choice(['CS', 'Engineering', 'Business', 'Arts', 'Science']) for _ in range(150)],
            'enrollment_year': [random.randint(2020, 2024) for _ in range(150)],
            'financial_aid': [random.choice([True, False]) for _ in range(150)]
        })
        demographics.to_parquet(project_dir / "student_demographics.parquet", index=False)
        print("  ✅ 3 sources: student_grades.csv, attendance_records.json, student_demographics.parquet")
    
    def generate_p10_saas(self):
        """P10: SaaS Usage Reporting & Tenant-Level KPIs"""
        print("☁️ P10: SaaS...")
        project_dir = self.data_path / "bronze/p10_saas"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: User events (CSV)
        events = pd.DataFrame({
            'event_id': [f"EVT{i:010d}" for i in range(1, 801)],
            'timestamp': [(datetime(2025, 1, 1) + timedelta(hours=random.randint(0, 720))).isoformat() for _ in range(800)],
            'user_id': [f"USER{random.randint(1, 100):06d}" for _ in range(800)],
            'tenant_id': [f"TENANT{random.randint(1, 20):03d}" for _ in range(800)],
            'event_type': [random.choice(['login', 'feature_use', 'api_call', 'report_generated', 'logout']) for _ in range(800)],
            'feature_name': [random.choice(['dashboard', 'analytics', 'export', 'settings', 'integrations']) for _ in range(800)],
            'session_duration_sec': [random.randint(60, 7200) for _ in range(800)]
        })
        events.to_csv(project_dir / "user_events.csv", index=False)
        
        # Source 2: Subscription data (JSON)
        subscriptions = []
        for i in range(1, 21):
            subscriptions.append({
                'tenant_id': f"TENANT{i:03d}",
                'subscription_tier': random.choice(['free', 'basic', 'pro', 'enterprise']),
                'start_date': (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))).date().isoformat(),
                'mrr': round(random.uniform(0, 5000), 2),
                'user_count': random.randint(1, 100),
                'status': random.choice(['active', 'active', 'active', 'churned'])
            })
        with open(project_dir / "subscription_data.json", 'w') as f:
            json.dump(subscriptions, f, indent=2)
        
        # Source 3: Feature flags (Parquet)
        features = pd.DataFrame({
            'tenant_id': [f"TENANT{random.randint(1, 20):03d}" for _ in range(60)],
            'feature_name': [random.choice(['advanced_analytics', 'api_access', 'custom_reports', 'sso', 'white_label']) for _ in range(60)],
            'enabled': [random.choice([True, False]) for _ in range(60)],
            'enabled_date': [(datetime(2025, 1, 1) + timedelta(days=random.randint(1, 30))).date() for _ in range(60)]
        })
        features.to_parquet(project_dir / "feature_flags.parquet", index=False)
        print("  ✅ 3 sources: user_events.csv, subscription_data.json, feature_flags.parquet")


if __name__ == "__main__":
    generator = MedallionDataGenerator()
    generator.generate_all()
