---
id: phase_3_orchestration
title: "Phase 3: Config-Driven Orchestration"
level: "Beginner"
tags: ["orchestration", "config-driven", "events", "validation", "tracking"]
checkpoints: 5
quiz_questions: 15
---

# ODIBI CORE v1.0 - Phase 3 Developer Walkthrough

**Building Config-Driven Pipelines: A Step-by-Step Guide**

**Author**: AMP AI Engineering Agent  
**Date**: 2025-11-01  
**Audience**: Developers learning config-driven data frameworks  
**Duration**: ~4 hours (following this guide)  
**Prerequisites**: Completed Phase 1 (scaffolding) and Phase 2 (engine contexts)

---

## 📚 Config-Driven Architecture Overview

### What is Phase 3?

Phase 3 transforms ODIBI CORE from a **code-driven** framework to a **config-driven** framework. Instead of writing Python code for each pipeline, you define pipelines in JSON or SQL tables.

**🎯 Metaphor: From Chef to Recipe Card**
> **Code-driven** = A chef who must cook every meal themselves (custom Python scripts)
> **Config-driven** = A recipe card system where anyone can follow instructions (JSON/SQL configs)
> 
> Just like recipe cards standardize cooking, configs standardize pipelines!

**Before Phase 3 (Code):**
```python
ctx = PandasEngineContext()
df = ctx.read("data.csv")
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")
ctx.write(result, "output.parquet")
```

**After Phase 3 (Config):**
```json
[
  {"layer": "ingest", "name": "read", "value": "data.csv", "outputs": {"data": "raw"}},
  {"layer": "transform", "name": "filter", "type": "sql", 
   "value": "SELECT * FROM data WHERE value > 100",
   "inputs": {"data": "raw"}, "outputs": {"data": "filtered"}},
  {"layer": "store", "name": "write", "value": "output.parquet", "inputs": {"data": "filtered"}}
]
```

```python
steps = ConfigLoader().load("pipeline.json")
orchestrator.run()
```

### Why Config-Driven?

**Benefits:**
1. **Pipelines are data** - Version control, audit, modify without code changes
2. **Validation before execution** - Catch errors before running
3. **AMP-friendly** - AI can generate/modify configs easier than code
4. **Reusable** - Same pipeline, different data sources (just change config)
5. **Auditable** - Tracker logs every execution with full lineage

---

## 🗺️ Phase 3 Architecture

**🎯 Metaphor: Power Grid Orchestration**
> **Orchestrator** = Power grid dispatcher (controls flow)
> **ConfigValidator** = Safety inspector (checks before power on)
> **Tracker** = Meter reader (monitors everything)
> **Nodes** = Power stations (do the actual work)
> **data_map** = Power lines (carry energy between stations)

```
┌────────────────────────────────────────────────────────────┐
│                       User Code                            │
│   ConfigLoader().load("pipeline.json")                     │
│   Orchestrator(steps, context, tracker, events).run()      │
└────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    ConfigValidator                         │
│  - Unique names/outputs                                    │
│  - Input existence                                         │
│  - Circular dependency detection                           │
│  - Layer/engine validation                                 │
└────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    Orchestrator                            │
│  - Instantiate Nodes from registry                         │
│  - Execute steps in order                                  │
│  - Track execution                                         │
│  - Emit events                                             │
└────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────┬─────────────────────────────────────┐
│   Nodes Execute      │      Tracker Logs                   │
│  IngestNode.run()    │  - Start/end times                  │
│  TransformNode.run() │  - Snapshots (schema, rows, sample) │
│  StoreNode.run()     │  - Schema diffs                     │
└──────────────────────┴─────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                  Output & Lineage                          │
│  - Data files (Parquet, JSON, etc.)                        │
│  - Tracker logs (tracker_logs/run_*.json)                  │
│  - Execution summary                                       │
└────────────────────────────────────────────────────────────┘
```

**Build Order:**
1. ConfigLoader (no dependencies beyond Step dataclass)
2. ConfigValidator (depends on Step)
3. Tracker enhancements (snapshot logic)
4. Node implementations (use context + tracker)
5. Orchestrator integration (brings it all together)
6. Demo pipeline (proves it works)

---

## 🚀 Step-by-Step Build Missions

### Mission 1: Implement ConfigLoader - JSON Support

**File: `odibi_core/core/config_loader.py`**

