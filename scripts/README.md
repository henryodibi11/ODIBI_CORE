# Scripts - Developer Utilities

**Purpose**: Collection of utility scripts for development, testing, validation, and maintenance of ODIBI Core.

---

## Overview

This directory contains helper scripts used during development, testing, and deployment of the ODIBI Core framework.

## Available Scripts

### Validation Scripts

#### `validate_learnodibi.py`
Validates the LearnODIBI platform configuration and content.

**Usage:**
```bash
python scripts/validate_learnodibi.py
```

**Checks:**
- Walkthrough manifest integrity
- Markdown file existence
- Quiz structure validation
- Link verification

#### `test_paths.py`
Tests file path resolution across different modules.

**Usage:**
```bash
python scripts/test_paths.py
```

### Cleanup Scripts

#### `fix_pass_statements.py`
Removes placeholder `pass` statements from code.

**Usage:**
```bash
python scripts/fix_pass_statements.py
```

#### `verify_reorganization.py`
Verifies project structure after reorganization.

**Usage:**
```bash
python scripts/verify_reorganization.py
```

### Build Scripts

#### `reorganize.ps1` (PowerShell)
Reorganizes project structure (Windows).

**Usage:**
```powershell
.\scripts\reorganize.ps1
```

## Development Workflow

### 1. Before Committing Code
```bash
# Validate project structure
python scripts/verify_reorganization.py

# Validate LearnODIBI content
python scripts/validate_learnodibi.py

# Run tests
pytest
```

### 2. After Major Refactoring
```bash
# Check path resolution
python scripts/test_paths.py

# Fix code quality issues
python scripts/fix_pass_statements.py
```

### 3. Preparing for Release
```bash
# Validate all content
python scripts/validate_learnodibi.py

# Run full test suite
pytest --cov=odibi_core

# Build package
pip install -e .
```

## Adding New Scripts

### Template for Utility Scripts

```python
#!/usr/bin/env python3
"""
Script Name: my_utility.py
Purpose: Brief description of what this script does
Author: Your Name
Date: YYYY-MM-DD
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main script logic."""
    print("Running utility...")
    # Your code here
    print("✅ Complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
```

### Best Practices

1. **Documentation**: Include docstrings and comments
2. **Error Handling**: Use try/except with meaningful error messages
3. **Exit Codes**: Return 0 for success, 1 for failure
4. **Path Handling**: Use `pathlib.Path` for cross-platform compatibility
5. **Logging**: Print progress and results clearly

## Script Categories

### 🧪 Testing & Validation
- `test_paths.py`
- `validate_learnodibi.py`
- `verify_reorganization.py`

### 🧹 Cleanup & Maintenance
- `fix_pass_statements.py`
- `reorganize.ps1`

### 🔧 Development Tools
- (Add custom dev scripts here)

### 📦 Build & Deploy
- (Add deployment scripts here)

## Dependencies

Most scripts require only standard library modules. Specific dependencies:

- `pathlib` (standard library)
- `json` (standard library)
- `argparse` (standard library)
- `pytest` (for testing scripts)

## Platform-Specific Notes

### Windows
- Use PowerShell scripts (`.ps1`) for Windows-specific tasks
- Git Bash works for most Python scripts

### Linux/Mac
- Make scripts executable: `chmod +x script.py`
- Use shebang: `#!/usr/bin/env python3`

## Troubleshooting

### Import Errors
```python
# Add project root to Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Path Issues
```python
# Use absolute paths relative to script location
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
```

## Contributing Scripts

When adding a new script:

1. Place in appropriate category directory
2. Add entry to this README
3. Include usage examples
4. Document dependencies
5. Test on target platforms

---

**Last Updated**: 2025-11-02
