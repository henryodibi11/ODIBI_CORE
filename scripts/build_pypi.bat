@echo off
REM ============================================
REM ODIBI CORE - PyPI Package Build Script (Windows)
REM ============================================
REM This script builds distribution packages for PyPI upload
REM Usage: scripts\build_pypi.bat

echo.
echo Building ODIBI CORE package for PyPI...
echo ==========================================
echo.

REM Check if build package is installed
python -c "import build" 2>nul
if errorlevel 1 (
    echo Installing build package...
    pip install --upgrade build twine
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Build source distribution and wheel
echo.
echo Building distribution packages...
python -m build

REM Check the built packages
echo.
echo Checking packages with twine...
twine check dist/*

REM Display built packages
echo.
echo ==========================================
echo Build complete! Generated packages:
echo ==========================================
dir dist

echo.
echo To upload to PyPI:
echo    Test PyPI:  twine upload --repository testpypi dist/*
echo    Production: twine upload dist/*
echo.
echo Verify installation:
echo    pip install odibi-core
echo    python -c "from odibi_core.engine import PandasEngineContext"
echo.

pause
