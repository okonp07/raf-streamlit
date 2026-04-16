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

    dark = st.session_state["theme"] == "dark"
    accent = ACCENT_DARK if dark else ACCENT_LIGHT
    st.session_state["plotly_template"] = "plotly_dark" if dark else "plotly"

    bg_file = "assets/dark_bg_soft.txt" if dark else "assets/light_bg_soft.txt"
    bg_b64 = ""
    if Path(bg_file).exists():
        bg_b64 = Path(bg_file).read_text().strip()

    # Import and inject card/component CSS from design system
    from components.design import card_css
    card_css()

    if dark:
        bg_css = f'background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed; background-size: cover;' if bg_b64 else 'background-color: #0e1117;'
        st.markdown(f"""
        <style>
            .stApp {{ {bg_css} color: #e2e8f0; }}
            [data-testid="stSidebar"] {{ background-color: rgba(15, 23, 42, 0.95); }}
            [data-testid="stHeader"] {{ background-color: rgba(14, 17, 23, 0.85); backdrop-filter: blur(8px); }}
            .stMarkdown, .stText, h1, h2, h3, p, span, label, .stMetricValue, .stMetricLabel {{
                color: #e2e8f0 !important;
            }}
            h1, h2, h3 {{ font-weight: 700 !important; letter-spacing: -0.02em; }}
            [data-testid="stMetricValue"] {{ color: #e2e8f0 !important; }}
            .stDataFrame {{ color: #e2e8f0; }}
            div[data-testid="stExpander"] {{ border-color: rgba(255,255,255,0.08); background-color: rgba(15, 23, 42, 0.6); }}
            .stTabs [data-baseweb="tab"] {{ color: #e2e8f0; }}
            .stButton > button[kind="primary"] {{ background-color: {accent}; border-color: {accent}; border-radius: 8px; }}
            .stButton > button[kind="primary"]:hover {{ background-color: #7ecbf0; border-color: #7ecbf0; }}
            a {{ color: {accent} !important; }}
            .stProgress > div > div {{ background-color: {accent}; }}
            [data-testid="stAlert"] {{ background-color: rgba(15, 23, 42, 0.6); border-radius: 8px; }}
            .stDataFrame, [data-testid="stTable"] {{ background-color: rgba(15, 23, 42, 0.6); }}
            [data-baseweb="select"] {{ background-color: rgba(30, 30, 50, 0.9); color: #e2e8f0; }}
            [data-baseweb="input"] {{ background-color: rgba(30, 30, 50, 0.9); color: #e2e8f0; }}
            /* JSON viewer fix for dark mode */
            [data-testid="stJson"], [data-testid="stJson"] * {{ background-color: rgba(15, 23, 42, 0.9) !important; color: #56b4e9 !important; }}
            pre {{ background-color: rgba(15, 23, 42, 0.9) !important; color: #e2e8f0 !important; }}
            code {{ color: #56b4e9 !important; }}
            .stJson {{ background-color: rgba(15, 23, 42, 0.9) !important; }}
            /* Theme toggle */
            .stButton > button {{ background-color: rgba(15, 23, 42, 0.8); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; }}
            .stButton > button:hover {{ background-color: #e2e8f0; color: #0f172a; border: 1px solid #e2e8f0; }}
            /* Dividers */
            hr {{ border-color: rgba(255,255,255,0.08) !important; }}
        </style>
        """, unsafe_allow_html=True)
    else:
        bg_css = f'background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed; background-size: cover;' if bg_b64 else 'background-color: #ffffff;'
        st.markdown(f"""
        <style>
            .stApp {{ {bg_css} color: #1a202c; }}
            [data-testid="stSidebar"] {{ background-color: rgba(248, 250, 252, 0.95); }}
            [data-testid="stHeader"] {{ background-color: rgba(255, 255, 255, 0.88); backdrop-filter: blur(8px); }}
            h1, h2, h3 {{ font-weight: 700 !important; letter-spacing: -0.02em; color: #1a202c !important; }}
            .stButton > button[kind="primary"] {{ background-color: {accent}; border-color: {accent}; border-radius: 8px; }}
            .stButton > button[kind="primary"]:hover {{ background-color: #1557b0; border-color: #1557b0; }}
            a {{ color: {accent} !important; }}
            .stProgress > div > div {{ background-color: {accent}; }}
            div[data-testid="stExpander"] {{ background-color: rgba(255, 255, 255, 0.75); border: 1px solid rgba(0,0,0,0.06); }}
            [data-testid="stAlert"] {{ background-color: rgba(255, 255, 255, 0.85); border-radius: 8px; }}
            .stDataFrame, [data-testid="stTable"] {{ background-color: rgba(255, 255, 255, 0.85); }}
            /* Theme toggle */
            .stButton > button {{ background-color: #ffffff; color: #1a202c; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; }}
            .stButton > button:hover {{ background-color: #0f172a; color: #e2e8f0; border: 1px solid #0f172a; }}
            /* Dividers */
            hr {{ border-color: rgba(0,0,0,0.06) !important; }}
        </style>
        """, unsafe_allow_html=True)