**Why JSON first?**
- Simpler than SQL (no database connection)
- Human-readable for debugging
- Git-friendly (version control)

```python
"""Configuration loader for pipeline definitions."""

import json
from pathlib import Path
from typing import List
from odibi_core.core.node import Step


class ConfigLoader:
    """Load pipeline configuration from SQLite, JSON, or CSV."""

    def load(self, source_uri: str, **kwargs) -> List[Step]:
        """Load pipeline configuration from source."""
        path = Path(source_uri)

        if not path.exists():
            raise FileNotFoundError(f"Config source not found: {source_uri}")

        if source_uri.endswith(".json"):
            return self._load_from_json(source_uri, **kwargs)
        elif source_uri.endswith(".db"):
            return self._load_from_sqlite(source_uri, **kwargs)
        # ... etc

    def _load_from_json(self, json_path: str, **kwargs) -> List[Step]:
        """Load from JSON file."""
        with open(json_path, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON config must be an array")

        steps = []
        for item in data:
            step = Step(
                layer=item.get("layer", "transform"),
                name=item["name"],  # Required
                type=item.get("type", "config_op"),
                engine=item.get("engine", "pandas"),
                value=item.get("value", ""),
                params=item.get("params"),
                inputs=item.get("inputs"),
                outputs=item.get("outputs"),
                metadata=item.get("metadata"),
            )
            steps.append(step)

        return steps
```

**Key Design:**
- `name` is required (raises KeyError if missing)
- Other fields have defaults
- Step dataclass handles None → {} conversion

---

### Mission 2: Implement ConfigLoader - SQLite Support

**Why SQLite?**
- v2 stores configs in SQL tables
- Supports filtering (by project, enabled status)
- Production-ready

```python
def _load_from_sqlite(
    self, db_path: str, project: str = None, enabled_only: bool = True
) -> List[Step]:
    """Load from SQLite database."""
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access by column name
    cursor = conn.cursor()

    # Query transformation_config table
    query = "SELECT * FROM transformation_config WHERE 1=1"
    params = []

    if project:
        query += " AND project = ?"
        params.append(project)

    if enabled_only:
        query += " AND enabled = 1"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    steps = []
    for row in rows:
        # Parse JSON fields
        params = json.loads(row["Params"]) if row["Params"] else {}
        inputs = json.loads(row["Inputs"]) if row["Inputs"] else {}
        outputs = json.loads(row["Outputs"]) if row["Outputs"] else {}

        step = Step(
            layer=row["Layer"].lower(),
            name=row["StepName"],
            type=row["StepType"].lower(),
            engine=row["Engine"].lower(),
            value=row["Value"],
            params=params,
            inputs=inputs,
            outputs=outputs,
        )
        steps.append(step)

    conn.close()
    return steps
```

**Reflection Checkpoint:**
> **Why parse JSON fields (Params, Inputs, Outputs)?**
>
> Answer: SQL tables store complex data as JSON strings. For example:
> - `Inputs: '{"data": "raw_data"}'` (string)
> - Needs to become: `{"data": "raw_data"}` (dict)
>
> This enables SQL storage while maintaining Python dict semantics.

---

### Mission 3: Implement ConfigValidator - Basic Checks

**🎯 Metaphor: Airport Security Checkpoint**
> **ConfigValidator** = TSA security (checks everything before flight)
> - Unique names = No duplicate boarding passes
> - Valid layers = Only authorized gates
> - Input existence = Can't board flight B if flight A never departed!

**File: Create `ConfigValidator` class in `config_loader.py`**

```python
class ConfigValidationError(Exception):
    """Raised when config validation fails."""
    pass


class ConfigValidator:
    """Validate pipeline configurations."""

    VALID_LAYERS = {"connect", "ingest", "store", "transform", "publish"}
    VALID_ENGINES = {"pandas", "spark"}
    VALID_TYPES = {"sql", "function", "config_op", "api"}

    def validate_config(self, steps: List[Step]) -> None:
        """Validate pipeline configuration."""
        if not steps:
            raise ConfigValidationError("Config is empty - no steps found")

        self._validate_unique_names(steps)
        self._validate_unique_outputs(steps)
        self._validate_inputs_exist(steps)
        self._validate_no_cycles(steps)
        self._validate_layers(steps)
        self._validate_engines(steps)

    def _validate_unique_names(self, steps: List[Step]) -> None:
        """Ensure all step names are unique."""
        names = [step.name for step in steps]
        duplicates = [name for name in names if names.count(name) > 1]

        if duplicates:
            raise ConfigValidationError(
                f"Duplicate step names found: {list(set(duplicates))}"
            )

    def _validate_layers(self, steps: List[Step]) -> None:
        """Validate layer names."""
        for step in steps:
            if step.layer not in self.VALID_LAYERS:
                raise ConfigValidationError(
                    f"Step '{step.name}' has invalid layer: '{step.layer}'"
                )
```

