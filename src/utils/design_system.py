"""
CompMe Neumorphic Design System

A soft, modern design system with neumorphic shadows and carefully
crafted color palette for the military-to-civilian compensation analyzer.
"""

# =============================================================================
# COLOR PALETTE
# =============================================================================

COLORS = {
    # Background colors
    'background': '#e0e5ec',
    'background_dark': '#d1d9e6',
    'background_light': '#f0f5fc',

    # Shadow colors (for neumorphic effect)
    'shadow_dark': '#a3b1c6',
    'shadow_light': '#ffffff',

    # Primary colors
    'primary': '#3b82f6',        # Blue - main accent
    'primary_dark': '#2563eb',
    'primary_light': '#60a5fa',

    # Semantic colors
    'success': '#10b981',        # Green - military (positive)
    'success_dark': '#059669',
    'success_light': '#34d399',

    'accent': '#8b5cf6',         # Purple - civilian
    'accent_dark': '#7c3aed',
    'accent_light': '#a78bfa',

    'warning': '#f59e0b',        # Amber
    'error': '#ef4444',          # Red
    'info': '#06b6d4',           # Cyan

    # Text colors
    'text_primary': '#1f2937',
    'text_secondary': '#4b5563',
    'text_muted': '#9ca3af',
    'text_light': '#f9fafb',

    # Chart colors
    'chart_military': '#10b981',
    'chart_civilian': '#3b82f6',
    'chart_equity': '#ec4899',
    'chart_bonus': '#8b5cf6',
}


# =============================================================================
# SHADOW SYSTEM
# =============================================================================

SHADOWS = {
    # Outset shadows (raised elements like cards, buttons)
    'outset_sm': '4px 4px 8px #a3b1c6, -4px -4px 8px #ffffff',
    'outset_md': '8px 8px 16px #a3b1c6, -8px -8px 16px #ffffff',
    'outset_lg': '12px 12px 24px #a3b1c6, -12px -12px 24px #ffffff',

    # Inset shadows (pressed elements like inputs, active tabs)
    'inset_sm': 'inset 2px 2px 4px #a3b1c6, inset -2px -2px 4px #ffffff',
    'inset_md': 'inset 4px 4px 8px #a3b1c6, inset -4px -4px 8px #ffffff',
    'inset_lg': 'inset 6px 6px 12px #a3b1c6, inset -6px -6px 12px #ffffff',

    # Flat (no shadow - for transitions)
    'flat': 'none',
}


# =============================================================================
# TYPOGRAPHY
# =============================================================================

TYPOGRAPHY = {
    'font_family': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",

    # Font sizes
    'h1': '2rem',
    'h2': '1.5rem',
    'h3': '1.25rem',
    'body': '1rem',
    'small': '0.875rem',
    'xs': '0.75rem',

    # Font weights
    'weight_normal': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',

    # Metric typography
    'metric_value': '1.5rem',
    'metric_label': '0.75rem',

    # Line heights
    'line_height_tight': '1.25',
    'line_height_normal': '1.5',
    'line_height_relaxed': '1.75',
}


# =============================================================================
# SPACING SCALE (4px base)
# =============================================================================

SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '16px',
    'lg': '24px',
    'xl': '32px',
    'xxl': '48px',
}


# =============================================================================
# BORDER RADIUS
# =============================================================================

RADIUS = {
    'sm': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '24px',
    'full': '9999px',
}


# =============================================================================
# CSS GENERATORS
# =============================================================================

