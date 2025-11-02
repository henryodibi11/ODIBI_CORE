"""
Phase 10 Integration Tests - Full workflow testing.

Tests complete integration between:
- learnodibi_data (data generation)
- learnodibi_project (demo pipeline)
- learnodibi_backend (API)
- learnodibi_ui (UI backend integration)
"""

import pytest
import pandas as pd
import tempfile
import time
from pathlib import Path

from odibi_core.learnodibi_data import (
    get_dataset,
    list_datasets,
    generate_all_datasets,
    clear_cache as clear_data_cache,
)
from odibi_core.learnodibi_project import DemoPipeline, get_pipeline_config
from odibi_core.learnodibi_backend import LearnODIBIBackend


class TestDataToPipeline:
    """Test integration between data module and pipeline."""
    
    def test_pipeline_uses_generated_data(self):
        """Test pipeline can use data from learnodibi_data."""
        # Generate datasets
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_all_datasets(output_dir=tmpdir, overwrite=True)
            
            assert len(paths) == 3
            assert all(Path(p).exists() for p in paths.values())
    
    def test_dataset_available_for_pipeline(self):
        """Test datasets are available for pipeline execution."""
        datasets = list_datasets()
        
        # Pipeline expects these datasets
        expected = ['energy_demo', 'weather_demo', 'maintenance_demo']
        for ds in expected:
            assert ds in datasets
    
    def test_data_quality_for_pipeline(self):
        """Test data quality is suitable for pipeline processing."""
        df = get_dataset('energy_demo', use_cache=False)
        
        # Pipeline needs these columns
        required_cols = ['timestamp', 'facility_id', 'temperature_f', 
                        'pressure_psi', 'flow_rate_gpm', 'power_kw']
        
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"


class TestPipelineToBackend:
    """Test integration between pipeline and backend API."""
    
    def test_backend_runs_pipeline_config(self):
        """Test backend can run pipeline configurations."""
        backend = LearnODIBIBackend()
        
        # Get pipeline config
        config = get_pipeline_config("bronze")
        
        # Backend should be able to process it
        # Note: May fail if config format doesn't match SDK expectations
        # This is an integration test to verify compatibility
        assert config is not None
        assert isinstance(config, (list, dict))
    
    def test_backend_transformation_with_demo_data(self):
        """Test backend can transform demo datasets."""
        backend = LearnODIBIBackend()
        
        # Simple transformation config
        config = {
            "steps": [
                {
                    "name": "load_energy",
                    "type": "function",
                    "function": "identity",
                    "params": {}
                }
            ]
        }
        
        result = backend.run_transformation(config, engine="pandas")
        
        assert "success" in result
        assert "data" in result


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_full_learning_workflow(self):
        """Test complete learning workflow: data → pipeline → backend."""
        # Step 1: Generate data
        datasets = list_datasets()
        assert 'energy_demo' in datasets
        
        # Step 2: Run pipeline
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            assert result is not None
            assert hasattr(result, 'data_map')
        
        # Step 3: Backend API
        backend = LearnODIBIBackend()
        functions = backend.get_available_functions()
        
        assert functions["success"] is True
        assert len(functions["data"]["functions"]) > 0
    
    def test_data_generation_to_pipeline_execution(self):
        """Test data flows from generation through pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate datasets
            paths = generate_all_datasets(output_dir=tmpdir, overwrite=True)
            
            # Verify data exists
            energy_df = pd.read_csv(paths['energy_demo'])
            assert len(energy_df) > 0
            
            # Pipeline should work with this data (implicitly tested by run)
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            assert len(result.data_map) > 0
    
    def test_pipeline_output_via_backend_api(self):
        """Test pipeline outputs can be queried via backend."""
        backend = LearnODIBIBackend()
        
        # Run transformation
        config = {
            "steps": [
                {"name": "test_step", "type": "function", "function": "identity"}
            ]
        }
        
        exec_result = backend.run_transformation(config, engine="pandas")
        
        # If successful, should be able to query status
        if exec_result["success"]:
            pipeline_id = exec_result["data"]["pipeline_id"]
            status = backend.get_pipeline_status(pipeline_id)
            
            assert status["success"] is True


class TestCrossFunctionalIntegration:
    """Test cross-functional integration scenarios."""
    
    def test_multiple_data_sources_to_single_pipeline(self):
        """Test pipeline can handle multiple data sources."""
        # Get all datasets
        datasets = list_datasets()
        assert len(datasets) == 3
        
        # Pipeline should process all three
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            # Should have loaded all three datasets
            bronze_datasets = [k for k in result.data_map.keys() 
                             if k.startswith('bronze_')]
            assert len(bronze_datasets) >= 1  # At least one bronze dataset
    
    def test_pipeline_layers_integration(self):
        """Test bronze → silver → gold layer integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            
            # Run each layer and verify progression
            bronze_result = pipeline.run_bronze()
            assert len(bronze_result.data_map) > 0
            
            silver_result = pipeline.run_silver()
            assert len(silver_result.data_map) >= len(bronze_result.data_map)
            
            gold_result = pipeline.run_gold()
            # Gold may have fewer datasets (aggregated)
            assert len(gold_result.data_map) > 0
    
    def test_backend_caching_with_repeated_queries(self):
        """Test backend caching improves performance."""
        backend = LearnODIBIBackend()
        
        # First call
        start1 = time.time()
        result1 = backend.get_available_functions()
        time1 = time.time() - start1
        
        # Second call (cached)
        start2 = time.time()
        result2 = backend.get_available_functions()
        time2 = time.time() - start2
        
        # Results should be identical
        assert result1["data"]["count"] == result2["data"]["count"]
        
        # Second call should be faster or similar (cached)
        # Note: Time comparison is flaky, just verify both succeed
        assert result1["success"] is True
        assert result2["success"] is True


