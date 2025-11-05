"""
Graph Builder - DAG Construction from Archetypes
=================================================
Builds realistic pipeline DAGs from scenario specs.
"""

import hashlib
import json
from typing import List, Dict, Any, Tuple
from .step_library import StepLibrary
from .scenario_spec import ScenarioSpec


class GraphBuilder:
    """Builds DAGs from archetypes and scenario specs."""
    
    ARCHETYPES = {
        "multi_source_conformance": {
            "topology": "FanIn",
            "complexity": "moderate",
            "description": "Merge multiple sources with schema standardization"
        },
        "star_schema": {
            "topology": "Star",
            "complexity": "high",
            "description": "Build star schema with dimensions and fact table"
        },
        "windowed_kpi": {
            "topology": "Linear",
            "complexity": "moderate",
            "description": "Time-windowed KPI aggregation with validation"
        },
        "quality_branch": {
            "topology": "Diamond",
            "complexity": "high",
            "description": "Data quality validation with quarantine branch"
        },
        "parallel_transform": {
            "topology": "Parallel",
            "complexity": "moderate",
            "description": "Independent parallel transformations"
        },
        "hierarchical_agg": {
            "topology": "FanOut",
            "complexity": "high",
            "description": "Hierarchical aggregations at multiple levels"
        },
        "scd2_merge": {
            "topology": "Diamond",
            "complexity": "high",
            "description": "Slowly Changing Dimension Type 2 merge"
        },
        "streaming_enrich": {
            "topology": "FanIn",
            "complexity": "extreme",
            "description": "Stream enrichment with multiple lookups"
        },
        "geo_segmentation": {
            "topology": "Linear",
            "complexity": "moderate",
            "description": "Geographic segmentation and proximity analysis"
        },
        "anomaly_detection": {
            "topology": "Diamond",
            "complexity": "high",
            "description": "Time series anomaly detection with alerting"
        }
    }
    
    def __init__(self):
        self.lib = StepLibrary()
    
    def build(self, spec: ScenarioSpec) -> Tuple[List[Dict[str, Any]], str]:
        """
        Build pipeline steps from scenario spec.
        Returns: (steps, dag_signature)
        """
        archetype = spec.archetype
        formats = list(spec.formats)
        
        if archetype == "multi_source_conformance":
            steps = self._build_fan_in(spec, formats)
        elif archetype == "star_schema":
            steps = self._build_star_schema(spec, formats)
        elif archetype == "windowed_kpi":
            steps = self._build_windowed_kpi(spec, formats)
        elif archetype == "quality_branch":
            steps = self._build_quality_branch(spec, formats)
        elif archetype == "parallel_transform":
            steps = self._build_parallel_transform(spec, formats)
        elif archetype == "hierarchical_agg":
            steps = self._build_hierarchical_agg(spec, formats)
        elif archetype == "scd2_merge":
            steps = self._build_scd2_merge(spec, formats)
        elif archetype == "streaming_enrich":
            steps = self._build_streaming_enrich(spec, formats)
        elif archetype == "geo_segmentation":
            steps = self._build_geo_segmentation(spec, formats)
        elif archetype == "anomaly_detection":
            steps = self._build_anomaly_detection(spec, formats)
        else:
            steps = self._build_simple_linear(spec, formats)
        
        dag_signature = self._compute_dag_signature(steps)
        
        return steps, dag_signature
    
    def _build_fan_in(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build fan-in merge pattern."""
        steps = []
        ingests = []
        
        # Ingest from multiple sources
        for i, fmt in enumerate(formats[:3], 1):
            name = f"ingest_{fmt.lower()}_{i}"
            if fmt == "CSV":
                steps.append(self.lib.ingest_csv(name, f"source_{i}.csv"))
            elif fmt == "JSON":
                steps.append(self.lib.ingest_json(name, f"source_{i}.json"))
            elif fmt == "PARQUET":
                steps.append(self.lib.ingest_parquet(name, f"source_{i}.parquet"))
            else:
                steps.append(self.lib.ingest_avro(name, f"source_{i}.avro"))
            ingests.append(name)
        
        # Merge all sources
        steps.append(self.lib.merge("merge_sources", ingests, "silver"))
        
        # Transform
        steps.append(self.lib.transform("standardize_schema", ["merge_sources"], "standardize", "silver"))
        
        # Validate
        if spec.complexity_level != "moderate":
            steps.append(self.lib.validate("validate_quality", ["standardize_schema"], "gold"))
            deps = ["validate_quality"]
        else:
            deps = ["standardize_schema"]
        
        # Cache if performance enabled
        if spec.perf.get("cache_enabled"):
            steps.append(self.lib.cache("cache_merged", deps, "gold"))
            deps = ["cache_merged"]
        
        # Publish
        steps.append(self.lib.publish("publish_final", deps, "parquet", "gold"))
        
        return steps
    
    def _build_star_schema(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build star schema pattern."""
        steps = []
        
        # Ingest dimensions
        dims = []
        for i, entity in enumerate(spec.entities[:3], 1):
            name = f"ingest_dim_{entity}"
            steps.append(self.lib.ingest_csv(name, f"{entity}_dim.csv", "bronze"))
            steps.append(self.lib.transform(f"transform_dim_{entity}", [name], "scd2", "silver"))
            dims.append(f"transform_dim_{entity}")
        
        # Ingest fact
        steps.append(self.lib.ingest_parquet("ingest_fact", "fact_table.parquet", "bronze"))
        
        # Join fact with dimensions
        all_deps = dims + ["ingest_fact"]
        steps.append(self.lib.merge("join_star", all_deps, "silver"))
        
        # Aggregate
        window = list(spec.windows.values())[0] if spec.windows else "1d"
        steps.append(self.lib.aggregate("aggregate_kpis", ["join_star"], window, "gold"))
        
        # Validate
        steps.append(self.lib.validate("validate_star", ["aggregate_kpis"], "gold"))
        
        # Publish
        steps.append(self.lib.publish("publish_star", ["validate_star"], "parquet", "gold"))
        
        return steps
    
    def _build_windowed_kpi(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build windowed KPI aggregation."""
        steps = []
        
        # Ingest
        fmt = formats[0] if formats else "CSV"
        if fmt == "CSV":
            steps.append(self.lib.ingest_csv("ingest_events", "events.csv", "bronze"))
        else:
            steps.append(self.lib.ingest_parquet("ingest_events", "events.parquet", "bronze"))
        
        # Deduplicate
        steps.append(self.lib.transform("dedupe_events", ["ingest_events"], "deduplicate", "silver"))
        
        # Window aggregation
        window = list(spec.windows.values())[0] if spec.windows else "1h"
        steps.append(self.lib.aggregate("window_agg", ["dedupe_events"], window, "silver"))
        
        # Calculate KPIs
        for i, kpi in enumerate(spec.kpis[:2], 1):
            deps = ["window_agg"] if i == 1 else [f"calculate_kpi_{i-1}"]
            steps.append(self.lib.transform(f"calculate_kpi_{i}", deps, "calculate", "silver"))
        
        # Validate
        last_kpi = f"calculate_kpi_{min(len(spec.kpis[:2]), 2)}"
        steps.append(self.lib.validate("validate_kpis", [last_kpi], "gold"))
        
        # Publish
        steps.append(self.lib.publish("publish_kpis", ["validate_kpis"], "parquet", "gold"))
        
        return steps
    
    def _build_quality_branch(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build quality validation with branch."""
        steps = []
        
        # Ingest
        steps.append(self.lib.ingest_csv("ingest_raw", "raw_data.csv", "bronze"))
        
        # Initial transform
        steps.append(self.lib.transform("transform_raw", ["ingest_raw"], "standardize", "silver"))
        
        # Quality validation (diamond pattern)
        steps.append(self.lib.validate("validate_quality", ["transform_raw"], "silver"))
        
        # Good path
        steps.append(self.lib.transform("process_valid", ["validate_quality"], "enrich", "gold"))
        
        # Quarantine path
        steps.append(self.lib.transform("quarantine_invalid", ["validate_quality"], "quarantine", "gold"))
        
        # Publish valid
        steps.append(self.lib.publish("publish_valid", ["process_valid"], "parquet", "gold"))
        
        # Publish quarantine
        steps.append(self.lib.publish("publish_quarantine", ["quarantine_invalid"], "csv", "gold"))
        
        return steps
    
    def _build_parallel_transform(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build parallel transformation pattern."""
        steps = []
        
        # Ingest
        steps.append(self.lib.ingest_csv("ingest_source", "source.csv", "bronze"))
        
        # Parallel branches
        parallel_steps = self.lib.branch_parallel("transform", ["ingest_source"], 3, "silver")
        steps.extend(parallel_steps)
        
        # Merge parallel results
        parallel_names = [s["name"] for s in parallel_steps]
        steps.append(self.lib.merge("merge_parallel", parallel_names, "gold"))
        
        # Validate
        steps.append(self.lib.validate("validate_merged", ["merge_parallel"], "gold"))
        
        # Publish
        steps.append(self.lib.publish("publish_final", ["validate_merged"], "parquet", "gold"))
        
        return steps
    
    def _build_hierarchical_agg(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build hierarchical aggregation."""
        steps = []
        
        # Ingest
        steps.append(self.lib.ingest_parquet("ingest_detail", "detail.parquet", "bronze"))
        
        # Level 1 - Detailed
        steps.append(self.lib.aggregate("agg_level1", ["ingest_detail"], "1h", "silver"))
        
        # Level 2 - Mid
        steps.append(self.lib.aggregate("agg_level2", ["agg_level1"], "1d", "silver"))
        
        # Level 3 - Summary
        steps.append(self.lib.aggregate("agg_level3", ["agg_level2"], "7d", "gold"))
        
        # Publish all levels
        steps.append(self.lib.publish("publish_level1", ["agg_level1"], "parquet", "gold"))
        steps.append(self.lib.publish("publish_level2", ["agg_level2"], "parquet", "gold"))
        steps.append(self.lib.publish("publish_level3", ["agg_level3"], "parquet", "gold"))
        
        return steps
    
    def _build_scd2_merge(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build SCD Type 2 merge pattern."""
        steps = []
        
        # Ingest current dimension
        steps.append(self.lib.ingest_csv("ingest_current_dim", "current.csv", "bronze"))
        
        # Ingest new records
        steps.append(self.lib.ingest_csv("ingest_new_records", "new.csv", "bronze"))
        
        # SCD2 merge
        steps.append(self.lib.transform("scd2_merge", ["ingest_current_dim", "ingest_new_records"], "scd2", "silver"))
        
        # Validate
        steps.append(self.lib.validate("validate_scd2", ["scd2_merge"], "gold"))
        
        # Publish
        steps.append(self.lib.publish("publish_dimension", ["validate_scd2"], "parquet", "gold"))
        
        return steps
    
    def _build_streaming_enrich(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build streaming enrichment pattern."""
        steps = []
        
        # Ingest stream
        steps.append(self.lib.ingest_json("ingest_stream", "stream.json", "bronze"))
        
        # Ingest lookups
        lookups = []
        for i, entity in enumerate(spec.entities[:3], 1):
            name = f"ingest_lookup_{entity}"
            steps.append(self.lib.ingest_csv(name, f"{entity}_lookup.csv", "bronze"))
            lookups.append(name)
        
        # Enrich stream with lookups
        all_deps = ["ingest_stream"] + lookups
        steps.append(self.lib.merge("enrich_stream", all_deps, "silver"))
        
        # Transform
        steps.append(self.lib.transform("transform_enriched", ["enrich_stream"], "calculate", "silver"))
        
        # Validate
        steps.append(self.lib.validate("validate_stream", ["transform_enriched"], "gold"))
        
        # Cache
        if spec.perf.get("cache_enabled"):
            steps.append(self.lib.cache("cache_enriched", ["validate_stream"], "gold"))
            deps = ["cache_enriched"]
        else:
            deps = ["validate_stream"]
        
        # Publish
        steps.append(self.lib.publish("publish_enriched", deps, "parquet", "gold"))
        
        return steps
    
    def _build_geo_segmentation(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build geographic segmentation."""
        steps = []
        
        # Ingest location data
        steps.append(self.lib.ingest_csv("ingest_locations", "locations.csv", "bronze"))
        
        # Geohash
        steps.append(self.lib.transform("geohash_locations", ["ingest_locations"], "geohash", "silver"))
        
        # Segment by region
        steps.append(self.lib.transform("segment_regions", ["geohash_locations"], "segment", "silver"))
        
        # Aggregate by segment
        window = list(spec.windows.values())[0] if spec.windows else "1d"
        steps.append(self.lib.aggregate("aggregate_segments", ["segment_regions"], window, "gold"))
        
        # Validate
        steps.append(self.lib.validate("validate_geo", ["aggregate_segments"], "gold"))
        
        # Publish
        steps.append(self.lib.publish("publish_geo", ["validate_geo"], "parquet", "gold"))
        
        return steps
    
    def _build_anomaly_detection(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build anomaly detection pattern."""
        steps = []
        
        # Ingest time series
        steps.append(self.lib.ingest_parquet("ingest_timeseries", "timeseries.parquet", "bronze"))
        
        # Window aggregation
        window = list(spec.windows.values())[0] if spec.windows else "1h"
        steps.append(self.lib.aggregate("window_stats", ["ingest_timeseries"], window, "silver"))
        
        # Calculate baseline
        steps.append(self.lib.transform("calculate_baseline", ["window_stats"], "baseline", "silver"))
        
        # Detect anomalies
        steps.append(self.lib.transform("detect_anomalies", ["calculate_baseline"], "anomaly_detection", "silver"))
        
        # Branch: normal vs anomaly
        steps.append(self.lib.transform("process_normal", ["detect_anomalies"], "filter_normal", "gold"))
        steps.append(self.lib.transform("flag_anomalies", ["detect_anomalies"], "filter_anomaly", "gold"))
        
        # Publish both paths
        steps.append(self.lib.publish("publish_normal", ["process_normal"], "parquet", "gold"))
        steps.append(self.lib.publish("publish_anomalies", ["flag_anomalies"], "json", "gold"))
        
        return steps
    
    def _build_simple_linear(self, spec: ScenarioSpec, formats: List[str]) -> List[Dict[str, Any]]:
        """Build simple linear pipeline."""
        steps = []
        
        fmt = formats[0] if formats else "CSV"
        if fmt == "CSV":
            steps.append(self.lib.ingest_csv("ingest_data", "data.csv", "bronze"))
        else:
            steps.append(self.lib.ingest_parquet("ingest_data", "data.parquet", "bronze"))
        
        steps.append(self.lib.transform("transform_data", ["ingest_data"], "calculate", "silver"))
        steps.append(self.lib.validate("validate_data", ["transform_data"], "gold"))
        steps.append(self.lib.publish("publish_data", ["validate_data"], "parquet", "gold"))
        
        return steps
    
    def _compute_dag_signature(self, steps: List[Dict[str, Any]]) -> str:
        """Compute DAG signature for pattern analysis."""
        # Extract topology info
        layers = {}
        for step in steps:
            layer = step.get("layer", "unknown")
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(step["operation"])
        
        # Build signature
        layer_order = ["bronze", "silver", "gold"]
        sig_parts = []
        sig_parts.append(f"layers:{len(layers)}")
        
        # Node counts by layer
        degrees = [len(layers.get(l, [])) for l in layer_order if l in layers]
        sig_parts.append(f"deg:{'-'.join(map(str, degrees))}")
        
        # Operation types
        ops = [s["operation"] for s in steps]
        sig_parts.append(f"types:{','.join(sorted(set(ops)))}")
        
        # Hash it
        sig_str = "|".join(sig_parts)
        return hashlib.sha1(sig_str.encode()).hexdigest()[:12]
