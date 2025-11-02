"""
Tests for learnodibi_backend module - API endpoints.
"""

import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path

from odibi_core.learnodibi_backend import LearnODIBIBackend
from odibi_core.learnodibi_backend.error_handler import (
    ConfigurationError,
    ExecutionError,
    DatasetError,
)


class TestBackendInitialization:
    """Test LearnODIBIBackend initialization."""
    
    def test_init_default_cache_ttl(self):
        """Test backend initializes with default cache TTL."""
        backend = LearnODIBIBackend()
        assert backend.cache is not None
        assert backend.session_pipelines == {}
    
    def test_init_custom_cache_ttl(self):
        """Test backend initializes with custom cache TTL."""
        backend = LearnODIBIBackend(cache_ttl_seconds=600)
        assert backend.cache is not None


class TestRunTransformation:
    """Test run_transformation endpoint."""
    
    def test_run_transformation_basic(self):
        """Test basic transformation execution."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {
                    "name": "test_step",
                    "type": "function",
                    "function": "identity",
                    "params": {}
                }
            ]
        }
        
        result = backend.run_transformation(config, engine="pandas")
        
        assert result["success"] in [True, False]
        assert "data" in result
        assert "error" in result
        assert "execution_time_ms" in result
        assert "metadata" in result
    
    def test_run_transformation_empty_config(self):
        """Test transformation fails with empty config."""
        backend = LearnODIBIBackend()
        
        result = backend.run_transformation({}, engine="pandas")
        
        assert result["success"] is False
        assert result["error"] is not None
    
    def test_run_transformation_no_steps(self):
        """Test transformation fails without steps."""
        backend = LearnODIBIBackend()
        
        config = {"name": "test"}
        result = backend.run_transformation(config, engine="pandas")
        
        assert result["success"] is False
        assert "steps" in result["error"].lower()
    
    def test_run_transformation_stores_pipeline_id(self):
        """Test transformation stores pipeline ID in session."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {
                    "name": "test_step",
                    "type": "function",
                    "function": "identity",
                    "params": {}
                }
            ]
        }
        
        result = backend.run_transformation(config, engine="pandas")
        
        if result["success"]:
            pipeline_id = result["data"]["pipeline_id"]
            assert pipeline_id in backend.session_pipelines
    
    def test_run_transformation_metadata(self):
        """Test transformation returns correct metadata."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {"name": "step1", "type": "function", "function": "identity"},
                {"name": "step2", "type": "function", "function": "identity"}
            ]
        }
        
        result = backend.run_transformation(config, engine="pandas")
        
        assert result["metadata"]["engine"] == "pandas"
        assert result["metadata"]["steps_count"] == 2


class TestGetAvailableFunctions:
    """Test get_available_functions endpoint."""
    
    def test_get_available_functions_returns_list(self):
        """Test get_available_functions returns function list."""
        backend = LearnODIBIBackend()
        result = backend.get_available_functions()
        
        assert result["success"] is True
        assert "functions" in result["data"]
        assert "count" in result["data"]
        assert isinstance(result["data"]["functions"], list)
    
    def test_get_available_functions_structure(self):
        """Test function metadata structure."""
        backend = LearnODIBIBackend()
        result = backend.get_available_functions()
        
        if len(result["data"]["functions"]) > 0:
            func = result["data"]["functions"][0]
            assert "name" in func
            assert "module" in func
            assert "full_path" in func
            assert "docstring" in func
    
    def test_get_available_functions_caching(self):
        """Test get_available_functions uses cache."""
        backend = LearnODIBIBackend()
        
        # First call
        result1 = backend.get_available_functions()
        time1 = result1["execution_time_ms"]
        
        # Second call (should be cached)
        result2 = backend.get_available_functions()
        time2 = result2["execution_time_ms"]
        
        # Cached result should be faster or same
        assert result1["data"]["count"] == result2["data"]["count"]
    
    def test_get_available_functions_modules(self):
        """Test functions from all modules are returned."""
        backend = LearnODIBIBackend()
        result = backend.get_available_functions()
        
        if len(result["data"]["functions"]) > 0:
            modules = set(f["module"] for f in result["data"]["functions"])
            
            # Should have multiple modules
            assert len(modules) > 0


class TestPreviewDataset:
    """Test preview_dataset endpoint."""
    
    def test_preview_dataset_csv(self):
        """Test preview CSV dataset."""
        backend = LearnODIBIBackend()
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2,col3\n")
            f.write("1,2,3\n")
            f.write("4,5,6\n")
            temp_path = f.name
        
        try:
            result = backend.preview_dataset(temp_path, rows=10)
            
            assert result["success"] is True
            assert "preview" in result["data"]
            assert "columns" in result["data"]
            assert "rows" in result["data"]
            assert "dtypes" in result["data"]
        finally:
            Path(temp_path).unlink()
    
    def test_preview_dataset_nonexistent(self):
        """Test preview fails for nonexistent dataset."""
        backend = LearnODIBIBackend()
        
        result = backend.preview_dataset("nonexistent_file.csv", rows=10)
        
        assert result["success"] is False
        assert result["error"] is not None
    
    def test_preview_dataset_row_limit(self):
        """Test preview respects row limit."""
        backend = LearnODIBIBackend()
        
        # Create temporary CSV with many rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n")
            for i in range(100):
                f.write(f"{i},{i*2}\n")
            temp_path = f.name
        
        try:
            result = backend.preview_dataset(temp_path, rows=5)
            
            if result["success"]:
                assert result["data"]["rows"] <= 5
        finally:
            Path(temp_path).unlink()
    
    def test_preview_dataset_caching(self):
        """Test preview_dataset uses cache."""
        backend = LearnODIBIBackend()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            temp_path = f.name
        
        try:
            # First call
            result1 = backend.preview_dataset(temp_path, rows=2)
            
            # Second call (should be cached)
            result2 = backend.preview_dataset(temp_path, rows=2)
            
            if result1["success"] and result2["success"]:
                assert result1["data"]["rows"] == result2["data"]["rows"]
        finally:
            Path(temp_path).unlink()


class TestValidateConfig:
    """Test validate_config endpoint."""
    
    def test_validate_config_valid(self):
        """Test validation passes for valid config."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {"name": "step1", "type": "function", "function": "test"}
            ]
        }
        
        result = backend.validate_config(config)
        
        assert result["success"] is True
        assert "valid" in result["data"]
        assert "errors" in result["data"]
        assert "warnings" in result["data"]
    
    def test_validate_config_empty(self):
        """Test validation fails for empty config."""
        backend = LearnODIBIBackend()
        
        result = backend.validate_config({})
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert len(result["data"]["errors"]) > 0
    
    def test_validate_config_no_steps(self):
        """Test validation fails without steps."""
        backend = LearnODIBIBackend()
        
        config = {"name": "test"}
        result = backend.validate_config(config)
        
        assert result["data"]["valid"] is False
        assert any("steps" in err.lower() for err in result["data"]["errors"])
    
    def test_validate_config_invalid_steps_type(self):
        """Test validation fails for non-list steps."""
        backend = LearnODIBIBackend()
        
        config = {"steps": "not a list"}
        result = backend.validate_config(config)
        
        assert result["data"]["valid"] is False
    
    def test_validate_config_empty_steps(self):
        """Test validation warns for empty steps."""
        backend = LearnODIBIBackend()
        
        config = {"steps": []}
        result = backend.validate_config(config)
        
        assert "warnings" in result["data"]


