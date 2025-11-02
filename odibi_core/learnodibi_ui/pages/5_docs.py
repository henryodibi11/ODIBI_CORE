"""
Documentation Viewer Page - Browse and read actual documentation files
"""

import streamlit as st
import sys
from pathlib import Path
import os
from datetime import datetime

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS

apply_theme()

# ============================================================================
# Helper Functions
# ============================================================================

def get_file_size(file_path: Path) -> str:
    """Get formatted file size"""
    size_bytes = file_path.stat().st_size
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_last_modified(file_path: Path) -> str:
    """Get formatted last modified time"""
    timestamp = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")


def scan_documentation_files():
    """Scan and organize all documentation files"""
    docs = {
        "📁 Root Documentation": [],
        "📘 Walkthroughs": [],
        "📊 Changelogs": [],
        "📖 Reference": []
    }
    
    # Root documentation files
    root_files = ["README.md", "INSTALL.md", "DOCUMENTATION_INDEX.md", 
                  "PROJECT_STATUS.md", "STUDIO_LAUNCH_GUIDE.md"]
    
    for filename in root_files:
        file_path = ODIBI_ROOT / filename
        if file_path.exists():
            docs["📁 Root Documentation"].append({
                "name": filename,
                "path": file_path,
                "size": get_file_size(file_path),
                "modified": get_last_modified(file_path)
            })
    
    # Walkthroughs
    walkthroughs_dir = ODIBI_ROOT / "docs" / "walkthroughs"
    if walkthroughs_dir.exists():
        for file_path in sorted(walkthroughs_dir.glob("*.md")):
            docs["📘 Walkthroughs"].append({
                "name": file_path.name,
                "path": file_path,
                "size": get_file_size(file_path),
                "modified": get_last_modified(file_path)
            })
    
    # Changelogs
    changelogs_dir = ODIBI_ROOT / "docs" / "changelogs"
    if changelogs_dir.exists():
        for file_path in sorted(changelogs_dir.glob("*.md")):
            docs["📊 Changelogs"].append({
                "name": file_path.name,
                "path": file_path,
                "size": get_file_size(file_path),
                "modified": get_last_modified(file_path)
            })
    
    # Reference
    reference_dir = ODIBI_ROOT / "docs" / "reference"
    if reference_dir.exists():
        for file_path in sorted(reference_dir.glob("*.md")):
            docs["📖 Reference"].append({
                "name": file_path.name,
                "path": file_path,
                "size": get_file_size(file_path),
                "modified": get_last_modified(file_path)
            })
    
    return docs


def extract_headers(content: str) -> list:
    """Extract headers from markdown content for table of contents"""
    headers = []
    for line in content.split('\n'):
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            if text:
                # Create anchor (simplified)
                anchor = text.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')
                headers.append({
                    'level': level,
                    'text': text,
                    'anchor': anchor
                })
    return headers


def search_in_content(content: str, query: str) -> list:
    """Search for query in content and return matching lines with context"""
    if not query:
        return []
    
    query_lower = query.lower()
    matches = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            # Add context (previous and next line)
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            context = '\n'.join(lines[start:end])
            matches.append({
                'line_num': i + 1,
                'text': line,
                'context': context
            })
    
    return matches


# ============================================================================
# Page Layout
# ============================================================================

st.title("📖 Documentation Browser")
st.markdown("Browse and search ODIBI CORE documentation files")
st.markdown("---")

# Initialize session state
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None
if 'doc_search_query' not in st.session_state:
    st.session_state.doc_search_query = ""

# Scan all documentation
all_docs = scan_documentation_files()

# Create layout: sidebar (30%) + main content (70%)
col_sidebar, col_main = st.columns([3, 7])

# ============================================================================
# LEFT SIDEBAR - Table of Contents
# ============================================================================

with col_sidebar:
    st.markdown("### 📑 Table of Contents")
    
    # File name filter
    filter_text = st.text_input("🔍 Filter files", placeholder="Type to filter...")
    
    st.markdown("---")
    
    # File browser organized by category
    for category, files in all_docs.items():
        if not files:
            continue
        
        # Apply filter
        filtered_files = files
        if filter_text:
            filtered_files = [
                f for f in files 
                if filter_text.lower() in f['name'].lower()
            ]
        
        if not filtered_files:
            continue
        
        with st.expander(f"{category} ({len(filtered_files)})", expanded=True):
            for doc in filtered_files:
                # Create clickable button for each file
                display_name = doc['name'].replace('.md', '')
                
                # Highlight selected file
                is_selected = (
                    st.session_state.selected_doc and 
                    st.session_state.selected_doc['path'] == doc['path']
                )
                
                button_style = "primary" if is_selected else "secondary"
                
                if st.button(
                    f"📄 {display_name}",
                    key=f"doc_{doc['path']}",
                    use_container_width=True,
                    type=button_style
                ):
                    st.session_state.selected_doc = doc
                    st.rerun()
                
                # Show metadata in small text
                st.caption(f"📏 {doc['size']} • 🕒 {doc['modified']}")

# ============================================================================
# MAIN CONTENT - Document Viewer
# ============================================================================

