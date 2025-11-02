"""
Custom theme and styling for ODIBI CORE Studio
"""

# Afro-futurist Color Scheme (Gold/Black/Emerald) - Dark Mode
COLORS_DARK = {
    "primary": "#F5B400",  # Bold Gold
    "secondary": "#00A86B",  # Emerald Green
    "accent": "#FFD700",  # Bright Gold
    "background": "#0A0A0A",  # Deep Black
    "surface": "#1A1A1A",  # Rich Black Surface
    "text": "#FFFFFF",  # Pure White text
    "text_secondary": "#C0C0C0",  # Silver Gray text
    "success": "#00A86B",  # Emerald
    "error": "#E63946",  # Bold Red
    "warning": "#F77F00",  # Vibrant Orange
    "info": "#06A6CE",  # Cyan Blue
    "gradient_start": "#F5B400",  # Gold
    "gradient_end": "#00A86B",  # Emerald
}

# Light Mode Colors - Vibrant Afro-futurist (Sun-kissed Gold/Emerald)
COLORS_LIGHT = {
    "primary": "#D97706",  # Deep Amber (better contrast on light bg)
    "secondary": "#047857",  # Deep Emerald (better contrast)
    "accent": "#F59E0B",  # Bright Gold accent
    "background": "#FFFBF0",  # Very light warm cream
    "surface": "#FFFFFF",  # Pure white surface
    "text": "#1F2937",  # Dark gray (excellent readability)
    "text_secondary": "#6B7280",  # Medium gray
    "success": "#10B981",  # Bright emerald green
    "error": "#DC2626",  # Deep red
    "warning": "#EA580C",  # Deep orange
    "info": "#2563EB",  # Deep blue
    "gradient_start": "#D97706",  # Deep Amber
    "gradient_end": "#047857",  # Deep Emerald
    "shadow": "rgba(217, 119, 6, 0.15)",  # Amber shadow
}

# Default to dark mode
COLORS = COLORS_DARK

# Custom CSS - Afro-futurist Aesthetic
CUSTOM_CSS = f"""
<style>
    /* Main theme - Afro-futurist minimalism */
    .stApp {{
        background-color: {COLORS['background']};
        background-image: 
            linear-gradient(rgba(245, 180, 0, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245, 180, 0, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
    }}
    
    /* Headers - Bold and confident */
    h1 {{
        color: {COLORS['primary']};
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: -0.02em;
        text-transform: none;
    }}
    
    h2 {{
        color: {COLORS['secondary']};
        font-weight: 700;
        letter-spacing: -0.01em;
    }}
    
    h3 {{
        color: {COLORS['accent']};
        font-weight: 600;
    }}
    
    /* Buttons - Vibrant and interactive */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        color: {COLORS['background']};
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(245, 180, 0, 0.3);
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['primary']});
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 168, 107, 0.4);
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: {COLORS['surface']};
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background-color: {COLORS['surface']};
        border-left: 3px solid {COLORS['primary']};
    }}
    
    /* Metrics */
    .css-1xarl3l {{
        background-color: {COLORS['surface']};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Info boxes */
    .info-box {{
        background-color: {COLORS['surface']};
        border-left: 4px solid {COLORS['info']};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }}
    
    .success-box {{
        background-color: {COLORS['surface']};
        border-left: 4px solid {COLORS['success']};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background-color: {COLORS['surface']};
        border-left: 4px solid {COLORS['warning']};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }}
    
    /* Cards */
    .card {{
        background-color: {COLORS['surface']};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['surface']};
        border-radius: 4px 4px 0 0;
        color: {COLORS['text_secondary']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']};
        color: {COLORS['background']};
    }}
    
    /* DataFrames */
    .dataframe {{
        border: 1px solid {COLORS['primary']} !important;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: {COLORS['surface']};
        border-radius: 4px;
    }}
</style>
"""

def apply_theme(theme_mode='dark'):
    """Apply custom theme to Streamlit app"""
    import streamlit as st
    
    # Select color scheme based on mode
    if theme_mode == 'light':
        colors = COLORS_LIGHT
    else:
        colors = COLORS_DARK
    
    # Generate CSS with selected colors
    css = generate_css(colors)
    st.markdown(css, unsafe_allow_html=True)
    
    return colors