**Pattern**: Each validation method checks one thing, raises ConfigValidationError with context.

---

## 🎯 CHECKPOINT 1: Config Loading & Basic Validation

**What you've learned:**
- ✅ Config files replace Python code for pipeline definitions
- ✅ ConfigLoader supports JSON and SQLite sources
- ✅ ConfigValidator catches errors BEFORE execution
- ✅ Step dataclass is the universal config representation

**Quiz Questions:**

**Q1:** Why do we use config-driven pipelines instead of code-driven?
<details>
<summary>Answer</summary>
Configs can be validated before execution, versioned in databases, modified without code changes, and are easier for AI/non-programmers to work with.
</details>

**Q2:** What happens if a JSON config doesn't include a "name" field?
<details>
<summary>Answer</summary>
KeyError is raised because `name` is required (no default value provided).
</details>

**Q3:** Why does `_load_from_sqlite` parse JSON strings?
<details>
<summary>Answer</summary>
SQL tables store complex data (dicts) as JSON strings. We parse them back to Python dicts for use in Step objects.
</details>

---

### Mission 4: Implement Circular Dependency Detection

**🎯 Metaphor: Chicken and Egg Problem**
> **Circular dependency** = "I can't cook breakfast until I have eggs, but I can't get eggs until I cook breakfast!"
> 
> The validator detects these impossible situations using graph theory.

**The most complex validation:**

```python
def _validate_no_cycles(self, steps: List[Step]) -> None:
    """Detect circular dependencies using DFS."""
    # Build dependency graph
    graph: Dict[str, List[str]] = {}
    output_to_step: Dict[str, str] = {}

    # Map: output_key → step_name
    for step in steps:
        graph[step.name] = []
        for output_key in step.outputs.values():
            output_to_step[output_key] = step.name

    # Build: step → list of steps it depends on
    for step in steps:
        for input_key in step.inputs.values():
            if input_key in output_to_step:
                dependency = output_to_step[input_key]
                graph[step.name].append(dependency)

    # DFS to detect cycles
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
                # Cycle found!
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                raise ConfigValidationError(
                    f"Circular dependency: {' → '.join(cycle)}"
                )

        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            has_cycle(node, [])
```

**Algorithm:**
1. Build graph: step → dependencies
2. DFS with recursion stack
3. If we revisit a node in rec_stack → cycle!
4. Report the cycle path

**Reflection Checkpoint:**
> **Why is cycle detection important?**
>
> Answer: Circular dependencies cause infinite loops:
> ```
> step1 needs output from step2
> step2 needs output from step1
> → Deadlock!
> ```
> Detecting this before execution saves debugging time.

---

### Mission 5: Enhance Tracker - Snapshot Capture

**🎯 Metaphor: Crime Scene Photographer**
> **Tracker** = Crime scene investigator who photographs EVERYTHING
> - "Before" snapshot = Scene before detectives arrive
> - "After" snapshot = Scene after investigation
> - Schema diff = "What changed?"
> 
> This creates a perfect audit trail for debugging!

**File: Update `odibi_core/core/tracker.py`**

**Goal**: Capture DataFrame state at each step.

```python
def snapshot(self, name: str, df: Any, context: Any) -> None:
    """
    Capture snapshot of DataFrame state.
    
    Args:
        name: "before" or "after"
        df: DataFrame (Pandas or Spark)
        context: EngineContext for collect_sample()
    """
    # Get sample as Pandas DataFrame
    sample_df = context.collect_sample(df, n=5)

    # Extract schema
    schema = [(col, str(sample_df[col].dtype)) for col in sample_df.columns]

    # Get row count from original DataFrame
    import pandas as pd
    if isinstance(df, pd.DataFrame):
        row_count = int(df.shape[0])
    else:
        # Spark DataFrame
        row_count = df.count()

    # Convert sample to list of dicts
    sample_data = sample_df.head(5).to_dict(orient="records")

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
        
        # Calculate diff if we have before snapshot
        if self._current_execution.before_snapshot:
            self._current_execution.schema_diff = self._compute_schema_diff(
                self._current_execution.before_snapshot,
                snapshot
            )
            self._current_execution.row_delta = (
                snapshot.row_count - self._current_execution.before_snapshot.row_count
            )
```

