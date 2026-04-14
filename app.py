"""Regime-Aware Forecasting — Streamlit App."""

import streamlit as st

st.set_page_config(page_title="Regime-Aware Forecasting", page_icon="📊", layout="wide")

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
