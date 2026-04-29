"""Shared theme injection for the single Streamlit application."""

import streamlit as st

ACCENT_LIGHT = "#2563eb"
ACCENT_DARK = "#38bdf8"


def render_footer():
    """Render a consistent footer at the bottom of every page."""
    st.markdown(
        """
        <div class="app-footer">
            <div class="app-footer-title">Regime-Aware Forecasting</div>
            <p>
                Designed by Hart Ofigwe and developed by Okon Prince and Hart Ofigwe.
                This tool is for research and decision support, not investment advice.
            </p>
            <p>Enquiries: <a href="mailto:okonp07@gmail.com">okonp07@gmail.com</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_toggle():
    """Render a dark/light mode toggle button at the top-right of the page."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    current_dark = st.session_state["theme"] == "dark"
    _, col_toggle = st.columns([5, 1])
    with col_toggle:
        st.markdown(
            """
            <div class="theme-toggle-label">
                <span>Theme</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        dark_mode = st.toggle(
            "Dark mode",
            value=current_dark,
            key="theme_toggle",
            help="Switch between the light and dark presentation modes.",
        )
        if dark_mode != current_dark:
            st.session_state["theme"] = "dark" if dark_mode else "light"
            st.rerun()


def apply_theme():
    """Inject CSS for the current theme. Call at the top of every page."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    dark = st.session_state["theme"] == "dark"
    accent = ACCENT_DARK if dark else ACCENT_LIGHT
    st.session_state["plotly_template"] = "plotly_dark" if dark else "plotly"

    # Import and inject card/component CSS from design system
    from components.design import card_css

    card_css()

    if dark:
        app_bg = """
            background:
                radial-gradient(circle at 0% 0%, rgba(20,184,166,0.20), transparent 26%),
                radial-gradient(circle at 100% 0%, rgba(79,124,255,0.22), transparent 30%),
                radial-gradient(circle at 50% 100%, rgba(249,115,102,0.12), transparent 24%),
                linear-gradient(180deg, #06121d 0%, #08131f 48%, #09131e 100%);
        """
        sidebar_bg = "rgba(7, 17, 30, 0.88)"
        panel_bg = "rgba(8, 18, 32, 0.68)"
        border = "rgba(255,255,255,0.08)"
        text = "#e5eef8"
        subtext = "#94a3b8"
    else:
        app_bg = """
            background:
                radial-gradient(circle at 0% 0%, rgba(37,99,235,0.12), transparent 24%),
                radial-gradient(circle at 100% 0%, rgba(20,184,166,0.14), transparent 30%),
                radial-gradient(circle at 50% 100%, rgba(249,115,102,0.10), transparent 22%),
                linear-gradient(180deg, #f4f8fc 0%, #eef4fb 50%, #f8fbff 100%);
        """
        sidebar_bg = "rgba(255, 255, 255, 0.78)"
        panel_bg = "rgba(255, 255, 255, 0.76)"
        border = "rgba(15,23,42,0.08)"
        text = "#0f172a"
        subtext = "#526274"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@500;600;700;800&display=swap');

            :root {{
                --app-panel-bg: {panel_bg};
                --app-border: {border};
                --app-text: {text};
                --app-subtext: {subtext};
                --app-accent: {accent};
            }}

            .stApp {{
                {app_bg}
                color: var(--app-text);
            }}

            .stApp, .stMarkdown, .stText, p, label, li {{
                font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            }}

            [class*="material-symbols"] {{
                font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
                font-weight: normal !important;
                font-style: normal !important;
                letter-spacing: normal !important;
                text-transform: none !important;
                white-space: nowrap !important;
            }}

            [data-testid="stImage"] img {{
                border-radius: 28px;
                border: 1px solid var(--app-border);
                box-shadow: 0 26px 60px rgba(15,23,42,0.16);
            }}

            .block-container {{
                padding-top: 1.35rem !important;
                padding-bottom: 3rem !important;
            }}

            [data-testid="stHeader"] {{
                background: rgba(255,255,255,0.02);
                backdrop-filter: blur(16px);
            }}

            [data-testid="stSidebar"] {{
                background: {sidebar_bg};
                border-right: 1px solid var(--app-border);
                backdrop-filter: blur(20px);
            }}

            [data-testid="stSidebarNav"] {{
                padding-top: 1rem;
            }}

            h1, h2, h3, h4 {{
                font-family: 'Sora', 'Manrope', sans-serif !important;
                letter-spacing: -0.03em;
                color: var(--app-text) !important;
            }}

            h1 {{
                font-size: clamp(2rem, 4vw, 3.1rem) !important;
                font-weight: 700 !important;
                line-height: 1.04;
                margin-bottom: 0.5rem !important;
            }}

            h2 {{
                font-size: 1.45rem !important;
                margin-top: 0.2rem !important;
            }}

            h3 {{
                font-size: 1.05rem !important;
            }}

            .hero-shell {{
                background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03));
                border: 1px solid var(--app-border);
                border-radius: 28px;
                padding: 2rem 2rem 1.5rem;
                margin: 0 0 1.25rem;
                backdrop-filter: blur(18px);
                box-shadow: 0 30px 80px rgba(15,23,42,0.10);
            }}

            .hero-shell p {{
                color: var(--app-subtext);
                max-width: 860px;
                line-height: 1.7;
                font-size: 1rem;
                margin-bottom: 0.9rem;
            }}

            .hero-eyebrow {{
                display: inline-block;
                padding: 0.4rem 0.75rem;
                border-radius: 999px;
                background: rgba(37,99,235,0.12);
                color: var(--app-accent);
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-size: 0.74rem;
                font-weight: 700;
                margin-bottom: 0.9rem;
            }}

            .hero-badges {{
                display: flex;
                gap: 0.55rem;
                flex-wrap: wrap;
                margin-top: 1rem;
            }}

            .hero-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.55rem 0.8rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.08);
                border: 1px solid var(--app-border);
                color: var(--app-subtext);
                font-size: 0.82rem;
                font-weight: 600;
            }}

            .hero-media-shell {{
                background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
                border: 1px solid var(--app-border);
                border-radius: 30px;
                padding: 0.85rem;
                backdrop-filter: blur(18px);
                box-shadow: 0 24px 60px rgba(15,23,42,0.12);
            }}

            .theme-toggle-label {{
                text-align: right;
                color: var(--app-subtext);
                font-size: 0.74rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.2rem;
            }}

            .glass-card, .metric-tile, .note-box {{
                background: var(--app-panel-bg);
                border: 1px solid var(--app-border);
                border-radius: 22px;
                backdrop-filter: blur(16px);
                box-shadow: 0 20px 40px rgba(15,23,42,0.08);
            }}

            .metric-tile {{
                padding: 1rem 1rem 0.95rem;
                min-height: 132px;
            }}

            .metric-label {{
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                color: var(--app-subtext);
                margin-bottom: 0.55rem;
            }}

            .metric-value {{
                font-family: 'Sora', 'Manrope', sans-serif;
                font-size: 1.75rem;
                font-weight: 700;
                color: var(--app-text);
                margin-bottom: 0.4rem;
            }}

            .metric-note {{
                color: var(--app-subtext);
                line-height: 1.5;
                font-size: 0.84rem;
            }}

            .info-card {{
                padding: 1.15rem 1.15rem 1rem;
                height: 100%;
            }}

            .info-card-kicker {{
                color: var(--app-accent);
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }}

            .info-card h3 {{
                margin-bottom: 0.55rem !important;
            }}

            .info-card p {{
                margin: 0;
                color: var(--app-subtext);
                line-height: 1.65;
                font-size: 0.92rem;
            }}

            .note-box {{
                padding: 0.95rem 1rem;
                color: var(--app-subtext);
                line-height: 1.6;
                margin: 0.6rem 0 1rem;
            }}

            .section-gap-md {{
                height: 0.7rem;
            }}

            .section-gap-lg {{
                height: 1.05rem;
            }}

            .note-box strong {{
                color: var(--app-text);
            }}

            .runway-card {{
                padding: 1.2rem 1.25rem 1.1rem;
                margin: 0.35rem 0 1rem;
            }}

            .runway-card h3 {{
                margin-bottom: 0.45rem !important;
            }}

            .runway-card p {{
                margin: 0 0 0.95rem;
                color: var(--app-subtext);
                line-height: 1.65;
            }}

            div[data-testid="stExpander"] details summary {{
                padding: 0.15rem 0.25rem;
            }}

            div[data-testid="stExpander"] details summary p {{
                margin: 0;
                color: var(--app-text);
                font-weight: 600;
                line-height: 1.35;
            }}

            .runway-track {{
                width: 100%;
                height: 14px;
                border-radius: 999px;
                background: rgba(148, 163, 184, 0.16);
                overflow: hidden;
                position: relative;
            }}

            .runway-fill {{
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, {accent}, #14b8a6);
                box-shadow: 0 10px 24px rgba(37,99,235,0.22);
            }}

            .runway-meta {{
                display: flex;
                gap: 0.75rem;
                flex-wrap: wrap;
                justify-content: space-between;
                color: var(--app-subtext);
                font-size: 0.82rem;
                margin-top: 0.8rem;
            }}

            .runway-meta strong {{
                color: var(--app-text);
            }}

            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stWidgetLabel"] + div [data-baseweb="switch"] {{
                border-radius: 14px !important;
                font-weight: 700 !important;
                border: 1px solid var(--app-border) !important;
                min-height: 2.8rem;
            }}

            .stButton > button[kind="primary"],
            .stDownloadButton > button {{
                background: linear-gradient(135deg, {accent}, #14b8a6) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 14px 30px rgba(37,99,235,0.22);
                white-space: normal !important;
                line-height: 1.35 !important;
                padding: 0.85rem 1rem !important;
            }}

            .stButton > button:hover,
            .stDownloadButton > button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 18px 40px rgba(37,99,235,0.18);
            }}

            [data-testid="stMetric"], .stForm, div[data-testid="stExpander"], [data-testid="stAlert"] {{
                background: var(--app-panel-bg);
                border: 1px solid var(--app-border);
                border-radius: 18px;
                backdrop-filter: blur(16px);
            }}

            [data-testid="stToggle"] {{
                display: flex;
                justify-content: flex-end;
            }}

            [data-testid="stToggle"] label {{
                gap: 0.65rem;
                color: var(--app-text) !important;
                font-weight: 700 !important;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.45rem;
                margin-bottom: 0.9rem;
            }}

            .stTabs [data-baseweb="tab"] {{
                background: rgba(255,255,255,0.03);
                border: 1px solid var(--app-border);
                border-radius: 999px;
                padding: 0.55rem 1rem;
                font-weight: 700;
            }}

            [data-baseweb="select"] > div,
            [data-baseweb="input"] > div,
            .stTextInput > div > div > input,
            .stNumberInput input {{
                border-radius: 14px !important;
                background: rgba(255,255,255,0.04) !important;
            }}

            .stSlider [data-baseweb="slider"] {{
                padding-top: 0.4rem;
            }}

            .stMarkdown a {{
                color: var(--app-accent) !important;
            }}

            .app-footer {{
                margin-top: 2.8rem;
                padding: 1.4rem 1.6rem;
                border-top: 1px solid var(--app-border);
                color: var(--app-subtext);
                text-align: center;
                line-height: 1.75;
            }}

            .app-footer-title {{
                font-family: 'Sora', 'Manrope', sans-serif;
                font-size: 1rem;
                font-weight: 700;
                color: var(--app-text);
                margin-bottom: 0.4rem;
            }}

            hr {{
                border-color: var(--app-border) !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
