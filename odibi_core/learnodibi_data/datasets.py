"""
Dataset loader with caching for ODIBI CORE demo datasets.

This module provides functions to load pre-generated demo datasets,
with automatic generation and caching for seamless user experience.
"""

import os
from typing import List, Optional
import pandas as pd

from odibi_core.learnodibi_data.data_generator import (
    generate_energy_demo,
    generate_weather_demo,
    generate_maintenance_demo,
    generate_all_datasets as _generate_all
)


# Dataset registry
_AVAILABLE_DATASETS = {
    'energy_demo': generate_energy_demo,
    'weather_demo': generate_weather_demo,
    'maintenance_demo': generate_maintenance_demo
}

# Cache for loaded datasets
_DATASET_CACHE = {}


def _get_datasets_dir() -> str:
    """
    Get the path to the datasets directory.
    
    Returns:
        Absolute path to the datasets directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'datasets')


def list_datasets() -> List[str]:
    """
    List all available demo datasets.
    
    Returns:
        List of dataset names
        
    Example:
        >>> list_datasets()
        ['energy_demo', 'weather_demo', 'maintenance_demo']
    """
    return sorted(_AVAILABLE_DATASETS.keys())


def get_dataset(
    name: str,
    use_cache: bool = True,
    regenerate: bool = False
) -> pd.DataFrame:
    """
    Get a demo dataset by name, generating if needed.
    
    Loads a dataset from CSV if available, otherwise generates it
    and saves to the datasets directory. Optionally uses in-memory
    cache for faster repeated access.
    
    Args:
        name: Dataset name ('energy_demo', 'weather_demo', 'maintenance_demo')
        use_cache: Whether to use in-memory cache (default: True)
        regenerate: Force regeneration even if file exists (default: False)
    
    Returns:
        DataFrame containing the requested dataset
        
    Raises:
        ValueError: If dataset name is not recognized
        
    Example:
        >>> df = get_dataset("energy_demo")
        >>> df.shape
        (1000, 7)
        >>> df = get_dataset("weather_demo", use_cache=False)
        >>> df.shape
        (1095, 6)
    """
    if name not in _AVAILABLE_DATASETS:
        available = ', '.join(list_datasets())
        raise ValueError(
            f"Unknown dataset: '{name}'. Available datasets: {available}"
        )
    
    # Check in-memory cache first
    if use_cache and name in _DATASET_CACHE and not regenerate:
        return _DATASET_CACHE[name].copy()
    
    # Check for CSV file
    datasets_dir = _get_datasets_dir()
    csv_path = os.path.join(datasets_dir, f"{name}.csv")
    
    if os.path.exists(csv_path) and not regenerate:
        df = pd.read_csv(csv_path)
        
        # Parse date/datetime columns
        if name == 'energy_demo' and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif name == 'weather_demo' and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        elif name == 'maintenance_demo' and 'maintenance_date' in df.columns:
            df['maintenance_date'] = pd.to_datetime(df['maintenance_date']).dt.date
    else:
        # Generate the dataset
        generator_func = _AVAILABLE_DATASETS[name]
        df = generator_func()
        
        # Save to CSV for future use
        os.makedirs(datasets_dir, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"Generated and saved {name} to {csv_path}")
    
    # Update cache
    if use_cache:
        _DATASET_CACHE[name] = df.copy()
    
    return df


def clear_cache() -> None:
    """
    Clear the in-memory dataset cache.
    
    Use this to free memory or force reloading from disk.
    
    Example:
        >>> clear_cache()
    """
    _DATASET_CACHE.clear()


def get_dataset_info(name: str) -> dict:
    """
    Get metadata about a dataset without loading it.
    
    Args:
        name: Dataset name
    
    Returns:
        Dictionary with dataset metadata (name, file_exists, cached)
        
    Example:
        >>> info = get_dataset_info("energy_demo")
        >>> info['name']
        'energy_demo'
    """
    if name not in _AVAILABLE_DATASETS:
        raise ValueError(f"Unknown dataset: '{name}'")
    
    datasets_dir = _get_datasets_dir()
    csv_path = os.path.join(datasets_dir, f"{name}.csv")
    
    info = {
        'name': name,
        'file_exists': os.path.exists(csv_path),
        'file_path': csv_path if os.path.exists(csv_path) else None,
        'cached': name in _DATASET_CACHE
    }
    
    if os.path.exists(csv_path):
        info['file_size_bytes'] = os.path.getsize(csv_path)
    
    return info


def generate_all_datasets(
    output_dir: Optional[str] = None,
    overwrite: bool = False
) -> dict:
    """
    Generate all demo datasets and save to CSV files.
    
    Args:
        output_dir: Directory to save CSV files (default: module's datasets/ dir)
        overwrite: Whether to overwrite existing files (default: False)
    
    Returns:
        Dictionary mapping dataset names to file paths
        
    Example:
        >>> paths = generate_all_datasets()
        Generated energy_demo: .../datasets/energy_demo.csv (1000 rows)
        Generated weather_demo: .../datasets/weather_demo.csv (1095 rows)
        Generated maintenance_demo: .../datasets/maintenance_demo.csv (100 rows)
    """
    if output_dir is None:
        output_dir = _get_datasets_dir()
    
    return _generate_all(output_dir=output_dir, overwrite=overwrite)
