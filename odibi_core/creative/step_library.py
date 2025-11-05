"""
Step Library - Composable Pipeline Fragments
=============================================
Provides reusable step fragments for building realistic pipelines.
"""

from typing import List, Dict, Any


class StepLibrary:
    """Library of composable step fragments."""
    
    @staticmethod
    def ingest_csv(name: str, source: str, layer: str = "bronze") -> Dict[str, Any]:
        """CSV ingestion step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "read",
            "engine": "pandas",
            "source_type": "csv",
            "source": source,
            "dependencies": []
        }
    
    @staticmethod
    def ingest_json(name: str, source: str, layer: str = "bronze") -> Dict[str, Any]:
        """JSON ingestion step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "read",
            "engine": "pandas",
            "source_type": "json",
            "source": source,
            "dependencies": []
        }
    
    @staticmethod
    def ingest_parquet(name: str, source: str, layer: str = "bronze") -> Dict[str, Any]:
        """Parquet ingestion step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "read",
            "engine": "pandas",
            "source_type": "parquet",
            "source": source,
            "dependencies": []
        }
    
    @staticmethod
    def ingest_avro(name: str, source: str, layer: str = "bronze") -> Dict[str, Any]:
        """Avro ingestion step (simulated)."""
        return {
            "name": name,
            "layer": layer,
            "operation": "read",
            "engine": "pandas",
            "source_type": "avro",
            "source": source,
            "dependencies": []
        }
    
    @staticmethod
    def merge(name: str, dependencies: List[str], layer: str = "silver") -> Dict[str, Any]:
        """Merge multiple sources."""
        return {
            "name": name,
            "layer": layer,
            "operation": "merge",
            "engine": "pandas",
            "dependencies": dependencies
        }
    
    @staticmethod
    def transform(name: str, dependencies: List[str], transform_type: str = "calculate", layer: str = "silver") -> Dict[str, Any]:
        """Generic transformation step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "transform",
            "engine": "pandas",
            "transform_type": transform_type,
            "dependencies": dependencies
        }
    
    @staticmethod
    def validate(name: str, dependencies: List[str], layer: str = "gold") -> Dict[str, Any]:
        """Validation step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "validate",
            "engine": "pandas",
            "dependencies": dependencies
        }
    
    @staticmethod
    def cache(name: str, dependencies: List[str], layer: str = "gold") -> Dict[str, Any]:
        """Cache step for performance."""
        return {
            "name": name,
            "layer": layer,
            "operation": "cache",
            "engine": "pandas",
            "dependencies": dependencies
        }
    
    @staticmethod
    def aggregate(name: str, dependencies: List[str], window: str = "1d", layer: str = "gold") -> Dict[str, Any]:
        """Windowed aggregation step."""
        return {
            "name": name,
            "layer": layer,
            "operation": "aggregate",
            "engine": "pandas",
            "window": window,
            "dependencies": dependencies
        }
    
    @staticmethod
    def branch_parallel(base_name: str, dependencies: List[str], count: int = 2, layer: str = "silver") -> List[Dict[str, Any]]:
        """Create parallel branch steps."""
        return [
            {
                "name": f"{base_name}_parallel_{i+1}",
                "layer": layer,
                "operation": "transform",
                "engine": "pandas",
                "transform_type": "parallel_branch",
                "dependencies": dependencies
            }
            for i in range(count)
        ]
    
    @staticmethod
    def publish(name: str, dependencies: List[str], format: str = "parquet", layer: str = "gold") -> Dict[str, Any]:
        """Publish final output."""
        return {
            "name": name,
            "layer": layer,
            "operation": "write",
            "engine": "pandas",
            "target_format": format,
            "dependencies": dependencies
        }
