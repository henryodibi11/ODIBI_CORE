"""
ODIBI CORE LearnODIBI Data Module

Synthetic dataset generation and loading for teaching and demonstration purposes.

This module provides:
- Realistic synthetic datasets (energy, weather, maintenance)
- Automatic dataset generation and caching
- Reproducible data with controlled quality issues for teaching

Quick Start:
    >>> from odibi_core.learnodibi_data import get_dataset, list_datasets
    >>> 
    >>> # List available datasets
    >>> datasets = list_datasets()
    >>> print(datasets)
    ['energy_demo', 'weather_demo', 'maintenance_demo']
    >>> 
    >>> # Load a dataset (auto-generates if needed)
    >>> energy_df = get_dataset("energy_demo")
    >>> print(energy_df.shape)
    (1000, 7)

Available Datasets:
    - energy_demo: 1000 rows of industrial energy metrics with quality issues
    - weather_demo: 1095 rows (365 days × 3 locations) of weather data
    - maintenance_demo: 100 maintenance records with costs and downtime
"""

from odibi_core.learnodibi_data.datasets import (
    get_dataset,
    list_datasets,
    generate_all_datasets,
    clear_cache,
    get_dataset_info
)

from odibi_core.learnodibi_data.data_generator import (
    generate_energy_demo,
    generate_weather_demo,
    generate_maintenance_demo
)


__all__ = [
    # Main API
    'get_dataset',
    'list_datasets',
    'generate_all_datasets',
    'clear_cache',
    'get_dataset_info',
    
    # Generator functions
    'generate_energy_demo',
    'generate_weather_demo',
    'generate_maintenance_demo'
]