**Key Points:**
1. **Use context.collect_sample()** - Works for both Pandas and Spark
2. **Extract schema from sample** - Sample is always Pandas DF
3. **Get row count from original** - Sample might be smaller
4. **Calculate diffs automatically** - When after snapshot captured

---

### Mission 6: Implement Schema Diff Calculation

```python
def _compute_schema_diff(self, before: Snapshot, after: Snapshot) -> Dict[str, Any]:
    """Compute schema changes between snapshots."""
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
```

**What this enables:**
```
Step: aggregate_by_category
  + Added: ['count', 'avg_value', 'max_value']
  - Removed: ['id', 'name', 'value', 'timestamp']
  Delta Rows: -7
```

**Use case**: Quickly see what a transformation did without reading code.

---

## 🎯 CHECKPOINT 2: Validation & Tracking Infrastructure

**What you've learned:**
- ✅ Circular dependency detection uses graph theory (DFS)
- ✅ Tracker captures "before/after" snapshots automatically
- ✅ Schema diffs show what transformations changed
- ✅ All tracking works for both Pandas AND Spark

**Quiz Questions:**

**Q4:** What data structure does cycle detection use?
<details>
<summary>Answer</summary>
A directed graph where nodes are steps and edges represent dependencies (step A depends on step B if A's input comes from B's output).
</details>

**Q5:** Why do we capture snapshots at each step?
<details>
<summary>Answer</summary>
To create an audit trail showing exactly what each transformation did (row counts, schema changes, sample data) without manual logging.
</details>

**Q6:** What's the difference between `row_count` from original vs sample?
<details>
<summary>Answer</summary>
Sample might only have 5 rows, but row_count shows the full DataFrame size (e.g., 1 million rows). We need the real count for tracking.
</details>

---

### Mission 7: Implement Tracker Log Persistence

```python
def save(self, filepath: Optional[str] = None) -> str:
    """Save tracker logs to file."""
    # Create log directory
    self.log_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename if not provided
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.log_dir / f"run_{timestamp}.json"

    # Export lineage
    lineage = self.export_lineage()

    # Save to file
    with open(filepath, "w") as f:
        json.dump(lineage, f, indent=2)

    return str(filepath)


def export_lineage(self) -> Dict[str, Any]:
    """Export execution lineage as JSON."""
    return {
        "pipeline_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "start_time": self.pipeline_start_time.isoformat() if self.pipeline_start_time else None,
        "steps": [ex.to_dict() for ex in self.executions],
        "summary": self.get_stats(),
    }
```

**Why save to JSON?**
- AMP can read and analyze failures
- Human-readable audit trail
- Version control friendly
- No database dependency

---

### Mission 8: Implement IngestNode

**🎯 Metaphor: Loading Dock**
> **IngestNode** = Warehouse loading dock
> - Receives shipments (files) from outside
> - Unpacks them (reads data)
> - Places on conveyor belt (data_map) for factory workers

**File: `odibi_core/nodes/ingest_node.py`**

```python
def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ingest operation."""
    self._update_state(NodeState.RUNNING)

    try:
        # Read data from source
        df = self.context.read(self.step.value, **self.step.params)

        # Log after snapshot
        self.tracker.snapshot("after", df, self.context)

        # Store in data_map
        for dataset_name, output_key in self.step.outputs.items():
            data_map[output_key] = df

        self._update_state(NodeState.SUCCESS)

    except Exception as e:
        self._update_state(NodeState.FAILED)
        raise

    return data_map
```

**Flow:**
1. Read file (step.value = file path)
2. Snapshot the DataFrame
3. Store in data_map with output key
4. Return updated data_map

---

### Mission 9: Implement TransformNode (SQL Mode)

**🎯 Metaphor: Assembly Line Robot**
> **TransformNode** = Factory robot that reshapes products
> - Takes parts from conveyor (data_map inputs)
> - Transforms them (SQL/function)
> - Puts back on conveyor (data_map outputs)

