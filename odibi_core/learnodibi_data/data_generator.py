"""
Synthetic dataset generator for ODIBI CORE demo and teaching purposes.

This module provides functions to generate realistic synthetic datasets
for energy, weather, and maintenance data with controlled quality issues.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def generate_energy_demo(
    num_rows: int = 1000,
    facilities: list = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic energy dataset with realistic industrial metrics.
    
    Creates hourly energy readings from multiple facilities with realistic
    patterns and intentional quality issues (nulls, outliers) for teaching
    data validation and cleaning.
    
    Args:
        num_rows: Number of rows to generate (default: 1000)
        facilities: List of facility IDs (default: ["PLANT_A", "PLANT_B", "PLANT_C"])
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        DataFrame with columns: timestamp, facility_id, temperature_f, 
        pressure_psi, flow_rate_gpm, power_kw, efficiency_pct
        
    Example:
        >>> df = generate_energy_demo(num_rows=100)
        >>> df.shape
        (100, 7)
        >>> df.columns.tolist()
        ['timestamp', 'facility_id', 'temperature_f', 'pressure_psi', 'flow_rate_gpm', 'power_kw', 'efficiency_pct']
    """
    if facilities is None:
        facilities = ["PLANT_A", "PLANT_B", "PLANT_C"]
    
    np.random.seed(seed)
    
    # Generate timestamps (hourly for ~42 days)
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    timestamps = [start_date + timedelta(hours=i) for i in range(num_rows)]
    
    # Distribute across facilities
    facility_ids = np.random.choice(facilities, size=num_rows)
    
    # Generate realistic metrics with patterns
    hours = np.array([ts.hour for ts in timestamps])
    
    # Temperature: 180-220°F with daily pattern (higher during day)
    base_temp = 200 + 10 * np.sin(2 * np.pi * hours / 24)
    temperature_f = base_temp + np.random.normal(0, 5, num_rows)
    
    # Pressure: 100-150 PSI with some variation
    pressure_psi = 125 + np.random.normal(0, 10, num_rows)
    
    # Flow rate: 50-200 GPM correlated with temperature
    flow_rate_gpm = 100 + 0.5 * (temperature_f - 200) + np.random.normal(0, 15, num_rows)
    
    # Power: 500-2000 kW correlated with flow rate
    power_kw = 1000 + 5 * (flow_rate_gpm - 100) + np.random.normal(0, 100, num_rows)
    
    # Efficiency: 75-95% inversely correlated with temperature
    efficiency_pct = 90 - 0.2 * (temperature_f - 200) + np.random.normal(0, 2, num_rows)
    efficiency_pct = np.clip(efficiency_pct, 70, 98)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'facility_id': facility_ids,
        'temperature_f': temperature_f,
        'pressure_psi': pressure_psi,
        'flow_rate_gpm': flow_rate_gpm,
        'power_kw': power_kw,
        'efficiency_pct': efficiency_pct
    })
    
    # Introduce quality issues (10% null values)
    null_mask = np.random.random(num_rows) < 0.10
    null_indices = np.where(null_mask)[0]
    null_columns = np.random.choice(
        ['temperature_f', 'pressure_psi', 'flow_rate_gpm', 'power_kw', 'efficiency_pct'],
        size=len(null_indices)
    )
    
    for idx, col in zip(null_indices, null_columns):
        df.loc[idx, col] = np.nan
    
    # Add some outliers (5% of data)
    outlier_mask = np.random.random(num_rows) < 0.05
    outlier_indices = np.where(outlier_mask)[0]
    
    for idx in outlier_indices:
        col = np.random.choice(['temperature_f', 'pressure_psi', 'flow_rate_gpm', 'power_kw'])
        df.loc[idx, col] = df[col].mean() + 5 * df[col].std()
    
    return df