def generate_css(colors):
    """Generate CSS with given color scheme"""
    shadow = colors.get('shadow', 'rgba(0, 0, 0, 0.1)')
    is_dark = colors.get('background', '#000000').startswith('#0') or colors.get('background', '#000000').startswith('#1')
    
    return f"""
<style>
    /* Main theme - Afro-futurist minimalism */
    .stApp {{
        background-color: {colors['background']};
        background-image: 
            linear-gradient(rgba(245, 158, 11, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245, 158, 11, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
    }}
    
    /* Headers - Bold and confident */
    h1 {{
        color: {colors['primary']};
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px {shadow};
    }}
    
    h2 {{
        color: {colors['secondary']};
        font-weight: 700;
        letter-spacing: -0.01em;
    }}
    
    h3 {{
        color: {colors['accent']};
        font-weight: 600;
    }}
    
    /* Text color - IMPORTANT (but exclude code blocks!) */
    p, div:not([data-testid="stCode"]), span:not(pre *), label, .stMarkdown {{
        color: {colors['text']} !important;
    }}
    
    /* Explicitly allow syntax highlighting in code blocks */
    pre code, pre code * {{
        color: inherit !important;
    }}
    
    /* Dropdown/Select boxes - FIX FOR LIGHT MODE */
    .stSelectbox > div > div {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border: 2px solid {colors['primary']}44 !important;
    }}
    
    .stSelectbox label {{
        color: {colors['text']} !important;
    }}
    
    /* Select dropdown container */
    div[data-baseweb="select"] {{
        background-color: {colors['surface']} !important;
    }}
    
    /* Select dropdown control (the clickable part) */
    div[data-baseweb="select"] > div {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['primary']}44 !important;
    }}
    
    /* Dropdown menu (the options list) - CRITICAL FIX */
    ul[role="listbox"] {{
        background-color: {colors['surface']} !important;
    }}
    
    /* Dropdown menu items */
    li[role="option"] {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Dropdown menu items on hover */
    li[role="option"]:hover {{
        background-color: {colors['primary']}22 !important;
        color: {colors['text']} !important;
    }}
    
    /* Selected option in dropdown */
    div[data-baseweb="select"] span {{
        color: {colors['text']} !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border: 2px solid {colors['primary']}44;
    }}
    
    /* Text areas */
    .stTextArea > div > div > textarea {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border: 2px solid {colors['primary']}44;
    }}
    
    /* Buttons - Vibrant and interactive with pulse animation */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['primary']}, {colors['accent']});
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px {shadow};
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {colors['secondary']}, {colors['primary']});
        color: white;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 24px {shadow};
        animation: pulse 0.6s ease-in-out;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: translateY(-2px) scale(1.02); }}
        50% {{ transform: translateY(-2px) scale(1.05); }}
    }}
    
    /* Sidebar - Enhanced */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {colors['surface']} 0%, {colors['background']} 100%) !important;
        border-right: 1px solid {colors['primary']}33;
    }}
    
    /* Sidebar content background */
    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
    }}
    
    /* Sidebar widgets */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stRadio > div,
    section[data-testid="stSidebar"] button {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Code blocks - Just add gold border and shadow, let Streamlit handle highlighting */
    pre[data-testid="stCode"] {{
        border: 3px solid {colors['primary']} !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(245, 180, 0, 0.4) !important;
        padding: 1.5rem !important;
        background-color: #0D1117 !important;
    }}
    
    pre code {{
        font-family: 'Fira Code', 'Consolas', 'Monaco', monospace !important;
        font-size: 1rem !important;
        line-height: 1.8 !important;
    }}
    
    /* Info boxes - Enhanced */
    .stAlert {{
        background-color: {colors['surface']};
        border-radius: 8px;
        box-shadow: 0 2px 8px {shadow};
    }}
    
    /* Progress bars */
    .stProgress > div > div {{
        background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: {colors['surface']}44;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        background-color: {colors['primary']}22;
        transform: translateX(4px);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {colors['surface']};
        border-radius: 8px 8px 0 0;
        color: {colors['text_secondary']};
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {colors['primary']}22;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
        color: white;
    }}
    
    /* Radio buttons and checkboxes */
    input[type="radio"]:checked {{
        background-color: {colors['primary']};
    }}
    
    /* Radio button labels - readable in both modes */
    .stRadio label {{
        color: {colors['text']} !important;
    }}
    
    /* Metric labels and values */
    .stMetric label {{
        color: {colors['text']} !important;
    }}
    
    .stMetric [data-testid="stMetricValue"] {{
        color: {colors['primary']} !important;
    }}
    
    /* Caption text */
    .caption, small {{
        color: {colors['text_secondary']} !important;
    }}
    
    /* Info/Success/Warning/Error boxes */
    .stAlert > div {{
        color: {colors['text']} !important;
    }}
    
    /* Ensure sidebar text is readable */
    section[data-testid="stSidebar"] * {{
        color: {colors['text']} !important;
    }}
    
    /* Navigation tree items */
    .css-1544g2n, .css-16huue1 {{
        color: {colors['text']} !important;
    }}
    
    /* Expander content - make sure it's readable */
    .streamlit-expanderContent {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}
    
    /* ALL selectbox related elements - nuclear option */
    [class*="selectbox"] * {{
        color: {colors['text']} !important;
    }}
    
    /* Popover/menu backgrounds (where dropdown options appear) */
    div[data-baseweb="popover"] {{
        background-color: {colors['surface']} !important;
    }}
    
    div[data-baseweb="popover"] * {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Menu list */
    div[data-baseweb="menu"] ul {{
        background-color: {colors['surface']} !important;
    }}
    
    /* Success toast animation */
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
</style>
"""

def info_box(message: str):
    """Display an info box"""
    import streamlit as st
    st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)

def success_box(message: str):
    """Display a success box"""
    import streamlit as st
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)

def warning_box(message: str):
    """Display a warning box"""
    import streamlit as st
    st.markdown(f'<div class="warning-box">⚠️ {message}</div>', unsafe_allow_html=True)

def error_box(message: str):
    """Display an error box"""
    import streamlit as st
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['error']}; 
                padding: 1rem; border-radius: 4px; margin: 1rem 0;'>
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def card(content: str):
    """Display content in a card"""
    import streamlit as st
    st.markdown(f'<div class="card">{content}</div>', unsafe_allow_html=True)