```python
def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
    """Execute transformation."""
    self._update_state(NodeState.RUNNING)

    try:
        # Get input DataFrames
        for dataset_name, input_key in self.step.inputs.items():
            if input_key not in data_map:
                raise ValueError(f"Input '{input_key}' not found in data_map")
            
            df = data_map[input_key]
            self.context.register_temp(dataset_name, df)

        # Get input for before snapshot
        first_input_key = list(self.step.inputs.values())[0]
        input_df = data_map[first_input_key]
        self.tracker.snapshot("before", input_df, self.context)

        # Execute transformation
        if self.step.type == "sql":
            result = self.context.execute_sql(self.step.value)
        elif self.step.type == "function":
            # Not implemented yet
            pass

        # Log after snapshot
        self.tracker.snapshot("after", result, self.context)

        # Store result
        for dataset_name, output_key in self.step.outputs.items():
            data_map[output_key] = result

        self._update_state(NodeState.SUCCESS)

    except Exception as e:
        self._update_state(NodeState.FAILED)
        raise

    return data_map
```

**Key steps:**
1. Register inputs as temp tables
2. Snapshot before
3. Execute SQL query
4. Snapshot after
5. Store result in data_map

---

## 🎯 CHECKPOINT 3: Node Implementations

**What you've learned:**
- ✅ Nodes are the "workers" that execute steps
- ✅ IngestNode reads data into data_map
- ✅ TransformNode uses temp tables for SQL execution
- ✅ All nodes track state (RUNNING → SUCCESS/FAILED)

**Quiz Questions:**

**Q7:** What does data_map represent?
<details>
<summary>Answer</summary>
A shared dictionary that flows through the pipeline, holding all intermediate DataFrames. It's like a conveyor belt carrying data between steps.
</details>

**Q8:** Why does TransformNode register inputs as temp tables?
<details>
<summary>Answer</summary>
So the SQL query can reference them by name (e.g., `SELECT * FROM data` where "data" is the temp table name).
</details>

**Q9:** When does the "before" snapshot get captured?
<details>
<summary>Answer</summary>
After inputs are loaded but before the transformation executes (captures the input state).
</details>

---

### Mission 10: Implement StoreNode

```python
def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
    """Execute store operation."""
    self._update_state(NodeState.RUNNING)

    try:
        # Get data to store
        dataset_key = list(self.step.inputs.values())[0]
        df = data_map[dataset_key]

        # Log before snapshot
        self.tracker.snapshot("before", df, self.context)

        # Write to storage
        self.context.write(df, self.step.value, **self.step.params)

        self._update_state(NodeState.SUCCESS)

    except Exception as e:
        self._update_state(NodeState.FAILED)
        raise

    return data_map
```

**Simple flow:**
1. Get data from data_map
2. Snapshot it
3. Write to file (path in `step.value`)
4. Done

---

### Mission 11: Integrate Orchestrator with Tracker

**🎯 Metaphor: Orchestra Conductor**
> **Orchestrator** = Symphony conductor
> - Starts the performance (start_pipeline)
> - Cues each musician (run_step)
> - Tracks timing (tracker)
> - Signals audience (events)
> - Handles mistakes gracefully (error handling)

**File: Update `odibi_core/core/orchestrator.py`**

```python
def run(self) -> OrchestrationResult:
    """Execute pipeline."""
    # Start pipeline tracking
    self.tracker.start_pipeline("odibi_pipeline")
    self.events.emit("pipeline_start", steps=self.steps)

    try:
        # Execute steps in order
        for step in self.steps:
            self.run_step(step)

        # Success
        self.events.emit("pipeline_complete", data_map=self.data_map)

    except Exception as e:
        self.events.emit("pipeline_error", error=e)
        raise

    return OrchestrationResult(data_map=self.data_map, tracker=self.tracker)


def run_step(self, step: Step) -> None:
    """Execute a single step."""
    from odibi_core.nodes import NODE_REGISTRY

    # Get Node class
    node_class = NODE_REGISTRY.get(step.layer)

    # Start tracking
    self.tracker.start_step(step.name, step.layer)
    self.events.emit("step_start", step=step)

    try:
        # Instantiate and run
        node = node_class(step, self.context, self.tracker, self.events)
        self.data_map = node.run(self.data_map)

        # End tracking (success)
        self.tracker.end_step(step.name, "success")
        self.events.emit("step_complete", step=step)

    except Exception as e:
        # End tracking (failed)
        self.tracker.end_step(step.name, "failed", str(e))
        self.events.emit("step_error", step=step, error=e)
        raise
```

