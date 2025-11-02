"""
Tests for DAG builder (Phase 5).
"""

import pytest
from odibi_core.core import DAGBuilder, Step


def test_dag_builder_simple_pipeline():
    """Test building a simple linear pipeline."""
    steps = [
        Step(
            layer="ingest",
            name="read_csv",
            type="config_op",
            engine="pandas",
            value="data.csv",
            outputs={"data": "raw_data"},
        ),
        Step(
            layer="transform",
            name="clean_data",
            type="sql",
            engine="pandas",
            value="SELECT * FROM input",
            inputs={"input": "raw_data"},
            outputs={"data": "clean_data"},
        ),
        Step(
            layer="publish",
            name="write_output",
            type="config_op",
            engine="pandas",
            value="output.csv",
            inputs={"data": "clean_data"},
            outputs={},
        ),
    ]

    builder = DAGBuilder(steps)
    dag = builder.build()

    assert len(dag) == 3
    assert dag["read_csv"].level == 0
    assert dag["clean_data"].level == 1
    assert dag["write_output"].level == 2


def test_dag_builder_parallel_branches():
    """Test DAG with parallel independent branches."""
    steps = [
        Step(
            layer="ingest",
            name="read_A",
            type="config_op",
            engine="pandas",
            value="a.csv",
            outputs={"data": "data_a"},
        ),
        Step(
            layer="ingest",
            name="read_B",
            type="config_op",
            engine="pandas",
            value="b.csv",
            outputs={"data": "data_b"},
        ),
        Step(
            layer="transform",
            name="transform_A",
            type="sql",
            engine="pandas",
            value="SELECT * FROM input",
            inputs={"input": "data_a"},
            outputs={"data": "result_a"},
        ),
        Step(
            layer="transform",
            name="transform_B",
            type="sql",
            engine="pandas",
            value="SELECT * FROM input",
            inputs={"input": "data_b"},
            outputs={"data": "result_b"},
        ),
        Step(
            layer="publish",
            name="merge",
            type="sql",
            engine="pandas",
            value="SELECT * FROM a UNION SELECT * FROM b",
            inputs={"a": "result_a", "b": "result_b"},
            outputs={"data": "final"},
        ),
    ]

    builder = DAGBuilder(steps)
    dag = builder.build()

    # read_A and read_B should be at level 0
    assert dag["read_A"].level == 0
    assert dag["read_B"].level == 0

    # transform_A and transform_B should be at level 1
    assert dag["transform_A"].level == 1
    assert dag["transform_B"].level == 1

    # merge should be at level 2
    assert dag["merge"].level == 2

    # Get parallel batches
    batches = builder.get_parallel_batches()
    assert len(batches) == 3
    assert len(batches[0]) == 2  # 2 parallel ingests
    assert len(batches[1]) == 2  # 2 parallel transforms
    assert len(batches[2]) == 1  # 1 merge


def test_dag_builder_cycle_detection():
    """Test that circular dependencies are detected."""
    steps = [
        Step(
            layer="transform",
            name="step_A",
            type="sql",
            engine="pandas",
            value="SELECT * FROM b",
            inputs={"input": "data_b"},
            outputs={"data": "data_a"},
        ),
        Step(
            layer="transform",
            name="step_B",
            type="sql",
            engine="pandas",
            value="SELECT * FROM a",
            inputs={"input": "data_a"},
            outputs={"data": "data_b"},
        ),
    ]

    builder = DAGBuilder(steps)

    with pytest.raises(ValueError, match="[Cc]ircular"):
        builder.build()


def test_dag_builder_dependencies():
    """Test dependency tracking."""
    steps = [
        Step(
            layer="ingest",
            name="source",
            type="config_op",
            engine="pandas",
            value="data.csv",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="derived",
            type="sql",
            engine="pandas",
            value="SELECT * FROM raw",
            inputs={"input": "raw"},
            outputs={"data": "processed"},
        ),
    ]

    builder = DAGBuilder(steps)
    dag = builder.build()

    # Check dependencies
    assert builder.get_dependencies("source") == []
    assert builder.get_dependencies("derived") == ["source"]

    # Check dependents
    assert builder.get_dependents("source") == ["derived"]
    assert builder.get_dependents("derived") == []


def test_dag_builder_visualization():
    """Test text visualization generation."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="data.csv",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="transform",
            type="sql",
            engine="pandas",
            value="SELECT * FROM raw",
            inputs={"input": "raw"},
            outputs={"data": "clean"},
        ),
    ]

    builder = DAGBuilder(steps)
    builder.build()

    viz = builder.visualize()
    assert "Level 0" in viz
    assert "Level 1" in viz
    assert "read" in viz
    assert "transform" in viz


def test_dag_builder_mermaid_export():
    """Test Mermaid diagram export."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="data.csv",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="transform",
            type="sql",
            engine="pandas",
            value="SELECT * FROM raw",
            inputs={"input": "raw"},
            outputs={"data": "clean"},
        ),
    ]

    builder = DAGBuilder(steps)
    builder.build()

    mermaid = builder.export_mermaid()
    assert "graph TD" in mermaid
    assert "read" in mermaid
    assert "transform" in mermaid
    assert "-->" in mermaid


def test_dag_builder_execution_order():
    """Test topological sort for execution order."""
    steps = [
        Step(
            layer="publish",
            name="final",
            type="config_op",
            engine="pandas",
            value="out.csv",
            inputs={"data": "result"},
            outputs={},
        ),
        Step(
            layer="ingest",
            name="source",
            type="config_op",
            engine="pandas",
            value="in.csv",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="process",
            type="sql",
            engine="pandas",
            value="SELECT * FROM raw",
            inputs={"input": "raw"},
            outputs={"data": "result"},
        ),
    ]

    builder = DAGBuilder(steps)
    dag = builder.build()

    order = builder.get_execution_order()
    names = [s.name for s in order]

    # source must come before process
    assert names.index("source") < names.index("process")
    # process must come before final
    assert names.index("process") < names.index("final")
