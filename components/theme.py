"""Shared theme injection — call apply_theme() at the top of every page."""

import streamlit as st
from pathlib import Path

ACCENT_LIGHT = "#1a73e8"
ACCENT_DARK = "#56b4e9"


def render_footer():
    """Render a consistent footer at the bottom of every page."""
    st.markdown("""
    <hr style="margin-top:3rem;margin-bottom:1rem;opacity:0.3;">
    <div style="text-align:center;font-size:0.82rem;opacity:0.7;line-height:1.8;">
        &copy; Okon Prince, 2026<br>
        This project was designed by Hart Ofigwe and developed by Okon Prince and Hart Ofigwe.<br>
        The authors are not liable for any loss that may arise from the use of this solution.<br>
        Enquiries: <a href="mailto:okonp07@gmail.com">okonp07@gmail.com</a>
    </div>
    """, unsafe_allow_html=True)


def render_toggle():
    """Render a dark/light mode toggle button at the top-right of the page."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    _, col_toggle = st.columns([5, 1])
    with col_toggle:
        theme_label = "🌙 Dark" if st.session_state["theme"] == "light" else "☀️ Light"
        import inspect, os
        caller = os.path.basename(inspect.stack()[1].filename)
        if st.button(theme_label, use_container_width=True, key=f"toggle_{caller}"):
            st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
            st.rerun()


def apply_theme():
    """Inject CSS for the current theme. Call at the top of every page."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    is_dark = st.session_state["theme"] == "dark"
    accent = ACCENT_DARK if is_dark else ACCENT_LIGHT
    st.session_state["plotly_template"] = "plotly_dark" if is_dark else "plotly"

    bg_file = "assets/dark_bg_soft.txt" if is_dark else "assets/light_bg_soft.txt"
    bg_b64 = ""
    if Path(bg_file).exists():
        bg_b64 = Path(bg_file).read_text().strip()

    if is_dark:
        bg_css = f'background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed; background-size: cover;' if bg_b64 else 'background-color: #0e1117;'
        st.markdown(f"""
        <style>
            .stApp {{ {bg_css} color: #fafafa; }}
            [data-testid="stSidebar"] {{ background-color: rgba(26, 26, 46, 0.95); }}
            [data-testid="stHeader"] {{ background-color: rgba(14, 17, 23, 0.8); }}
            .stMarkdown, .stText, h1, h2, h3, p, span, label, .stMetricValue, .stMetricLabel {{
                color: #fafafa !important;
            }}
            [data-testid="stMetricValue"] {{ color: #fafafa !important; }}
            .stDataFrame {{ color: #fafafa; }}
            div[data-testid="stExpander"] {{ border-color: #333; background-color: rgba(14, 17, 23, 0.7); }}
            .stTabs [data-baseweb="tab"] {{ color: #fafafa; }}
            .stButton > button[kind="primary"] {{ background-color: {accent}; border-color: {accent}; }}
            .stButton > button[kind="primary"]:hover {{ background-color: #7ecbf0; border-color: #7ecbf0; }}
            a {{ color: {accent} !important; }}
            .stProgress > div > div {{ background-color: {accent}; }}
            [data-testid="stMetric"] {{ background-color: rgba(14, 17, 23, 0.6); padding: 12px; border-radius: 8px; }}
            [data-testid="stAlert"] {{ background-color: rgba(14, 17, 23, 0.7); }}
            .stDataFrame, [data-testid="stTable"] {{ background-color: rgba(14, 17, 23, 0.7); }}
            .stSelectbox, .stMultiSelect, .stNumberInput, .stTextInput {{  }}
            [data-baseweb="select"] {{ background-color: rgba(30, 30, 50, 0.9); color: #fafafa; }}
            [data-baseweb="input"] {{ background-color: rgba(30, 30, 50, 0.9); color: #fafafa; }}
            /* JSON viewer fix for dark mode */
            [data-testid="stJson"], [data-testid="stJson"] * {{ background-color: rgba(14, 17, 23, 0.9) !important; color: #56b4e9 !important; }}
            pre {{ background-color: rgba(14, 17, 23, 0.9) !important; color: #fafafa !important; }}
            code {{ color: #56b4e9 !important; }}
            .stJson {{ background-color: rgba(14, 17, 23, 0.9) !important; }}
            /* Theme toggle: dark at rest, light on hover */
            .stButton > button {{ background-color: #1a1a2e; color: #fafafa; border: 1px solid #333; }}
            .stButton > button:hover {{ background-color: #fafafa; color: #1a1a2e; border: 1px solid #fafafa; }}
        </style>
        """, unsafe_allow_html=True)
    else:
        bg_css = f'background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed; background-size: cover;' if bg_b64 else 'background-color: #ffffff;'
        st.markdown(f"""
        <style>
            .stApp {{ {bg_css} color: #1a1a1a; }}
            [data-testid="stSidebar"] {{ background-color: rgba(245, 245, 245, 0.95); }}
            [data-testid="stHeader"] {{ background-color: rgba(255, 255, 255, 0.85); }}
            .stButton > button[kind="primary"] {{ background-color: {accent}; border-color: {accent}; }}
            .stButton > button[kind="primary"]:hover {{ background-color: #1557b0; border-color: #1557b0; }}
            a {{ color: {accent} !important; }}
            .stProgress > div > div {{ background-color: {accent}; }}
            div[data-testid="stExpander"] {{ background-color: rgba(255, 255, 255, 0.8); }}
            [data-testid="stMetric"] {{ background-color: rgba(255, 255, 255, 0.75); padding: 12px; border-radius: 8px; }}
            [data-testid="stAlert"] {{ background-color: rgba(255, 255, 255, 0.85); }}
            .stDataFrame, [data-testid="stTable"] {{ background-color: rgba(255, 255, 255, 0.85); }}
            /* Theme toggle: light at rest, dark on hover */
            .stButton > button {{ background-color: #ffffff; color: #1a1a1a; border: 1px solid #ddd; }}
            .stButton > button:hover {{ background-color: #1a1a2e; color: #fafafa; border: 1px solid #1a1a2e; }}
        </style>
        """, unsafe_allow_html=True)