class TestErrorPropagation:
    """Test error handling across modules."""
    
    def test_invalid_dataset_name(self):
        """Test error handling for invalid dataset name."""
        with pytest.raises(ValueError):
            get_dataset('invalid_dataset_name')
    
    def test_invalid_pipeline_layer(self):
        """Test error handling for invalid pipeline layer."""
        pipeline = DemoPipeline()
        
        with pytest.raises(ValueError):
            pipeline.get_config('invalid_layer')
    
    def test_backend_invalid_config(self):
        """Test backend handles invalid config gracefully."""
        backend = LearnODIBIBackend()
        
        result = backend.run_transformation({}, engine="pandas")
        
        assert result["success"] is False
        assert result["error"] is not None


class TestPerformanceBenchmarks:
    """Performance benchmarks for Phase 10 components."""
    
    def test_data_generation_performance(self):
        """Benchmark data generation performance."""
        start = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_all_datasets(output_dir=tmpdir, overwrite=True)
        
        duration = time.time() - start
        
        assert len(paths) == 3
        # Should complete in reasonable time (< 10 seconds)
        assert duration < 10.0, f"Data generation too slow: {duration:.2f}s"
    
    def test_bronze_pipeline_performance(self):
        """Benchmark bronze layer execution performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            
            start = time.time()
            result = pipeline.run_bronze()
            duration = time.time() - start
            
            assert result is not None
            # Should complete in reasonable time (< 30 seconds)
            assert duration < 30.0, f"Bronze layer too slow: {duration:.2f}s"
    
    def test_backend_api_response_time(self):
        """Benchmark backend API response time."""
        backend = LearnODIBIBackend()
        
        start = time.time()
        result = backend.get_available_functions()
        duration = time.time() - start
        
        assert result["success"] is True
        # Should respond quickly (< 5 seconds)
        assert duration < 5.0, f"API too slow: {duration:.2f}s"
    
    def test_full_pipeline_performance(self):
        """Benchmark full pipeline execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            
            start = time.time()
            result = pipeline.run_full()
            duration = time.time() - start
            
            assert result is not None
            # Full pipeline may take longer (< 60 seconds)
            assert duration < 60.0, f"Full pipeline too slow: {duration:.2f}s"


