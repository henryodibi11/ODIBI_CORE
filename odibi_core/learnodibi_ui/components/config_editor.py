"""
JSON Configuration Editor Component
"""

import streamlit as st
import json
from typing import Dict, Any, Optional


def config_editor(
    config: Dict[str, Any],
    title: str = "Configuration Editor",
    key: str = "config_editor",
    help_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Interactive JSON configuration editor
    
    Args:
        config: Initial configuration dictionary
        title: Editor title
        key: Unique key for the component
        help_text: Optional help text to display
        
    Returns:
        Updated configuration dictionary
    """
    st.subheader(title)
    
    if help_text:
        st.info(help_text)
    
    # Create tabs for visual and JSON editing
    tab1, tab2 = st.tabs(["📝 Visual Editor", "🔧 JSON Editor"])
    
    with tab1:
        edited_config = _visual_editor(config, key)
    
    with tab2:
        edited_config = _json_editor(config, key)
    
    # Validation
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("✅ Validate Configuration", key=f"{key}_validate"):
            is_valid, message = _validate_config(edited_config)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
    
    with col2:
        if st.button("🔄 Reset", key=f"{key}_reset"):
            st.rerun()
    
    return edited_config


def _visual_editor(config: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Visual form-based editor"""
    edited = {}
    
    st.markdown("##### Edit configuration fields:")
    
    for field_key, value in config.items():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"**{field_key}**")
        
        with col2:
            if isinstance(value, bool):
                edited[field_key] = st.checkbox(
                    "Value",
                    value=value,
                    key=f"{key}_visual_{field_key}",
                    label_visibility="collapsed"
                )
            elif isinstance(value, int):
                edited[field_key] = st.number_input(
                    "Value",
                    value=value,
                    key=f"{key}_visual_{field_key}",
                    label_visibility="collapsed"
                )
            elif isinstance(value, float):
                edited[field_key] = st.number_input(
                    "Value",
                    value=value,
                    format="%.4f",
                    key=f"{key}_visual_{field_key}",
                    label_visibility="collapsed"
                )
            elif isinstance(value, (list, dict)):
                # For complex types, show as JSON
                json_str = json.dumps(value, indent=2)
                edited_json = st.text_area(
                    "Value",
                    value=json_str,
                    height=100,
                    key=f"{key}_visual_{field_key}",
                    label_visibility="collapsed"
                )
                try:
                    edited[field_key] = json.loads(edited_json)
                except json.JSONDecodeError:
                    edited[field_key] = value
                    st.error(f"Invalid JSON for {field_key}")
            else:
                edited[field_key] = st.text_input(
                    "Value",
                    value=str(value),
                    key=f"{key}_visual_{field_key}",
                    label_visibility="collapsed"
                )
    
    return edited


def _json_editor(config: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Raw JSON editor"""
    json_str = json.dumps(config, indent=2)
    
    st.markdown("##### Edit raw JSON:")
    
    edited_json = st.text_area(
        "JSON Configuration",
        value=json_str,
        height=400,
        key=f"{key}_json",
        help="Edit the JSON configuration directly",
        label_visibility="collapsed"
    )
    
    try:
        edited_config = json.loads(edited_json)
        st.success("✅ Valid JSON")
        return edited_config
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON: {str(e)}")
        return config


def _validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """Validate configuration"""
    if not config:
        return False, "Configuration is empty"
    
    # Basic validation
    required_fields = []  # Add required fields if needed
    
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    return True, "Configuration is valid"


def config_template_selector(templates: Dict[str, Dict[str, Any]], key: str = "template") -> Optional[Dict[str, Any]]:
    """Select from predefined configuration templates"""
    st.markdown("##### Choose a template:")
    
    template_names = ["Custom"] + list(templates.keys())
    selected = st.selectbox(
        "Template",
        template_names,
        key=f"{key}_selector",
        label_visibility="collapsed"
    )
    
    if selected == "Custom":
        return None
    else:
        return templates[selected]
