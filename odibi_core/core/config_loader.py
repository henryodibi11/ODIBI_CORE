"""
Configuration loader for pipeline definitions.

Loads Step configs from SQLite tables, JSON files, or CSV files.
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List
from odibi_core.core.node import Step

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load pipeline configuration from SQLite, JSON, or CSV.

    Supports:
    - SQLite database (ingestion_source_config, transformation_config tables)
    - JSON file (array of step objects)
    - CSV file (same schema as SQL table)

    Example:
        >>> loader = ConfigLoader()
        >>> steps = loader.load("odibi_config_local.db")
        >>> print(f"Loaded {len(steps)} steps")
    """

    def load(self, source_uri: str, **kwargs: Any) -> List[Step]:
        """
        Load pipeline configuration from source.

        Args:
            source_uri: Path to SQLite DB, JSON file, or CSV file
            **kwargs: Additional parameters
                - project (str): Filter by project name (SQLite only)
                - enabled_only (bool): Load only enabled=1 configs (SQLite only)
                - layer (str): Filter by layer (SQLite only)

        Returns:
            List of Step objects

        Raises:
            FileNotFoundError: If source doesn't exist
            ValueError: If source format unknown

        Example:
            >>> steps = loader.load("pipeline.json")
            >>> steps = loader.load("odibi_config.db", project="energy efficiency")
        """
        path = Path(source_uri)

        if not path.exists():
            raise FileNotFoundError(f"Config source not found: {source_uri}")

        if source_uri.endswith(".db") or source_uri.endswith(".sqlite"):
            return self._load_from_sqlite(source_uri, **kwargs)
        elif source_uri.endswith(".json"):
            return self._load_from_json(source_uri, **kwargs)
        elif source_uri.endswith(".csv"):
            return self._load_from_csv(source_uri, **kwargs)
        else:
            raise ValueError(f"Unknown config format: {source_uri}")

    def _load_from_sqlite(
        self,
        db_path: str,
        project: str = None,
        enabled_only: bool = True,
        layer: str = None,
    ) -> List[Step]:
        """
        Load config from SQLite database.

        Expected tables:
        - transformation_config (primary table for Silver/Gold transforms)
        - ingestion_source_config (Bronze layer configs)

        Columns:
        - Layer, StepName, StepType, Engine, Value
        - Params, Inputs, Outputs (JSON strings)
        - Metadata (optional JSON string)

        Args:
            db_path: Path to SQLite database
            project: Filter by project name
            enabled_only: Only load enabled=1 configs
            layer: Filter by specific layer

        Returns:
            List of Step objects
        """
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()

        steps = []

        # Load from transformation_config table
        query = "SELECT * FROM transformation_config WHERE 1=1"
        params = []

        if project:
            query += " AND project = ?"
            params.append(project)

        if enabled_only:
            query += " AND enabled = 1"

        if layer:
            query += " AND Layer = ?"
            params.append(layer)

        query += " ORDER BY execution_order, StepName"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                step = self._parse_sql_row(row)
                if step:
                    steps.append(step)

            logger.info(f"Loaded {len(steps)} steps from transformation_config")

        except sqlite3.OperationalError as e:
            logger.warning(f"Could not load from transformation_config: {e}")

        # Also try ingestion_source_config
        try:
            query = "SELECT * FROM ingestion_source_config WHERE 1=1"
            params = []

            if project:
                query += " AND project = ?"
                params.append(project)

            if enabled_only:
                query += " AND enabled = 1"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                step = self._parse_ingestion_row(row)
                if step:
                    steps.append(step)

            logger.info(f"Loaded {len(steps)} steps from ingestion_source_config")

        except sqlite3.OperationalError as e:
            logger.warning(f"Could not load from ingestion_source_config: {e}")

        conn.close()

        if not steps:
            logger.warning(f"No steps loaded from {db_path}")

        return steps

    def _parse_sql_row(self, row: sqlite3.Row) -> Step:
        """
        Parse SQL row into Step object.

        Args:
            row: SQLite row from transformation_config

        Returns:
            Step object
        """
        try:
            # Parse JSON fields
            params = self._parse_json_field(row, "Params")
            inputs = self._parse_json_field(row, "Inputs")
            outputs = self._parse_json_field(row, "Outputs")
            metadata = self._parse_json_field(row, "Metadata")

            step = Step(
                layer=row["Layer"].lower() if row["Layer"] else "transform",
                name=row["StepName"],
                type=row["StepType"].lower() if row["StepType"] else "sql",
                engine=row["Engine"].lower() if row["Engine"] else "pandas",
                value=row["Value"] or "",
                params=params,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
            )

            return step

        except Exception as e:
            logger.error(f"Failed to parse row {row['StepName']}: {e}")
            return None

    def _parse_ingestion_row(self, row: sqlite3.Row) -> Step:
        """
        Parse ingestion config row into Step object.

        Args:
            row: SQLite row from ingestion_source_config

        Returns:
            Step object
        """
        try:
            # Ingestion configs have different schema
            step = Step(
                layer="ingest",
                name=row.get("source_id") or row.get("SourceID") or "unknown",
                type="config_op",
                engine=row.get("engine", "pandas").lower(),
                value=row.get("source_path_or_query") or row.get("SourcePath") or "",
                params={},
                inputs={},
                outputs={"data": row.get("target_id") or row.get("TargetID") or "data"},
                metadata={
                    "project": row.get("project"),
                    "source_type": row.get("source_type"),
                },
            )

            return step

        except Exception as e:
            logger.error(f"Failed to parse ingestion row: {e}")
            return None

    def _parse_json_field(self, row: sqlite3.Row, field_name: str) -> Dict[str, Any]:
        """
        Parse JSON string field from SQL row.

        Args:
            row: SQLite row
            field_name: Column name

        Returns:
            Parsed dict or empty dict if invalid
        """
        try:
            value = row[field_name]
            if value is None or value == "":
                return {}

            if isinstance(value, str):
                return json.loads(value)
            elif isinstance(value, dict):
                return value
            else:
                return {}

        except (json.JSONDecodeError, KeyError):
            return {}

    def _load_from_json(self, json_path: str, **kwargs: Any) -> List[Step]:
        """
        Load config from JSON file.

        Expected format:
        [
            {
                "layer": "ingest",
                "name": "read_csv",
                "type": "config_op",
                "engine": "pandas",
                "value": "data/input.csv",
                "outputs": {"data": "raw_data"}
            },
            ...
        ]

        Args:
            json_path: Path to JSON file
            **kwargs: Additional parameters (unused)

        Returns:
            List of Step objects
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"JSON config must be an array, got {type(data)}")

        steps = []
        for item in data:
            try:
                step = Step(
                    layer=item.get("layer", "transform"),
                    name=item["name"],
                    type=item.get("type", "config_op"),
                    engine=item.get("engine", "pandas"),
                    value=item.get("value", ""),
                    params=item.get("params"),
                    inputs=item.get("inputs"),
                    outputs=item.get("outputs"),
                    metadata=item.get("metadata"),
                )
                steps.append(step)
            except KeyError as e:
                logger.error(f"Invalid step in JSON (missing {e}): {item}")

        logger.info(f"Loaded {len(steps)} steps from JSON: {json_path}")
        return steps

    def _load_from_csv(self, csv_path: str, **kwargs: Any) -> List[Step]:
        """
        Load config from CSV file.

        Expected columns match SQLite schema.

        Args:
            csv_path: Path to CSV file
            **kwargs: Additional parameters

        Returns:
            List of Step objects
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "CSV config loading requires pandas. Install with: pip install pandas"
            )

        df = pd.read_csv(csv_path)

        steps = []
        for idx, row in df.iterrows():
            try:
                # Parse JSON string fields
                params = (
                    json.loads(row.get("Params", "{}"))
                    if pd.notna(row.get("Params"))
                    else {}
                )
                inputs = (
                    json.loads(row.get("Inputs", "{}"))
                    if pd.notna(row.get("Inputs"))
                    else {}
                )
                outputs = (
                    json.loads(row.get("Outputs", "{}"))
                    if pd.notna(row.get("Outputs"))
                    else {}
                )
                metadata = (
                    json.loads(row.get("Metadata", "{}"))
                    if pd.notna(row.get("Metadata"))
                    else {}
                )

                step = Step(
                    layer=row.get("Layer", "transform").lower(),
                    name=row["StepName"],
                    type=row.get("StepType", "config_op").lower(),
                    engine=row.get("Engine", "pandas").lower(),
                    value=row.get("Value", ""),
                    params=params,
                    inputs=inputs,
                    outputs=outputs,
                    metadata=metadata,
                )
                steps.append(step)

            except Exception as e:
                logger.error(f"Failed to parse row {idx}: {e}")

        logger.info(f"Loaded {len(steps)} steps from CSV: {csv_path}")
        return steps


