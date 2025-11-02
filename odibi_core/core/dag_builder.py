"""
DAG builder for pipeline execution planning.

Parses Step configurations into nodes and edges, detects circular dependencies,
and performs topological sort for execution order.
"""

import logging
from typing import Any, Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from odibi_core.core.node import Step

logger = logging.getLogger(__name__)


@dataclass
class DAGNode:
    """
    Node in the execution DAG.

    Attributes:
        step: Step configuration
        dependencies: List of step names this node depends on
        dependents: List of step names that depend on this node
        level: Topological level (0 = no dependencies)
    """

    step: Step
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    level: int = 0

    @property
    def name(self) -> str:
        """Get step name."""
        return self.step.name


class DAGBuilder:
    """
    Build directed acyclic graph from pipeline steps.

    Analyzes step inputs/outputs to construct dependency graph,
    detects cycles, and computes topological ordering.

    Example:
        >>> builder = DAGBuilder(steps)
        >>> dag = builder.build()
        >>> execution_order = builder.get_execution_order()
        >>> for step in execution_order:
        ...     print(f"{step.name} (level {dag[step.name].level})")
    """

    def __init__(self, steps: List[Step]) -> None:
        """
        Initialize DAG builder.

        Args:
            steps: List of Step configurations
        """
        self.steps = steps
        self.dag: Dict[str, DAGNode] = {}
        self._output_map: Dict[str, str] = {}  # output_key → step_name

    def build(self) -> Dict[str, DAGNode]:
        """
        Build dependency graph from steps.

        Returns:
            Dictionary mapping step_name → DAGNode

        Raises:
            ValueError: If circular dependencies detected

        Example:
            >>> dag = builder.build()
            >>> node = dag["transform_silver"]
            >>> print(f"Dependencies: {node.dependencies}")
        """
        # Initialize nodes
        self._initialize_nodes()

        # Build output map
        self._build_output_map()

        # Build dependency edges
        self._build_dependencies()

        # Detect cycles
        if self._has_cycles():
            raise ValueError("Circular dependencies detected in pipeline configuration")

        # Compute topological levels
        self._compute_levels()

        logger.info(
            f"Built DAG with {len(self.dag)} nodes, "
            f"max depth: {max((n.level for n in self.dag.values()), default=0)}"
        )

        return self.dag

    def _initialize_nodes(self) -> None:
        """Create DAGNode for each step."""
        for step in self.steps:
            self.dag[step.name] = DAGNode(step=step)

    def _build_output_map(self) -> None:
        """
        Map output keys to producing steps.

        Builds reverse index: output_key → step_name
        """
        for step in self.steps:
            for output_key in step.outputs.values():
                if output_key in self._output_map:
                    raise ValueError(
                        f"Duplicate output key '{output_key}' produced by "
                        f"'{self._output_map[output_key]}' and '{step.name}'"
                    )
                self._output_map[output_key] = step.name

    def _build_dependencies(self) -> None:
        """
        Build dependency edges between nodes.

        For each step, find which steps produce its input datasets.
        """
        for step in self.steps:
            node = self.dag[step.name]

            # Find dependencies based on inputs
            for input_key in step.inputs.values():
                if input_key in self._output_map:
                    dependency_name = self._output_map[input_key]

                    # Add edge: dependency → current
                    node.dependencies.append(dependency_name)
                    self.dag[dependency_name].dependents.append(step.name)

            logger.debug(f"Node '{step.name}' depends on: {node.dependencies}")

    def _has_cycles(self) -> bool:
        """
        Detect circular dependencies using DFS.

        Returns:
            True if cycles exist, False otherwise
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def visit(node_name: str, path: List[str]) -> bool:
            """DFS visit with cycle detection."""
            if node_name in rec_stack:
                # Cycle detected
                cycle_start = path.index(node_name)
                cycle = path[cycle_start:] + [node_name]
                logger.error(f"Cycle detected: {' → '.join(cycle)}")
                return True

            if node_name in visited:
                return False

            visited.add(node_name)
            rec_stack.add(node_name)
            path.append(node_name)

            # Visit dependencies (reverse direction for cycle detection)
            node = self.dag[node_name]
            for dep_name in node.dependencies:
                if visit(dep_name, path.copy()):
                    return True

            rec_stack.remove(node_name)
            return False

        # Check all nodes
        for node_name in self.dag:
            if node_name not in visited:
                if visit(node_name, []):
                    return True

        return False

    def _compute_levels(self) -> None:
        """
        Compute topological levels for parallel execution.

        Level 0: Nodes with no dependencies
        Level N: Nodes whose dependencies are all at level < N

        Nodes at the same level can execute in parallel.
        """
        # Find nodes with no dependencies (level 0)
        level_queue: List[str] = [
            name for name, node in self.dag.items() if not node.dependencies
        ]

        for node_name in level_queue:
            self.dag[node_name].level = 0

        # Process levels
        current_level = 0
        while level_queue:
            next_queue: List[str] = []

            for node_name in level_queue:
                node = self.dag[node_name]

                # Check dependents
                for dependent_name in node.dependents:
                    dependent = self.dag[dependent_name]

                    # Can we schedule this dependent?
                    dep_levels = [
                        self.dag[dep].level
                        for dep in dependent.dependencies
                        if dep in self.dag
                    ]

                    if dep_levels and all(lvl >= 0 for lvl in dep_levels):
                        # All dependencies resolved
                        dependent.level = max(dep_levels) + 1

                        if dependent_name not in next_queue:
                            next_queue.append(dependent_name)

            level_queue = next_queue
            current_level += 1

    def get_execution_order(self) -> List[Step]:
        """
        Get steps in topological execution order.

        Returns:
            List of Steps ordered by dependencies

        Example:
            >>> for step in builder.get_execution_order():
            ...     print(f"{step.name} at level {builder.dag[step.name].level}")
        """
        # Sort by level, then by name for determinism
        sorted_nodes = sorted(self.dag.values(), key=lambda n: (n.level, n.name))

        return [node.step for node in sorted_nodes]

    def get_parallel_batches(self) -> List[List[Step]]:
        """
        Get steps grouped by topological level for parallel execution.

        Returns:
            List of batches, where each batch contains steps that can run in parallel

        Example:
            >>> batches = builder.get_parallel_batches()
            >>> for i, batch in enumerate(batches):
            ...     print(f"Level {i}: {[s.name for s in batch]}")
        """
        # Group by level
        levels: Dict[int, List[Step]] = {}
        for node in self.dag.values():
            if node.level not in levels:
                levels[node.level] = []
            levels[node.level].append(node.step)

        # Convert to sorted list
        max_level = max(levels.keys()) if levels else -1
        batches = [levels.get(i, []) for i in range(max_level + 1)]

        return batches

    def get_dependencies(self, step_name: str) -> List[str]:
        """
        Get direct dependencies for a step.

        Args:
            step_name: Name of the step

        Returns:
            List of step names this step depends on

        Example:
            >>> deps = builder.get_dependencies("transform_gold")
            >>> print(f"Must run before gold: {deps}")
        """
        if step_name not in self.dag:
            return []
        return self.dag[step_name].dependencies.copy()

    def get_dependents(self, step_name: str) -> List[str]:
        """
        Get steps that depend on this step.

        Args:
            step_name: Name of the step

        Returns:
            List of step names that depend on this step

        Example:
            >>> dependents = builder.get_dependents("transform_silver")
            >>> print(f"Will run after silver: {dependents}")
        """
        if step_name not in self.dag:
            return []
        return self.dag[step_name].dependents.copy()

    def visualize(self) -> str:
        """
        Generate text visualization of DAG.

        Returns:
            Multi-line string showing DAG structure

        Example:
            >>> print(builder.visualize())
        """
        lines = ["=" * 70, "DAG Structure", "=" * 70, ""]

        batches = self.get_parallel_batches()

        for level, batch in enumerate(batches):
            lines.append(f"Level {level}:")
            for step in batch:
                node = self.dag[step.name]
                deps_str = ", ".join(node.dependencies) if node.dependencies else "none"
                lines.append(f"  - {step.name} (depends on: {deps_str})")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)

    def export_mermaid(self) -> str:
        """
        Export DAG as Mermaid diagram syntax.

        Returns:
            Mermaid graph definition

        Example:
            >>> mermaid = builder.export_mermaid()
            >>> with open("dag.md", "w") as f:
            ...     f.write(f"```mermaid\\n{mermaid}\\n```")
        """
        lines = ["graph TD"]

        # Add nodes
        for node in self.dag.values():
            # Color by layer
            layer_colors = {
                "ingest": "fill:#e1f5ff",
                "store": "fill:#fff3e0",
                "transform": "fill:#f3e5f5",
                "publish": "fill:#e8f5e9",
            }
            color = layer_colors.get(node.step.layer, "fill:#fafafa")

            lines.append(f"    {node.name}[{node.name}]")
            lines.append(f"    style {node.name} {color}")

        # Add edges
        for node in self.dag.values():
            for dep in node.dependencies:
                lines.append(f"    {dep} --> {node.name}")

        return "\n".join(lines)
