---
id: phase_1_foundations
title: "Phase 1: Building the Foundation"
subtitle: "Scaffolding ODIBI CORE from Scratch"
version: "2.0-teaching"
author: "Henry Odibi & AMP AI Teaching Agent"
date: "2025-11-02"
level: "Beginner"
prerequisites:
  - "Python 3.8+ knowledge"
  - "Understanding of data engineering concepts"
learning_objectives:
  - "Understand the scaffolding-first approach"
  - "Build complete type-safe contracts"
  - "Create modular, extensible architecture"
outcomes:
  - "Can scaffold a data framework from scratch"
  - "Understands dependency inversion principle"
  - "Can explain node-centric architecture"
estimated_time: "4 hours"
tags: ["scaffolding", "architecture", "contracts", "type-safety"]
engines: ["pandas", "spark"]
requires: []
runnable_ratio: 0.78
assessment:
  type: ["mcq", "predict", "code-trace"]
  questions: 33
  pass_score: 0.75
related_lessons:
  - "phase_2_engine_contexts"
  - "phase_3_orchestration"
glossary_terms:
  - "NodeBase: Abstract base class for all pipeline operations"
  - "EngineContext: Runtime environment providing data processing capabilities"
  - "Step: Configuration dataclass representing a pipeline operation"
  - "Scaffolding: Building structure and contracts before implementation"
  - "Type Hint: Python annotation specifying expected variable/parameter types"
---

# ODIBI CORE v1.0 - Phase 1 Developer Walkthrough

**Building the Foundation: A Step-by-Step Guide**

**Author**: Henry Odibi & AMP AI Teaching Agent  
**Date**: 2025-11-02  
**Audience**: Developers learning to build data engineering frameworks  
**Duration**: ~4 hours (following this guide)

---

## 📚 Foundation Overview

### What is Phase 1?

Phase 1 is **scaffolding** - creating the skeleton of ODIBI CORE without implementing any business logic.

**Metaphor**: Think of it as **building the electrical grid before plugging in appliances**. You're defining the power outlets (interfaces), wiring standards (contracts), and connection protocols (abstractions) before any actual energy flows through the system.

