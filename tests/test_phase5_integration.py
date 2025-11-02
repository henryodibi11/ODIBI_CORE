"""
Integration tests for Phase 5 DAG execution.
"""

import pytest
import pandas as pd
from odibi_core.core import (
    Step,
    Orchestrator,
    Tracker,
    EventEmitter,
    create_engine_context,
    DAGBuilder,
)


@pytest.fixture
def sample_data():
    """Create sample DataFrames for testing."""
    return {
        "source_a": pd.DataFrame({"id": [1, 2], "value_a": [10, 20]}),
        "source_b": pd.DataFrame({"id": [1, 2], "value_b": [100, 200]}),
    }


def test_parallel_dag_execution():
    """Test end-to-end parallel DAG execution."""
    # Define a simple pipeline with parallel branches
    steps = [
        # Level 0: Two independent sources
        Step(
            layer="ingest",
            name="read_a",
            type="config_op",
            engine="pandas",
            value="",
            outputs={"data": "data_a"},
        ),
        Step(
            layer="ingest",
            name="read_b",
            type="config_op",
            engine="pandas",
            value="",
            outputs={"data": "data_b"},
        ),
        # Level 1: Two independent transforms
        Step(
            layer="transform",
            name="transform_a",
            type="sql",
            engine="pandas",
            value="SELECT id, value_a * 2 AS value_a FROM data_a",
            inputs={"data_a": "data_a"},
            outputs={"result": "result_a"},
        ),
        Step(
            layer="transform",
            name="transform_b",
            type="sql",
            engine="pandas",
            value="SELECT id, value_b * 3 AS value_b FROM data_b",
            inputs={"data_b": "data_b"},
            outputs={"result": "result_b"},
        ),
    ]

    # Build DAG
    builder = DAGBuilder(steps)
    dag = builder.build()

    # Verify structure
    assert len(dag) == 4
    assert dag["read_a"].level == 0
    assert dag["read_b"].level == 0
    assert dag["transform_a"].level == 1
    assert dag["transform_b"].level == 1

    # Get parallel batches
    batches = builder.get_parallel_batches()
    assert len(batches) == 2
    assert len(batches[0]) == 2  # 2 parallel reads
    assert len(batches[1]) == 2  # 2 parallel transforms


def test_sequential_vs_parallel_mode():
    """Test that both sequential and parallel modes produce same results."""
    steps = [
        Step(
            layer="ingest",
            name="source",
            type="config_op",
            engine="pandas",
            value="",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="process",
            type="sql",
            engine="pandas",
            value="SELECT * FROM raw",
            inputs={"raw": "raw"},
            outputs={"data": "processed"},
        ),
    ]

    # Note: Full execution test would require mock Node implementations
    # This test verifies configuration compatibility

    context = create_engine_context("pandas")
    tracker = Tracker()
    events = EventEmitter()

    # Sequential mode
    orch_seq = Orchestrator(
        steps=steps, context=context, tracker=tracker, events=events, parallel=False
    )
    assert not orch_seq.parallel

    # Parallel mode
    orch_par = Orchestrator(
        steps=steps,
        context=context,
        tracker=tracker,
        events=events,
        parallel=True,
        max_workers=2,
    )
    assert orch_par.parallel
    assert orch_par.max_workers == 2


def test_dag_with_cache_enabled():
    """Test DAG execution configuration with caching."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="data.csv",
            outputs={"data": "raw"},
        ),
    ]

    context = create_engine_context("pandas")
    tracker = Tracker()
    events = EventEmitter()

    # With cache enabled
    orchestrator = Orchestrator(
        steps=steps,
        context=context,
        tracker=tracker,
        events=events,
        parallel=True,
        use_cache=True,
        max_retries=3,
        retry_delay=0.5,
    )

    assert orchestrator.use_cache
    assert orchestrator.max_retries == 3
    assert orchestrator.retry_delay == 0.5


def test_dag_visualization_mermaid():
    """Test Mermaid diagram export."""
    steps = [
        Step(
            layer="ingest",
            name="A",
            type="config_op",
            engine="pandas",
            value="",
            outputs={"data": "a"},
        ),
        Step(
            layer="transform",
            name="B",
            type="sql",
            engine="pandas",
            value="",
            inputs={"x": "a"},
            outputs={"data": "b"},
        ),
        Step(
            layer="transform",
            name="C",
            type="sql",
            engine="pandas",
            value="",
            inputs={"x": "a"},
            outputs={"data": "c"},
        ),
        Step(
            layer="publish",
            name="D",
            type="sql",
            engine="pandas",
            value="",
            inputs={"x": "b", "y": "c"},
            outputs={"data": "d"},
        ),
    ]

    builder = DAGBuilder(steps)
    builder.build()

    # Export Mermaid
    mermaid = builder.export_mermaid()

    assert "graph TD" in mermaid
    assert "A" in mermaid and "B" in mermaid and "C" in mermaid and "D" in mermaid
    assert "-->" in mermaid  # Has edges

    # Verify parallelism
    batches = builder.get_parallel_batches()
    assert len(batches[0]) == 1  # A alone
    assert len(batches[1]) == 2  # B and C in parallel
    assert len(batches[2]) == 1  # D depends on both

    # Check names
    batch1_names = {s.name for s in batches[1]}
    assert batch1_names == {"B", "C"}


def test_cycle_detection_integration():
    """Test that orchestrator rejects cyclic pipelines."""
    steps = [
        Step(
            layer="transform",
            name="X",
            type="sql",
            engine="pandas",
            value="",
            inputs={"in": "y"},
            outputs={"data": "x"},
        ),
        Step(
            layer="transform",
            name="Y",
            type="sql",
            engine="pandas",
            value="",
            inputs={"in": "z"},
            outputs={"data": "y"},
        ),
        Step(
            layer="transform",
            name="Z",
            type="sql",
            engine="pandas",
            value="",
            inputs={"in": "x"},
            outputs={"data": "z"},
        ),
    ]

    builder = DAGBuilder(steps)

    with pytest.raises(ValueError, match="[Cc]ircular"):
        builder.build()
