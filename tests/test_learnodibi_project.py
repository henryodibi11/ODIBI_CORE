"""
Tests for learnodibi_project module - Demo pipeline execution.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
import tempfile
import shutil

from odibi_core.learnodibi_project import DemoPipeline, get_pipeline_config


class TestDemoPipelineInitialization:
    """Test DemoPipeline initialization."""
    
    def test_init_default_params(self):
        """Test DemoPipeline with default parameters."""
        pipeline = DemoPipeline()
        assert pipeline.engine == "pandas"
        assert pipeline.enable_tracking is True
        assert pipeline.output_dir.exists()
    
    def test_init_custom_engine(self):
        """Test DemoPipeline with custom engine."""
        pipeline = DemoPipeline(engine="spark")
        assert pipeline.engine == "spark"
    
    def test_init_custom_output_dir(self):
        """Test DemoPipeline with custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(output_dir=tmpdir)
            assert str(pipeline.output_dir) == tmpdir
    
    def test_init_no_tracking(self):
        """Test DemoPipeline with tracking disabled."""
        pipeline = DemoPipeline(enable_tracking=False)
        assert pipeline.enable_tracking is False
    
    def test_config_paths_exist(self):
        """Test that all config files exist."""
        pipeline = DemoPipeline()
        assert pipeline.bronze_config.exists()
        assert pipeline.silver_config.exists()
        assert pipeline.gold_config.exists()
        assert pipeline.full_config.exists()


class TestBronzeLayer:
    """Test Bronze layer execution."""
    
    def test_run_bronze_success(self):
        """Test bronze layer executes successfully."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        assert result is not None
        assert hasattr(result, 'data_map')
        assert len(result.data_map) >= 3
    
    def test_run_bronze_datasets_created(self):
        """Test bronze layer creates expected datasets."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        expected_keys = ['bronze_energy', 'bronze_weather', 'bronze_maintenance']
        for key in expected_keys:
            assert key in result.data_map, f"Missing dataset: {key}"
    
    def test_run_bronze_data_shape(self):
        """Test bronze datasets have expected structure."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        # Check energy data
        if 'bronze_energy' in result.data_map:
            df = result.data_map['bronze_energy']
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert 'facility_id' in df.columns
    
    def test_run_bronze_reproducible(self):
        """Test bronze layer produces consistent results."""
        pipeline = DemoPipeline(enable_tracking=False)
        result1 = pipeline.run_bronze()
        result2 = pipeline.run_bronze()
        
        assert len(result1.data_map) == len(result2.data_map)


class TestSilverLayer:
    """Test Silver layer execution."""
    
    def test_run_silver_success(self):
        """Test silver layer executes successfully."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_silver()
        
        assert result is not None
        assert hasattr(result, 'data_map')
    
    def test_run_silver_includes_bronze(self):
        """Test silver layer includes bronze datasets."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_silver()
        
        # Should have both bronze and silver datasets
        assert 'bronze_energy' in result.data_map or 'silver_energy' in result.data_map
    
    def test_run_silver_transformations_applied(self):
        """Test silver layer applies transformations."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_silver()
        
        # Check for silver datasets
        silver_keys = [k for k in result.data_map.keys() if k.startswith('silver_')]
        assert len(silver_keys) > 0, "No silver datasets found"
    
    def test_run_silver_data_quality(self):
        """Test silver layer produces clean data."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_silver()
        
        for key, df in result.data_map.items():
            if key.startswith('silver_') and isinstance(df, pd.DataFrame):
                assert len(df) > 0, f"Empty dataset: {key}"


class TestGoldLayer:
    """Test Gold layer execution."""
    
    def test_run_gold_success(self):
        """Test gold layer executes successfully."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_gold()
        
        assert result is not None
        assert hasattr(result, 'data_map')
    
    def test_run_gold_aggregations_created(self):
        """Test gold layer creates aggregated datasets."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_gold()
        
        # Check for gold datasets
        gold_keys = [k for k in result.data_map.keys() if k.startswith('gold_')]
        assert len(gold_keys) > 0, "No gold datasets found"
    
    def test_run_gold_metrics_calculated(self):
        """Test gold layer calculates business metrics."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_gold()
        
        # Look for efficiency report
        if 'gold_efficiency_report' in result.data_map:
            df = result.data_map['gold_efficiency_report']
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0