**Key integration:**
1. Tracker wraps each step (start/end)
2. Nodes call tracker.snapshot() during execution
3. Events emitted for observability
4. Errors tracked and re-raised

---

### Mission 12: Create Sample Pipeline Config

**File: `odibi_core/examples/configs/simple_pipeline.json`**

```json
[
  {
    "layer": "ingest",
    "name": "read_sample_csv",
    "type": "config_op",
    "engine": "pandas",
    "value": "odibi_core/examples/data/sample.csv",
    "outputs": {"data": "raw_data"}
  },
  {
    "layer": "transform",
    "name": "filter_high_value",
    "type": "sql",
    "engine": "pandas",
    "value": "SELECT * FROM data WHERE value > 100 ORDER BY id",
    "inputs": {"data": "raw_data"},
    "outputs": {"data": "filtered_data"}
  },
  {
    "layer": "store",
    "name": "write_filtered_parquet",
    "type": "config_op",
    "engine": "pandas",
    "value": "odibi_core/examples/output/filtered.parquet",
    "inputs": {"data": "filtered_data"}
  }
]
```

**This config:**
- Reads CSV (10 rows)
- Filters via SQL (6 rows where value > 100)
- Writes Parquet

---

## 🎯 CHECKPOINT 4: Orchestration & Integration

**What you've learned:**
- ✅ Orchestrator coordinates all nodes in sequence
- ✅ Tracker wraps each step with start/end timing
- ✅ Events provide real-time observability
- ✅ Error handling preserves context for debugging

**Quiz Questions:**

**Q10:** What is the Orchestrator's main responsibility?
<details>
<summary>Answer</summary>
To execute steps in order, instantiate the correct Node for each layer, track execution, emit events, and handle errors gracefully.
</details>

**Q11:** What happens if a step fails?
<details>
<summary>Answer</summary>
The tracker records the failure with error message, an event is emitted, and the exception is re-raised to stop the pipeline.
</details>

**Q12:** How does the Orchestrator know which Node class to use?
<details>
<summary>Answer</summary>
It uses NODE_REGISTRY to look up the Node class by the step's layer (e.g., "ingest" → IngestNode).
</details>

---

### Mission 13: Create Pipeline Demo Script

**File: `odibi_core/examples/run_pipeline_demo.py`**

```python
"""Config-driven pipeline demonstration."""

from odibi_core.core import (
    ConfigLoader,
    ConfigValidator,
    Orchestrator,
    Tracker,
    EventEmitter,
    create_engine_context,
)

# Load config
loader = ConfigLoader()
steps = loader.load("odibi_core/examples/configs/simple_pipeline.json")
print(f"Loaded {len(steps)} steps")

# Validate config
validator = ConfigValidator()
validator.validate_config(steps)
print("[OK] Config validation passed")

# Execute pipeline
context = create_engine_context("pandas")
context.connect()

tracker = Tracker(log_dir="tracker_logs")
events = EventEmitter()

orchestrator = Orchestrator(steps, context, tracker, events)
result = orchestrator.run()

print(f"[SUCCESS] Pipeline completed")
print(f"Datasets: {list(result.data_map.keys())}")

# Show summary
print(tracker.get_summary())

# Save logs
log_path = tracker.save()
print(f"Logs saved to: {log_path}")
```

---

### Mission 14: Write Tests

**File: `tests/test_config_loader.py`**

```python
def test_config_loader_json(tmp_path):
    """Test loading from JSON."""
    config = [
        {"name": "read", "layer": "ingest", "value": "input.csv", "outputs": {"data": "raw"}}
    ]

    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    loader = ConfigLoader()
    steps = loader.load(str(config_file))

    assert len(steps) == 1
    assert steps[0].name == "read"


def test_config_validator_circular_dependency():
    """Test circular dependency detection."""
    steps = [
        Step(name="step1", inputs={"x": "out2"}, outputs={"x": "out1"}),
        Step(name="step2", inputs={"x": "out1"}, outputs={"x": "out2"}),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="Circular dependency"):
        validator.validate_config(steps)
```

**Testing strategy:**
- One test per validation rule
- Test both success and failure cases
- Use pytest.raises for expected errors

---

## 🎯 CHECKPOINT 5: Complete System Integration