with col_main:
    if st.session_state.selected_doc:
        doc = st.session_state.selected_doc
        
        # Document header with metadata
        st.markdown(f"### 📄 {doc['name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📏 Size: {doc['size']}")
        with col2:
            st.caption(f"🕒 Modified: {doc['modified']}")
        with col3:
            st.caption(f"📂 Path: {doc['path'].relative_to(ODIBI_ROOT)}")
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns([2, 2, 6])
        
        with col1:
            show_raw = st.checkbox("Show Raw", value=False)
        
        with col2:
            show_toc = st.checkbox("Show TOC", value=False)
        
        # Search within document
        st.markdown("#### 🔍 Search in Document")
        doc_search = st.text_input(
            "Search within this document",
            value=st.session_state.doc_search_query,
            key="search_in_doc",
            placeholder="Enter search term..."
        )
        
        # Read file content
        try:
            content = doc['path'].read_text(encoding='utf-8')
            
            # Show search results if query exists
            if doc_search:
                st.session_state.doc_search_query = doc_search
                matches = search_in_content(content, doc_search)
                
                if matches:
                    st.success(f"Found {len(matches)} matches")
                    
                    with st.expander(f"📍 View {len(matches)} matches", expanded=True):
                        for match in matches[:20]:  # Limit to 20 matches
                            st.markdown(f"**Line {match['line_num']}:**")
                            st.code(match['context'], language='markdown')
                            st.markdown("---")
                        
                        if len(matches) > 20:
                            st.info(f"Showing first 20 of {len(matches)} matches")
                else:
                    st.warning(f"No matches found for '{doc_search}'")
                
                st.markdown("---")
            
            # Show table of contents if enabled
            if show_toc:
                headers = extract_headers(content)
                
                if headers:
                    st.markdown("#### 📋 Table of Contents")
                    
                    with st.expander("Document Structure", expanded=True):
                        for header in headers:
                            indent = "  " * (header['level'] - 1)
                            st.markdown(f"{indent}- {header['text']}")
                    
                    st.markdown("---")
            
            # Display content
            st.markdown("#### 📖 Content")
            
            if show_raw:
                # Show raw markdown
                st.code(content, language='markdown')
            else:
                # Render markdown
                st.markdown(content, unsafe_allow_html=False)
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.code(str(doc['path']))
    
    else:
        # Welcome screen when no document selected
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 3rem; border-radius: 12px; text-align: center; margin-top: 2rem;'>
            <h2 style='color: {COLORS['primary']}; margin-bottom: 1rem;'>📚 Welcome to Documentation Browser</h2>
            <p style='font-size: 1.2em; line-height: 1.6; color: {COLORS['text']};'>
                Select a document from the sidebar to start reading.
            </p>
            <p style='margin-top: 2rem; color: {COLORS['text_secondary']};'>
                Browse through walkthroughs, changelogs, reference guides, and more.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show quick stats
        st.markdown("---")
        st.markdown("### 📊 Documentation Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_docs = sum(len(files) for files in all_docs.values())
        
        with col1:
            st.metric("Total Documents", total_docs)
        
        with col2:
            st.metric("Walkthroughs", len(all_docs.get("📘 Walkthroughs", [])))
        
        with col3:
            st.metric("Changelogs", len(all_docs.get("📊 Changelogs", [])))
        
        with col4:
            st.metric("Reference Docs", len(all_docs.get("📖 Reference", [])))
        
        # Show featured documents
        st.markdown("---")
        st.markdown("### ⭐ Featured Documents")
        
        featured = [
            {
                "name": "README.md",
                "category": "📁 Root Documentation",
                "description": "Project overview and quick start guide"
            },
            {
                "name": "INSTALL.md",
                "category": "📁 Root Documentation",
                "description": "Installation instructions and requirements"
            },
            {
                "name": "PHASE_10_COMPLETE.md",
                "category": "📘 Walkthroughs",
                "description": "Complete Phase 10 implementation walkthrough"
            },
            {
                "name": "FORMAT_SUPPORT.md",
                "category": "📖 Reference",
                "description": "Supported file formats and data sources"
            },
            {
                "name": "SQL_DATABASE_SUPPORT.md",
                "category": "📖 Reference",
                "description": "SQL database connection and usage guide"
            }
        ]
        
        for feat in featured:
            # Find the actual doc
            category_docs = all_docs.get(feat['category'], [])
            doc = next((d for d in category_docs if d['name'] == feat['name']), None)
            
            if doc:
                with st.expander(f"📄 {feat['name']}", expanded=False):
                    st.markdown(feat['description'])
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.caption(f"📏 {doc['size']} • 🕒 {doc['modified']}")
                    
                    with col2:
                        if st.button("Open", key=f"open_{feat['name']}"):
                            st.session_state.selected_doc = doc
                            st.rerun()

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>💡 Tip</h4>
        <p>Use Ctrl+F to search within the page</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>📖 Quick Access</h4>
        <p>Filter files using the search box</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; text-align: center;'>
        <h4>🔄 Updates</h4>
        <p>Docs auto-refresh on file changes</p>
    </div>
    """, unsafe_allow_html=True)