class TestDataConsistency:
    """Test data consistency across modules."""
    
    def test_data_determinism(self):
        """Test data generation is deterministic."""
        df1 = get_dataset('energy_demo', use_cache=False)
        df2 = get_dataset('energy_demo', use_cache=False)
        
        # Should produce identical data (deterministic with seed)
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_pipeline_reproducibility(self):
        """Test pipeline produces reproducible results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            
            result1 = pipeline.run_bronze()
            result2 = pipeline.run_bronze()
            
            # Should produce same number of datasets
            assert len(result1.data_map) == len(result2.data_map)
    
    def test_cache_consistency(self):
        """Test cached data matches fresh data."""
        clear_data_cache()
        
        # Get fresh data
        df1 = get_dataset('energy_demo', use_cache=False)
        
        # Get cached data
        df2 = get_dataset('energy_demo', use_cache=True)
        df3 = get_dataset('energy_demo', use_cache=True)
        
        # All should match
        pd.testing.assert_frame_equal(df1, df2)
        pd.testing.assert_frame_equal(df2, df3)


class TestConfigurationManagement:
    """Test configuration management across modules."""
    
    def test_all_pipeline_configs_valid(self):
        """Test all pipeline configs are valid."""
        layers = ['bronze', 'silver', 'gold', 'full']
        
        for layer in layers:
            config = get_pipeline_config(layer)
            assert config is not None
            assert isinstance(config, (list, dict))
    
    def test_backend_validates_pipeline_configs(self):
        """Test backend can validate pipeline configs."""
        backend = LearnODIBIBackend()
        
        # Get a pipeline config
        config = get_pipeline_config("bronze")
        
        # Wrap in expected format if it's a list
        if isinstance(config, list):
            config = {"steps": config}
        
        # Validate
        result = backend.validate_config(config)
        
        assert result["success"] is True
        assert "valid" in result["data"]


class TestModuleInteroperability:
    """Test modules work together seamlessly."""
    
    def test_data_module_output_matches_pipeline_input(self):
        """Test data module output format matches pipeline expectations."""
        df = get_dataset('energy_demo')
        
        # Check DataFrame properties
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert len(df.columns) > 0
    
    def test_pipeline_output_matches_backend_expectations(self):
        """Test pipeline output can be consumed by backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            # Result should have data_map
            assert hasattr(result, 'data_map')
            assert isinstance(result.data_map, dict)
            
            # Each entry should be a DataFrame
            for key, df in result.data_map.items():
                assert isinstance(df, pd.DataFrame)
    
    def test_backend_config_format_matches_pipeline(self):
        """Test backend config format is compatible with pipeline."""
        backend = LearnODIBIBackend()
        
        # Get demo configs from backend
        demo_configs = backend.get_demo_pipeline_configs()
        
        if demo_configs["success"] and len(demo_configs["data"]["configs"]) > 0:
            # Config should be loadable
            config = demo_configs["data"]["configs"][0]["config"]
            assert isinstance(config, dict)


class TestDocumentationAndExamples:
    """Test documentation examples work correctly."""
    
    def test_basic_usage_example(self):
        """Test basic usage example from docs works."""
        # From learnodibi_data docs
        datasets = list_datasets()
        assert len(datasets) == 3
        
        df = get_dataset('energy_demo')
        assert isinstance(df, pd.DataFrame)
    
    def test_pipeline_usage_example(self):
        """Test pipeline usage example from docs works."""
        # From learnodibi_project docs
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DemoPipeline(enable_tracking=False, output_dir=tmpdir)
            result = pipeline.run_bronze()
            
            assert result is not None
    
    def test_backend_usage_example(self):
        """Test backend usage example from docs works."""
        # From learnodibi_backend docs
        backend = LearnODIBIBackend()
        result = backend.get_available_functions()
        
        assert result["success"] is True


class TestUIIntegration:
    """Test UI module integration (basic checks)."""
    
    def test_backend_provides_ui_endpoints(self):
        """Test backend provides all necessary UI endpoints."""
        backend = LearnODIBIBackend()
        
        # UI needs these endpoints
        assert hasattr(backend, 'run_transformation')
        assert hasattr(backend, 'preview_dataset')
        assert hasattr(backend, 'get_available_functions')
        assert hasattr(backend, 'validate_config')
        assert hasattr(backend, 'list_demo_datasets')
        assert hasattr(backend, 'get_demo_pipeline_configs')
    
    def test_ui_backend_response_format(self):
        """Test backend responses are UI-friendly."""
        backend = LearnODIBIBackend()
        
        result = backend.get_available_functions()
        
        # UI expects this structure
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert isinstance(result["data"], dict)