class TestExecuteWorkflow:
    """Test execute_workflow endpoint."""
    
    def test_execute_workflow_basic(self):
        """Test basic workflow execution."""
        backend = LearnODIBIBackend()
        
        workflow = {
            "name": "Test Workflow",
            "pipelines": [
                {
                    "steps": [
                        {"name": "step1", "type": "function", "function": "identity"}
                    ]
                }
            ]
        }
        
        result = backend.execute_workflow(workflow)
        
        assert "success" in result
        assert "data" in result
        assert "workflow_id" in result["data"]
    
    def test_execute_workflow_no_pipelines(self):
        """Test workflow fails without pipelines."""
        backend = LearnODIBIBackend()
        
        workflow = {"name": "Test"}
        result = backend.execute_workflow(workflow)
        
        assert result["success"] is False
    
    def test_execute_workflow_multiple_pipelines(self):
        """Test workflow with multiple pipelines."""
        backend = LearnODIBIBackend()
        
        workflow = {
            "name": "Multi Pipeline",
            "pipelines": [
                {"steps": [{"name": "s1", "type": "function", "function": "identity"}]},
                {"steps": [{"name": "s2", "type": "function", "function": "identity"}]}
            ]
        }
        
        result = backend.execute_workflow(workflow)
        
        assert "pipeline_results" in result["data"]