def get_streamlit_css() -> str:
    """
    Generate the complete Streamlit CSS for the neumorphic design system.

    Returns:
        Complete CSS string to inject via st.markdown
    """
    return f"""
    <style>
    /* =================================================================
       COMPME NEUMORPHIC DESIGN SYSTEM
       ================================================================= */

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Root variables */
    :root {{
        --bg-main: {COLORS['background']};
        --bg-dark: {COLORS['background_dark']};
        --shadow-dark: {COLORS['shadow_dark']};
        --shadow-light: {COLORS['shadow_light']};
        --primary: {COLORS['primary']};
        --success: {COLORS['success']};
        --accent: {COLORS['accent']};
        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
    }}

    /* Main background */
    .main, .stApp {{
        background-color: {COLORS['background']} !important;
    }}

    /* Neumorphic containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {COLORS['background']};
        border-radius: {RADIUS['lg']};
        box-shadow: {SHADOWS['outset_md']};
        border: none !important;
        padding: {SPACING['md']};
    }}

    /* Inset inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: {COLORS['background']} !important;
        border: none !important;
        border-radius: {RADIUS['md']};
        box-shadow: {SHADOWS['inset_md']};
        padding: {SPACING['sm']} {SPACING['md']};
        color: {COLORS['text_primary']};
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        box-shadow: {SHADOWS['inset_lg']};
        outline: none;
    }}

    /* Neumorphic buttons */
    .stButton > button {{
        background: {COLORS['background']};
        border: none !important;
        border-radius: {RADIUS['md']};
        box-shadow: {SHADOWS['outset_sm']};
        color: {COLORS['text_primary']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        padding: {SPACING['sm']} {SPACING['lg']};
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        box-shadow: {SHADOWS['outset_md']};
    }}

    .stButton > button:active {{
        box-shadow: {SHADOWS['inset_sm']};
    }}

    /* Primary button variant */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(145deg, {COLORS['primary']}, {COLORS['primary_dark']});
        color: {COLORS['text_light']};
        box-shadow: 4px 4px 8px {COLORS['shadow_dark']}, -2px -2px 6px {COLORS['primary_light']};
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 6px 6px 12px {COLORS['shadow_dark']}, -3px -3px 8px {COLORS['primary_light']};
    }}

    /* Tabs - neumorphic style */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['background']};
        border-radius: {RADIUS['md']};
        box-shadow: {SHADOWS['inset_sm']};
        padding: {SPACING['xs']};
        gap: {SPACING['xs']};
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: {RADIUS['sm']};
        color: {COLORS['text_secondary']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        padding: {SPACING['sm']} {SPACING['md']};
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['background']};
        box-shadow: {SHADOWS['outset_sm']};
        color: {COLORS['primary']};
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY['metric_value']} !important;
        font-weight: {TYPOGRAPHY['weight_bold']};
        color: {COLORS['text_primary']};
    }}

    [data-testid="stMetricLabel"] {{
        font-size: {TYPOGRAPHY['metric_label']} !important;
        font-weight: {TYPOGRAPHY['weight_medium']};
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Positive/negative delta colors */
    .positive {{
        color: {COLORS['success']};
    }}

    .negative {{
        color: {COLORS['error']};
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background: {COLORS['background']};
        border-radius: {RADIUS['md']};
        box-shadow: {SHADOWS['outset_sm']};
        border: none !important;
    }}

    .streamlit-expanderContent {{
        background: {COLORS['background']};
        border-radius: 0 0 {RADIUS['md']} {RADIUS['md']};
        box-shadow: {SHADOWS['inset_sm']};
    }}

    /* Slider */
    .stSlider > div > div > div {{
        background: {COLORS['background']};
        box-shadow: {SHADOWS['inset_sm']};
        border-radius: {RADIUS['full']};
    }}

    .stSlider > div > div > div > div {{
        background: {COLORS['primary']};
        box-shadow: {SHADOWS['outset_sm']};
    }}

    /* Checkbox */
    .stCheckbox > label > div {{
        background: {COLORS['background']};
        box-shadow: {SHADOWS['inset_sm']};
        border-radius: {RADIUS['sm']};
    }}

    /* Radio buttons */
    .stRadio > div {{
        background: {COLORS['background']};
        border-radius: {RADIUS['md']};
        padding: {SPACING['sm']};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {COLORS['background_dark']};
    }}

    section[data-testid="stSidebar"] > div {{
        background: {COLORS['background_dark']};
    }}

    /* Info/Warning/Error boxes */
    .stAlert {{
        background: {COLORS['background']};
        border-radius: {RADIUS['md']};
        box-shadow: {SHADOWS['inset_sm']};
        border-left: 4px solid;
    }}

    /* Remove default borders */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, {COLORS['shadow_dark']}, transparent);
        margin: {SPACING['lg']} 0;
    }}

    /* Subheaders */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {COLORS['text_primary']};
    }}

    /* Equal height containers */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
        min-height: 100%;
        height: 100%;
    }}

    /* Chart container styling */
    .js-plotly-plot {{
        border-radius: {RADIUS['md']};
    }}

    </style>
    """


def get_chart_colors() -> dict:
    """
    Get the color palette for Plotly charts.

    Returns:
        Dictionary of chart-specific colors
    """
    return {
        'military': COLORS['chart_military'],
        'civilian': COLORS['chart_civilian'],
        'equity': COLORS['chart_equity'],
        'bonus': COLORS['chart_bonus'],
        'background': COLORS['background'],
        'grid': 'rgba(163, 177, 198, 0.3)',
        'text': COLORS['text_primary'],
        'text_secondary': COLORS['text_secondary'],
    }


def get_chart_layout_defaults() -> dict:
    """
    Get default Plotly layout settings matching the design system.

    Returns:
        Dictionary of layout settings for Plotly figures
    """
    return {
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'font': {
            'family': TYPOGRAPHY['font_family'],
            'color': COLORS['text_primary'],
            'size': 14,
        },
        'title': {
            'font': {
                'size': 18,
                'color': COLORS['text_primary'],
            },
            'x': 0.5,
            'xanchor': 'center',
        },
        'xaxis': {
            'gridcolor': 'rgba(163, 177, 198, 0.3)',
            'linecolor': COLORS['shadow_dark'],
        },
        'yaxis': {
            'gridcolor': 'rgba(163, 177, 198, 0.3)',
            'linecolor': COLORS['shadow_dark'],
        },
        'legend': {
            'bgcolor': 'rgba(224, 229, 236, 0.8)',
            'bordercolor': 'transparent',
        },
    }
