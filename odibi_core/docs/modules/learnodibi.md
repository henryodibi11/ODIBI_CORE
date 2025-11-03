# LearnODIBI - Interactive Teaching Module

**Purpose**: Educational interface for learning ODIBI Core through interactive walkthroughs and hands-on exercises.

---

## Overview

LearnODIBI is the teaching layer of ODIBI Core, providing an interactive Streamlit-based UI that guides users through 11 comprehensive walkthroughs covering all aspects of the framework.

## Features

- 📚 **11 Structured Walkthroughs**: From beginner to advanced (39.5 hours total)
- 🎯 **Interactive Quizzes**: Test knowledge with challenge questions
- 💻 **Code Examples**: Live demonstrations with syntax highlighting
- 📊 **Progress Tracking**: Monitor completion across all walkthroughs
- 🎨 **Modern UI**: Dark/light themes with smooth animations

## Quick Start

### Launch from Python

```python
from odibi_core.learnodibi import launch_ui

# Launch on default port (8501)
launch_ui()

# Launch on custom port
launch_ui(port=8502)
```

### Launch from CLI

```bash
# Using the learnodibi command (after installation)
learnodibi

# Or directly with streamlit
streamlit run odibi_core/learnodibi_ui/app.py
```

## Walkthrough Structure

### Beginner Track (12 hours)
1. **Scaffolding** (2h) - Project setup and architecture
2. **Dual-Engine** (5h) - Pandas and Spark parity
3. **Orchestration** (5h) - DAG execution and dependencies

### Intermediate Track (18 hours)
4. **Documentation** (1h) - Writing good docs
5. **Parallelism** (3h) - Concurrent execution
6. **Streaming** (6h) - Real-time data processing
7. **Functions** (8h) - Pure computational functions

### Advanced Track (9.5 hours)
8. **Cloud** (4h) - Azure, S3, distributed systems
9. **Observability** (1.5h) - Logging, metrics, monitoring
10. **SDK/CLI** (4h) - Building the developer interface

## Module Structure

```
learnodibi/
├── __init__.py           # Public API (launch_ui)
└── README.md             # This file

Related modules:
├── learnodibi_backend/   # Data loading and walkthrough logic
├── learnodibi_data/      # Walkthrough content (markdown files)
├── learnodibi_project/   # Project metadata
└── learnodibi_ui/        # Streamlit UI components
```

## Dependencies

- `streamlit >= 1.32` - Web UI framework
- `markdown` - Markdown rendering
- `pandas >= 2.0` - Data manipulation
- Python 3.8+

## Usage Examples

### Example 1: Launch and Learn
```python
from odibi_core.learnodibi import launch_ui

# Start the teaching platform
launch_ui()

# Navigate to http://localhost:8501
# Select a walkthrough from the sidebar
# Follow along with the interactive content
```

### Example 2: Integrate into Training Program
```python
from odibi_core.learnodibi import launch_ui
import webbrowser

# Automated training session
port = 8501
launch_ui(port=port)

# Auto-open browser (runs in background)
webbrowser.open(f"http://localhost:{port}")
```

## Configuration

The walkthrough content is defined in `resources/walkthrough_manifest.json`:

```json
{
  "walkthroughs": [
    {
      "id": "phase1_scaffolding",
      "title": "Phase 1: Foundation & Scaffolding",
      "duration_hours": 2,
      "difficulty": "beginner",
      "content_file": "DEVELOPER_WALKTHROUGH_PHASE_1.md"
    }
  ]
}
```

## Contributing Walkthroughs

To add a new walkthrough:

1. Create markdown file in `learnodibi_data/`
2. Add entry to `walkthrough_manifest.json`
3. Include quiz questions (optional)
4. Test with `launch_ui()`

## Notes

- LearnODIBI is designed for educational purposes; production pipelines should use the core SDK directly
- All walkthrough content is stored as markdown for easy editing
- The UI automatically detects and renders new walkthroughs from the manifest
- Progress tracking is session-based (not persisted)

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-02
