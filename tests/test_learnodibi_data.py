"""
Tests for learnodibi_data module.
"""

import pytest
import pandas as pd
import os
import tempfile
import shutil

from odibi_core.learnodibi_data import (
    get_dataset,
    list_datasets,
    generate_all_datasets,
    clear_cache,
    get_dataset_info,
    generate_energy_demo,
    generate_weather_demo,
    generate_maintenance_demo
)


class TestDataGenerators:
    """Test dataset generation functions."""
    
    def test_generate_energy_demo_shape(self):
        """Test energy demo has correct shape."""
        df = generate_energy_demo(num_rows=100)
        assert df.shape == (100, 7)
    
    def test_generate_energy_demo_columns(self):
        """Test energy demo has expected columns."""
        df = generate_energy_demo()
        expected_cols = [
            'timestamp', 'facility_id', 'temperature_f', 
            'pressure_psi', 'flow_rate_gpm', 'power_kw', 'efficiency_pct'
        ]
        assert df.columns.tolist() == expected_cols
    
    def test_generate_energy_demo_facilities(self):
        """Test energy demo has correct facilities."""
        df = generate_energy_demo()
        facilities = df['facility_id'].unique()
        assert len(facilities) <= 3
        assert all(f in ['PLANT_A', 'PLANT_B', 'PLANT_C'] for f in facilities)
    
    def test_generate_energy_demo_reproducible(self):
        """Test energy demo is reproducible with same seed."""
        df1 = generate_energy_demo(num_rows=50, seed=42)
        df2 = generate_energy_demo(num_rows=50, seed=42)
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_generate_energy_demo_has_nulls(self):
        """Test energy demo contains null values."""
        df = generate_energy_demo(num_rows=1000)
        # Should have some nulls in numeric columns
        numeric_cols = ['temperature_f', 'pressure_psi', 'flow_rate_gpm', 'power_kw', 'efficiency_pct']
        total_nulls = df[numeric_cols].isnull().sum().sum()
        assert total_nulls > 0, "Expected some null values for teaching purposes"
    
    def test_generate_weather_demo_shape(self):
        """Test weather demo has correct shape."""
        df = generate_weather_demo(num_days=30)
        # 30 days × 3 locations = 90 rows
        assert df.shape == (90, 6)
    
    def test_generate_weather_demo_columns(self):
        """Test weather demo has expected columns."""
        df = generate_weather_demo()
        expected_cols = ['date', 'location', 'temp_celsius', 'humidity_pct', 'pressure_mb', 'wind_speed_kph']
        assert df.columns.tolist() == expected_cols
    
    def test_generate_weather_demo_locations(self):
        """Test weather demo has correct locations."""
        df = generate_weather_demo()
        locations = df['location'].unique()
        assert len(locations) == 3
        assert all('PLANT' in loc for loc in locations)
    
    def test_generate_weather_demo_reproducible(self):
        """Test weather demo is reproducible with same seed."""
        df1 = generate_weather_demo(num_days=30, seed=42)
        df2 = generate_weather_demo(num_days=30, seed=42)
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_generate_maintenance_demo_shape(self):
        """Test maintenance demo has correct shape."""
        df = generate_maintenance_demo(num_records=50)
        assert df.shape == (50, 5)
    
    def test_generate_maintenance_demo_columns(self):
        """Test maintenance demo has expected columns."""
        df = generate_maintenance_demo()
        expected_cols = ['equipment_id', 'maintenance_date', 'status', 'cost', 'downtime_hours']
        assert df.columns.tolist() == expected_cols
    
    def test_generate_maintenance_demo_statuses(self):
        """Test maintenance demo has correct status values."""
        df = generate_maintenance_demo(num_records=100)
        statuses = df['status'].unique()
        assert all(s in ['SCHEDULED', 'COMPLETED', 'OVERDUE'] for s in statuses)
    
    def test_generate_maintenance_demo_cost_range(self):
        """Test maintenance costs are in expected range."""
        df = generate_maintenance_demo()
        assert df['cost'].min() >= 500
        assert df['cost'].max() <= 50000
    
    def test_generate_maintenance_demo_reproducible(self):
        """Test maintenance demo is reproducible with same seed."""
        df1 = generate_maintenance_demo(num_records=50, seed=42)
        df2 = generate_maintenance_demo(num_records=50, seed=42)
        pd.testing.assert_frame_equal(df1, df2)


class TestDatasetLoader:
    """Test dataset loading and caching."""
    
    def test_list_datasets(self):
        """Test list_datasets returns expected datasets."""
        datasets = list_datasets()
        assert len(datasets) == 3
        assert 'energy_demo' in datasets
        assert 'weather_demo' in datasets
        assert 'maintenance_demo' in datasets
    
    def test_get_dataset_energy(self):
        """Test loading energy dataset."""
        df = get_dataset('energy_demo')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1000
        assert 'timestamp' in df.columns
    
    def test_get_dataset_weather(self):
        """Test loading weather dataset."""
        df = get_dataset('weather_demo')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1095  # 365 days × 3 locations
        assert 'date' in df.columns
    
    def test_get_dataset_maintenance(self):
        """Test loading maintenance dataset."""
        df = get_dataset('maintenance_demo')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert 'equipment_id' in df.columns
    
    def test_get_dataset_invalid_name(self):
        """Test get_dataset raises error for invalid name."""
        with pytest.raises(ValueError, match="Unknown dataset"):
            get_dataset('invalid_dataset')
    
    def test_get_dataset_caching(self):
        """Test dataset caching works."""
        clear_cache()
        df1 = get_dataset('energy_demo', use_cache=True)
        df2 = get_dataset('energy_demo', use_cache=True)
        # Both should be DataFrames with same content
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_get_dataset_no_cache(self):
        """Test loading without cache."""
        clear_cache()
        df = get_dataset('energy_demo', use_cache=False)
        assert isinstance(df, pd.DataFrame)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        get_dataset('energy_demo', use_cache=True)
        clear_cache()
        # Cache should be cleared (this is implicit, just ensure no errors)
        df = get_dataset('energy_demo', use_cache=True)
        assert isinstance(df, pd.DataFrame)
    
    def test_get_dataset_info(self):
        """Test dataset info retrieval."""
        info = get_dataset_info('energy_demo')
        assert info['name'] == 'energy_demo'
        assert 'file_exists' in info
        assert 'cached' in info
    
    def test_get_dataset_info_invalid(self):
        """Test get_dataset_info raises error for invalid name."""
        with pytest.raises(ValueError, match="Unknown dataset"):
            get_dataset_info('invalid_dataset')


class TestGenerateAll:
    """Test generating all datasets."""
    
    def test_generate_all_datasets(self):
        """Test generating all datasets to temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_all_datasets(output_dir=tmpdir, overwrite=True)
            
            assert len(paths) == 3
            assert 'energy_demo' in paths
            assert 'weather_demo' in paths
            assert 'maintenance_demo' in paths
            
            # Verify files exist
            for name, path in paths.items():
                assert os.path.exists(path)
                df = pd.read_csv(path)
                assert len(df) > 0
    
    def test_generate_all_datasets_no_overwrite(self):
        """Test generate_all respects no overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate once
            generate_all_datasets(output_dir=tmpdir, overwrite=True)
            
            # Try to generate again without overwrite
            paths = generate_all_datasets(output_dir=tmpdir, overwrite=False)
            
            # Should still return paths
            assert len(paths) == 3
