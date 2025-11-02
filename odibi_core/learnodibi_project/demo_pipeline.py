"""
ODIBI CORE Demo Pipeline - Bronze → Silver → Gold

Demonstrates a complete medallion architecture pipeline with:
- Bronze Layer: Raw data ingestion (energy, weather, maintenance)
- Silver Layer: Data cleaning and enrichment (joins, filters)
- Gold Layer: Business aggregations and KPIs

Example:
    >>> from odibi_core.learnodibi_project import DemoPipeline
    >>> pipeline = DemoPipeline()
    >>> result = pipeline.run_full()
    >>> print(result.summary())
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from odibi_core.core import (
    ConfigLoader,
    ConfigValidator,
    Orchestrator,
    Tracker,
    EventEmitter,
    create_engine_context,
)

logger = logging.getLogger(__name__)


class DemoPipeline:
    """
    Demonstration pipeline showcasing Bronze → Silver → Gold architecture.

    The pipeline processes energy facility data through three layers:
    - Bronze: Ingest raw CSV files (energy, weather, maintenance)
    - Silver: Clean, validate, and join datasets
    - Gold: Calculate business metrics and efficiency KPIs

    Example:
        >>> # Run full pipeline
        >>> pipeline = DemoPipeline()
        >>> result = pipeline.run_full()
        >>> print(f"Produced {len(result.data_map)} datasets")

        >>> # Run only bronze layer
        >>> result = pipeline.run_bronze()

        >>> # Run bronze + silver
        >>> result = pipeline.run_silver()

        >>> # Run bronze + silver + gold
        >>> result = pipeline.run_gold()
    """

    def __init__(
        self,
        engine: str = "pandas",
        enable_tracking: bool = True,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize demo pipeline.

        Args:
            engine: Execution engine ("pandas" or "spark")
            enable_tracking: Enable tracker for lineage and metrics
            output_dir: Custom output directory (defaults to learnodibi_project/output)
        """
        self.engine = engine
        self.enable_tracking = enable_tracking

        # Paths
        self.module_dir = Path(__file__).parent
        self.output_dir = (
            Path(output_dir) if output_dir else self.module_dir / "output"
        )
        self.output_dir.mkdir(exist_ok=True)

        # Config paths
        self.bronze_config = self.module_dir / "bronze_config.json"
        self.silver_config = self.module_dir / "silver_config.json"
        self.gold_config = self.module_dir / "gold_config.json"
        self.full_config = self.module_dir / "full_pipeline_config.json"

        logger.info(f"DemoPipeline initialized with engine={engine}")

    def run_bronze(self) -> Any:
        """
        Run Bronze layer only (ingestion).

        Reads:
            - energy_demo.csv → bronze_energy
            - weather_demo.csv → bronze_weather
            - maintenance_demo.csv → bronze_maintenance

        Returns:
            PipelineResult with bronze datasets

        Example:
            >>> pipeline = DemoPipeline()
            >>> result = pipeline.run_bronze()
            >>> print(result.data_map.keys())
            dict_keys(['bronze_energy', 'bronze_weather', 'bronze_maintenance'])
        """
        logger.info("Running Bronze Layer (Ingestion)")
        return self._run_config(self.bronze_config, "Bronze")

    def run_silver(self) -> Any:
        """
        Run Bronze + Silver layers (ingestion + transformation).

        Produces:
            - silver_energy (cleaned)
            - silver_energy_weather (joined with weather)
            - silver_maintenance (cleaned)

        Returns:
            PipelineResult with bronze and silver datasets

        Example:
            >>> pipeline = DemoPipeline()
            >>> result = pipeline.run_silver()
            >>> silver_data = result.data_map['silver_energy_weather']
        """
        logger.info("Running Bronze + Silver Layers (Ingestion + Transformation)")
        return self._run_config(self.silver_config, "Silver")

    def run_gold(self) -> Any:
        """
        Run Bronze + Silver + Gold layers (full pipeline without publishing).

        Produces:
            - gold_daily_summary (facility aggregations)
            - gold_efficiency_report (KPIs)
            - gold_maintenance_costs (cost analysis)

        Returns:
            PipelineResult with all datasets

        Example:
            >>> pipeline = DemoPipeline()
            >>> result = pipeline.run_gold()
            >>> efficiency = result.data_map['gold_efficiency_report']
        """
        logger.info("Running Bronze + Silver + Gold Layers (Full Aggregation)")
        return self._run_config(self.gold_config, "Gold")

    def run_full(self) -> Any:
        """
        Run complete Bronze → Silver → Gold pipeline with publishing.

        Executes all layers and saves outputs:
            - gold_daily_summary.parquet
            - gold_efficiency_report.json
            - gold_maintenance_costs.csv

        Returns:
            PipelineResult with all datasets and saved files

        Example:
            >>> pipeline = DemoPipeline()
            >>> result = pipeline.run_full()
            >>> print(result.summary())
        """
        logger.info("Running Full Pipeline (Bronze → Silver → Gold + Publish)")
        return self._run_config(self.full_config, "Full")

    def _run_config(self, config_path: Path, layer_name: str) -> Any:
        """
        Execute pipeline from config file.

        Args:
            config_path: Path to JSON config
            layer_name: Layer name for logging

        Returns:
            PipelineResult from orchestrator
        """
        logger.info(f"Loading config: {config_path}")

        # Load and validate config
        loader = ConfigLoader()
        steps = loader.load(str(config_path))

        validator = ConfigValidator()
        validator.validate_config(steps)

        logger.info(f"Loaded {len(steps)} steps, validation passed")

        # Create engine context
        context = create_engine_context(self.engine)
        context.connect()

        # Create tracker and events
        tracker = None
        events = EventEmitter()

        if self.enable_tracking:
            tracker = Tracker(log_dir=str(self.output_dir / "tracker_logs"))
            events.on(
                "step_complete",
                lambda step, duration_ms: logger.info(
                    f"✓ {step.name} ({duration_ms:.2f}ms)"
                ),
            )

        # Execute pipeline
        orchestrator = Orchestrator(steps, context, tracker, events)
        result = orchestrator.run()

        logger.info(
            f"{layer_name} layer complete: {len(result.data_map)} datasets produced"
        )

        # Save tracker if enabled
        if tracker:
            log_path = tracker.save()
            logger.info(f"Tracker logs saved: {log_path}")

        return result

    def get_config(self, layer: str) -> Dict[str, Any]:
        """
        Get configuration for a specific layer.

        Args:
            layer: "bronze", "silver", "gold", or "full"

        Returns:
            Dictionary containing config steps

        Example:
            >>> pipeline = DemoPipeline()
            >>> config = pipeline.get_config("bronze")
            >>> print(config[0]['name'])
            read_energy_data
        """
        import json

        config_map = {
            "bronze": self.bronze_config,
            "silver": self.silver_config,
            "gold": self.gold_config,
            "full": self.full_config,
        }

        if layer not in config_map:
            raise ValueError(
                f"Invalid layer '{layer}'. Choose: bronze, silver, gold, full"
            )

        with open(config_map[layer], "r") as f:
            return json.load(f)

    def describe(self) -> str:
        """
        Get pipeline description.

        Returns:
            Formatted string describing the pipeline architecture

        Example:
            >>> pipeline = DemoPipeline()
            >>> print(pipeline.describe())
        """
        return """
ODIBI CORE Demo Pipeline - Medallion Architecture
==================================================

BRONZE LAYER (Ingestion)
  • read_energy_data      → bronze_energy
  • read_weather_data     → bronze_weather
  • read_maintenance_data → bronze_maintenance

SILVER LAYER (Transformation)
  • clean_energy_data         → silver_energy
  • join_energy_weather       → silver_energy_weather
  • clean_maintenance_data    → silver_maintenance

GOLD LAYER (Aggregation)
  • aggregate_daily_by_facility    → gold_daily_summary
  • calculate_efficiency_metrics   → gold_efficiency_report
  • analyze_maintenance_costs      → gold_maintenance_costs

PUBLISH LAYER (Output)
  • save_daily_summary       → gold_daily_summary.parquet
  • save_efficiency_report   → gold_efficiency_report.json
  • save_maintenance_costs   → gold_maintenance_costs.csv

Usage:
  pipeline = DemoPipeline()
  result = pipeline.run_full()  # Run all layers
  result = pipeline.run_bronze()  # Bronze only
  result = pipeline.run_silver()  # Bronze + Silver
  result = pipeline.run_gold()    # Bronze + Silver + Gold
        """.strip()


def get_pipeline_config(layer: str) -> Dict[str, Any]:
    """
    Get pipeline configuration for a specific layer.

    Args:
        layer: "bronze", "silver", "gold", or "full"

    Returns:
        JSON configuration as dictionary

    Example:
        >>> from odibi_core.learnodibi_project import get_pipeline_config
        >>> config = get_pipeline_config("bronze")
        >>> print(f"Bronze has {len(config)} steps")
    """
    pipeline = DemoPipeline()
    return pipeline.get_config(layer)