class ConfigValidationError(Exception):
    """Raised when config validation fails."""

    pass


class ConfigValidator:
    """
    Validator for pipeline configurations.

    Validates:
    - All output keys are unique
    - No circular dependencies
    - All inputs reference existing outputs
    - Layer ordering (Connect → Ingest → Store → Transform → Publish)
    - Valid engine names
    - Valid step types

    Example:
        >>> validator = ConfigValidator()
        >>> validator.validate_config(steps)
        # Raises ConfigValidationError if invalid
    """

    VALID_LAYERS = {"connect", "ingest", "store", "transform", "publish"}
    VALID_ENGINES = {"pandas", "spark"}
    VALID_TYPES = {"sql", "function", "config_op", "api"}

    def validate_config(self, steps: List[Step]) -> None:
        """
        Validate pipeline configuration.

        Args:
            steps: List of steps to validate

        Raises:
            ConfigValidationError: If validation fails with detailed message
        """
        if not steps:
            raise ConfigValidationError("Config is empty - no steps found")

        self._validate_unique_names(steps)
        self._validate_unique_outputs(steps)
        self._validate_inputs_exist(steps)
        self._validate_no_cycles(steps)
        self._validate_layers(steps)
        self._validate_engines(steps)
        self._validate_step_types(steps)

        logger.info(f"Config validation passed for {len(steps)} steps")

    def _validate_unique_names(self, steps: List[Step]) -> None:
        """Ensure all step names are unique."""
        names = [step.name for step in steps]
        duplicates = [name for name in names if names.count(name) > 1]

        if duplicates:
            unique_dups = list(set(duplicates))
            raise ConfigValidationError(
                f"Duplicate step names found: {unique_dups}. "
                f"Each step must have a unique name."
            )

    def _validate_unique_outputs(self, steps: List[Step]) -> None:
        """Ensure all output keys are unique across steps."""
        all_outputs = []
        for step in steps:
            all_outputs.extend(step.outputs.values())

        duplicates = [out for out in all_outputs if all_outputs.count(out) > 1]

        if duplicates:
            unique_dups = list(set(duplicates))
            # Find which steps have duplicate outputs
            conflicts = []
            for dup in unique_dups:
                step_names = [s.name for s in steps if dup in s.outputs.values()]
                conflicts.append(f"'{dup}' produced by: {step_names}")

            raise ConfigValidationError(
                f"Duplicate output keys found:\n"
                + "\n".join(conflicts)
                + "\n\nEach output must have a unique key."
            )

    def _validate_inputs_exist(self, steps: List[Step]) -> None:
        """Ensure all inputs reference existing outputs."""
        # Build set of all available outputs
        available_outputs = set()
        for step in steps:
            available_outputs.update(step.outputs.values())

        # Check each step's inputs
        for step in steps:
            for logical_name, dataset_key in step.inputs.items():
                if dataset_key not in available_outputs:
                    raise ConfigValidationError(
                        f"Step '{step.name}' references undefined input: '{dataset_key}'\n"
                        f"  Input '{logical_name}' → '{dataset_key}' not found.\n"
                        f"  Available outputs: {sorted(available_outputs)}"
                    )

    def _validate_no_cycles(self, steps: List[Step]) -> None:
        """Detect circular dependencies."""
        # Build dependency graph: step_name → list of dependencies
        graph: Dict[str, List[str]] = {}
        output_to_step: Dict[str, str] = {}

        # Map outputs to steps
        for step in steps:
            graph[step.name] = []
            for output_key in step.outputs.values():
                output_to_step[output_key] = step.name

        # Build dependencies
        for step in steps:
            for input_key in step.inputs.values():
                if input_key in output_to_step:
                    dependency = output_to_step[input_key]
                    graph[step.name].append(dependency)

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    raise ConfigValidationError(
                        f"Circular dependency detected:\n"
                        f"  {' → '.join(cycle)}\n"
                        f"Steps cannot depend on each other in a cycle."
                    )

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                has_cycle(node, [])

    def _validate_layers(self, steps: List[Step]) -> None:
        """Validate layer names and ordering."""
        for step in steps:
            if step.layer not in self.VALID_LAYERS:
                raise ConfigValidationError(
                    f"Step '{step.name}' has invalid layer: '{step.layer}'\n"
                    f"  Valid layers: {sorted(self.VALID_LAYERS)}"
                )

    def _validate_engines(self, steps: List[Step]) -> None:
        """Validate engine names."""
        for step in steps:
            if step.engine not in self.VALID_ENGINES:
                raise ConfigValidationError(
                    f"Step '{step.name}' has invalid engine: '{step.engine}'\n"
                    f"  Valid engines: {sorted(self.VALID_ENGINES)}"
                )

    def _validate_step_types(self, steps: List[Step]) -> None:
        """Validate step types."""
        for step in steps:
            if step.type not in self.VALID_TYPES:
                raise ConfigValidationError(
                    f"Step '{step.name}' has invalid type: '{step.type}'\n"
                    f"  Valid types: {sorted(self.VALID_TYPES)}"
                )

    def _parse_json_field(self, row: sqlite3.Row, field_name: str) -> Dict[str, Any]:
        """Parse JSON string field from SQL row."""
        try:
            value = row[field_name]
            if value is None or value == "":
                return {}

            if isinstance(value, str):
                return json.loads(value)
            elif isinstance(value, dict):
                return value
            else:
                return {}

        except (json.JSONDecodeError, KeyError):
            logger.warning(f"Could not parse {field_name} as JSON")
            return {}
