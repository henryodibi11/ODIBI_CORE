# LearnODIBI UI - Streamlit Application

**Purpose**: Streamlit-based web interface for the LearnODIBI teaching platform.

---

## Overview

This module contains the Streamlit application that powers the LearnODIBI interactive learning experience. It provides a modern, responsive UI with walkthrough navigation, progress tracking, quizzes, and code examples.

## Architecture

### Entry Point
- `app.py` - Main Streamlit application

### UI Components
- **Sidebar Navigation**: Walkthrough selection and progress overview
- **Main Content Area**: Markdown rendering with syntax highlighting
- **Quiz Module**: Interactive challenge questions
- **Progress Tracker**: Visual completion indicators
- **Theme Switcher**: Dark/light mode toggle

### Key Features

#### 1. Walkthrough Rendering
- Loads markdown content from `learnodibi_data/`
- Syntax highlighting for code blocks
- Interactive table of contents
- Duration and difficulty indicators

#### 2. Quiz System
- Multiple-choice questions embedded in walkthroughs
- Instant feedback with explanations
- Progress tracking per walkthrough

#### 3. Progress Management
- Session-based completion tracking
- Visual progress bars
- Time estimation for remaining content

#### 4. Responsive Design
- Mobile-friendly layout
- Adaptive sidebar
- Smooth transitions and animations

## File Structure

```
learnodibi_ui/
├── app.py                    # Main Streamlit application
├── components/               # Reusable UI components
│   ├── sidebar.py           # Navigation sidebar
│   ├── content_viewer.py    # Markdown renderer
│   ├── quiz.py              # Quiz interface
│   └── progress.py          # Progress tracking
├── styles/                   # Custom CSS
│   ├── main.css             # Global styles
│   ├── dark_theme.css       # Dark mode
│   └── light_theme.css      # Light mode
├── utils/                    # Helper functions
│   ├── markdown_parser.py   # Markdown processing
│   ├── quiz_loader.py       # Quiz data extraction
│   └── state_manager.py     # Streamlit state management
└── README.md                # This file
```

## Running the UI

### Method 1: Python Import
```python
from odibi_core.learnodibi import launch_ui
launch_ui(port=8501)
```

### Method 2: Direct Streamlit
```bash
streamlit run odibi_core/learnodibi_ui/app.py --server.port 8501
```

### Method 3: Development Mode
```bash
cd odibi_core/learnodibi_ui
streamlit run app.py --server.runOnSave true
```

## Configuration

The UI reads configuration from:

1. **Manifest File**: `resources/walkthrough_manifest.json`
   - Walkthrough metadata
   - Content file paths
   - Quiz definitions

2. **Streamlit Config**: `.streamlit/config.toml` (project root)
   - Server settings
   - Theme defaults
   - Browser settings

3. **Environment Variables** (optional):
   - `LEARNODIBI_PORT` - Override default port
   - `LEARNODIBI_THEME` - Force dark/light theme

## Development

### Adding New Components

```python
# components/custom_widget.py
import streamlit as st

def render_custom_widget(data):
    """Render a custom UI widget."""
    st.markdown(f"### {data['title']}")
    # Your component logic
```

### Customizing Styles

```css
/* styles/custom.css */
.walkthrough-container {
    padding: 2rem;
    border-radius: 8px;
}

.code-block {
    background: #1e1e1e;
    padding: 1rem;
}
```

### State Management

```python
import streamlit as st

# Initialize state
if 'progress' not in st.session_state:
    st.session_state.progress = {}

# Update state
st.session_state.progress[walkthrough_id] = {
    'completed': True,
    'quiz_score': 85
}
```

## Dependencies

Core dependencies:
```
streamlit >= 1.32
markdown
pygments  # Syntax highlighting
```

Optional dependencies:
```
plotly    # Interactive charts
pandas    # Data display
```

## Troubleshooting

### Port Already in Use
```python
# Use a different port
launch_ui(port=8502)
```

### Content Not Loading
- Verify `resources/walkthrough_manifest.json` exists
- Check that markdown files are in `learnodibi_data/`
- Ensure file paths in manifest are correct

### Styling Issues
- Clear Streamlit cache: `streamlit cache clear`
- Check browser console for CSS errors
- Verify `.streamlit/config.toml` settings

## Performance Optimization

### Caching Walkthrough Content
```python
@st.cache_data
def load_walkthrough(content_file):
    """Cache walkthrough content for faster loading."""
    return read_markdown(content_file)
```

### Lazy Loading
```python
# Load content only when selected
if st.session_state.selected_walkthrough:
    content = load_walkthrough(
        st.session_state.selected_walkthrough
    )
```

## Accessibility

- Keyboard navigation support
- Screen reader compatible
- High contrast mode
- Adjustable font sizes

## Browser Compatibility

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Notes

- The UI uses Streamlit's session state for progress tracking (not persisted between sessions)
- All markdown content is sanitized before rendering
- Quiz answers are not sent to any server (client-side only)
- Theme preference is stored in browser localStorage

---

**Version**: 1.0.0  
**Framework**: Streamlit 1.32+  
**Last Updated**: 2025-11-02
