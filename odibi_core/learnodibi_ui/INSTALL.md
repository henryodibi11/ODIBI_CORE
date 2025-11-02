# ODIBI CORE Studio Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- ODIBI CORE installed

## Installation Steps

### 1. Install ODIBI CORE

If not already installed:

```bash
cd /d:/projects/odibi_core
pip install -e .
```

### 2. Install Required Dependencies

```bash
pip install streamlit plotly pandas numpy
```

Or install from requirements file (if available):

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import streamlit; import plotly; print('All dependencies installed!')"
```

## Running ODIBI CORE Studio

### Option 1: Using Quick Launch Scripts

**Windows:**
```bash
run_studio.bat
```

**Linux/Mac:**
```bash
chmod +x run_studio.sh
./run_studio.sh
```

### Option 2: Direct Streamlit Command

From project root:
```bash
streamlit run odibi_core/learnodibi_ui/app.py
```

### Option 3: Custom Port

```bash
streamlit run odibi_core/learnodibi_ui/app.py --server.port 8502
```

### Option 4: Headless Mode (Server)

```bash
streamlit run odibi_core/learnodibi_ui/app.py --server.headless true
```

## Configuration

### Custom Theme

Edit `theme.py` to customize colors:

```python
COLORS = {
    "primary": "#YOUR_COLOR",
    "secondary": "#YOUR_COLOR",
    # ...
}
```

### Custom Port (Persistent)

Create `.streamlit/config.toml`:

```toml
[server]
port = 8502
```

### Browser Settings

```toml
[browser]
gatherUsageStats = false
serverAddress = "localhost"
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'odibi_core'"

**Solution:**
```bash
# Ensure ODIBI CORE is in Python path
export PYTHONPATH="${PYTHONPATH}:/d:/projects/odibi_core"

# Or reinstall
cd /d:/projects/odibi_core
pip install -e .
```

### Issue: "Port 8501 is already in use"

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502

# Or kill existing process
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8501
kill -9 <PID>
```

### Issue: Theme not applying

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Or manually delete cache
rm -rf ~/.streamlit/cache
```

### Issue: Import errors for components

**Solution:**
Check that all component files exist:
```bash
ls odibi_core/learnodibi_ui/components/
# Should show: __init__.py, config_editor.py, data_preview.py, metrics_display.py
```

## Development Setup

### For Contributors

1. **Clone the repository:**
```bash
git clone https://github.com/yourorg/odibi_core.git
cd odibi_core
```

2. **Install in development mode:**
```bash
pip install -e ".[dev]"
```

3. **Install pre-commit hooks:**
```bash
pre-commit install
```

4. **Run in debug mode:**
```bash
streamlit run odibi_core/learnodibi_ui/app.py --logger.level=debug
```

### Running Tests

```bash
# Run all tests
pytest odibi_core/learnodibi_ui/tests/

# Run with coverage
pytest --cov=odibi_core.learnodibi_ui
```

## Docker Deployment (Optional)

### Build Image

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -e .
RUN pip install streamlit plotly

EXPOSE 8501

CMD ["streamlit", "run", "odibi_core/learnodibi_ui/app.py", "--server.address", "0.0.0.0"]
```

### Run Container

```bash
docker build -t odibi-studio .
docker run -p 8501:8501 odibi-studio
```

## Performance Optimization

### For Large Datasets

Add to `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 1000
maxMessageSize = 1000

[runner]
fastReruns = true
```

### Caching

Use Streamlit's caching decorators in custom code:

```python
@st.cache_data
def load_large_dataset():
    # Your code here
    pass
```

## Next Steps

After installation:

1. **Visit the home page** at http://localhost:8501
2. **Start with Core Concepts** to learn the fundamentals
3. **Explore the Functions Explorer** to discover available functions
4. **Run the Demo Project** to see a complete pipeline
5. **Read the Documentation** for deeper understanding

## Getting Help

- **Documentation**: Visit the Docs page in the app
- **Examples**: Check the SDK Examples page
- **Issues**: Report bugs on GitHub
- **Community**: Join discussions

## Uninstallation

To remove ODIBI CORE Studio:

```bash
pip uninstall odibi-core
rm -rf ~/.streamlit/
```

## Version Information

Check your installation:

```bash
streamlit --version
python -c "import odibi_core; print(odibi_core.__version__)"
```

---

**Created by Henry Odibi**
Part of the ODIBI CORE Framework
