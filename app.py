"""Regime-Aware Forecasting — Streamlit App."""

import streamlit as st
from pathlib import Path
from components.theme import apply_theme, render_footer, render_toggle

st.set_page_config(page_title="Regime-Aware Forecasting", page_icon="📊", layout="wide")

render_toggle()
apply_theme()

# --- Hero banner ---
is_dark = st.session_state["theme"] == "dark"
banner = "assets/dark.png" if is_dark else "assets/light.png"
if Path(banner).exists():
    st.image(banner, use_container_width=True)

st.caption("Market Regime Detection & Walk-Forward Validation")

# --- Why this app exists ---
st.markdown("""
---

### Why This App Was Created

Financial markets move through changing regimes such as growth, crisis, recovery, and calm, but these shifts are not obvious from raw price charts. Most traditional analysis assumes markets behave consistently over time, which can lead to poor portfolio decisions, misleading risk estimates, and trading strategies that fail when conditions change. This app was created to make market regime detection practical, rigorous, and accessible by automatically identifying market states with a Gaussian Hidden Markov Model, validating them through walk-forward testing, and presenting the results through interactive visuals, downloadable outputs, and clear interpretation. Its value is broad: it helps portfolio managers adapt allocation to market conditions, improves risk estimates for risk managers, helps traders match strategies to the right environment, and gives researchers and students a hands-on way to explore an important concept in quantitative finance.

---

### How the Engine Works
""")

st.markdown("""
1. **Data Ingestion** — Fetch historical OHLCV data from Yahoo Finance for any listed asset
2. **Feature Engineering** — Compute 19 regime-relevant features (volatility, momentum, drawdown, RSI, MACD, and more)
3. **Regime Detection** — Identify latent market regimes using a Gaussian Hidden Markov Model
4. **Walk-Forward Validation** — Evaluate model robustness with chronological train/test splits — no data leakage
5. **Results & Export** — Inspect regime assignments visually, compare folds, and download reports

---

Use the sidebar to navigate through the pages in order.

| Step | Page | Description |
|------|------|-------------|
| 1 | Data Ingestion | Fetch and preview market data |
| 2 | Feature Config | Select features for regime detection |
| 3 | Model Config | Set HMM parameters |
| 4 | Walk-Forward Setup | Configure validation engine |
| 5 | Configuration Guide | Detailed reference for all parameters |
| 6 | Run Analysis | Execute the full pipeline |
| 7 | Results Dashboard | Explore charts and regime assignments |
| 8 | Export | Download reports and CSV files |
| 9 | Regime Monitor | Live probabilities, transition alerts & forward projections |
| 10 | About | Author profiles and project credits |
""")

col1, col2, col3 = st.columns(3)
col1.info(f"**Ticker:** {st.session_state.get('ticker', 'SPY')}")
col2.info("**Default States:** 3")
col3.info("**Validation:** Walk-Forward")

render_footer()