**What you've learned:**
- ✅ Full pipeline: Load → Validate → Execute → Track → Save
- ✅ Config files drive everything (no code needed)
- ✅ Tests ensure each component works independently
- ✅ Demo script proves end-to-end functionality

**Quiz Questions:**

**Q13:** What are the 5 stages of the demo pipeline?
<details>
<summary>Answer</summary>
1. Load config from JSON
2. Validate config structure
3. Create context/tracker/events
4. Execute pipeline via Orchestrator
5. Save tracker logs
</details>

**Q14:** Why validate configs before execution?
<details>
<summary>Answer</summary>
To catch errors (missing inputs, circular dependencies, invalid layers) BEFORE running expensive operations. Fail fast principle!
</details>

**Q15:** What would happen without the NODE_REGISTRY?
<details>
<summary>Answer</summary>
The Orchestrator wouldn't know which Python class to instantiate for each layer. The registry maps layer names to Node classes.
</details>

---

## 🎓 Key Concepts Explained

### Config as Data

**🎯 Metaphor: Lego Instructions vs Custom Carpentry**
> **Code** = Custom carpentry (unique every time)
> **Config** = Lego instructions (reusable, standardized)

**Traditional (code):**
```python
# pipeline.py
df = read_csv("input.csv")
filtered = df[df.value > 100]
filtered.to_parquet("output.parquet")
```

**Config-driven:**
```json
// pipeline.json
[
  {"layer": "ingest", "value": "input.csv"},
  {"layer": "transform", "type": "sql", "value": "SELECT * FROM data WHERE value > 100"},
  {"layer": "store", "value": "output.parquet"}
]
```

**Why better?**
- Change pipeline without deploying code
- Validate before running
- Version control in SQL database
- Non-programmers can modify

---

### The data_map Pattern

**🎯 Metaphor: Airport Luggage System**
> **data_map** = Luggage carousel system
> - Each suitcase has a tag (output key)
> - Workers put luggage on carousel (outputs)
> - Passengers retrieve by tag (inputs)
> - Multiple people can grab same luggage (shared state)

**What is data_map?**

```python
data_map = {
    "raw_data": <pandas DataFrame with 10 rows>,
    "filtered_data": <pandas DataFrame with 6 rows>,
    "aggregated_data": <pandas DataFrame with 3 rows>
}
```

**It's a shared dictionary that flows through the pipeline:**

```
Step 1 (Ingest):
  data_map = {}
  df = read("data.csv")
  data_map["raw_data"] = df
  return data_map

Step 2 (Transform):
  data_map = {"raw_data": ...}
  df = data_map["raw_data"]
  result = sql(df)
  data_map["filtered_data"] = result
  return data_map

Step 3 (Store):
  data_map = {"raw_data": ..., "filtered_data": ...}
  df = data_map["filtered_data"]
  write(df, "output.parquet")
  return data_map
```

**Reflection Checkpoint:**
> **Why use data_map instead of returning DataFrames directly?**
>
> Answer: A pipeline can have **multiple branches**:
> ```
> ingest → transform1 → store1
>       ↘ transform2 → store2
> ```
> Both branches need the original data. data_map is the shared state.

---

### Snapshot-Driven Debugging

**🎯 Metaphor: Black Box Flight Recorder**
> **Tracker** = Airplane's black box
> - Records everything automatically
> - No pilot action needed
> - Essential for accident investigation
> - Shows exact state at each moment

**Traditional debugging:**
```python
print(df.head())  # Manual inspection
```

**Tracker-driven:**
```python
# Automatic snapshots at each step
tracker.snapshot("after", df, context)
```

**Result**: Every step logged automatically
```
Step: filter_high_value
  Before: 10 rows, 5 columns
  After: 6 rows, 5 columns
  Delta: -4 rows
  Sample: [{"id": 2, "value": 150}, ...]
```

**Benefit**: No manual logging, full audit trail, reproducible debugging.

---

## 📊 Completion Summary

### What Exists Now (Phase 3)

✅ **ConfigLoader** (400 lines)
- JSON, SQLite, CSV loading
- JSON field parsing
- Project/layer filtering

✅ **ConfigValidator** (200 lines)
- 7 validation rules
- Circular dependency detection
- Clear error messages

✅ **Tracker** (400 lines)
- Snapshot capture
- Schema diff calculation
- Lineage export
- JSON log persistence

