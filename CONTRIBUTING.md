# Contributing to ODIBI Core

Thank you for your interest in contributing to ODIBI Core! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/odibi_core.git
cd odibi_core
```

### 2. Install Development Dependencies

```bash
# Install with all development tools
pip install -e ".[dev]"

# Verify installation
odibi version
pytest --version
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-description
```

---

## Development Workflow

### Project Structure

```
odibi_core/
├── odibi_core/          # Core framework code
│   ├── core/            # Base classes (Node, EngineContext, Orchestrator)
│   ├── nodes/           # Node implementations
│   ├── engine/          # Pandas and Spark engines
│   ├── functions/       # Pure computational functions
│   ├── learnodibi/      # Teaching module
│   └── learnodibi_ui/   # Streamlit UI
├── tests/               # Test suite
├── scripts/             # Development utilities
├── docs/                # Documentation
└── examples/            # Example pipelines
```

### Development Commands

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_pandas_engine.py

# Run with coverage
pytest --cov=odibi_core --cov-report=html

# Format code
black odibi_core/

# Type check
mypy odibi_core/

# Validate project structure
python scripts/verify_reorganization.py

# Validate LearnODIBI content
python scripts/validate_learnodibi.py
```

---

## Code Style Guidelines

### Python Code Style

- **Formatter**: Black (line length: 100)
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings with Args/Returns/Example sections
- **Imports**: Standard library → third-party → local modules

**Example:**

```python
from typing import Dict, Any
from pathlib import Path

def process_data(data: Dict[str, Any], config_path: Path) -> Dict[str, Any]:
    """
    Process data according to configuration.
    
    Args:
        data: Input data dictionary
        config_path: Path to configuration file
        
    Returns:
        Processed data dictionary
        
    Example:
        >>> result = process_data({"key": "value"}, Path("config.json"))
    """
    # Implementation
    return data
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `DataReader`, `TransformNode`)
- **Functions/Variables**: snake_case (e.g., `read_data`, `file_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private Members**: Leading underscore (e.g., `_internal_method`)

### Error Handling

Use the `log_exceptions` decorator for all public methods:

```python
from odibi_core.logger.decorator import log_exceptions

@log_exceptions(module="my_module", component="MyClass", error_type="ProcessingError")
def process(self, data):
    # Implementation
    pass
```

---

## Testing

### Writing Tests

- Use `pytest` for all tests
- Place tests in `tests/` directory mirroring source structure
- Use fixtures defined in `conftest.py`
- Use `unittest.mock.MagicMock` for mocking

**Example Test:**

```python
import pytest
from unittest.mock import MagicMock
from odibi_core.engine import PandasEngineContext

def test_read_csv(tmp_path):
    """Test reading CSV files with Pandas engine."""
    # Setup
    ctx = PandasEngineContext()
    test_file = tmp_path / "data.csv"
    test_file.write_text("col1,col2\\n1,2\\n3,4")
    
    # Execute
    df = ctx.read(str(test_file))
    
    # Assert
    assert len(df) == 2
    assert list(df.columns) == ["col1", "col2"]
```

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_flow():
    pass

@pytest.mark.parity
def test_pandas_spark_parity():
    pass
```

Run specific categories:

```bash
pytest -m unit      # Unit tests only
pytest -m parity    # Parity tests only
```

---

## Documentation

### Documentation Standards

1. **Update READMEs**: When adding new modules, create a README.md
2. **Docstrings**: All public functions/classes must have docstrings
3. **Walkthroughs**: Update LearnODIBI content for major features
4. **AGENTS.md**: Document build commands and conventions

### Documentation Locations

- **User Docs**: `README.md`, `INSTALL.md`, `QUICK_START.md`
- **Module Docs**: `odibi_core/MODULE/README.md`
- **API Reference**: Inline docstrings (auto-generated in Phase 10)
- **Walkthroughs**: `docs/walkthroughs/`
- **Guides**: `docs/guides/`

---

## Submitting Changes

### Before Submitting

1. **Run all tests**: `pytest`
2. **Format code**: `black odibi_core/`
3. **Type check**: `mypy odibi_core/`
4. **Update documentation**: Add/update relevant docs
5. **Add tests**: Ensure new code has test coverage

### Commit Messages

Use conventional commit format:

```
type(scope): brief description

Detailed explanation of changes (optional)

Fixes #issue_number (if applicable)
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

**Examples:**

```
feat(nodes): add S3 connector node
fix(engine): resolve Spark temp view registration bug
docs(learnodibi): update Phase 5 walkthrough
test(parity): add cross-engine validation for SQL transforms
```

### Pull Request Process

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**:
   - Describe what the PR does
   - Reference related issues
   - Include screenshots for UI changes

3. **CI/CD Checks**:
   - All tests must pass
   - Code coverage must not decrease
   - Black formatting enforced

4. **Code Review**:
   - Address reviewer feedback
   - Make requested changes
   - Re-request review after updates

5. **Merge**:
   - Maintainer will merge once approved
   - Branch will be deleted after merge

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions and reviews

### Reporting Bugs

When reporting bugs, include:

1. **Description**: What happened vs. what was expected
2. **Steps to reproduce**: Minimal reproducible example
3. **Environment**: Python version, OS, ODIBI version
4. **Error messages**: Full stack traces if applicable

**Template:**

```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happened

**Environment:**
- ODIBI Version: 1.1.0
- Python Version: 3.10.5
- OS: Windows 11 / macOS / Linux

**Error Message:**
\```
Paste full error here
\```
```

### Feature Requests

For feature requests, describe:

1. **Use case**: What problem does it solve?
2. **Proposed solution**: How would it work?
3. **Alternatives**: Other approaches considered
4. **Impact**: Who would benefit?

---

## Areas to Contribute

### High Priority

- 🐛 **Bug Fixes**: Check open issues
- 📝 **Documentation**: Improve clarity, fix typos, add examples
- 🧪 **Tests**: Increase coverage, add parity tests
- 🎨 **LearnODIBI**: Improve UI, add walkthroughs, expand quizzes

### Medium Priority

- ✨ **Features**: Implement planned roadmap items
- 🔧 **Tools**: Add development utilities
- 📊 **Examples**: Create sample pipelines

### Advanced

- 🚀 **Performance**: Optimize critical paths
- 🔌 **Connectors**: Add new data sources (databases, APIs, cloud)
- 🎓 **Teaching**: Create video tutorials, blog posts

---

## Questions?

If you have questions about contributing:

- Check the [docs/index.md](docs/index.md) for project overview
- Read existing code and tests for examples
- Ask in GitHub Discussions
- Email: henry@odibi.com

---

**Thank you for contributing to ODIBI Core!** 🎉

Your contributions help make data engineering more accessible and productive for everyone.
