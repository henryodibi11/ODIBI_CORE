# Phase 9 Quick Reference Card

**ODIBI CORE v1.0.0-phase9** - SDK & CLI Reference

---

## Installation

```bash
cd /d:/projects/odibi_core
pip install -e ".[dev]"
odibi version
```

---

## CLI Commands

### Execute Pipeline
```bash
odibi run --config pipeline.json --engine pandas
odibi run -c config.db -e spark -w 8 -v
odibi run -c pipeline.json --secrets '{"key": "value"}'
```

### Validate Configuration
```bash
odibi validate --config pipeline.json
odibi validate -c config.db --strict
```

### Check Version
```bash
odibi version
```

### Generate Docs (Phase 10)
```bash
odibi docs --output docs/ --format markdown
```

---

## SDK - Quick Execution

```python
from odibi_core.sdk import ODIBI

# One-line execution
result = ODIBI.run("pipeline.json", engine="pandas")
print(result.summary())

# With configuration
result = ODIBI.run(
    "pipeline.json",
    engine="spark",
    secrets={"db_pass": "xxx"},
    max_workers=8
)
```

---

## SDK - Advanced Usage

```python
from odibi_core.sdk import Pipeline

# Create and configure pipeline
pipeline = Pipeline.from_config("pipeline.json")
pipeline.set_engine("pandas")
pipeline.set_secrets({"db_pass": "secret"})
pipeline.set_parallelism(max_workers=8)

# Execute
result = pipeline.execute()

# Check results
if result.is_success():
    print(f"✅ Success: {result.total_duration_ms}ms")
else:
    print(f"❌ Failed: {result.failed_count} nodes")
```

---

## Configuration Validation

```python
from odibi_core.sdk import ODIBI

# Validate before execution
try:
    ODIBI.validate("pipeline.json")
    print("✅ Valid")
except Exception as e:
    print(f"❌ Invalid: {e}")
```

**Advanced validation**:
```python
from odibi_core.sdk.config_validator import ConfigValidator

validator = ConfigValidator()
is_valid = validator.validate("pipeline.json", strict=True)

if not is_valid:
    validator.print_issues()
    
print(validator.get_summary())
```

---

## Programmatic Pipeline Creation

```python
from odibi_core.sdk import Pipeline
from odibi_core.core.node import Step

steps = [
    Step(
        layer="ingest",
        name="read_csv",
        type="config_op",
        engine="pandas",
        value="data.csv",
        outputs={"data": "raw"}
    ),
    Step(
        layer="transform",
        name="filter",
        type="sql",
        engine="pandas",
        value="SELECT * FROM data WHERE value > 100",
        inputs={"data": "raw"},
        outputs={"data": "filtered"}
    )
]

pipeline = Pipeline(steps, name="custom")
result = pipeline.execute()
```

---

## Environment-Based Execution

```python
import os
from odibi_core.sdk import Pipeline

env = os.getenv("ENV", "dev")
config = f"configs/{env}_pipeline.json"

secrets = {
    "db_pass": os.getenv("DB_PASS"),
    "api_key": os.getenv("API_KEY")
}

pipeline = Pipeline.from_config(config)
pipeline.set_engine("pandas").set_secrets(secrets)
result = pipeline.execute()
```

---

## Version Information

```python
from odibi_core.__version__ import (
    __version__, 
    __phase__, 
    __supported_engines__
)

print(f"Version: {__version__}")
print(f"Phase: {__phase__}")
print(f"Engines: {__supported_engines__}")
```

---

## Access Result Data

```python
result = pipeline.execute()

# Summary
print(result.summary())

# Status
is_success = result.is_success()

# Metrics
print(f"Success: {result.success_count}")
print(f"Failed: {result.failed_count}")
print(f"Duration: {result.total_duration_ms}ms")

# Output data
for name, df in result.data_map.items():
    print(f"{name}: {len(df)} rows")

# Node results
for node_result in result.results:
    print(f"{node_result.node_name}: {node_result.state}")
```

---

## Legacy API (Still Works)

```python
from odibi_core.core import ConfigLoader
from odibi_core.core import create_engine_context
from odibi_core.core import Tracker, EventEmitter

loader = ConfigLoader()
steps = loader.load("pipeline.json")

context = create_engine_context("pandas")
tracker = Tracker()
events = EventEmitter()

# ... execute as before
```

---

## Common Patterns

### Validate Then Execute
```bash
odibi validate --config pipeline.json && \
odibi run --config pipeline.json
```

### Python Script with Error Handling
```python
from odibi_core.sdk import ODIBI

try:
    ODIBI.validate("pipeline.json")
    result = ODIBI.run("pipeline.json")
    if not result.is_success():
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
```

### CI/CD Integration
```yaml
- name: Run Pipeline
  run: |
    pip install -e .
    odibi validate --config pipeline.json --strict
    odibi run --config pipeline.json --verbose
  env:
    DB_PASS: ${{ secrets.DB_PASS }}
```

---

## Error Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Validation failed or pipeline failed |

---

## Files & Locations

| File | Purpose |
|------|---------|
| `odibi_core/sdk/__init__.py` | SDK entry point |
| `odibi_core/cli.py` | CLI commands |
| `odibi_core/__version__.py` | Version info |
| `manifest.json` | Framework metadata |
| `pyproject.toml` | Package config |

---

## Documentation

- **Installation**: INSTALL.md
- **Full Guide**: DEVELOPER_WALKTHROUGH_PHASE_9.md
- **Completion Report**: PHASE_9_COMPLETE.md
- **This Card**: PHASE_9_QUICK_REFERENCE.md

---

## Verification

```bash
python verify_phase9.py
```

Expected: `6/6 tests passed`

---

**End of Quick Reference**  
*For detailed examples, see DEVELOPER_WALKTHROUGH_PHASE_9.md*