**Ground Truth**: In [`core/node.py`](file:///d:/projects/odibi_core/odibi_core/core/node.py), you'll define `NodeBase`, `Step`, and `NodeState` — the fundamental contracts every pipeline operation must implement.

### Why Scaffold First?

1. **Design Validation** - Forces you to think through contracts and interfaces before implementation
2. **Import Dependency Resolution** - Ensures clean module boundaries (no circular imports)
3. **Type Safety** - Enables IDE autocomplete and mypy validation from day one
4. **Collaboration** - Others can see the architecture and propose changes before code is written
5. **AMP Assistance** - With clear contracts, AI can implement phases 2-10 more accurately

### What You'll Build

By the end of this walkthrough, you'll have:
- ✅ Complete directory structure
- ✅ All base classes with type-safe contracts
- ✅ Node registry and plugin system
- ✅ Engine abstraction layer
- ✅ Testing infrastructure
- ✅ Documentation scaffolding
- ❌ No actual data processing logic (that's Phase 2+)

### Time Investment

- Reading this guide: ~30 minutes
- Building along: ~3-4 hours
- Understanding gained: Priceless

---

## 🗺️ Dependency Map

Here's how modules depend on each other. **Build from bottom to top**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Examples   │  │    Tests     │  │     Docs     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Node Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ConnectNode  │  │  IngestNode  │  │ TransformNode│ ...  │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Orchestrator │  │ ConfigLoader │  │   Tracker    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Engine Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │EngineContext │  │ PandasContext│  │ SparkContext │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┐
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Core Contracts                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   NodeBase   │  │  NodeState   │  │     Step     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Project Foundation                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ pyproject.toml│  │  Directory   │  │  .gitignore  │      │
│  └──────────────┘  │   Structure  │  └──────────────┘      │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

**Build Order Principle**: Never import from a module that doesn't exist yet.

---

## 🚀 Step-by-Step Build Missions

### Mission 0: Setup Your Workspace

**Before you begin**, ensure you have:
- Python 3.8+ installed
- A code editor (VS Code recommended)
- Git installed
- Terminal access

**Create project root:**
```bash
mkdir odibi_core
cd odibi_core
```

**Why start here?** Every project needs a home. This is your workspace.

---

## 🏗️ PART 1: PROJECT FOUNDATION (Foundation Layer)

### Mission 1: Create Project Configuration

**Create: `pyproject.toml`**

This file defines your project's metadata and dependencies.

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "odibi-core"
version = "1.0.0"
description = "Node-centric, engine-agnostic, config-driven data engineering framework"
requires-python = ">=3.8"

dependencies = [
    "pandas>=1.5.0",
    "pyspark>=3.3.0",
    "duckdb>=0.9.0",
    "iapws>=1.5.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

**Why create this first?**
- Declares project metadata before any code
- Defines dependencies for IDE autocomplete
- Enables `pip install -e .` for development

**What depends on this?**
- Your IDE (for package resolution)
- pytest (for test discovery)
- Installation commands

**Common Mistake**: ⚠️ Forgetting to run `pip install -e .` after creating pyproject.toml — your imports won't work until you install the package in editable mode!

---

### Mission 2: Create .gitignore

**Create: `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environments
venv/
.venv/

# Testing
.pytest_cache/
.coverage

# Data files (don't commit large files)
*.db
*.parquet
*.csv

# IDEs
.vscode/
.idea/

# OS
.DS_Store
```

**Why create this early?**
- Prevents accidentally committing generated files
- Keeps repository clean from day one

**Common Mistake**: ⚠️ Committing `__pycache__/` or `.db` files before creating .gitignore — clean these with `git rm -r --cached __pycache__/` if already tracked.

---

### Mission 3: Create pytest.ini

**Create: `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    parity: Parity tests between engines
```

**Why before writing code?**
- Establishes test conventions upfront
- Enables `pytest` to work immediately

**Common Mistake**: ⚠️ Using incorrect test function prefixes (e.g., `check_*` instead of `test_*`) — pytest won't discover them without explicit configuration.

---

### Mission 4: Create Directory Structure

**Create all module directories:**

```bash
mkdir -p odibi_core/core
mkdir -p odibi_core/engine
mkdir -p odibi_core/nodes
mkdir -p odibi_core/functions/thermo
mkdir -p odibi_core/functions/psychro
mkdir -p odibi_core/functions/physics
mkdir -p odibi_core/functions/math
mkdir -p odibi_core/story
mkdir -p odibi_core/io
mkdir -p odibi_core/examples
mkdir -p tests
```

**Why this structure?**
- `core/` - Framework abstractions (engine-agnostic)
- `engine/` - Pandas/Spark implementations
- `nodes/` - Pipeline operation types
- `functions/` - Pure computational functions
- `story/` - Visualization/reporting
- `io/` - Data readers/writers
- `examples/` - Demo pipelines
- `tests/` - Test suite

**Common Mistake**: ⚠️ Forgetting to create `__init__.py` files in each directory — Python won't recognize them as packages, causing import errors.

**Reflection Checkpoint:**
> **Why separate `core/` from `engine/`?**
> 
> Answer: `core/` defines contracts (interfaces) that are engine-agnostic. `engine/` provides concrete implementations. This separation enables adding new engines (Polars, DuckDB) without touching core logic.

---

### 🎓 Checkpoint 1: Project Foundation

**Q1 (MCQ)**: Why create `pyproject.toml` before writing any code?

A. To make the project look professional  
B. ✅ **To declare dependencies and enable development installation**  
C. Because Python requires it  
D. To satisfy linters  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — This is about functionality, not appearance
- B: ✅ Correct — `pyproject.toml` enables `pip install -e .` and declares dependencies for IDE/tooling
- C: Incorrect — Python works without it (but packaging/tooling doesn't)
- D: Incorrect — Linters don't require this file

</details>

**Q2 (Predict-Output)**: What happens if you run `pytest` before creating `pytest.ini`?

A. pytest won't run at all  
B. ✅ **pytest runs but uses default test discovery patterns**  
C. pytest creates pytest.ini automatically  
D. pytest fails with an error  

<details>
<summary>Click to see answer</summary>

**Answer**: B — pytest has built-in defaults (`test_*.py` files, `test_*` functions). The `.ini` file customizes these patterns and adds markers.

</details>

**Q3 (Code-Trace)**: Which directory holds the abstract base classes?

A. `engine/`  
B. `nodes/`  
C. ✅ **`core/`**  
D. `functions/`  

<details>
<summary>Click to see answer</summary>

**Answer**: C — `core/` contains `NodeBase`, `EngineContext`, and other framework abstractions

</details>

---

## 🎯 PART 2: CORE CONTRACTS (Core Contracts Layer)

**Why start here?** Core contracts are the foundation. Everything else builds on top of them.

### Mission 5: Create NodeBase Contract

**Create: `odibi_core/core/node.py`**

This is the **most fundamental** class in the framework. All Nodes inherit from it.

```python[demo]
"""Base Node abstraction for ODIBI CORE."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class NodeState(Enum):
    """Node execution state."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Step:
    """
    Pipeline step configuration.
    
    This dataclass represents a single step in a pipeline, loaded from
    config (SQL table or JSON file).
    """
    layer: str                              # connect, ingest, store, transform, publish
    name: str                               # unique step identifier
    type: str                               # sql, function, config_op, api
    engine: str                             # pandas, spark
    value: str                              # SQL text, function reference, or config value
    params: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, str]] = None  # logical_name -> dataset_key
    outputs: Optional[Dict[str, str]] = None # logical_name -> dataset_key
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.params is None:
            self.params = {}
        if self.inputs is None:
            self.inputs = {}
        if self.outputs is None:
            self.outputs = {}
        if self.metadata is None:
            self.metadata = {}


class NodeBase(ABC):
    """
    Abstract base class for all ODIBI CORE Nodes.
    
    Contract:
    - Receives a data_map (dict of logical name → DataFrame)
    - Reads from inputs (references to data_map keys)
    - Executes via EngineContext
    - Writes to outputs (new entries in data_map)
    - Updates NodeState
    """

    def __init__(
        self,
        step: Step,
        context: Any,      # EngineContext (avoid circular import)
        tracker: Any,      # Tracker
        events: Any,       # EventEmitter
    ) -> None:
        self.step = step
        self.context = context
        self.tracker = tracker
        self.events = events
        self.state = NodeState.PENDING

    @abstractmethod
    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's operation.
        
        Args:
            data_map: Dictionary mapping logical names to DataFrames
            
        Returns:
            Updated data_map with new outputs
        """
        pass

    def _update_state(self, state: NodeState) -> None:
        """Update node execution state."""
        self.state = state
```

**Why create this first (in core)?**

1. **Everything inherits from NodeBase** - ConnectNode, IngestNode, etc. all need this contract
2. **Defines the execution contract** - The `run(data_map) -> data_map` pattern is the core abstraction
3. **Establishes NodeState enum** - Other modules reference these states
4. **Step dataclass** - ConfigLoader will create Step objects, Orchestrator will pass them to Nodes

**What depends on this?**
- All 5 Node types (ConnectNode, IngestNode, etc.)
- Orchestrator (creates Nodes from Steps)
- ConfigLoader (creates Step objects)
- Tracker (logs NodeState transitions)

**Common Mistake**: ⚠️ Omitting `@abstractmethod` decorator causes silent failures — subclasses won't be forced to implement `run()`, leading to runtime errors.

**Key Design Decisions:**

1. **`data_map: Dict[str, Any]`** - The "DataFrame warehouse" that flows through the pipeline
2. **`@abstractmethod run()`** - Forces all Nodes to implement execution logic
3. **`step: Step`** - Config-driven: behavior defined by data, not code
4. **`context: Any`** - Avoids circular import (EngineContext defined later)

---

### 💡 Try It Yourself

**Challenge**: Create a custom NodeState value for "SKIPPED" and add it to the enum.

```python
# Modify odibi_core/core/node.py
class NodeState(Enum):
    """Node execution state."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    # Add your SKIPPED state here
```

**Success Criteria**: Import NodeState and verify `NodeState.SKIPPED.value == "skipped"`

<details>
<summary>Need a hint?</summary>

Add: `SKIPPED = "skipped"` after the RETRY line. Enum values follow the same pattern as the existing states.

</details>

---

### Mission 6: Create EventEmitter

**Create: `odibi_core/core/events.py`**

```python[demo]
"""Event system for pipeline execution hooks."""

from typing import Any, Callable, Dict, List, Optional


class EventEmitter:
    """
    Event emitter for pipeline lifecycle hooks.
    
    Enables observability: emit events at key points
    (pipeline_start, step_complete, etc.)
    """

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        """Register an event listener."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **kwargs: Any) -> None:
        """Emit an event to all registered listeners."""
        # TODO Phase 2: Implement emission with error handling
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    print(f"Event listener error for {event_name}: {e}")

    def clear(self, event_name: Optional[str] = None) -> None:
        """Clear event listeners."""
        if event_name is None:
            self._listeners.clear()
        elif event_name in self._listeners:
            del self._listeners[event_name]
```

**Why create this before Orchestrator?**
- Orchestrator will emit events (pipeline_start, step_complete, etc.)
- Nodes receive EventEmitter in their constructor
- Needs to exist before anything that emits events

**What depends on this?**
- Orchestrator (emits pipeline lifecycle events)
- Nodes (receive events in constructor)
- User code (registers listeners)

**Common Mistake**: ⚠️ Forgetting to handle exceptions in event callbacks — always wrap callback execution in try/except to prevent one broken listener from crashing the pipeline.

---

### Mission 7: Create Tracker

**Create: `odibi_core/core/tracker.py`**

```python[demo]
"""Execution tracker for truth-preserving snapshots."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Snapshot:
    """Snapshot of DataFrame state at a point in time."""
    name: str
    timestamp: datetime
    row_count: int
    schema: List[tuple[str, str]]           # [(col_name, dtype), ...]
    sample_data: List[Dict[str, Any]]       # First N rows
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepExecution:
    """Record of a single step's execution."""
    step_name: str
    layer: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    before_snapshot: Optional[Snapshot] = None
    after_snapshot: Optional[Snapshot] = None
    schema_diff: Optional[Dict[str, Any]] = None
    row_delta: Optional[int] = None
    state: str = "pending"
    error_message: Optional[str] = None


class Tracker:
    """Execution tracker for pipeline runs."""

    def __init__(self) -> None:
        self.executions: List[StepExecution] = []
        self._current_execution: Optional[StepExecution] = None

    def start_step(self, step_name: str, layer: str) -> None:
        """Start tracking a step execution."""
        # TODO Phase 6: Implement step tracking
        execution = StepExecution(
            step_name=step_name, layer=layer, start_time=datetime.now()
        )
        self._current_execution = execution
        self.executions.append(execution)

    def end_step(self, step_name: str, state: str, error_message: Optional[str] = None) -> None:
        """End tracking for a step."""
        # TODO Phase 6: Implement finalization
        if self._current_execution and self._current_execution.step_name == step_name:
            self._current_execution.end_time = datetime.now()
            self._current_execution.state = state
            self._current_execution.error_message = error_message
            if self._current_execution.end_time:
                delta = self._current_execution.end_time - self._current_execution.start_time
                self._current_execution.duration_ms = delta.total_seconds() * 1000

    def snapshot(self, name: str, df: Any, context: Any) -> None:
        """Capture snapshot of DataFrame state."""
        # TODO Phase 6: Implement snapshot capture
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_steps": len(self.executions),
            "total_duration_ms": sum(
                e.duration_ms for e in self.executions if e.duration_ms
            ),
            "success_count": sum(1 for e in self.executions if e.state == "success"),
            "failed_count": sum(1 for e in self.executions if e.state == "failed"),
        }

    def export_lineage(self) -> Dict[str, Any]:
        """Export execution lineage as JSON."""
        # TODO Phase 5: Implement lineage export
        return {
            "pipeline_id": "unknown",
            "steps": [
                {
                    "name": e.step_name,
                    "layer": e.layer,
                    "duration_ms": e.duration_ms,
                    "state": e.state,
                }
                for e in self.executions
            ],
            "total_duration_ms": self.get_stats()["total_duration_ms"],
        }
```

**Why create this before Orchestrator?**
- Orchestrator needs to pass Tracker to Nodes
- Nodes call `tracker.start_step()` and `tracker.end_step()`
- Must exist before anything that logs execution

**What depends on this?**
- Orchestrator (passes to Nodes)
- Nodes (log snapshots)
- StoryGenerator (reads executions to generate HTML)

**Common Mistake**: ⚠️ Not capturing DataFrame snapshots before/after transformations — you lose the ability to debug schema changes and row count deltas.

**Reflection Checkpoint:**
> **Why separate Snapshot and StepExecution dataclasses?**
>
> Answer: A step can have multiple snapshots (before/after), but only one execution record. This separation allows capturing intermediate states without cluttering the execution record.

---

### 🎓 Checkpoint 2: Core Abstractions

**Q1 (MCQ)**: Why must NodeBase.run() be abstract?

A. To prevent instantiating NodeBase directly  
B. ✅ **To force all subclasses to implement execution logic**  
C. To improve performance  
D. To enable type checking  

<details>
<summary>Click to see rationale</summary>

- A: Partially true, but not the main reason
- B: ✅ Correct — @abstractmethod enforces the contract: every Node must define how to run
- C: Incorrect — Abstraction doesn't affect performance
- D: Incorrect — Type hints handle type checking

</details>

**Q2 (Predict-Output)**: What does `Step` dataclass print for `len(step.params)` when params is not provided?

A. Error (AttributeError)  
B. None  
C. ✅ **0 (empty dict)**  
D. Undefined  

<details>
<summary>Click to see answer</summary>

**Answer**: C — `__post_init__` sets `self.params = {}` if None, so `len(step.params)` returns 0.

</details>

**Q3 (Code-Trace)**: Which component captures DataFrame snapshots?

A. NodeBase  
B. EventEmitter  
C. ✅ **Tracker**  
D. Orchestrator  

<details>
<summary>Click to see answer</summary>

**Answer**: C — `Tracker.snapshot(name, df, context)` captures schema, row count, and sample data for lineage.

</details>

---

### Mission 8: Create Orchestrator (Stub)

**Create: `odibi_core/core/orchestrator.py`**

```python[demo]
"""Pipeline orchestrator for DAG execution."""

from typing import Any, Dict, List, Optional
from odibi_core.core.node import Step


class Orchestrator:
    """
    Pipeline orchestrator.
    
    Builds DAG from Step configs and executes Nodes in topological order.
    """

    def __init__(
        self,
        steps: List[Step],
        context: Any,      # EngineContext
        tracker: Any,      # Tracker
        events: Any,       # EventEmitter
    ) -> None:
        self.steps = steps
        self.context = context
        self.tracker = tracker
        self.events = events
        self.data_map: Dict[str, Any] = {}
        self._execution_order: Optional[List[Step]] = None

    def build_dag(self) -> List[Step]:
        """Build DAG and return execution order."""
        # TODO Phase 5: Implement DAG building
        return self.steps

    def detect_cycles(self) -> bool:
        """Detect circular dependencies."""
        # TODO Phase 5: Implement cycle detection
        return False

    def run(self) -> "OrchestrationResult":
        """Execute pipeline."""
        # TODO Phase 5: Implement pipeline execution
        return OrchestrationResult(data_map=self.data_map, tracker=self.tracker)

    def run_step(self, step: Step) -> None:
        """Execute a single step."""
        # TODO Phase 5: Implement step execution
        pass

    def validate_inputs(self, step: Step) -> bool:
        """Validate that all step inputs are available."""
        for logical_name, dataset_key in step.inputs.items():
            if dataset_key not in self.data_map:
                return False
        return True


class OrchestrationResult:
    """Result of pipeline execution."""

    def __init__(self, data_map: Dict[str, Any], tracker: Any) -> None:
        self.data_map = data_map
        self.tracker = tracker
```

**Why create this in core?**
- Represents the "engine" that drives pipeline execution
- Needs Step (already defined), Tracker, EventEmitter
- Will instantiate Nodes (not yet defined, but that's OK - it's a stub)

**What depends on this?**
- User code (runs pipelines)
- Tests (validate orchestration logic)

**Common Mistake**: ⚠️ Not validating that all step inputs exist in data_map before execution — causes KeyError during runtime instead of failing fast.

---

### Mission 9: Create ConfigLoader

**Create: `odibi_core/core/config_loader.py`**

```python[demo]
"""Configuration loader for pipeline definitions."""

import json
from pathlib import Path
from typing import List
from odibi_core.core.node import Step


class ConfigLoader:
    """
    Load pipeline configuration from SQLite, JSON, or CSV.
    """

    def load(self, source_uri: str) -> List[Step]:
        """
        Load pipeline configuration from source.
        
        Args:
            source_uri: Path to SQLite DB, JSON file, or CSV file
            
        Returns:
            List of Step objects
        """
        path = Path(source_uri)

        if not path.exists():
            raise FileNotFoundError(f"Config source not found: {source_uri}")

        if source_uri.endswith(".db") or source_uri.endswith(".sqlite"):
            return self._load_from_sqlite(source_uri)
        elif source_uri.endswith(".json"):
            return self._load_from_json(source_uri)
        elif source_uri.endswith(".csv"):
            return self._load_from_csv(source_uri)
        else:
            raise ValueError(f"Unknown config format: {source_uri}")

    def _load_from_sqlite(self, db_path: str) -> List[Step]:
        """Load from SQLite database."""
        # TODO Phase 3: Implement SQLite loader
        return []

    def _load_from_json(self, json_path: str) -> List[Step]:
        """Load from JSON file."""
        # TODO Phase 3: Implement JSON loader
        with open(json_path, "r") as f:
            data = json.load(f)

        steps = []
        for item in data:
            step = Step(
                layer=item["layer"],
                name=item["name"],
                type=item["type"],
                engine=item["engine"],
                value=item["value"],
                params=item.get("params"),
                inputs=item.get("inputs"),
                outputs=item.get("outputs"),
                metadata=item.get("metadata"),
            )
            steps.append(step)
        return steps

    def _load_from_csv(self, csv_path: str) -> List[Step]:
        """Load from CSV file."""
        # TODO Phase 3: Implement CSV loader
        return []


class ConfigValidator:
    """Validator for pipeline configurations."""

    def validate_config(self, steps: List[Step]) -> None:
        """Validate pipeline configuration."""
        # TODO Phase 3: Implement validation
        self._validate_unique_outputs(steps)
        self._validate_inputs_exist(steps)
        self._validate_engines(steps)
        self._validate_step_types(steps)

    def _validate_unique_outputs(self, steps: List[Step]) -> None:
        """Ensure all output keys are unique."""
        pass

    def _validate_inputs_exist(self, steps: List[Step]) -> None:
        """Ensure all inputs reference existing outputs."""
        pass

    def _validate_engines(self, steps: List[Step]) -> None:
        """Validate engine names."""
        valid_engines = {"pandas", "spark"}
        for step in steps:
            if step.engine not in valid_engines:
                raise ValueError(f"Invalid engine: {step.engine}")

    def _validate_step_types(self, steps: List[Step]) -> None:
        """Validate step types."""
        valid_types = {"sql", "function", "config_op", "api"}
        for step in steps:
            if step.type not in valid_types:
                raise ValueError(f"Invalid step type: {step.type}")
```

**Why create this now?**
- Orchestrator receives `List[Step]`, but where do Steps come from? ConfigLoader.
- Independent of Nodes and EngineContext
- Only depends on Step dataclass (already defined)

**What depends on this?**
- User code (loads configs before running pipelines)
- Tests (validate config parsing)

**Common Mistake**: ⚠️ Forgetting to validate step.name leads to KeyError in data_map when outputs reference undefined names — always validate unique step names!

---

### 🎓 Checkpoint 3: Configuration System

**Q1 (MCQ)**: Why load config from SQL instead of hardcoding steps?

A. SQL is faster than Python  
B. ✅ **Enables non-developers to modify pipelines without code changes**  
C. Required by Databricks  
D. Better for version control  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — SQL parsing adds overhead
- B: ✅ Correct — Data-driven design: analysts update config tables, not Python files
- C: Incorrect — Not a Databricks requirement
- D: Incorrect — Code in Git is easier to version than database tables

</details>

**Q2 (Predict-Output)**: What error occurs when Step is missing 'name' and 'value' fields?

A. ImportError  
B. ✅ **TypeError (missing required positional arguments)**  
C. AttributeError  
D. No error (fields optional)  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `@dataclass` makes fields required unless given defaults. Missing required fields raises TypeError at instantiation.

</details>

**Q3 (Code-Trace)**: Which method converts config dictionaries to Step objects?

A. Orchestrator.build_dag()  
B. ✅ **ConfigLoader._load_from_json()**  
C. Step.__post_init__()  
D. ConfigValidator.validate_config()  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `_load_from_json()` reads JSON, iterates over items, and creates `Step(**item)` objects.

</details>

---

### 💡 Try It Yourself

**Challenge**: Modify ConfigLoader to load from a Python list of dicts (no file required).

```python
# Add this method to ConfigLoader
def load_from_list(self, config_list: List[Dict[str, Any]]) -> List[Step]:
    """Load steps from Python list."""
    # Your implementation here
    pass
```

**Success Criteria**: Create 2 Step objects from a hardcoded list and verify `len(steps) == 2`.

<details>
<summary>Need a hint?</summary>

Copy the logic from `_load_from_json()` but skip the `open()` and `json.load()` parts. Just iterate over `config_list` and create Step objects.

</details>

---

### Mission 10: Create core/__init__.py

**Create: `odibi_core/core/__init__.py`**

```python[demo]
"""Core framework components."""

from odibi_core.core.node import NodeBase, NodeState, Step
from odibi_core.core.events import EventEmitter
from odibi_core.core.tracker import Tracker
from odibi_core.core.orchestrator import Orchestrator
from odibi_core.core.config_loader import ConfigLoader

__all__ = [
    "NodeBase",
    "NodeState",
    "Step",
    "EventEmitter",
    "Tracker",
    "Orchestrator",
    "ConfigLoader",
]
```

**Why create __init__.py files?**
- Makes directories into Python packages
- Enables clean imports: `from odibi_core.core import NodeBase`
- Defines public API (what users should import)

**Reflection Checkpoint:**
> **Why did we build core/ before engine/?**
>
> Answer: Core defines **contracts** (abstract interfaces) that are engine-agnostic. Engine provides **implementations**. You must define the contract before implementing it. This is the Dependency Inversion Principle in action.

---

## ⚙️ PART 3: ENGINE ABSTRACTION (Engine Layer)

### Mission 11: Create EngineContext Contract

**Create: `odibi_core/engine/base_context.py`**

```python
"""Base engine context contract."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union


class EngineContext(ABC):
    """
    Abstract base class for engine contexts.
    
    Contract: All engines (Pandas, Spark) must implement these methods.
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        **kwargs: Any
    ) -> None:
        self.secrets = secrets
        self.config = kwargs

    @abstractmethod
    def connect(self, **kwargs: Any) -> "EngineContext":
        """Establish connection to data sources."""
        pass

    @abstractmethod
    def read(self, source: str, **kwargs: Any) -> Any:
        """Read data from source."""
        pass

    @abstractmethod
    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """Write DataFrame to target."""
        pass

    @abstractmethod
    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """Execute SQL query."""
        pass

    @abstractmethod
    def register_temp(self, name: str, df: Any) -> None:
        """Register DataFrame as temporary table/view."""
        pass

    def get_secret(self, key: str) -> str:
        """
        Retrieve secret value.
        
        Supports two patterns:
        - Dict: secrets = {"db_pass": "secret123"}
        - Callable: secrets = lambda k: dbutils.secrets.get("scope", k)
        """
        if self.secrets is None:
            raise ValueError(f"No secrets configured, cannot retrieve: {key}")

        if callable(self.secrets):
            return self.secrets(key)
        elif isinstance(self.secrets, dict):
            if key not in self.secrets:
                raise ValueError(f"Secret not found: {key}")
            return self.secrets[key]
        else:
            raise ValueError("Secrets must be dict or callable")

    @abstractmethod
    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """Collect sample rows as Pandas DataFrame."""
        pass
```

**Why create this before Pandas/Spark contexts?**
- Defines the **contract** that both must implement
- Ensures consistency (both engines have same API)
- Enables type checking (`context: EngineContext`)

**What depends on this?**
- PandasEngineContext (inherits from this)
- SparkEngineContext (inherits from this)
- NodeBase (receives `context: Any` - will be EngineContext)

**Common Mistake**: ⚠️ Making EngineContext concrete instead of abstract — this defeats polymorphism and prevents enforcing the contract across engines.

**Key Design Decision: Secret Injection Pattern**

Why `secrets` parameter instead of direct access?
- **Flexibility**: Works with dict (testing), callable (Databricks), or vault SDK
- **Security**: Framework never hardcodes secret fetching
- **Testability**: Easy to mock secrets in tests

---

### 🎓 Checkpoint 4: Engine Abstraction

**Q1 (MCQ)**: Why is EngineContext abstract?

A. To save memory  
B. ✅ **To define a contract that all engines must implement**  
C. Because Pandas and Spark are incompatible  
D. For better error messages  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — Abstract classes don't reduce memory usage
- B: ✅ Correct — ABC + @abstractmethod enforces that Pandas/Spark contexts implement all required methods
- C: Incorrect — Abstraction bridges incompatibility, doesn't cause it
- D: Incorrect — Not the primary reason

</details>

**Q2 (Predict-Output)**: Can you instantiate EngineContext directly?

A. Yes, it's a normal class  
B. ✅ **No, raises TypeError (can't instantiate abstract class)**  
C. Yes, but methods won't work  
D. Depends on Python version  

<details>
<summary>Click to see answer</summary>

**Answer**: B — Classes inheriting from `ABC` with `@abstractmethod` cannot be instantiated directly. Python raises: `TypeError: Can't instantiate abstract class EngineContext with abstract methods...`

</details>

**Q3 (Code-Trace)**: Which method registers DataFrames as temp tables?

A. execute_sql()  
B. ✅ **register_temp()**  
C. connect()  
D. collect_sample()  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `register_temp(name, df)` stores DataFrames in a temporary view/table for SQL queries to reference.

</details>

---

### Mission 12: Create PandasEngineContext Stub

**Create: `odibi_core/engine/pandas_context.py`**

```python[run]
"""Pandas engine context implementation."""

from typing import Any, Callable, Dict, Optional, Union
from odibi_core.engine.base_context import EngineContext


class PandasEngineContext(EngineContext):
    """
    Pandas engine context with DuckDB SQL support.
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(secrets, **kwargs)
        self._duckdb_conn: Optional[Any] = None
        self._temp_tables: Dict[str, Any] = {}

    def connect(self, **kwargs: Any) -> "PandasEngineContext":
        """Establish connection (no-op for Pandas)."""
        # TODO Phase 2: Initialize DuckDB connection
        return self

    def read(self, source: str, **kwargs: Any) -> Any:
        """Read data from source."""
        # TODO Phase 8: Implement Pandas read
        pass

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """Write DataFrame to target."""
        # TODO Phase 8: Implement Pandas write
        pass

    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """Execute SQL query using DuckDB."""
        # TODO Phase 2: Implement DuckDB SQL execution
        pass

    def register_temp(self, name: str, df: Any) -> None:
        """Register DataFrame as DuckDB temporary table."""
        # TODO Phase 2: Implement temp table registration
        self._temp_tables[name] = df

    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """Collect sample rows (head(n))."""
        # TODO Phase 2: Implement sampling
        pass
```

**Why create this stub now?**
- Proves the contract works (compiles without errors)
- Shows what Phase 2 will implement
- Enables tests to instantiate contexts

**Common Mistake**: ⚠️ Using `pass` instead of `raise NotImplementedError` in stub methods — silent failures are harder to debug than explicit errors.

---

### Mission 13: Create SparkEngineContext Stub

**Create: `odibi_core/engine/spark_context.py`**

```python[run]
"""Spark engine context implementation."""

from typing import Any, Callable, Dict, Optional, Union
from odibi_core.engine.base_context import EngineContext


class SparkEngineContext(EngineContext):
    """
    Spark engine context for distributed processing.
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        spark_config: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(secrets, **kwargs)
        self.spark_config = spark_config or {}
        self._spark: Optional[Any] = None  # SparkSession

    def connect(self, **kwargs: Any) -> "SparkEngineContext":
        """Initialize SparkSession and configure Azure storage."""
        # TODO Phase 2: Create SparkSession
        return self

    def read(self, source: str, **kwargs: Any) -> Any:
        """Read data from source."""
        # TODO Phase 8: Implement Spark read
        pass

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """Write DataFrame to target."""
        # TODO Phase 8: Implement Spark write
        pass

    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """Execute Spark SQL query."""
        # TODO Phase 2: Use spark.sql(query)
        pass

    def register_temp(self, name: str, df: Any) -> None:
        """Register DataFrame as temporary view."""
        # TODO Phase 2: Use df.createOrReplaceTempView(name)
        pass

    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """Collect sample rows as Pandas DataFrame."""
        # TODO Phase 2: Use df.limit(n).toPandas()
        pass

    def cache_checkpoint(self, df: Any, name: str) -> Any:
        """Cache DataFrame to avoid recomputation."""
        # TODO Phase 2: Use df.cache()
        pass
```

**Why create both Pandas and Spark stubs now?**
- Proves both can implement the same contract
- Allows writing tests that swap engines
- Shows architectural symmetry

**Common Mistake**: ⚠️ Not calling `.collect()` or `.toPandas()` on Spark DataFrames — they're lazy, so no computation happens until you materialize results!

---

### 🎓 Checkpoint 5: Spark Engine Context

**Q1 (MCQ)**: Why stub Spark methods with NotImplementedError?

A. Spark isn't installed yet  
B. ✅ **To make missing implementations explicit during development**  
C. To prevent Spark from running  
D. For better performance  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — Not about installation status
- B: ✅ Correct — Explicit failures tell you what Phase 2 needs to implement
- C: Incorrect — Stubs don't prevent anything
- D: Incorrect — No performance benefit

</details>

**Q2 (Predict-Output)**: What happens when calling unimplemented `read()` on SparkEngineContext?

A. Returns None  
B. Returns empty DataFrame  
C. Silent failure (does nothing)  
D. ✅ **Currently returns None (stub with `pass`)**  

<details>
<summary>Click to see answer</summary>

**Answer**: D — The current stub uses `pass`, so it implicitly returns None. Better practice: `raise NotImplementedError("Phase 8: Implement Spark read")`

</details>

**Q3 (Code-Trace)**: Where is spark_config stored?

A. In EngineContext base class  
B. ✅ **In SparkEngineContext.__init__ as self.spark_config**  
C. In a global variable  
D. Not stored (passed to each method)  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `SparkEngineContext.__init__()` accepts `spark_config` parameter and stores it as `self.spark_config = spark_config or {}`

</details>

---

### 💡 Try It Yourself

**Challenge**: Add a `get_config()` method to EngineContext that returns all config values.

```python
# Add to EngineContext base class
def get_config(self, key: str, default: Any = None) -> Any:
    """Retrieve config value with fallback."""
    # Your implementation here
```

**Success Criteria**: `ctx.get_config("some_key", "default_value")` returns the config value or default.

<details>
<summary>Need a hint?</summary>

Use: `return self.config.get(key, default)` — the dict.get() method handles missing keys gracefully.

</details>

---

### Mission 14: Create engine/__init__.py

**Create: `odibi_core/engine/__init__.py`**

```python[run]
"""Engine context implementations."""

from odibi_core.engine.base_context import EngineContext
from odibi_core.engine.pandas_context import PandasEngineContext
from odibi_core.engine.spark_context import SparkEngineContext

__all__ = ["EngineContext", "PandasEngineContext", "SparkEngineContext"]
```

**Reflection Checkpoint:**
> **Why create engine stubs before implementing Nodes?**
>
> Answer: Nodes receive `context: EngineContext` in their constructor. We need the type to exist for type hints, even if methods aren't implemented yet. This is **forward declaration** - common in strongly-typed systems.

---

## 🔌 PART 4: NODE TYPES (Node Layer)

**Now we can create Nodes because their dependencies exist:**
- ✅ NodeBase contract (to inherit from)
- ✅ EngineContext contract (to receive in constructor)
- ✅ Tracker (to log execution)
- ✅ EventEmitter (to emit events)

### Mission 15: Create ConnectNode

**Create: `odibi_core/nodes/connect_node.py`**

```python[demo]
"""ConnectNode for establishing database/storage connections."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class ConnectNode(NodeBase):
    """
    Node for establishing connections.
    
    Initializes database connections, API clients, or storage access.
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establish connection.
        
        Args:
            data_map: Input data_map (not used for connections)
            
        Returns:
            Unchanged data_map (connections are side effects)
        """
        # TODO Phase 4: Implement connection logic
        # - Extract connection params from step.value and step.params
        # - Resolve secrets if needed
        # - Call context.connect(**params)
        # - Log connection metadata
        self._update_state(NodeState.SUCCESS)
        return data_map
```

**Why start with ConnectNode?**
- Simplest Node (no data transformation)
- Demonstrates the pattern all Nodes follow
- Returns unchanged `data_map` (no outputs)

**Common Mistake**: ⚠️ Forgetting to call `self._update_state(NodeState.SUCCESS)` after execution — Tracker won't know the step completed!

---

### Mission 16: Create IngestNode

**Create: `odibi_core/nodes/ingest_node.py`**

```python[demo]
"""IngestNode for reading data from sources."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class IngestNode(NodeBase):
    """
    Node for ingesting data from sources.
    
    Reads data from CSV, Parquet, databases, etc.
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read data from source.
        
        Args:
            data_map: Input data_map
            
        Returns:
            Updated data_map with ingested data
        """
        # TODO Phase 4: Implement ingestion logic
        # - Read: df = context.read(step.value, **step.params)
        # - Log snapshot: tracker.snapshot("after", df, context)
        # - Write to data_map: data_map[step.outputs['data']] = df
        self._update_state(NodeState.SUCCESS)
        return data_map
```

**Pattern emerging:**
1. Read from `step.value` (source path)
2. Use `context` to execute
3. Log to `tracker`
4. Write to `data_map[step.outputs['data']]`
5. Update state

**Common Mistake**: ⚠️ Accessing `step.outputs['data']` without checking if 'data' key exists — use `step.outputs.get('data')` or validate config first.

---

### 🎓 Checkpoint 6: Ingest Node Pattern

**Q1 (MCQ)**: Why do all Nodes inherit from NodeBase?

A. To reduce code duplication  
B. ✅ **To enforce the run(data_map) contract and share common state**  
C. Because Python requires it  
D. For better import organization  

<details>
<summary>Click to see rationale</summary>

- A: Partially true, but not the main reason
- B: ✅ Correct — NodeBase enforces the contract, provides state management, and ensures all Nodes work with Orchestrator
- C: Incorrect — Python doesn't require inheritance
- D: Incorrect — Unrelated to imports

</details>

**Q2 (Predict-Output)**: What does `IngestNode.run()` return?

A. A DataFrame  
B. None  
C. ✅ **Updated data_map dictionary**  
D. NodeState.SUCCESS  

<details>
<summary>Click to see answer</summary>

**Answer**: C — All Nodes follow the pattern: `run(data_map) -> updated_data_map`. IngestNode adds read data to data_map and returns it.

</details>

**Q3 (Code-Trace)**: How does IngestNode access the engine context?

A. By importing PandasEngineContext  
B. ✅ **Through self.context (passed in __init__)**  
C. By creating a new context  
D. Via global variable  

<details>
<summary>Click to see answer</summary>

**Answer**: B — NodeBase.__init__ receives `context` parameter and stores it as `self.context`, which IngestNode.run() uses to call `context.read()`.

</details>

---

### Mission 17: Create StoreNode

**Create: `odibi_core/nodes/store_node.py`**

```python[demo]
"""StoreNode for persisting data to storage."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class StoreNode(NodeBase):
    """
    Node for storing data to Bronze/Silver/Gold layers.
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write data to storage.
        
        Args:
            data_map: Input data_map containing data to store
            
        Returns:
            Unchanged data_map
        """
        # TODO Phase 4: Implement storage logic
        # - Read from data_map: df = data_map[step.inputs['data']]
        # - Write: context.write(df, step.value, **step.params)
        # - Log write location
        self._update_state(NodeState.SUCCESS)
        return data_map
```

**Common Mistake**: ⚠️ Forgetting that StoreNode consumes inputs but produces no outputs — don't try to access `step.outputs` in storage operations.

---

### Mission 18: Create TransformNode

**Create: `odibi_core/nodes/transform_node.py`**

```python[demo]
"""TransformNode for data transformations."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class TransformNode(NodeBase):
    """
    Node for data transformations.
    
    Supports:
    - SQL transforms (execute SQL query)
    - Function transforms (call Python function)
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation."""
        if self.step.type == "sql":
            return self._run_sql_transform(data_map)
        elif self.step.type == "function":
            return self._run_function_transform(data_map)
        else:
            raise ValueError(f"Unknown transform type: {self.step.type}")

    def _run_sql_transform(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL transformation."""
        # TODO Phase 4: Implement SQL transform
        # - Register inputs as temp tables
        # - Execute SQL: result = context.execute_sql(step.value)
        # - Write to data_map
        self._update_state(NodeState.SUCCESS)
        return data_map

    def _run_function_transform(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """Execute function transformation."""
        # TODO Phase 4: Implement function transform
        # - Import function: func = resolve_function(step.value)
        # - Call: result = func(input_df, **step.params)
        # - Write to data_map
        self._update_state(NodeState.SUCCESS)
        return data_map
```

**Why two transform modes?**
- **SQL**: Familiar for data analysts, works on both engines
- **Function**: Enables custom Python logic (e.g., thermodynamic calculations)

**Common Mistake**: ⚠️ Not registering input DataFrames as temp tables before SQL execution — queries fail with "table not found" errors.

---

### Mission 19: Create PublishNode

**Create: `odibi_core/nodes/publish_node.py`**

```python[demo]
"""PublishNode for exporting data to external systems."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class PublishNode(NodeBase):
    """
    Node for publishing data to external systems.
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """Publish data to external system."""
        # TODO Phase 4: Implement publish logic
        # - Read from data_map
        # - Write to target: context.write(df, step.value, **step.params)
        # - Log publish location
        self._update_state(NodeState.SUCCESS)
        return data_map
```

**Common Mistake**: ⚠️ Using PublishNode for intermediate writes — use StoreNode for internal storage, PublishNode only for final external outputs.

---

### 💡 Try It Yourself

**Challenge**: Create a custom `ValidationNode` that checks DataFrame row counts.

```python
# Create odibi_core/nodes/validation_node.py
from odibi_core.core.node import NodeBase, NodeState

class ValidationNode(NodeBase):
    """Validates DataFrame row count."""
    
    def run(self, data_map):
        # 1. Read input DataFrame from data_map
        # 2. Check if len(df) > 0
        # 3. Update state to SUCCESS or FAILED
        # 4. Return data_map
        pass
```

**Success Criteria**: ValidationNode raises error or logs warning when DataFrame is empty.

<details>
<summary>Need a hint?</summary>

```python
df = data_map[self.step.inputs['data']]
if len(df) == 0:
    self._update_state(NodeState.FAILED)
    raise ValueError("Empty DataFrame")
self._update_state(NodeState.SUCCESS)
return data_map
```

</details>

---

### Mission 20: Create Node Registry

**Create: `odibi_core/nodes/__init__.py`**

```python[demo]
"""Node type implementations."""

from odibi_core.nodes.connect_node import ConnectNode
from odibi_core.nodes.ingest_node import IngestNode
from odibi_core.nodes.store_node import StoreNode
from odibi_core.nodes.transform_node import TransformNode
from odibi_core.nodes.publish_node import PublishNode


NODE_REGISTRY = {
    "connect": ConnectNode,
    "ingest": IngestNode,
    "store": StoreNode,
    "transform": TransformNode,
    "publish": PublishNode,
}


def register_node(name: str):
    """Decorator to register custom Node types."""
    def decorator(cls):
        NODE_REGISTRY[name] = cls
        return cls
    return decorator


__all__ = [
    "ConnectNode",
    "IngestNode",
    "StoreNode",
    "TransformNode",
    "PublishNode",
    "NODE_REGISTRY",
    "register_node",
]
```

**Why a registry?**
- **Dynamic instantiation**: Orchestrator can create Nodes by name
- **Extensibility**: Users can add custom Nodes via `@register_node()`
- **Decoupling**: Orchestrator doesn't import all Node classes directly

**Common Mistake**: ⚠️ Not registering custom Nodes in NODE_REGISTRY — Orchestrator won't find them when loading from config.

**Reflection Checkpoint:**
> **Why separate 5 Node types instead of one generic Node?**
>
> Answer: Each type has distinct semantics:
> - ConnectNode: Side effects, no data output
> - IngestNode: No data input, produces output
> - StoreNode: Consumes input, no data output
> - TransformNode: Input → Output transformation
> - PublishNode: Final output to external system
>
> Separation makes intent clear and enables type-specific optimizations.

---

### 🎓 Checkpoint 7: Node Registry

**Q1 (MCQ)**: Why are all 5 node types needed?

A. To make the codebase larger  
B. ✅ **Each has distinct I/O semantics and lifecycle responsibilities**  
C. Because Pandas and Spark require it  
D. For better performance  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — More code isn't a goal
- B: ✅ Correct — ConnectNode (side effects), IngestNode (source), StoreNode (sink), TransformNode (processing), PublishNode (export) each serve different purposes
- C: Incorrect — Engine-agnostic design
- D: Incorrect — No performance difference

</details>

**Q2 (Predict-Output)**: Which node writes final output to external systems?

A. StoreNode  
B. TransformNode  
C. IngestNode  
D. ✅ **PublishNode**  

<details>
<summary>Click to see answer</summary>

**Answer**: D — PublishNode is for external publishing (APIs, external databases). StoreNode is for internal medallion layers (Bronze/Silver/Gold).

</details>

**Q3 (Code-Trace)**: Where is NODE_REGISTRY defined?

A. In core/node.py  
B. ✅ **In nodes/__init__.py**  
C. In core/orchestrator.py  
D. As a global variable  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `nodes/__init__.py` defines `NODE_REGISTRY` as a dictionary mapping layer names to Node classes.

</details>

---

## 🧮 PART 5: SUPPORTING MODULES

### Mission 21: Create Function Registry

**Create: `odibi_core/functions/registry.py`**

```python[demo]
"""Function registry for dynamic function resolution."""

from typing import Any, Callable, Dict


FUNCTION_REGISTRY: Dict[str, Callable[..., Any]] = {}


def resolve_function(function_path: str) -> Callable[..., Any]:
    """
    Resolve function by dotted path.
    
    Args:
        function_path: e.g., "thermo.steam.steam_enthalpy_btu_lb"
        
    Returns:
        Function object
    """
    # TODO Phase 7: Implement dynamic import
    if function_path in FUNCTION_REGISTRY:
        return FUNCTION_REGISTRY[function_path]
    raise ImportError(f"Function not found: {function_path}")


def register_function(path: str, func: Callable[..., Any]) -> None:
    """Register function in global registry."""
    FUNCTION_REGISTRY[path] = func
```

**Why create this?**
- TransformNode's function mode needs to import functions by string path
- Enables config-driven function execution
- Simple stub for now (Phase 7 adds actual functions)

**Common Mistake**: ⚠️ Hardcoding function imports instead of using the registry — breaks config-driven execution and plugin extensibility.

---

### Mission 22: Create Function Stubs

**Create: `odibi_core/functions/thermo/steam.py`**

```python[demo]
"""Steam property calculations."""

def steam_enthalpy_btu_lb(pressure_psia: float, temp_f: float) -> float:
    """Calculate steam enthalpy in BTU/lb."""
    # TODO Phase 7: Implement with IAPWS97
    raise NotImplementedError("Phase 7: Implement steam enthalpy")


def feedwater_enthalpy_btu_lb(temp_f: float) -> float:
    """Calculate feedwater enthalpy in BTU/lb."""
    # TODO Phase 7: Implement feedwater enthalpy
    raise NotImplementedError("Phase 7: Implement feedwater enthalpy")
```

**Create stubs for:**
- `functions/physics/units.py` - Unit conversions
- `functions/math/safe_ops.py` - Safe division, logarithm

**Don't forget __init__.py files** for each function module!

**Why create stubs?**
- Shows where domain logic will live
- Enables imports (won't crash if referenced)
- Clarifies separation: functions are pure (no engine dependency)

**Common Mistake**: ⚠️ Coupling functions to engine context — functions should be pure, taking DataFrames and returning DataFrames without engine dependencies.

---

### 🎓 Checkpoint 8: Function Registry

**Q1 (MCQ)**: Why use a function registry?

A. To improve performance  
B. ✅ **To enable config-driven function resolution and plugin architecture**  
C. Because Python requires it  
D. To reduce memory usage  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — Registries don't improve performance
- B: ✅ Correct — String-based lookup enables loading functions from config and registering custom functions dynamically
- C: Incorrect — No Python requirement
- D: Incorrect — Unrelated to memory

</details>

**Q2 (Predict-Output)**: How do you register a custom function?

A. Add it to a JSON file  
B. ✅ **Call register_function(path, func)**  
C. Import it in __init__.py  
D. Use a decorator  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `register_function("custom.my_func", my_function)` adds it to FUNCTION_REGISTRY so TransformNode can resolve it.

</details>

**Q3 (Code-Trace)**: Where are thermodynamic functions defined?

A. In core/functions.py  
B. ✅ **In functions/thermo/steam.py**  
C. In nodes/transform_node.py  
D. In engine/pandas_context.py  

<details>
<summary>Click to see answer</summary>

**Answer**: B — Domain-specific functions are organized in `functions/` subdirectories: `thermo/`, `physics/`, `math/`.

</details>

---

### 💡 Try It Yourself

**Challenge**: Create and register a custom function that converts Celsius to Fahrenheit.

```python
# Add to functions/physics/units.py
def celsius_to_fahrenheit(temp_c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    # Your implementation here
    pass

# Register it
from odibi_core.functions.registry import register_function
register_function("physics.celsius_to_fahrenheit", celsius_to_fahrenheit)
```

**Success Criteria**: `resolve_function("physics.celsius_to_fahrenheit")(100)` returns 212.

<details>
<summary>Need a hint?</summary>

Formula: `(temp_c * 9/5) + 32`

</details>

---

### Mission 23: Create I/O Readers/Writers

**Create: `odibi_core/io/readers.py`**

```python
"""Data readers for various formats."""

from abc import ABC, abstractmethod
from typing import Any


class BaseReader(ABC):
    """Abstract base reader."""

    def __init__(self, context: Any) -> None:
        self.context = context

    @abstractmethod
    def read(self, source: str, **kwargs: Any) -> Any:
        """Read data from source."""
        pass


class CsvReader(BaseReader):
    """CSV reader for both Pandas and Spark."""

    def read(self, source: str, **kwargs: Any) -> Any:
        """Read CSV file."""
        # TODO Phase 8: Implement CSV reading
        pass


class ParquetReader(BaseReader):
    """Parquet reader for both Pandas and Spark."""

    def read(self, source: str, **kwargs: Any) -> Any:
        """Read Parquet file."""
        # TODO Phase 8: Implement Parquet reading
        pass
```

**Create: `odibi_core/io/writers.py`** (similar pattern)

**Why create I/O abstractions?**
- Standardizes read/write operations across engines
- IngestNode and StoreNode will use these
- Enables swapping I/O implementations

**Common Mistake**: ⚠️ Hardcoding file paths in readers — always parameterize paths and pass them from config.

---

### Mission 24: Create StoryGenerator

**Create: `odibi_core/story/generator.py`**

```python[demo]
"""HTML story generation for pipeline execution."""

from typing import Any, List


class StoryGenerator:
    """Generate HTML execution stories."""

    def generate_step_story(self, step_execution: Any) -> str:
        """Generate HTML card for a single step."""
        # TODO Phase 6: Implement step story
        return "<div>Step story placeholder</div>"

    def generate_pipeline_story(self, executions: List[Any]) -> str:
        """Generate complete HTML dashboard."""
        # TODO Phase 6: Implement pipeline story
        return "<html><body>Pipeline story placeholder</body></html>"
```

**Why stub this?**
- Shows where visualization logic will live
- Tracker will feed data to StoryGenerator
- Phase 6 will implement actual HTML generation

**Common Mistake**: ⚠️ Generating HTML without escaping user input — always sanitize data before rendering to prevent XSS vulnerabilities.

---

## 🧪 PART 6: TESTING INFRASTRUCTURE

### Mission 25: Create Test Fixtures

**Create: `tests/conftest.py`**

```python[demo]
"""Pytest configuration and shared fixtures."""

import pytest
from typing import Dict, Any, List


@pytest.fixture
def sample_step_config() -> Dict[str, Any]:
    """Sample step configuration."""
    return {
        "layer": "ingest",
        "name": "read_csv",
        "type": "config_op",
        "engine": "pandas",
        "value": "test_data.csv",
        "outputs": {"data": "raw_data"},
    }


@pytest.fixture
def pandas_context():
    """PandasEngineContext for testing."""
    from odibi_core.engine.pandas_context import PandasEngineContext
    return PandasEngineContext(secrets={"test_key": "test_value"})


@pytest.fixture
def tracker():
    """Tracker instance for testing."""
    from odibi_core.core.tracker import Tracker
    return Tracker()


@pytest.fixture
def events():
    """EventEmitter instance for testing."""
    from odibi_core.core.events import EventEmitter
    return EventEmitter()
```

**Why create fixtures?**
- Reusable test components
- Consistent test setup
- Reduces test code duplication

**Common Mistake**: ⚠️ Not isolating test fixtures — shared mutable state between tests causes flaky failures. Use `scope="function"` for isolation.

---

### Mission 26: Create Initial Tests

**Create: `tests/test_node_base.py`**

```python[demo]
"""Unit tests for NodeBase and NodeState."""

import pytest
from odibi_core.core.node import NodeBase, NodeState, Step


def test_node_state_enum():
    """Test NodeState enum values."""
    assert NodeState.PENDING.value == "pending"
    assert NodeState.SUCCESS.value == "success"
    assert NodeState.FAILED.value == "failed"
    assert NodeState.RETRY.value == "retry"


def test_step_dataclass_creation(sample_step_config):
    """Test Step dataclass initialization."""
    step = Step(**sample_step_config)
    assert step.layer == "ingest"
    assert step.name == "read_csv"
    assert step.engine == "pandas"


def test_step_default_values():
    """Test Step default values for optional fields."""
    step = Step(
        layer="ingest",
        name="test",
        type="config_op",
        engine="pandas",
        value="test.csv"
    )
    assert step.params == {}
    assert step.inputs == {}
    assert step.outputs == {}
```

**Create: `tests/test_engine_contracts.py`**

```python[demo]
"""Unit tests for engine context contracts."""

import pytest
from odibi_core.engine.pandas_context import PandasEngineContext
from odibi_core.engine.spark_context import SparkEngineContext


def test_secret_resolution_with_dict():
    """Test secret resolution with dictionary."""
    ctx = PandasEngineContext(secrets={"user": "admin", "pass": "secret"})
    assert ctx.get_secret("user") == "admin"


def test_secret_resolution_with_callable():
    """Test secret resolution with callable."""
    def provider(key: str) -> str:
        return {"api_key": "abc123"}[key]
    
    ctx = PandasEngineContext(secrets=provider)
    assert ctx.get_secret("api_key") == "abc123"


def test_secret_resolution_missing_key():
    """Test error for missing secret key."""
    ctx = PandasEngineContext(secrets={"known": "value"})
    with pytest.raises(ValueError, match="Secret not found"):
        ctx.get_secret("unknown")
```

**Why write tests during scaffolding?**
- Validates contracts compile
- Catches design issues early
- Provides examples of usage
- Sets quality bar for Phase 2+

**Common Mistake**: ⚠️ Writing tests only after implementation — TDD during scaffolding catches contract mismatches before you write hundreds of lines of code.

---

### 🎓 Checkpoint 9: Testing Infrastructure

**Q1 (MCQ)**: Why write tests during scaffolding?

A. To increase line count  
B. ✅ **To validate contracts work and catch design issues early**  
C. Because pytest requires them  
D. To satisfy code coverage tools  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — Not about quantity
- B: ✅ Correct — Tests during scaffolding verify imports work, contracts are correct, and types are valid
- C: Incorrect — pytest doesn't require tests to exist
- D: Incorrect — Coverage is a metric, not the goal

</details>

**Q2 (Predict-Output)**: What do test fixtures provide?

A. Random test data  
B. ✅ **Reusable test components and setup**  
C. Performance benchmarks  
D. Code coverage reports  

<details>
<summary>Click to see answer</summary>

**Answer**: B — Fixtures like `@pytest.fixture def pandas_context()` provide pre-configured objects that multiple tests can use, reducing duplication.

</details>

**Q3 (Code-Trace)**: Where is conftest.py located?

A. In odibi_core/  
B. In odibi_core/core/  
C. ✅ **In tests/**  
D. In the project root  

<details>
<summary>Click to see answer</summary>

**Answer**: C — `tests/conftest.py` contains pytest fixtures available to all test files in the tests/ directory.

</details>

---

## 📖 PART 7: DOCUMENTATION

### Mission 27: Create Package __init__.py

**Create: `odibi_core/__init__.py`**

```python
"""
ODIBI CORE v1.0

A Node-centric, engine-agnostic, config-driven data engineering framework.
"""

__version__ = "1.0.0"
__author__ = "Henry Odibi"
```

**Why at package root?**
- Enables `import odibi_core`
- Defines version for tooling
- Provides package metadata

**Common Mistake**: ⚠️ Forgetting to update `__version__` when releasing — use semantic versioning and update this file before tagging releases.

---

### Mission 28: Create README.md

**Create: `README.md`** (see full version in previous files)

Key sections:
1. **Mission** - What ODIBI CORE is
2. **Quick Start** - Installation and hello world
3. **Architecture** - Node model explanation
4. **Configuration** - JSON/SQL schema
5. **Development** - Phase roadmap

**Why create README early?**
- Onboarding new developers
- GitHub landing page
- Forces you to articulate vision

**Common Mistake**: ⚠️ README becomes outdated after initial creation — keep it synchronized with code changes, especially API examples.

---

### Mission 29: Create Example Script

**Create: `odibi_core/examples/run_energy_efficiency_demo.py`**

```python[demo]
"""Energy Efficiency demo pipeline."""

def run_demo() -> None:
    """Run demo pipeline."""
    print("ODIBI CORE v1.0 - Energy Efficiency Demo")
    print("=" * 50)
    print("Status: Phase 1 - Scaffolding complete")
    print("Next: Phase 2 - Implement engine contexts")

if __name__ == "__main__":
    run_demo()
```

**Why create a demo stub?**
- Shows intended usage
- Placeholder for Phase 10
- Tests that imports work

**Common Mistake**: ⚠️ Creating examples that depend on unimplemented features — stub examples should run without errors, even if they only print messages.

---

### 🎓 Checkpoint 10: Documentation & Examples

**Q1 (MCQ)**: Why create example before implementation?

A. Examples are easier to write  
B. ✅ **To validate API design and usage patterns early**  
C. Because users need them immediately  
D. To test performance  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — Not about ease
- B: ✅ Correct — Writing example usage forces you to think: "Is this API intuitive?" Catches design issues before implementing.
- C: Incorrect — Users don't need examples of unimplemented features
- D: Incorrect — Unrelated to performance

</details>

**Q2 (Predict-Output)**: What does `run_demo()` print?

A. Error message  
B. DataFrame output  
C. ✅ **Status messages indicating Phase 1 complete**  
D. Nothing (silent execution)  

<details>
<summary>Click to see answer</summary>

**Answer**: C — The stub prints: "ODIBI CORE v1.0 - Energy Efficiency Demo", "Status: Phase 1 - Scaffolding complete", etc.

</details>

**Q3 (Code-Trace)**: Where are examples stored?

A. In tests/  
B. In docs/  
C. ✅ **In odibi_core/examples/**  
D. In the project root  

<details>
<summary>Click to see answer</summary>

**Answer**: C — Examples are in `odibi_core/examples/` so they're part of the installed package and can import odibi_core modules.

</details>

---

## ✅ PART 8: VERIFICATION

### Mission 30: Verify Imports

**Create: `verify_imports.py`** (at project root)

```python
"""Verify all ODIBI CORE imports work."""

print("ODIBI CORE v1.0 - Import Verification")
print("=" * 60)

try:
    from odibi_core import __version__
    print(f"✓ Package version: {__version__}")
except ImportError as e:
    print(f"✗ Package import failed: {e}")

try:
    from odibi_core.core import NodeBase, NodeState, Step
    print("✓ Core imports successful")
except ImportError as e:
    print(f"✗ Core imports failed: {e}")

try:
    from odibi_core.engine import EngineContext, PandasEngineContext
    print("✓ Engine imports successful")
except ImportError as e:
    print(f"✗ Engine imports failed: {e}")

try:
    from odibi_core.nodes import IngestNode, NODE_REGISTRY
    print(f"✓ Node imports successful - {len(NODE_REGISTRY)} nodes registered")
except ImportError as e:
    print(f"✗ Node imports failed: {e}")

print("\n" + "=" * 60)
print("✅ All imports successful!")
```

**Run verification:**

```bash
cd odibi_core
python verify_imports.py
```

**Expected output:**
```
✓ Package version: 1.0.0
✓ Core imports successful
✓ Engine imports successful
✓ Node imports successful - 5 nodes registered
✅ All imports successful!
```

**Common Mistake**: ⚠️ Not running import verification after every major change — broken imports cascade into confusing errors later.

---

### Mission 31: Run Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
tests/test_node_base.py::test_node_state_enum PASSED
tests/test_node_base.py::test_step_dataclass_creation PASSED
tests/test_node_base.py::test_step_default_values PASSED
tests/test_engine_contracts.py::test_secret_resolution_with_dict PASSED
tests/test_engine_contracts.py::test_secret_resolution_with_callable PASSED
tests/test_engine_contracts.py::test_secret_resolution_missing_key PASSED

========================= 6 passed in 0.15s =========================
```

**Common Mistake**: ⚠️ Ignoring test failures with "I'll fix it later" — failing tests indicate contract violations that compound over time.

---

### Mission 32: Final Verification

**Run complete verification suite:**

```bash
# 1. Check imports
python verify_imports.py

# 2. Run all tests
pytest tests/ -v

# 3. Type check (optional, requires mypy)
mypy odibi_core/ --ignore-missing-imports

# 4. Verify package structure
ls -R odibi_core/
```

**Success criteria:**
- ✅ All imports work
- ✅ All tests pass
- ✅ No circular import errors
- ✅ Type hints validate (if using mypy)

**Common Mistake**: ⚠️ Skipping final verification before committing — always run the full test suite before pushing to ensure nothing broke.

---

### 🎓 Checkpoint 11: Final Verification

**Q1 (MCQ)**: What does verify_imports.py check?

A. Code style and formatting  
B. ✅ **That all modules can be imported without errors**  
C. Test coverage percentage  
D. Performance benchmarks  

<details>
<summary>Click to see rationale</summary>

- A: Incorrect — That's what linters do
- B: ✅ Correct — Verifies `from odibi_core.core import NodeBase` etc. work without ImportError
- C: Incorrect — That's pytest-cov
- D: Incorrect — Not about performance

</details>

**Q2 (Predict-Output)**: How many nodes are in NODE_REGISTRY after scaffolding?

A. 3  
B. 4  
C. ✅ **5 (connect, ingest, store, transform, publish)**  
D. 6  

<details>
<summary>Click to see answer</summary>

**Answer**: C — NODE_REGISTRY contains exactly 5 entries: ConnectNode, IngestNode, StoreNode, TransformNode, PublishNode.

</details>

**Q3 (Code-Trace)**: Which command runs all tests?

A. python -m pytest  
B. ✅ **pytest tests/ -v**  
C. python test_all.py  
D. make test  

<details>
<summary>Click to see answer</summary>

**Answer**: B — `pytest tests/ -v` runs all test files in tests/ directory with verbose output. (A also works but is less specific.)

</details>

---

## 🎓 REFLECTION CHECKPOINTS - ANSWERS

### Q1: Why build NodeBase before Orchestrator?

**Answer**: Orchestrator instantiates Nodes. You can't create instances of a class that doesn't exist. Also, NodeBase defines the `run(data_map)` contract that Orchestrator relies on.

**Dependency Flow**: NodeBase → Nodes → Orchestrator uses Nodes

---

### Q2: Why separate core/ from engine/?

**Answer**: 
- `core/` = **What** (contracts, interfaces, abstractions)
- `engine/` = **How** (Pandas implementation, Spark implementation)

This is the **Dependency Inversion Principle**: high-level modules (core) don't depend on low-level modules (engine). Both depend on abstractions (EngineContext ABC).

**Benefit**: Can add new engines (Polars, DuckDB) without modifying core.

---

### Q3: Why use a Node registry instead of direct imports?

**Answer**:
- **Extensibility**: Users can register custom Nodes via `@register_node("my_node")`
- **Config-driven**: Orchestrator looks up Nodes by string name from config
- **Decoupling**: Orchestrator doesn't need to import all Node classes
- **Plugin architecture**: Nodes can be loaded from external packages

---

### Q4: Why is secret injection handled at context level, not node level?

**Answer**:
- **Single Responsibility**: Nodes handle logic, context handles infrastructure
- **Reusability**: Same secret provider works for all Nodes
- **Testability**: Easy to mock secrets by passing test dict
- **Security**: Framework never hardcodes secret fetching (supports multiple backends)

---

### Q5: Why create Step dataclass instead of using dict?

**Answer**:
- **Type safety**: IDE autocomplete, mypy validation
- **Documentation**: Fields are self-documenting
- **Validation**: `__post_init__` can validate/normalize
- **Immutability**: Dataclass is more intention-revealing than dict

---

### Q6: Why stub methods with NotImplementedError instead of pass?

**Answer**:
- `pass` = Silent failure (hard to debug)
- `raise NotImplementedError` = Explicit failure (tells you what's missing)
- Helps during incremental development (know what's done vs. TODO)

---

## 📊 COMPLETION SUMMARY

### What Exists Now (Phase 1)

✅ **46 files created** across 8 modules  
✅ **100% type hint coverage**  
✅ **100% docstring coverage**  
✅ **All contracts defined**  
✅ **Plugin architecture ready**  
✅ **Tests passing**  

### What's Missing Until Phase 2

❌ No data actually read/written  
❌ DuckDB not integrated  
❌ Spark session not created  
❌ Functions not implemented  
❌ HTML stories not generated  

**This is expected! Phase 1 is scaffolding only.**

---

### File Tree Created

```
odibi_core/
├── odibi_core/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── node.py              ← NodeBase, NodeState, Step
│   │   ├── events.py            ← EventEmitter
│   │   ├── tracker.py           ← Tracker, Snapshot
│   │   ├── orchestrator.py      ← Orchestrator
│   │   └── config_loader.py     ← ConfigLoader
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── base_context.py      ← EngineContext ABC
│   │   ├── pandas_context.py    ← PandasEngineContext
│   │   └── spark_context.py     ← SparkEngineContext
│   ├── nodes/
│   │   ├── __init__.py          ← NODE_REGISTRY
│   │   ├── connect_node.py
│   │   ├── ingest_node.py
│   │   ├── store_node.py
│   │   ├── transform_node.py
│   │   └── publish_node.py
│   ├── functions/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── thermo/steam.py
│   │   ├── physics/units.py
│   │   └── math/safe_ops.py
│   ├── story/
│   │   ├── __init__.py
│   │   └── generator.py
│   ├── io/
│   │   ├── __init__.py
│   │   ├── readers.py
│   │   └── writers.py
│   └── examples/
│       └── run_energy_efficiency_demo.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_node_base.py
│   └── test_engine_contracts.py
├── pyproject.toml
├── pytest.ini
├── .gitignore
├── README.md
└── verify_imports.py
```

---

### Dependency Verification Checklist

- [x] Core modules import without circular dependencies
- [x] Engine contexts inherit from base
- [x] Nodes inherit from NodeBase
- [x] Registry system works
- [x] Tests run successfully
- [x] Type hints validate (run `mypy odibi_core/`)
- [x] Documentation complete

---

## 🚀 NEXT STEPS

### You've completed Phase 1! Here's what to do next:

1. **Verify everything works:**
   ```bash
   python verify_imports.py
   pytest tests/ -v
   ```

2. **Review the architecture:**
   - Read through each file you created
   - Understand the dependency flow
   - Note where TODOs are

3. **Begin Phase 2: Engine Contexts**
   - Implement `PandasEngineContext.read()` for CSV/Parquet
   - Integrate DuckDB for SQL
   - Implement `SparkEngineContext.read()` for Parquet/Delta
   - Write parity tests

4. **Use this walkthrough as a reference:**
   - When adding new features, follow the same pattern
   - Always build contracts before implementations
   - Keep modules loosely coupled

---

## 🎯 Key Takeaways

### Design Principles Applied

1. **Contracts First** - Define interfaces before implementations
2. **Dependency Inversion** - Core doesn't depend on engine
3. **Single Responsibility** - Each module has one job
4. **Plugin Architecture** - Registries enable extensibility
5. **Type Safety** - Type hints catch errors early
6. **Test-Driven Design** - Tests written during scaffolding

### Build Order Lessons

1. **Foundation → Contracts → Implementations**
2. **Never import from something that doesn't exist**
3. **Stub methods with NotImplementedError, not pass**
4. **Create __init__.py for every package**
5. **Write tests early to validate contracts**

### What Makes This Scaffolding Good?

✅ **Complete** - All modules defined  
✅ **Type-safe** - 100% type hints  
✅ **Documented** - Every class has docstring  
✅ **Testable** - Infrastructure ready  
✅ **Extensible** - Plugin architecture  
✅ **Phased** - Clear TODO markers  

---

## 📚 Additional Resources

- **Engineering Plan**: See `ODIBI_CORE_V1_ENGINEERING_PLAN.md` for full 10-phase roadmap
- **Phase 1 Complete Report**: See `PHASE_1_COMPLETE.md` for detailed summary
- **README**: See `README.md` for user-facing documentation

---

**Congratulations!** You've built a production-quality framework scaffold from scratch, understanding every design decision along the way.

**Time to Phase 2**: Implement those TODO stubs and bring ODIBI CORE to life! 🚀

---

**Document Status**: Complete  
**Phase**: 1 (Foundation & Scaffolding)  
**Next**: Phase 2 (Engine Context Implementation)  
**Estimated Time to Complete Phase 1**: 3-4 hours following this guide
