#!/bin/bash
# ============================================
# ODIBI CORE - PyPI Package Build Script
# ============================================
# This script builds distribution packages for PyPI upload
# Usage: ./scripts/build_pypi.sh

set -e  # Exit on error

echo "🔨 Building ODIBI CORE package for PyPI..."
echo "=========================================="

# Check if build package is installed
if ! python -c "import build" 2>/dev/null; then
    echo "📦 Installing build package..."
    pip install --upgrade build twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build source distribution and wheel
echo "📦 Building distribution packages..."
python -m build

# Check the built packages
echo "✅ Checking packages with twine..."
twine check dist/*

# Display built packages
echo ""
echo "✅ Build complete! Generated packages:"
echo "=========================================="
ls -lh dist/

echo ""
echo "📤 To upload to PyPI:"
echo "   Test PyPI:  twine upload --repository testpypi dist/*"
echo "   Production: twine upload dist/*"
echo ""
echo "📖 Verify installation:"
echo "   pip install odibi-core"
echo "   python -c 'from odibi_core.engine import PandasEngineContext'"