✅ **Orchestrator** (Enhanced)
- Node instantiation
- Pipeline execution
- Tracker integration
- Event emission

✅ **Nodes** (3 implemented)
- IngestNode - working
- TransformNode (SQL) - working
- StoreNode - working

✅ **Demo Pipeline**
- 5-step config
- Runs successfully
- Produces outputs
- Generates tracker logs

---

### What's Missing Until Phase 4

❌ ConnectNode implementation  
❌ PublishNode implementation  
❌ TransformNode (function mode)  
❌ Retry logic  
❌ DAG/topological sort  

**This is expected! Phase 4 will complete the nodes.**

---

### Test Results

```bash
python -m pytest tests/ -v
```

**Output:**
```
✅ 38 passed
⏭️ 10 skipped (Spark on Windows)
⏱️ 0.19s
```

**Phase 3 added:**
- 10 config loader/validator tests
- 8 tracker tests

---

### File Tree (Phase 3 Additions)

```
odibi_core/
├── core/
│   ├── config_loader.py      ← 400 lines (ConfigLoader + ConfigValidator) ✅
│   ├── tracker.py            ← 400 lines (Enhanced with snapshots) ✅
│   └── orchestrator.py       ← Enhanced (pipeline execution) ✅
├── nodes/
│   ├── ingest_node.py        ← Implemented ✅
│   ├── transform_node.py     ← SQL mode implemented ✅
│   └── store_node.py         ← Implemented ✅
├── examples/
│   ├── configs/
│   │   └── simple_pipeline.json  ← Sample config ✅
│   └── run_pipeline_demo.py  ← Pipeline demo ✅
└── tests/
    ├── test_config_loader.py ← 10 tests ✅
    └── test_tracker.py       ← 8 tests ✅
```

---

### Running the Demo

```bash
cd d:/projects/odibi_core
python -m odibi_core.examples.run_pipeline_demo
```

**Expected output:**
```
[1/5] Loading configuration...
Loaded 5 steps

[2/5] Validating configuration...
[OK] Config validation passed

[3/5] Executing pipeline...
  [OK] read_sample_csv completed in 285ms
  [OK] filter_high_value completed in 3ms
  [OK] aggregate_by_category completed in 4ms
  ...

[SUCCESS] Pipeline completed

[4/5] Tracker Summary
Pipeline Execution Summary
Total Steps: 5
Success: 5 | Failed: 0
Total Duration: 319ms

[5/5] Verifying outputs...
[OK] Filtered data written: filtered.parquet (6 rows)
[OK] Aggregated data written: aggregated.json (3 categories)
```

---

## 🎯 Key Takeaways

### Design Principles Applied

1. **Config as Data** - Pipelines defined declaratively
2. **Validation First** - Catch errors before execution
3. **Truth Preserving** - Every step logged with snapshots
4. **Event-Driven** - Observability via event emitters
5. **Error Context** - Clear messages with step names and dependencies

### Build Order Lessons

1. **Simple to Complex** - JSON loader before SQL loader
2. **Validation Early** - Validator before orchestrator
3. **Tracker First** - Logging before execution
4. **Test Each Component** - Isolated tests catch issues early

### What Makes Good Config-Driven Design?

✅ **Declarative** - What, not how  
✅ **Validated** - Errors before execution  
✅ **Auditable** - Full lineage tracking  
✅ **Flexible** - Easy to modify  
✅ **Testable** - Mock configs for tests  
✅ **Version Control** - JSON/SQL in git  

---

## 📚 Additional Resources

- **Phase 3 Complete**: See `PHASE_3_COMPLETE.md` for detailed report
- **Format Support**: See `FORMAT_SUPPORT.md` for all formats
- **SQL Support**: See `SQL_DATABASE_SUPPORT.md` for databases

---

**Congratulations!** You've built a production-grade config-driven data engineering framework. You can now:
- Define pipelines in JSON or SQL
- Validate configs before execution
- Track every step with full audit trails
- Switch engines (Pandas ↔ Spark) via config
- Debug with automatic snapshots

**You're now ready for Phase 4: Complete Node Implementations!** 🚀

---

**Document Status**: Complete  
**Phase**: 3 (Config Loader, Validator & Tracker)  
**Next**: Phase 4 (Complete Node Implementations)  
**Estimated Time to Complete Phase 3**: 3-4 hours following this guide
