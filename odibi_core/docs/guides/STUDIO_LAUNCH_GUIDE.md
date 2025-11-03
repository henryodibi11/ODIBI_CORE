# ODB-CORE Studio - Launch Guide

## 🚀 Quick Start

### Windows
```cmd
# Option 1: Use batch file
launch_studio.bat

# Option 2: Direct command
python -m streamlit run odibi_core\learnodibi_ui\app.py
```

### Linux/Mac
```bash
# Option 1: Use shell script  
./run_studio.sh

# Option 2: Direct command
python -m streamlit run odibi_core/learnodibi_ui/app.py
```

## 📍 Access

Once launched, the studio will be available at:
- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

## ⚠️ Troubleshooting

### Issue: "streamlit is not recognized"
**Solution**: The Python Scripts folder is not in your PATH. Use:
```cmd
python -m streamlit run odibi_core\learnodibi_ui\app.py
```

### Issue: ModuleNotFoundError for streamlit/plotly
**Solution**: Install dependencies:
```cmd
pip install streamlit plotly watchdog
```

Or install all studio dependencies:
```cmd
pip install -e ".[studio]"
```

### Issue: Page configuration error
**Solution**: This was fixed. Make sure you have the latest app.py with `st.set_page_config()` as the first Streamlit command.

### Issue: Import errors for odibi_core modules
**Solution**: Install the package in development mode:
```cmd
cd d:\projects\odibi_core
pip install -e .
```

### Issue: Unicode/encoding errors on Windows
**Solution**: The code now handles Windows console encoding automatically.

## 🔧 Advanced Options

### Custom Port
```cmd
python -m streamlit run odibi_core\learnodibi_ui\app.py --server.port=8502
```

### Headless Mode (for servers)
```cmd
python -m streamlit run odibi_core\learnodibi_ui\app.py --server.headless=true
```

### Enable CORS (for remote access)
```cmd
python -m streamlit run odibi_core\learnodibi_ui\app.py --server.enableCORS=false
```

## 📚 What to Expect

Once launched, you'll see:

1. **Home Page** - Welcome screen with feature overview
2. **5 Navigation Pages**:
   - **Core Concepts** - Learn the 5 canonical node types
   - **Functions Explorer** - Browse and test functions interactively
   - **SDK Examples** - Runnable code examples
   - **Demo Project** - Complete Bronze→Silver→Gold pipeline
   - **Docs** - Documentation viewer

3. **Professional Theme**:
   - Gold (#F5B400) primary color
   - Teal (#00796B) secondary color
   - Dark background for reduced eye strain

4. **Interactive Features**:
   - Click "Try It" buttons to run examples
   - Download results as CSV/JSON/Parquet
   - Real-time execution metrics
   - Visualizations with Plotly charts

## ✅ Verification

To verify everything is working:
```cmd
python verify_phase10.py
```

This will check:
- All modules import correctly
- All UI files exist
- Backend API is functional
- Demo pipeline runs successfully

Expected output: `PHASE 10 VERIFICATION: PASSED (8/8)`

## 🆘 Still Having Issues?

1. Check you're in the correct directory:
   ```cmd
   cd d:\projects\odibi_core
   ```

2. Verify Python version (3.8+ required):
   ```cmd
   python --version
   ```

3. Check installed packages:
   ```cmd
   pip list | findstr streamlit
   pip list | findstr plotly
   ```

4. View full error logs:
   ```cmd
   python -m streamlit run odibi_core\learnodibi_ui\app.py > studio_log.txt 2>&1
   ```

## 📞 Support

- Check [README.md](README.md) for general project info
- See [INSTALL.md](INSTALL.md) for installation details
- Read [PHASE_10_COMPLETE.md](PHASE_10_COMPLETE.md) for Phase 10 details
- View [LEARNODIBI_STUDIO_VERIFICATION.md](LEARNODIBI_STUDIO_VERIFICATION.md) for verification report

---

**Happy Learning with ODB-CORE Studio!** 🎉
