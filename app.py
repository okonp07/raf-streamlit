"""Regime-Aware Forecasting — Streamlit App."""

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Regime-Aware Forecasting", page_icon="📊", layout="wide")

# --- Theme toggle ---
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

col_title, col_toggle = st.columns([5, 1])
with col_toggle:
    theme_label = "🌙 Dark" if st.session_state["theme"] == "light" else "☀️ Light"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
        st.rerun()

is_dark = st.session_state["theme"] == "dark"

# Inject theme CSS
if is_dark:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        [data-testid="stSidebar"] { background-color: #1a1a2e; }
        [data-testid="stHeader"] { background-color: #0e1117; }
        .stMarkdown, .stText, h1, h2, h3, p, span, label, .stMetricValue, .stMetricLabel {
            color: #fafafa !important;
        }
        [data-testid="stMetricValue"] { color: #fafafa !important; }
        .stDataFrame { color: #fafafa; }
        div[data-testid="stExpander"] { border-color: #333; }
        .stTabs [data-baseweb="tab"] { color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff; color: #1a1a1a; }
        [data-testid="stSidebar"] { background-color: #f5f5f5; }
    </style>
    """, unsafe_allow_html=True)

# Store theme for charts
st.session_state["plotly_template"] = "plotly_dark" if is_dark else "plotly"

# --- Hero banner ---
banner = "assets/dark.png" if is_dark else "assets/light.png"
if Path(banner).exists():
    st.image(banner, use_container_width=True)

with col_title:
    st.title("Regime-Aware Forecasting")

st.markdown("### SPY Market Regime Detection & Walk-Forward Validation")

st.markdown("""
---

**What this app does:**

1. **Data Ingestion** — Fetch SPY historical OHLCV data from Yahoo Finance
2. **Feature Engineering** — Compute regime-relevant features (volatility, momentum, drawdown, etc.)
3. **Regime Detection** — Identify latent market regimes using Gaussian HMM
4. **Walk-Forward Validation** — Evaluate model robustness with chronological train/test splits
5. **Results & Export** — Inspect regime assignments, compare folds, and download reports

---

Use the sidebar to navigate through the pages in order.

| Step | Page | Description |
|------|------|-------------|
| 1 | Data Ingestion | Fetch and preview market data |
| 2 | Feature Config | Select features for regime detection |
| 3 | Model Config | Set HMM parameters |
| 4 | Walk-Forward Setup | Configure validation engine |
| 5 | Run Analysis | Execute the full pipeline |
| 6 | Results Dashboard | Explore charts and regime assignments |
| 7 | Export | Download reports and CSV files |
""")

col1, col2, col3 = st.columns(3)
col1.info("**Default Ticker:** SPY")
col2.info("**Default States:** 3")
col3.info("**Validation:** Walk-Forward")
