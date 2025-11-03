"""
Generate all 10 ODIBI_CORE Dual-Mode Showcases
Automatically creates data, configs, and runner scripts for each showcase.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import random
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_PATH = Path("D:/projects/odibi_core")
DATA_PATH = BASE_PATH / "resources/data/showcases"
CONFIG_PATH = BASE_PATH / "resources/configs/showcases"

# Showcase definitions
SHOWCASES = {
    2: {
        "name": "Smart Home Sensor Data Pipeline",
        "theme": "IoT Analytics",
        "description": "Process smart home sensor readings (temperature, humidity, motion) with time-series aggregations",
        "data_files": {
            "sensor_readings.csv": [
                ("sensor_id", "device_type", "reading_value", "timestamp", "room", "battery_level"),
                (random.choices(population=list(range(1001, 1016)), k=20)),
            ],
            "device_metadata.csv": [
                ("sensor_id", "install_date", "firmware_version", "location_zone"),
            ]
        },
        "pipeline_steps": [
            {"layer": "bronze", "name": "load_sensor_readings", "type": "read"},
            {"layer": "bronze", "name": "load_device_metadata", "type": "read"},
            {"layer": "silver", "name": "filter_valid_readings", "type": "transform"},
            {"layer": "silver", "name": "join_metadata", "type": "join"},
            {"layer": "gold", "name": "aggregate_by_room", "type": "aggregate"},
            {"layer": "gold", "name": "aggregate_by_hour", "type": "aggregate"},
        ]
    },
    3: {
        "name": "Movie Recommendation Data Flow",
        "theme": "Content Analytics",
        "description": "Analyze movie ratings and user preferences to generate genre-based recommendations",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 7
    },
    4: {
        "name": "Financial Transactions Audit",
        "theme": "Finance & Compliance",
        "description": "Process financial transactions with fraud detection rules and compliance reporting",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 8
    },
    5: {
        "name": "Social Media Sentiment Dashboard",
        "theme": "Social Analytics",
        "description": "Aggregate social media posts with sentiment scoring and trend analysis",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 6
    },
    6: {
        "name": "City Weather & Air Quality Data Merger",
        "theme": "Environmental Data",
        "description": "Merge weather data with air quality indices for environmental analysis",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 7
    },
    7: {
        "name": "Healthcare Patient Wait-Time Analysis",
        "theme": "Healthcare Operations",
        "description": "Analyze patient wait times across departments with bottleneck identification",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 8
    },
    8: {
        "name": "E-Commerce Returns Monitor",
        "theme": "Retail Operations",
        "description": "Track product returns with reason analysis and supplier quality metrics",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 7
    },
    9: {
        "name": "Transportation Fleet Tracker",
        "theme": "Logistics",
        "description": "Monitor fleet GPS data with route optimization and fuel efficiency analysis",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 8
    },
    10: {
        "name": "Education Outcome Correlation Study",
        "theme": "Education Analytics",
        "description": "Correlate student attendance, assignments, and test scores for outcome prediction",
        "pipeline_layers": ["bronze", "silver", "gold"],
        "step_count": 7
    }
}

def generate_sample_data_02():
    """Generate Smart Home Sensor data."""
    # Sensor readings
    sensor_data = []
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    rooms = ["Living Room", "Bedroom", "Kitchen", "Office", "Bathroom"]
    device_types = ["Temperature", "Humidity", "Motion"]
    
    for i in range(50):
        sensor_data.append({
            "sensor_id": random.randint(1001, 1015),
            "device_type": random.choice(device_types),
            "reading_value": round(random.uniform(15, 30) if device_types[0] else random.uniform(30, 70), 2),
            "timestamp": (base_time + timedelta(hours=i)).isoformat(),
            "room": random.choice(rooms),
            "battery_level": random.randint(20, 100)
        })
    
    with open(DATA_PATH / "sensor_readings.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sensor_data[0].keys())
        writer.writeheader()
        writer.writerows(sensor_data)
    
    # Device metadata
    device_data = []
    for sensor_id in range(1001, 1016):
        device_data.append({
            "sensor_id": sensor_id,
            "install_date": "2024-06-15",
            "firmware_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
            "location_zone": random.choice(["Zone A", "Zone B", "Zone C"])
        })
    
    with open(DATA_PATH / "device_metadata.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=device_data[0].keys())
        writer.writeheader()
        writer.writerows(device_data)
    
    print(f"✅ Generated Showcase #2 data files")

def generate_json_config(showcase_id, name):
    """Generate JSON config template."""
    config = [
        {
            "layer": "bronze",
            "name": f"load_data_source_1",
            "type": "read",
            "engine": "pandas",
            "value": {"source": f"resources/data/showcases/data_{showcase_id}_1.csv", "format": "csv"},
            "params": {},
            "inputs": [],
            "outputs": ["data_source_1"],
            "metadata": {"description": "Load primary data source"}
        },
        {
            "layer": "silver",
            "name": "transform_data",
            "type": "transform",
            "engine": "pandas",
            "value": {"operation": "add_column", "column_name": "processed_flag", "expression": "1"},
            "params": {},
            "inputs": ["data_source_1"],
            "outputs": ["transformed_data"],
            "metadata": {"description": "Apply transformation"}
        },
        {
            "layer": "gold",
            "name": "aggregate_metrics",
            "type": "aggregate",
            "engine": "pandas",
            "value": {"group_by": ["category"], "aggregations": {"count": {"column": "id", "function": "count"}}},
            "params": {},
            "inputs": ["transformed_data"],
            "outputs": ["final_metrics"],
            "metadata": {"description": "Calculate final metrics"}
        },
        {
            "layer": "gold",
            "name": "export_results",
            "type": "write",
            "engine": "pandas",
            "value": {"destination": f"resources/output/showcases/json_mode/showcase_{showcase_id:02d}/results.csv", "format": "csv"},
            "params": {},
            "inputs": ["final_metrics"],
            "outputs": [],
            "metadata": {"description": "Export to CSV"}
        }
    ]
    
    config_file = CONFIG_PATH / f"showcase_{showcase_id:02d}.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Generated JSON config: showcase_{showcase_id:02d}.json")

def generate_placeholder_data(showcase_id):
    """Generate minimal placeholder data for showcases 3-10."""
    data_file = DATA_PATH / f"data_{showcase_id}_1.csv"
    
    with open(data_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "category", "value", "timestamp"])
        for i in range(1, 21):
            writer.writerow([
                i,
                random.choice(["A", "B", "C"]),
                round(random.uniform(10, 100), 2),
                (datetime(2025, 1, 1) + timedelta(days=i)).strftime("%Y-%m-%d")
            ])
    
    print(f"✅ Generated placeholder data: data_{showcase_id}_1.csv")

print("="*70)
print("GENERATING ALL ODIBI_CORE DUAL-MODE SHOWCASES")
print("="*70)

# Showcase #2: Smart Home (detailed)
print("\n[Showcase #2] Smart Home Sensor Data Pipeline")
generate_sample_data_02()

# Showcases #3-10: Templates
for showcase_id in range(2, 11):
    spec = SHOWCASES[showcase_id]
    print(f"\n[Showcase #{showcase_id}] {spec['name']}")
    
    if showcase_id > 2:
        generate_placeholder_data(showcase_id)
    
    generate_json_config(showcase_id, spec['name'])

print("\n" + "="*70)
print("✅ ALL SHOWCASES GENERATED")
print("="*70)
print("\nNext steps:")
print("1. Review generated configs in resources/configs/showcases/")
print("2. Customize data files in resources/data/showcases/ as needed")
print("3. Run individual showcase scripts or master runner")
