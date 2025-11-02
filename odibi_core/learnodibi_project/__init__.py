"""
ODIBI CORE Learn Project - Bronze → Silver → Gold Demo

A complete demonstration of the medallion architecture using ODIBI CORE.
Shows data ingestion, transformation, aggregation, and publishing in a
config-driven pipeline.

Quick Start:
    >>> from odibi_core.learnodibi_project import DemoPipeline
    >>>
    >>> # Run full pipeline
    >>> pipeline = DemoPipeline()
    >>> result = pipeline.run_full()
    >>> print(result.summary())

Layer-by-Layer Execution:
    >>> # Bronze only (ingestion)
    >>> result = pipeline.run_bronze()
    >>>
    >>> # Bronze + Silver (transformation)
    >>> result = pipeline.run_silver()
    >>>
    >>> # Bronze + Silver + Gold (aggregation)
    >>> result = pipeline.run_gold()

Configuration Inspection:
    >>> from odibi_core.learnodibi_project import get_pipeline_config
    >>>
    >>> # Get bronze layer config
    >>> config = get_pipeline_config("bronze")
    >>> print(config[0]['name'])  # read_energy_data

Pipeline Architecture:
    Bronze Layer (Ingestion):
        - Read energy_demo.csv → bronze_energy
        - Read weather_demo.csv → bronze_weather
        - Read maintenance_demo.csv → bronze_maintenance

    Silver Layer (Transformation):
        - Clean energy data (nulls, outliers) → silver_energy
        - Join energy + weather → silver_energy_weather
        - Clean maintenance data → silver_maintenance

    Gold Layer (Aggregation):
        - Daily aggregation by facility → gold_daily_summary
        - Calculate efficiency metrics → gold_efficiency_report
        - Maintenance cost analysis → gold_maintenance_costs

    Publish Layer (Output):
        - Save to Parquet, JSON, CSV

Features Demonstrated:
    • Config-driven pipeline execution
    • Medallion architecture (Bronze/Silver/Gold)
    • SQL transformations with Pandas engine
    • Multi-source data ingestion
    • Data quality rules (null checks, range validation)
    • Inner joins across datasets
    • Business aggregations and KPIs
    • Multiple output formats (Parquet, JSON, CSV)
    • Tracker-based lineage and metrics
    • Event-driven execution monitoring

Configuration Files:
    - bronze_config.json: Ingestion only
    - silver_config.json: Ingestion + transformation
    - gold_config.json: Ingestion + transformation + aggregation
    - full_pipeline_config.json: Complete end-to-end pipeline

Example - Custom Engine:
    >>> # Use Spark instead of Pandas
    >>> pipeline = DemoPipeline(engine="spark")
    >>> result = pipeline.run_full()

Example - Get Pipeline Description:
    >>> pipeline = DemoPipeline()
    >>> print(pipeline.describe())

Example - Access Output Data:
    >>> result = pipeline.run_gold()
    >>> efficiency_df = result.data_map['gold_efficiency_report']
    >>> print(efficiency_df.head())
"""

from .demo_pipeline import DemoPipeline, get_pipeline_config

__all__ = ["DemoPipeline", "get_pipeline_config"]