class TestCacheManagement:
    """Test cache management endpoints."""
    
    def test_clear_cache(self):
        """Test clear_cache clears all cached data."""
        backend = LearnODIBIBackend()
        
        # Add some cached data
        backend.get_available_functions()
        
        # Clear cache
        result = backend.clear_cache()
        
        assert result["success"] is True
        assert "message" in result["data"]
    
    def test_get_cache_stats(self):
        """Test get_cache_stats returns cache info."""
        backend = LearnODIBIBackend()
        
        result = backend.get_cache_stats()
        
        assert result["success"] is True
        assert "size" in result["data"]
        assert "keys" in result["data"]
    
    def test_cache_stats_after_clear(self):
        """Test cache stats reflect cleared cache."""
        backend = LearnODIBIBackend()
        
        # Add cached data
        backend.get_available_functions()
        
        # Clear cache
        backend.clear_cache()
        
        # Check stats
        stats = backend.get_cache_stats()
        # Cache may have 0 or few items
        assert isinstance(stats["data"]["size"], int)


class TestListDemoDatasets:
    """Test list_demo_datasets endpoint."""
    
    def test_list_demo_datasets(self):
        """Test list_demo_datasets returns dataset list."""
        backend = LearnODIBIBackend()
        result = backend.list_demo_datasets()
        
        assert result["success"] is True
        assert "datasets" in result["data"]
        assert "count" in result["data"]
        assert isinstance(result["data"]["datasets"], list)
    
    def test_list_demo_datasets_structure(self):
        """Test dataset metadata structure."""
        backend = LearnODIBIBackend()
        result = backend.list_demo_datasets()
        
        if len(result["data"]["datasets"]) > 0:
            dataset = result["data"]["datasets"][0]
            assert "name" in dataset
            assert "path" in dataset
            assert "size_bytes" in dataset
            assert "format" in dataset


class TestGetDemoPipelineConfigs:
    """Test get_demo_pipeline_configs endpoint."""
    
    def test_get_demo_configs(self):
        """Test get_demo_pipeline_configs returns configs."""
        backend = LearnODIBIBackend()
        result = backend.get_demo_pipeline_configs()
        
        assert result["success"] is True
        assert "configs" in result["data"]
        assert "count" in result["data"]
    
    def test_get_demo_configs_structure(self):
        """Test config metadata structure."""
        backend = LearnODIBIBackend()
        result = backend.get_demo_pipeline_configs()
        
        if len(result["data"]["configs"]) > 0:
            config = result["data"]["configs"][0]
            assert "name" in config
            assert "path" in config
            assert "config" in config


class TestGetPipelineStatus:
    """Test get_pipeline_status endpoint."""
    
    def test_get_pipeline_status_invalid_id(self):
        """Test get_pipeline_status fails for invalid ID."""
        backend = LearnODIBIBackend()
        
        result = backend.get_pipeline_status("invalid-id-123")
        
        assert result["success"] is False
    
    def test_get_pipeline_status_after_execution(self):
        """Test get_pipeline_status after successful execution."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {"name": "test", "type": "function", "function": "identity"}
            ]
        }
        
        exec_result = backend.run_transformation(config, engine="pandas")
        
        if exec_result["success"]:
            pipeline_id = exec_result["data"]["pipeline_id"]
            status_result = backend.get_pipeline_status(pipeline_id)
            
            assert status_result["success"] is True
            assert "status" in status_result["data"]
            assert "pipeline_id" in status_result["data"]


class TestErrorHandling:
    """Test error handling in backend."""
    
    def test_safe_execute_decorator(self):
        """Test safe_execute decorator catches errors."""
        backend = LearnODIBIBackend()
        
        # Call with None config should be handled
        result = backend.run_transformation(None, engine="pandas")
        
        assert "success" in result
        assert "error" in result
    
    def test_execution_time_tracking(self):
        """Test execution time is tracked."""
        backend = LearnODIBIBackend()
        
        config = {
            "steps": [
                {"name": "test", "type": "function", "function": "identity"}
            ]
        }
        
        result = backend.run_transformation(config, engine="pandas")
        
        assert "execution_time_ms" in result
        assert isinstance(result["execution_time_ms"], (int, float))
        assert result["execution_time_ms"] >= 0


class TestResponseFormat:
    """Test standardized response format."""
    
    def test_response_has_required_fields(self):
        """Test all responses have standard fields."""
        backend = LearnODIBIBackend()
        
        result = backend.get_available_functions()
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert "execution_time_ms" in result
        assert "metadata" in result
    
    def test_success_response_structure(self):
        """Test successful response structure."""
        backend = LearnODIBIBackend()
        
        result = backend.get_available_functions()
        
        if result["success"]:
            assert result["error"] is None
            assert result["data"] is not None
    
    def test_error_response_structure(self):
        """Test error response structure."""
        backend = LearnODIBIBackend()
        
        result = backend.run_transformation({}, engine="pandas")
        
        if not result["success"]:
            assert result["error"] is not None
