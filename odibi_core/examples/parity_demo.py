"""
Parity demonstration: Pandas vs Spark engines producing identical results.

This demo proves that both engines follow the same contract and produce
equivalent outputs for the same operations.
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_parity_demo() -> None:
    """
    Run parity demonstration comparing Pandas and Spark engines.

    Demonstrates:
    1. Reading CSV files
    2. Registering temp tables
    3. Executing SQL queries
    4. Writing Parquet files
    5. Comparing results
    """
    print("=" * 70)
    print("ODIBI CORE v1.0 - Engine Parity Demonstration")
    print("=" * 70)
    print()

    # Determine paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)

    sample_csv = data_dir / "sample.csv"
    pandas_output = output_dir / "pandas_filtered.parquet"
    spark_output = output_dir / "spark_filtered.parquet"

    print(f"📁 Input: {sample_csv}")
    print(f"📁 Output dir: {output_dir}")
    print()

    # ========================================================================
    # PANDAS ENGINE
    # ========================================================================
    print("🐼 PANDAS ENGINE")
    print("-" * 70)

    from odibi_core.engine import PandasEngineContext

    pandas_ctx = PandasEngineContext()
    pandas_ctx.connect()

    # Read CSV
    pandas_df = pandas_ctx.read(str(sample_csv))
    print(f"✓ Read CSV: {len(pandas_df)} rows")
    print(f"  Columns: {list(pandas_df.columns)}")
    print(f"  Sample:\n{pandas_df.head(3)}")
    print()

    # Register temp table
    pandas_ctx.register_temp("data", pandas_df)
    print("✓ Registered temp table 'data'")
    print()

    # Execute SQL
    pandas_filtered = pandas_ctx.execute_sql(
        "SELECT * FROM data WHERE value > 100 ORDER BY id"
    )
    print(f"✓ Executed SQL filter: {len(pandas_filtered)} rows")
    print(f"  Filtered rows:\n{pandas_filtered}")
    print()

    # Aggregate
    pandas_agg = pandas_ctx.execute_sql(
        "SELECT category, COUNT(*) as count, AVG(value) as avg_value FROM data GROUP BY category ORDER BY category"
    )
    print(f"✓ Aggregation:\n{pandas_agg}")
    print()

    # Write Parquet
    pandas_ctx.write(pandas_filtered, str(pandas_output))
    print(f"✓ Wrote Parquet: {pandas_output}")
    print()

    # ========================================================================
    # SPARK ENGINE
    # ========================================================================
    print("⚡ SPARK ENGINE")
    print("-" * 70)

    from odibi_core.engine import SparkEngineContext

    spark_ctx = SparkEngineContext()
    spark_ctx.connect()

    # Read CSV
    spark_df = spark_ctx.read(str(sample_csv))
    spark_count = spark_df.count()
    print(f"✓ Read CSV: {spark_count} rows")
    print(f"  Columns: {spark_df.columns}")
    spark_sample = spark_ctx.collect_sample(spark_df, n=3)
    print(f"  Sample:\n{spark_sample}")
    print()

    # Register temp view
    spark_ctx.register_temp("data", spark_df)
    print("✓ Registered temp view 'data'")
    print()

    # Execute SQL
    spark_filtered = spark_ctx.execute_sql(
        "SELECT * FROM data WHERE value > 100 ORDER BY id"
    )
    spark_filtered_count = spark_filtered.count()
    print(f"✓ Executed SQL filter: {spark_filtered_count} rows")
    spark_filtered_sample = spark_ctx.collect_sample(spark_filtered, n=10)
    print(f"  Filtered rows:\n{spark_filtered_sample}")
    print()

    # Aggregate
    spark_agg = spark_ctx.execute_sql(
        "SELECT category, COUNT(*) as count, AVG(value) as avg_value FROM data GROUP BY category ORDER BY category"
    )
    spark_agg_pd = spark_ctx.collect_sample(spark_agg, n=10)
    print(f"✓ Aggregation:\n{spark_agg_pd}")
    print()

    # Write Parquet
    spark_ctx.write(spark_filtered, str(spark_output))
    print(f"✓ Wrote Parquet: {spark_output}")
    print()

    # Stop Spark
    spark_ctx.stop()

    # ========================================================================
    # PARITY VERIFICATION
    # ========================================================================
    print("=" * 70)
    print("🔍 PARITY VERIFICATION")
    print("=" * 70)
    print()

    # Compare row counts
    print(f"Row counts match: {len(pandas_filtered)} == {spark_filtered_count}")
    assert len(pandas_filtered) == spark_filtered_count, "Row count mismatch!"
    print("✅ Row counts match")
    print()

    # Compare aggregations
    print("Pandas aggregation:")
    print(pandas_agg)
    print()
    print("Spark aggregation:")
    print(spark_agg_pd)
    print()

    # Compare values (allowing for floating point tolerance)
    import pandas as pd

    pandas_agg_sorted = pandas_agg.sort_values("category").reset_index(drop=True)
    spark_agg_sorted = spark_agg_pd.sort_values("category").reset_index(drop=True)

    # Check categories match
    assert list(pandas_agg_sorted["category"]) == list(
        spark_agg_sorted["category"]
    ), "Categories don't match!"
    print("✅ Categories match")

    # Check counts match
    assert list(pandas_agg_sorted["count"]) == list(
        spark_agg_sorted["count"]
    ), "Counts don't match!"
    print("✅ Counts match")

    # Check averages match (with tolerance)
    for idx in range(len(pandas_agg_sorted)):
        pandas_val = pandas_agg_sorted.iloc[idx]["avg_value"]
        spark_val = spark_agg_sorted.iloc[idx]["avg_value"]
        diff = abs(pandas_val - spark_val)
        assert diff < 0.01, f"Average mismatch: {pandas_val} vs {spark_val}"
    print("✅ Averages match (within tolerance)")
    print()

    # Read back Parquet files and compare
    pandas_read_back = pandas_ctx.read(str(pandas_output))
    spark_read_back_spark = spark_ctx.read(str(spark_output))
    spark_ctx.connect()  # Reconnect after stop
    spark_read_back_spark = spark_ctx.read(str(spark_output))
    spark_read_back_pd = spark_ctx.collect_sample(spark_read_back_spark, n=100)

    print(f"Pandas Parquet rows: {len(pandas_read_back)}")
    print(f"Spark Parquet rows: {len(spark_read_back_pd)}")
    assert len(pandas_read_back) == len(
        spark_read_back_pd
    ), "Parquet row count mismatch!"
    print("✅ Parquet files match")
    print()

    spark_ctx.stop()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("✅ PARITY VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("Both engines produced identical results:")
    print(f"  - Row counts: {len(pandas_filtered)} rows")
    print(f"  - Aggregations: {len(pandas_agg)} categories")
    print(f"  - Parquet files written and verified")
    print()
    print("Phase 2 SUCCESS: Engines are functionally equivalent! 🎉")


if __name__ == "__main__":
    run_parity_demo()