def generate_weather_demo(
    num_days: int = 365,
    locations: list = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic weather dataset with seasonal patterns.
    
    Creates daily weather data for multiple locations with realistic
    seasonal temperature and weather patterns.
    
    Args:
        num_days: Number of days to generate (default: 365)
        locations: List of location names (default: matches energy facilities)
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        DataFrame with columns: date, location, temp_celsius, humidity_pct,
        pressure_mb, wind_speed_kph
        
    Example:
        >>> df = generate_weather_demo(num_days=30)
        >>> df.shape
        (90, 6)  # 30 days × 3 locations
    """
    if locations is None:
        locations = ["PLANT_A_LOCATION", "PLANT_B_LOCATION", "PLANT_C_LOCATION"]
    
    np.random.seed(seed)
    
    # Generate dates
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # Create entry for each location
    data_rows = []
    
    for location in locations:
        location_seed = seed + hash(location) % 1000
        np.random.seed(location_seed)
        
        for day_num, date in enumerate(dates):
            # Seasonal temperature pattern (sinusoidal over year)
            day_of_year = date.timetuple().tm_yday
            base_temp = 15 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            temp_celsius = base_temp + np.random.normal(0, 5)
            
            # Humidity: inversely correlated with temperature
            humidity_pct = 70 - 0.8 * (temp_celsius - 15) + np.random.normal(0, 10)
            humidity_pct = np.clip(humidity_pct, 20, 95)
            
            # Pressure: 980-1030 mb with weather patterns
            pressure_mb = 1010 + np.random.normal(0, 15)
            
            # Wind speed: 5-30 kph
            wind_speed_kph = 15 + np.random.exponential(5)
            wind_speed_kph = np.clip(wind_speed_kph, 0, 50)
            
            data_rows.append({
                'date': date.date(),
                'location': location,
                'temp_celsius': round(temp_celsius, 1),
                'humidity_pct': round(humidity_pct, 1),
                'pressure_mb': round(pressure_mb, 1),
                'wind_speed_kph': round(wind_speed_kph, 1)
            })
    
    return pd.DataFrame(data_rows)


def generate_maintenance_demo(
    num_records: int = 100,
    equipment_prefix: str = "EQ",
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic maintenance records dataset.
    
    Creates maintenance records with realistic costs, statuses, and
    downtime patterns for teaching maintenance tracking and analysis.
    
    Args:
        num_records: Number of maintenance records (default: 100)
        equipment_prefix: Prefix for equipment IDs (default: "EQ")
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        DataFrame with columns: equipment_id, maintenance_date, status,
        cost, downtime_hours
        
    Example:
        >>> df = generate_maintenance_demo(num_records=50)
        >>> df['status'].unique()
        array(['SCHEDULED', 'COMPLETED', 'OVERDUE'], dtype=object)
    """
    np.random.seed(seed)
    
    # Generate equipment IDs (15-20 unique pieces of equipment)
    num_equipment = np.random.randint(15, 21)
    equipment_ids = [f"{equipment_prefix}_{i:03d}" for i in range(1, num_equipment + 1)]
    
    # Generate maintenance records
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    data_rows = []
    
    for _ in range(num_records):
        equipment_id = np.random.choice(equipment_ids)
        
        # Random maintenance date
        days_offset = np.random.randint(0, date_range)
        maintenance_date = start_date + timedelta(days=days_offset)
        
        # Status distribution: 60% COMPLETED, 30% SCHEDULED, 10% OVERDUE
        status = np.random.choice(
            ['COMPLETED', 'SCHEDULED', 'OVERDUE'],
            p=[0.60, 0.30, 0.10]
        )
        
        # Cost: $500-$50,000 with log-normal distribution
        base_cost = np.random.lognormal(mean=8.5, sigma=1.2)
        cost = np.clip(base_cost, 500, 50000)
        
        # Downtime: correlated with cost (more expensive = more downtime)
        # 0-48 hours, with some scheduled maintenance having 0 downtime
        if status == 'SCHEDULED':
            downtime_hours = 0.0 if np.random.random() < 0.5 else np.random.uniform(1, 8)
        else:
            downtime_hours = np.random.exponential(scale=cost / 2000)
            downtime_hours = np.clip(downtime_hours, 0, 48)
        
        data_rows.append({
            'equipment_id': equipment_id,
            'maintenance_date': maintenance_date.date(),
            'status': status,
            'cost': round(cost, 2),
            'downtime_hours': round(downtime_hours, 1)
        })
    
    df = pd.DataFrame(data_rows)
    df = df.sort_values('maintenance_date').reset_index(drop=True)
    
    return df


def generate_all_datasets(
    output_dir: str,
    overwrite: bool = False
) -> Dict[str, str]:
    """
    Generate all demo datasets and save to CSV files.
    
    Creates energy, weather, and maintenance datasets and saves them
    to the specified output directory.
    
    Args:
        output_dir: Directory to save CSV files
        overwrite: Whether to overwrite existing files (default: False)
    
    Returns:
        Dictionary mapping dataset names to file paths
        
    Example:
        >>> paths = generate_all_datasets("data/demo")
        >>> paths.keys()
        dict_keys(['energy_demo', 'weather_demo', 'maintenance_demo'])
    """
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    datasets = {
        'energy_demo': generate_energy_demo(),
        'weather_demo': generate_weather_demo(),
        'maintenance_demo': generate_maintenance_demo()
    }
    
    file_paths = {}
    
    for name, df in datasets.items():
        file_path = os.path.join(output_dir, f"{name}.csv")
        
        if os.path.exists(file_path) and not overwrite:
            print(f"Skipping {name} (file exists, use overwrite=True to replace)")
            file_paths[name] = file_path
            continue
        
        df.to_csv(file_path, index=False)
        print(f"Generated {name}: {file_path} ({len(df)} rows)")
        file_paths[name] = file_path
    
    return file_paths