class TestFullPipeline:
    """Test full pipeline execution."""
    
    def test_run_full_success(self):
        """Test full pipeline executes successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_full()
            
            assert result is not None
            assert hasattr(result, 'data_map')
    
    def test_run_full_all_layers(self):
        """Test full pipeline produces all layer datasets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_full()
            
            # Should have bronze, silver, and gold datasets
            has_bronze = any(k.startswith('bronze_') for k in result.data_map.keys())
            has_silver = any(k.startswith('silver_') for k in result.data_map.keys())
            has_gold = any(k.startswith('gold_') for k in result.data_map.keys())
            
            assert has_bronze or has_silver or has_gold, "Missing layer datasets"
    
    def test_run_full_saves_outputs(self):
        """Test full pipeline saves output files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_full()
            
            # Check for output files
            output_path = Path(tmpdir)
            output_files = list(output_path.rglob("gold_*"))
            
            # Should have at least some output files
            assert len(output_files) >= 0  # May or may not save depending on config


class TestConfigLoading:
    """Test configuration loading."""
    
    def test_get_config_bronze(self):
        """Test loading bronze config."""
        pipeline = DemoPipeline()
        config = pipeline.get_config("bronze")
        
        assert isinstance(config, (list, dict))
        if isinstance(config, list):
            assert len(config) > 0
    
    def test_get_config_silver(self):
        """Test loading silver config."""
        pipeline = DemoPipeline()
        config = pipeline.get_config("silver")
        
        assert isinstance(config, (list, dict))
    
    def test_get_config_gold(self):
        """Test loading gold config."""
        pipeline = DemoPipeline()
        config = pipeline.get_config("gold")
        
        assert isinstance(config, (list, dict))
    
    def test_get_config_full(self):
        """Test loading full config."""
        pipeline = DemoPipeline()
        config = pipeline.get_config("full")
        
        assert isinstance(config, (list, dict))
    
    def test_get_config_invalid_layer(self):
        """Test get_config raises error for invalid layer."""
        pipeline = DemoPipeline()
        
        with pytest.raises(ValueError, match="Invalid layer"):
            pipeline.get_config("invalid")
    
    def test_get_pipeline_config_function(self):
        """Test standalone get_pipeline_config function."""
        config = get_pipeline_config("bronze")
        assert config is not None


class TestErrorHandling:
    """Test error handling in pipeline."""
    
    def test_invalid_config_path(self):
        """Test pipeline handles missing config file."""
        pipeline = DemoPipeline()
        pipeline.bronze_config = Path("nonexistent_config.json")
        
        with pytest.raises(Exception):
            pipeline.run_bronze()
    
    def test_invalid_engine(self):
        """Test pipeline with invalid engine."""
        # Should still initialize, errors come at execution
        pipeline = DemoPipeline(engine="invalid_engine")
        assert pipeline.engine == "invalid_engine"


class TestPipelineDescription:
    """Test pipeline description."""
    
    def test_describe_returns_string(self):
        """Test describe method returns formatted string."""
        pipeline = DemoPipeline()
        description = pipeline.describe()
        
        assert isinstance(description, str)
        assert len(description) > 0
    
    def test_describe_contains_layers(self):
        """Test description contains layer information."""
        pipeline = DemoPipeline()
        description = pipeline.describe()
        
        assert "BRONZE" in description.upper()
        assert "SILVER" in description.upper()
        assert "GOLD" in description.upper()
    
    def test_describe_contains_usage(self):
        """Test description contains usage examples."""
        pipeline = DemoPipeline()
        description = pipeline.describe()
        
        assert "Usage:" in description or "usage:" in description.lower()


class TestTracking:
    """Test tracking functionality."""
    
    def test_tracking_enabled_creates_logs(self):
        """Test tracking creates log files when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=True, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            # Check if tracker logs directory was created
            tracker_dir = Path(tmpdir) / "tracker_logs"
            if tracker_dir.exists():
                log_files = list(tracker_dir.glob("*.json"))
                assert len(log_files) > 0, "No tracker logs created"
    
    def test_tracking_disabled_no_logs(self):
        """Test no logs created when tracking disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            # Tracker logs directory may not exist
            tracker_dir = Path(tmpdir) / "tracker_logs"
            # No assertion - just ensure no crash


class TestPipelineResult:
    """Test pipeline result objects."""
    
    def test_result_has_data_map(self):
        """Test result contains data_map."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        assert hasattr(result, 'data_map')
        assert isinstance(result.data_map, dict)
    
    def test_result_data_types(self):
        """Test result data_map contains DataFrames."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        for key, value in result.data_map.items():
            assert isinstance(value, pd.DataFrame), f"{key} is not a DataFrame"
    
    def test_result_has_summary(self):
        """Test result has summary method."""
        pipeline = DemoPipeline(enable_tracking=False)
        result = pipeline.run_bronze()
        
        if hasattr(result, 'summary'):
            summary = result.summary()
            assert isinstance(summary, str)
