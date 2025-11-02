"""
ODIBI CORE v1.0

A Node-centric, engine-agnostic, config-driven data engineering framework.

Design Principles:
- Node is Law: Every operation is a Node
- Config Drives All: Pipelines defined by configs, not code
- Engine Agnostic: Spark and Pandas share identical Node contracts
- Truth Preserving: Full execution lineage and snapshots
- Composable and Replaceable: Nodes run independently
"""

from odibi_core.__version__ import __version__, __author__, __phase__
