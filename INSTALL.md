# ODIBI CORE v1.0 - Installation Guide

## Quick Install

### Option 1: Docker (Recommended for Quick Start with LearnODIBI Studio)

**Prerequisites:** Docker and Docker Compose installed

```bash
cd odibi_core

# Build and run with Docker Compose (one command!)
docker-compose up

# Access LearnODIBI Studio at: http://localhost:8501
```

**Benefits:**
- ✅ No Python installation required
- ✅ All dependencies included
- ✅ LearnODIBI Studio ready out-of-the-box
- ✅ Isolated environment
- ✅ Easy cleanup

See [Docker Installation](#docker-installation) section below for details.

---

### Option 2: Install with All Dependencies (Recommended for Development)

```bash
cd odibi_core
pip install -e ".[dev]"
```

This installs:
- ✅ pandas (required)
- ✅ duckdb (for PandasEngineContext SQL)
- ✅ pyspark (for SparkEngineContext)
- ✅ pytest and development tools

### Option 3: Minimal Install (Pandas Only)

```bash
pip install -e .
```

This installs only:
- pandas
- typing-extensions

Then add engines as needed:
```bash
# For PandasEngineContext with SQL
pip install duckdb

# For SparkEngineContext
pip install pyspark
```

### Option 4: Install from requirements.txt

```bash
pip install -r requirements.txt
```

### Option 5: Install LearnODIBI Studio (Interactive Learning UI)

```bash
# Install with Studio dependencies
pip install -e ".[studio]"

# Or install full dev environment (includes Studio)
pip install -e ".[dev]"

# Launch Studio
streamlit run odibi_core/learnodibi_ui/app.py
# Or use convenience scripts:
# Linux/Mac: ./run_studio.sh
# Windows: run_studio.bat
```

**Studio Features:**
- 🎓 Interactive tutorials and examples
- 📊 Visual DataFrame operations
- 🔄 Live code execution
- 📈 Data visualization with Plotly
- 🧪 Experimentation sandbox

---

## Dependency Matrix

| Component | Required | Optional | Purpose |
|-----------|----------|----------|---------|
| **pandas** | ✅ | | Core DataFrame operations |
| **duckdb** | | ✅ | SQL support in PandasEngineContext |
| **pyspark** | | ✅ | SparkEngineContext |
| **iapws** | | ✅ | Thermodynamic functions (Phase 7+) |
| **pytest** | | ✅ | Running tests |

---

## Installation Options

### For End Users (Using Pandas)

```bash
pip install pandas duckdb
```

Then:
```python
from odibi_core.engine import PandasEngineContext

ctx = PandasEngineContext()
ctx.connect()
```

### For End Users (Using Spark)

```bash
pip install pandas pyspark
```

Then:
```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()
ctx.connect()
```

### For Developers

```bash
# Clone repository
git clone <repo-url>
cd odibi_core

# Install in editable mode with all dependencies
pip install -e ".[dev]"

# Verify installation
python verify_phase2.py
```

---

## Verify Installation

### Quick Verification

```bash
python verify_phase2.py
```

**Expected output:**
```
✅ Engine imports successful
✅ Pandas context created and connected
✅ All Pandas methods present
✅ Spark context created
✅ All Spark methods present
✅ Engine factory works
```

### Run Tests

```bash
# All tests
pytest

# Pandas tests only
pytest tests/test_pandas_engine.py -v

# Spark tests only  
pytest tests/test_spark_engine.py -v

# Parity demo
python -m odibi_core.examples.parity_demo
```

---

## Troubleshooting

### Issue: "ImportError: No module named 'duckdb'"

**Solution:**
```bash
pip install duckdb
```

Or install without DuckDB and avoid SQL operations in PandasEngineContext.

### Issue: "ImportError: No module named 'pyspark'"

**Solution:**
```bash
pip install pyspark
```

Or use PandasEngineContext instead.

### Issue: "JAVA_HOME not set" (Spark on Windows)

**Solution:**
1. Install Java 8 or 11
2. Set JAVA_HOME environment variable
3. Restart terminal

Or use PandasEngineContext for local development.

### Issue: Tests are skipped

Tests automatically skip if dependencies are missing:
- `test_pandas_engine.py` - Skips SQL tests if duckdb not installed
- `test_spark_engine.py` - Skips all tests if pyspark not installed

This is expected behavior. Install the missing dependency to run those tests.

---

## Python Version Requirements

**Minimum**: Python 3.8  
**Recommended**: Python 3.10+

Check your version:
```bash
python --version
```

---

## Virtual Environment (Recommended)

Create isolated environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install ODIBI CORE
pip install -e ".[dev]"
```

---

## Platform-Specific Notes

### Windows

- Use `python` instead of `python3`
- Use `pip` instead of `pip3`
- Backslashes in paths: `d:\projects\odibi_core`
- May need to install Java for Spark

### Linux/Mac

- May need `python3` and `pip3` explicitly
- Forward slashes in paths: `/home/user/odibi_core`
- Spark works out of the box (includes Java)

### Docker

See [Docker Installation](#docker-installation) section for complete setup.

---

---

## Docker Installation

### Quick Start with Docker Compose

**1. Start ODIBI CORE Studio:**

```bash
# Start in foreground (see logs)
docker-compose up

# Or start in background (detached mode)
docker-compose up -d
```

**2. Access LearnODIBI Studio:**

Open your browser: [http://localhost:8501](http://localhost:8501)

**3. Stop the service:**

```bash
# If running in foreground: Ctrl+C

# If running in background:
docker-compose down
```

---

### Docker Build Options

**Build from scratch:**

```bash
# Build the image
docker build -t odibi-core:latest .

# Run the container
docker run -p 8501:8501 \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  odibi-core:latest
```

**Custom configuration:**

```bash
# Run with custom environment variables
docker run -p 8501:8501 \
  -e ODIBI_LOG_LEVEL=DEBUG \
  -e STREAMLIT_SERVER_PORT=8501 \
  -v $(pwd)/data:/data \
  odibi-core:latest
```

---

### Docker Compose Configuration

The `docker-compose.yml` includes:

- ✅ **Port mapping:** 8501:8501 (Streamlit)
- ✅ **Volume mounts:** 
  - `./logs` - Persistent logs
  - `./artifacts` - Output files
  - `./data` - Data files
  - `./examples` - Example notebooks
- ✅ **Health checks:** Automatic service monitoring
- ✅ **Restart policy:** Auto-restart on failure
- ✅ **Resource limits:** CPU and memory controls

**Customize volumes in docker-compose.yml:**

```yaml
volumes:
  - ./my-data:/data
  - ./my-logs:/logs
```

---

### Docker Commands Reference

```bash
# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Rebuild after code changes
docker-compose up --build

# Remove containers and volumes
docker-compose down -v

# Check service health
docker-compose ps

# Execute commands in running container
docker-compose exec odibi-studio bash
```

---

### Docker Image Features

- 🐳 **Multi-stage build** - Optimized size (~500MB)
- 🔒 **Non-root user** - Enhanced security
- ✅ **Health checks** - Automatic monitoring
- 📦 **All dependencies** - Studio, DuckDB, functions
- 🚀 **Production-ready** - Minimal attack surface

---

## Next Steps

After successful installation:

1. **Run verification:** `python verify_phase2.py`
2. **Run tests:** `pytest`
3. **Try parity demo:** `python -m odibi_core.examples.parity_demo`
4. **Launch LearnODIBI Studio:** `streamlit run odibi_core/learnodibi_ui/app.py`
5. **Read documentation:** See [README.md](README.md)
6. **Explore examples:** See `odibi_core/examples/`

---

## Building PyPI Package

For maintainers who want to publish to PyPI:

**Linux/Mac:**

```bash
chmod +x scripts/build_pypi.sh
./scripts/build_pypi.sh
```

**Windows:**

```bash
scripts\build_pypi.bat
```

**Upload to PyPI:**

```bash
# Test PyPI first (recommended)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

---

## Support

**Issue tracking:** Create GitHub issue  
**Documentation:** See [README.md](README.md) and [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md)  
**Developer guide:** See [DEVELOPER_WALKTHROUGH_PHASE_1.md](DEVELOPER_WALKTHROUGH_PHASE_1.md)
