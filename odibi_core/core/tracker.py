"""
Execution tracker for truth-preserving snapshots.

Captures before/after state, schema diffs, row counts, and timing for every Node.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Snapshot:
    """
    Snapshot of DataFrame state at a point in time.

    Attributes:
        name: Identifier for the snapshot
        timestamp: When snapshot was captured
        row_count: Number of rows in DataFrame
        schema: List of (column_name, data_type) tuples
        sample_data: First N rows as list of dicts
        metadata: Additional metadata
    """

    name: str
    timestamp: str
    row_count: int
    schema: List[tuple]
    sample_data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "row_count": self.row_count,
            "schema": [
                {"column": col, "type": str(dtype)} for col, dtype in self.schema
            ],
            "sample_data": self.sample_data,
            "metadata": self.metadata,
        }


@dataclass
class StepExecution:
    """
    Record of a single step's execution.

    Attributes:
        step_name: Name of the step
        layer: Pipeline layer
        start_time: Execution start timestamp
        end_time: Execution end timestamp
        duration_ms: Execution duration in milliseconds
        before_snapshot: Snapshot of input data (if applicable)
        after_snapshot: Snapshot of output data
        schema_diff: Changes in schema (added/removed/changed columns)
        row_delta: Change in row count
        state: Final state of step
        error_message: Error message if failed
        iteration: Iteration number (for streaming mode)
        checkpoint_id: Associated checkpoint ID (if any)
    """

    step_name: str
    layer: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    before_snapshot: Optional[Snapshot] = None
    after_snapshot: Optional[Snapshot] = None
    schema_diff: Optional[Dict[str, Any]] = None
    row_delta: Optional[int] = None
    state: str = "pending"
    error_message: Optional[str] = None
    iteration: int = 0
    checkpoint_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "step_name": self.step_name,
            "layer": self.layer,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "before_snapshot": (
                self.before_snapshot.to_dict() if self.before_snapshot else None
            ),
            "after_snapshot": (
                self.after_snapshot.to_dict() if self.after_snapshot else None
            ),
            "schema_diff": self.schema_diff,
            "row_delta": self.row_delta,
            "state": self.state,
            "error_message": self.error_message,
            "iteration": self.iteration,
            "checkpoint_id": self.checkpoint_id,
        }


class Tracker:
    """
    Execution tracker for pipeline runs.

    Captures snapshots, timing, schema changes, and lineage for every step.
    Enables debugging, compliance, and AMP self-improvement.

    Example:
        >>> tracker = Tracker()
        >>> tracker.start_step("ingest_csv", "ingest")
        >>> tracker.snapshot("after", output_df, context)
        >>> tracker.end_step("ingest_csv", "success")
        >>> tracker.save("tracker_logs/run_001.json")
    """

    def __init__(self, log_dir: Optional[str] = None) -> None:
        """
        Initialize tracker.

        Args:
            log_dir: Directory to save tracker logs (default: tracker_logs/)
        """
        self.executions: List[StepExecution] = []
        self._current_execution: Optional[StepExecution] = None
        self.log_dir = Path(log_dir) if log_dir else Path("tracker_logs")
        self.pipeline_start_time: Optional[datetime] = None

    def start_pipeline(self, pipeline_name: str = "unknown") -> None:
        """
        Start tracking a pipeline execution.

        Args:
            pipeline_name: Name of the pipeline
        """
        self.pipeline_start_time = datetime.now()
        logger.info(
            f"Pipeline '{pipeline_name}' started at {self.pipeline_start_time.isoformat()}"
        )

    def start_step(self, step_name: str, layer: str) -> None:
        """
        Start tracking a step execution.

        Args:
            step_name: Name of the step
            layer: Pipeline layer (connect, ingest, store, transform, publish)
        """
        execution = StepExecution(
            step_name=step_name, layer=layer, start_time=datetime.now().isoformat()
        )
        self._current_execution = execution
        self.executions.append(execution)
        logger.info(f"Started step: {step_name} ({layer})")

    def end_step(
        self, step_name: str, state: str, error_message: Optional[str] = None
    ) -> None:
        """
        End tracking for a step.

        Args:
            step_name: Name of the step
            state: Final state (success, failed, retry)
            error_message: Error message if failed
        """
        if self._current_execution and self._current_execution.step_name == step_name:
            end_time = datetime.now()
            self._current_execution.end_time = end_time.isoformat()
            self._current_execution.state = state
            self._current_execution.error_message = error_message

            # Calculate duration
            start_dt = datetime.fromisoformat(self._current_execution.start_time)
            delta = end_time - start_dt
            self._current_execution.duration_ms = delta.total_seconds() * 1000

            logger.info(
                f"Completed step: {step_name} - {state} in {self._current_execution.duration_ms:.2f}ms"
            )

    def snapshot(self, name: str, df: Any, context: Any) -> None:
        """
        Capture snapshot of DataFrame state.

        Calls context.collect_sample() to get Pandas DataFrame, then extracts:
        - Schema (column names and types)
        - Row count
        - Sample data (first 5 rows)

        Args:
            name: Snapshot identifier (e.g., "before", "after")
            df: DataFrame to snapshot (Pandas or Spark)
            context: Engine context for sampling

        Example:
            >>> tracker.snapshot("before_transform", input_df, pandas_context)
        """
        if not self._current_execution:
            logger.warning("Cannot create snapshot - no active step")
            return

        try:
            # Get sample as Pandas DataFrame
            sample_df = context.collect_sample(df, n=5)

            # Extract schema
            schema = [(col, str(sample_df[col].dtype)) for col in sample_df.columns]

            # Get row count from original DataFrame (not sample)
            try:
                # Try Pandas first
                import pandas as pd

                if isinstance(df, pd.DataFrame):
                    row_count = int(df.shape[0])
                else:
                    # Spark DataFrame
                    row_count = df.count()
            except:
                # Fallback
                row_count = len(sample_df)

            # Convert sample to list of dicts (ensure we have a DataFrame, not Series)
            if len(sample_df) > 0:
                sample_data = sample_df.head(5).to_dict(orient="records")
            else:
                sample_data = []

            # Create snapshot
            snapshot = Snapshot(
                name=name,
                timestamp=datetime.now().isoformat(),
                row_count=row_count,
                schema=schema,
                sample_data=sample_data,
            )

            # Store in current execution
            if name == "before":
                self._current_execution.before_snapshot = snapshot
            elif name == "after":
                self._current_execution.after_snapshot = snapshot

                # Calculate schema diff if we have before snapshot
                if self._current_execution.before_snapshot:
                    self._current_execution.schema_diff = self._compute_schema_diff(
                        self._current_execution.before_snapshot, snapshot
                    )
                    self._current_execution.row_delta = (
                        snapshot.row_count
                        - self._current_execution.before_snapshot.row_count
                    )

            logger.info(
                f"Captured snapshot '{name}': {row_count} rows, {len(schema)} columns"
            )

        except Exception as e:
            logger.error(f"Failed to capture snapshot '{name}': {e}")

    def _compute_schema_diff(self, before: Snapshot, after: Snapshot) -> Dict[str, Any]:
        """
        Compute difference between two snapshots.

        Args:
            before: Earlier snapshot
            after: Later snapshot

        Returns:
            Dictionary with added/removed/changed columns
        """
        before_cols = {col: dtype for col, dtype in before.schema}
        after_cols = {col: dtype for col, dtype in after.schema}

        added = [col for col in after_cols if col not in before_cols]
        removed = [col for col in before_cols if col not in after_cols]
        changed = [
            {"column": col, "before": before_cols[col], "after": after_cols[col]}
            for col in before_cols
            if col in after_cols and before_cols[col] != after_cols[col]
        ]

        return {
            "added_columns": added,
            "removed_columns": removed,
            "changed_types": changed,
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with total duration, step count, success rate, etc.

        Example:
            >>> stats = tracker.get_stats()
            >>> print(f"Total duration: {stats['total_duration_ms']}ms")
        """
        total_duration = sum(e.duration_ms for e in self.executions if e.duration_ms)
        success_count = sum(1 for e in self.executions if e.state == "success")
        failed_count = sum(1 for e in self.executions if e.state == "failed")

        return {
            "total_steps": len(self.executions),
            "total_duration_ms": total_duration,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": (
                (success_count / len(self.executions) * 100) if self.executions else 0
            ),
        }

    def export_lineage(self) -> Dict[str, Any]:
        """
        Export execution lineage as JSON-serializable dict.

        Returns:
            Lineage data with all step executions and dependencies

        Example:
            >>> lineage = tracker.export_lineage()
            >>> with open("lineage.json", "w") as f:
            ...     json.dump(lineage, f, indent=2)
        """
        return {
            "pipeline_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": (
                self.pipeline_start_time.isoformat()
                if self.pipeline_start_time
                else None
            ),
            "steps": [e.to_dict() for e in self.executions],
            "summary": self.get_stats(),
        }

    def save(self, filepath: Optional[str] = None) -> str:
        """
        Save tracker logs to file.

        Args:
            filepath: Output file path (default: tracker_logs/run_TIMESTAMP.json)

        Returns:
            Path to saved file

        Example:
            >>> path = tracker.save()
            >>> print(f"Logs saved to: {path}")
        """
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.log_dir / f"run_{timestamp}.json"
        else:
            filepath = Path(filepath)

        # Export lineage
        lineage = self.export_lineage()

        # Save to file
        with open(filepath, "w") as f:
            json.dump(lineage, f, indent=2)

        logger.info(f"Tracker logs saved to: {filepath}")
        return str(filepath)

    def get_summary(self) -> str:
        """
        Get human-readable summary of execution.

        Returns:
            Formatted summary string

        Example:
            >>> print(tracker.get_summary())
        """
        stats = self.get_stats()
        lines = [
            "=" * 70,
            "Pipeline Execution Summary",
            "=" * 70,
            f"Total Steps: {stats['total_steps']}",
            f"Success: {stats['success_count']} | Failed: {stats['failed_count']}",
            f"Success Rate: {stats['success_rate']:.1f}%",
            f"Total Duration: {stats['total_duration_ms']:.2f}ms",
            "",
            "Step Details:",
            "-" * 70,
        ]

        for ex in self.executions:
            status_icon = "[OK]" if ex.state == "success" else "[FAIL]"
            duration = f"{ex.duration_ms:.2f}ms" if ex.duration_ms else "N/A"
            lines.append(
                f"{status_icon} {ex.step_name:<30} {ex.layer:<12} {duration:>12}"
            )

        lines.append("=" * 70)
        return "\n".join(lines)

    def export_to_story(
        self,
        story_dir: str = "stories",
        explanations: Optional[Dict[str, Any]] = None,
        dag_builder: Optional[Any] = None,
    ) -> str:
        """
        Export tracker data to HTML story.

        Args:
            story_dir: Directory to save story HTML
            explanations: Optional dict of step_name → explanation
            dag_builder: Optional DAG builder for dependency visualization

        Returns:
            Path to saved story file

        Example:
            >>> story_path = tracker.export_to_story()
            >>> # With explanations and DAG
            >>> explanations = {
            ...     "calc_efficiency": "**Purpose:** Calculate boiler efficiency using IAPWS-97"
            ... }
            >>> story_path = tracker.export_to_story(
            ...     explanations=explanations,
            ...     dag_builder=my_dag_builder
            ... )
        """
        from odibi_core.story import StoryGenerator

        # Export lineage
        lineage = self.export_lineage()

        # Generate story
        generator = StoryGenerator(
            output_dir=story_dir,
            explanations=explanations,
            dag_builder=dag_builder,
        )
        story_path = generator.save_story(lineage)

        return story_path
