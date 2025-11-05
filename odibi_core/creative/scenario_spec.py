"""
Scenario Specification for Advanced Showcases
==============================================
Defines data structures for scenario metadata and pipeline specs.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Any
import hashlib
import json


@dataclass
class ScenarioSpec:
    """Complete specification for a showcase scenario."""
    id: int
    domain: str
    batch_type: str  # "domain", "format", "transformation", "performance"
    archetype: str  # "fan_in", "star_schema", "windowed_kpi", etc.
    dag_topology: str  # "Linear", "FanIn", "FanOut", "Diamond", "Star", "Parallel"
    complexity_level: str  # "moderate", "high", "extreme"
    
    # Data elements
    formats: Set[str] = field(default_factory=set)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    transforms: List[str] = field(default_factory=list)
    kpis: List[str] = field(default_factory=list)
    windows: Dict[str, str] = field(default_factory=dict)
    error_injections: List[str] = field(default_factory=list)
    
    # Performance toggles
    perf: Dict[str, Any] = field(default_factory=lambda: {
        "cache_enabled": True,
        "parallel": True,
        "max_workers": 4
    })
    
    # Metadata for rich explanations
    title: str = ""
    backstory: str = ""
    data_goal: str = ""
    entities: List[str] = field(default_factory=list)
    problem_statement: str = ""
    design_rationale: str = ""
    trade_offs: str = ""
    
    @property
    def fingerprint(self) -> str:
        """Generate unique fingerprint for deduplication."""
        components = [
            self.domain,
            self.archetype,
            self.dag_topology,
            tuple(sorted(self.formats)),
            tuple(sorted(self.transforms)),
            tuple(sorted(self.kpis)),
            frozenset(self.windows.items()) if self.windows else frozenset(),
            tuple(sorted(self.error_injections))
        ]
        hash_str = json.dumps([str(c) for c in components], sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()[:16]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d['formats'] = list(self.formats)
        d['fingerprint'] = self.fingerprint
        return d


@dataclass
class ShowcaseMetadata:
    """Metadata for a generated showcase."""
    showcase_id: int
    title: str
    domain: str
    backstory: str
    data_goal: str
    dag_topology: str
    complexity_level: str
    batch_type: str
    archetype: str
    kpis: List[str]
    formats: List[str]
    errors_injected: List[str]
    windows: Dict[str, str]
    perf_toggles: Dict[str, Any]
    entities: List[str]
    problem_statement: str
    design_rationale: str
    trade_offs: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
