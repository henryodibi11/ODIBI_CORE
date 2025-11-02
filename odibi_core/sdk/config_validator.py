"""
Configuration validator for pipeline definitions.

Validates JSON, SQLite, and CSV configurations against required schema.
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Validation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """
    Represents a validation issue.

    Attributes:
        level: Severity level
        message: Issue description
        step_name: Name of the step (if applicable)
        field: Field name (if applicable)
    """

    level: ValidationLevel
    message: str
    step_name: Optional[str] = None
    field: Optional[str] = None

    def __str__(self) -> str:
        prefix = "❌" if self.level == ValidationLevel.ERROR else "⚠️"
        step_info = f" [{self.step_name}]" if self.step_name else ""
        field_info = f" (field: {self.field})" if self.field else ""
        return f"{prefix} {self.message}{step_info}{field_info}"


class ConfigValidator:
    """
    Validate pipeline configuration files.

    Example:
        >>> validator = ConfigValidator()
        >>> result = validator.validate("pipeline.json")
        >>> if not result:
        ...     for issue in validator.issues:
        ...         print(issue)
    """

    REQUIRED_FIELDS = {"layer", "name", "type"}
    VALID_LAYERS = {"connect", "ingest", "store", "transform", "publish"}
    VALID_ENGINES = {"pandas", "spark"}

    def __init__(self) -> None:
        self.issues: List[ValidationIssue] = []
        self.step_names: Set[str] = set()

    def validate(self, config_path: str, strict: bool = False) -> bool:
        """
        Validate configuration file.

        Args:
            config_path: Path to configuration file
            strict: If True, warnings also fail validation

        Returns:
            True if valid, False otherwise

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        self.issues = []
        self.step_names = set()

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Load config based on type
        if config_file.suffix == ".json":
            steps = self._load_json(config_file)
        elif config_file.suffix == ".db":
            steps = self._load_sqlite(config_file)
        elif config_file.suffix == ".csv":
            steps = self._load_csv(config_file)
        else:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Unsupported file format: {config_file.suffix}",
                )
            )
            return False

        if not steps:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR, message="No steps found in config"
                )
            )
            return False

        # Validate each step
        for step in steps:
            self._validate_step(step)

        # Check for circular dependencies
        self._check_circular_dependencies(steps)

        # Check for errors
        has_errors = any(issue.level == ValidationLevel.ERROR for issue in self.issues)
        has_warnings = any(
            issue.level == ValidationLevel.WARNING for issue in self.issues
        )

        if strict and has_warnings:
            return False

        return not has_errors

    def _validate_step(self, step: Dict[str, Any]) -> None:
        """Validate a single step configuration."""
        step_name = step.get("name", "<unnamed>")

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in step:
                self.issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Missing required field: {field}",
                        step_name=step_name,
                        field=field,
                    )
                )

        # Check layer validity
        layer = step.get("layer", "")
        if layer and layer not in self.VALID_LAYERS:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Invalid layer: {layer}. Must be one of {self.VALID_LAYERS}",
                    step_name=step_name,
                    field="layer",
                )
            )

        # Check engine validity
        engine = step.get("engine", "")
        if engine and engine not in self.VALID_ENGINES:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Unknown engine: {engine}. Expected: {self.VALID_ENGINES}",
                    step_name=step_name,
                    field="engine",
                )
            )

        # Check for duplicate step names
        if step_name in self.step_names:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Duplicate step name: {step_name}",
                    step_name=step_name,
                )
            )
        self.step_names.add(step_name)

        # Check SQL steps have query
        if step.get("type") == "sql" and not step.get("value"):
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="SQL step missing 'value' (query)",
                    step_name=step_name,
                    field="value",
                )
            )

        # Check inputs/outputs are valid JSON
        for field_name in ["inputs", "outputs", "params", "metadata"]:
            if field_name in step:
                value = step[field_name]
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        self.issues.append(
                            ValidationIssue(
                                level=ValidationLevel.ERROR,
                                message=f"Invalid JSON in field: {field_name}",
                                step_name=step_name,
                                field=field_name,
                            )
                        )

    def _check_circular_dependencies(self, steps: List[Dict[str, Any]]) -> None:
        """Check for circular dependencies in step inputs/outputs."""
        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}

        for step in steps:
            step_name = step.get("name", "")
            if not step_name:
                continue

            inputs = step.get("inputs", {})
            if isinstance(inputs, str):
                try:
                    inputs = json.loads(inputs)
                except json.JSONDecodeError:
                    continue

            if isinstance(inputs, dict):
                # Inputs reference logical names from other steps
                dependencies[step_name] = set(inputs.values())

        # Simple cycle detection using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in dependencies:
            if node not in visited:
                if has_cycle(node):
                    self.issues.append(
                        ValidationIssue(
                            level=ValidationLevel.ERROR,
                            message=f"Circular dependency detected involving: {node}",
                        )
                    )
                    break

    def _load_json(self, path: Path) -> List[Dict[str, Any]]:
        """Load configuration from JSON file."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    self.issues.append(
                        ValidationIssue(
                            level=ValidationLevel.ERROR,
                            message="JSON must contain an array of steps",
                        )
                    )
                    return []
        except json.JSONDecodeError as e:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR, message=f"Invalid JSON: {e}"
                )
            )
            return []

    def _load_sqlite(self, path: Path) -> List[Dict[str, Any]]:
        """Load configuration from SQLite database."""
        try:
            conn = sqlite3.connect(str(path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Try transformation_config table first
            try:
                cursor.execute("SELECT * FROM transformation_config")
                rows = cursor.fetchall()
                conn.close()

                return [dict(row) for row in rows]
            except sqlite3.OperationalError:
                # Try ingestion_source_config
                cursor.execute("SELECT * FROM ingestion_source_config")
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]

        except sqlite3.Error as e:
            self.issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR, message=f"SQLite error: {e}"
                )
            )
            return []

    def _load_csv(self, path: Path) -> List[Dict[str, Any]]:
        """Load configuration from CSV file."""
        try:
            import pandas as pd

            df = pd.read_csv(path)
            return df.to_dict("records")
        except Exception as e:
            self.issues.append(
                ValidationIssue(level=ValidationLevel.ERROR, message=f"CSV error: {e}")
            )
            return []

    def print_issues(self) -> None:
        """Print all validation issues."""
        if not self.issues:
            print("✅ Configuration is valid")
            return

        print(f"\n{'='*60}")
        print(f"Validation Issues ({len(self.issues)} found)")
        print(f"{'='*60}\n")

        for issue in self.issues:
            print(issue)

    def get_summary(self) -> str:
        """Get validation summary."""
        errors = sum(1 for i in self.issues if i.level == ValidationLevel.ERROR)
        warnings = sum(1 for i in self.issues if i.level == ValidationLevel.WARNING)
        infos = sum(1 for i in self.issues if i.level == ValidationLevel.INFO)

        if not self.issues:
            return "✅ Configuration is valid"

        return f"Validation: {errors} errors, {warnings} warnings, {infos} info"
