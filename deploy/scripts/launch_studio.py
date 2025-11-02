"""
Launch ODB-CORE Studio with error handling
"""
import sys
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("Launching ODB-CORE Studio...")
print("=" * 70)
print()

# Check if streamlit is available
try:
    import streamlit
    print(f"[OK] Streamlit {streamlit.__version__} found")
except ImportError:
    print("[ERROR] Streamlit not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "watchdog"])
    print("[OK] Dependencies installed")

# Check for required modules
print("\nChecking modules...")
required_modules = [
    "odibi_core.learnodibi_ui",
    "odibi_core.learnodibi_backend", 
    "odibi_core.learnodibi_data",
    "odibi_core.learnodibi_project"
]

all_ok = True
for module in required_modules:
    try:
        __import__(module)
        print(f"  [OK] {module}")
    except ImportError as e:
        print(f"  [ERROR] {module} - {e}")
        all_ok = False

if not all_ok:
    print("\n[ERROR] Some modules are missing. Please ensure the project is properly installed.")
    sys.exit(1)

print("\n" + "=" * 70)
print("Starting Streamlit server...")
print("=" * 70)
print("\nURL: http://localhost:8501")
print("Press Ctrl+C to stop\n")

# Launch streamlit
app_path = Path(__file__).parent / "odibi_core" / "learnodibi_ui" / "app.py"
subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)])
