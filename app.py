"""Regime-Aware Forecasting — Streamlit App."""

import streamlit as st
from pathlib import Path
from components.theme import apply_theme, render_footer

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

apply_theme()

# --- Hero banner ---
is_dark = st.session_state["theme"] == "dark"
banner = "assets/dark.png" if is_dark else "assets/light.png"
if Path(banner).exists():
    st.image(banner, use_container_width=True)

with col_title:
    ticker = st.session_state.get("ticker", "SPY")
    st.caption(f"{ticker} Market Regime Detection & Walk-Forward Validation")

# --- Why this app exists ---
st.markdown("""
---

### Why This App Was Created

Financial markets do not behave the same way all the time. Periods of steady growth give way to sudden crashes, which resolve into volatile recoveries before calm returns. These distinct behavioral phases — known as **market regimes** — are invisible in raw price data. They cannot be read off a chart. They must be inferred.

Traditional market analysis assumes that conditions are stationary. Standard risk metrics like annualized volatility, Sharpe ratios, and correlation matrices are computed over long historical windows as if the market behaves the same way throughout. It does not — and the consequences are real:

- A portfolio optimized on 10 years of data allocates risk based on average conditions, not current conditions. When the market shifts from calm to crisis, the portfolio is wrong by construction.
- A risk model that estimates Value-at-Risk from the full historical distribution understates tail risk during stress and overstates it during calm.
- A trading strategy that works in trending markets may hemorrhage capital in volatile, mean-reverting markets — and vice versa.

Most investors and analysts either ignore regimes entirely or identify them only in hindsight. This app was built to change that — making regime detection **accessible, rigorous, and validated**. It provides a complete workflow from raw market data to statistically tested regime assignments, solving the problem by:

1. **Detecting regimes automatically** using a Gaussian Hidden Markov Model — a probabilistic model that learns to identify distinct market states from observable features like volatility, momentum, and drawdown.
2. **Validating the detection rigorously** using walk-forward testing — the same chronological backtesting standard used by institutional quant teams — so you know whether the regimes are real patterns or statistical artifacts.
3. **Making results actionable** through interactive visualizations, downloadable data, and interpretive reports.

---

### Economic Importance

Regime awareness has direct economic value across the financial industry:

**For Portfolio Managers:**
Regime-conditioned allocation can significantly improve risk-adjusted returns. During detected stress regimes, reducing equity exposure or increasing hedges protects capital. During confirmed bull regimes, maintaining full exposure captures upside. Studies in quantitative finance consistently show that regime-aware strategies outperform static allocations over full market cycles.

**For Risk Managers:**
Accurate regime identification improves risk measurement. Volatility forecasts that condition on the current regime are more accurate than unconditional forecasts. This means tighter, more reliable Value-at-Risk and Expected Shortfall estimates — directly reducing the capital reserves firms must hold.

**For Traders and Strategists:**
Different strategies work in different regimes. Momentum strategies thrive in trending markets but fail in volatile, choppy conditions. Mean-reversion strategies do the opposite. Knowing which regime the market is in — and how confident that assessment is — allows traders to select and size strategies appropriately.

**For Researchers and Students:**
Regime detection is a foundational concept in financial econometrics. This app provides a hands-on platform for exploring Hidden Markov Models, walk-forward validation, and feature engineering — skills that are directly applicable in quantitative finance careers.

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
| 5 | Run Analysis | Execute the full pipeline |
| 6 | Results Dashboard | Explore charts and regime assignments |
| 7 | Export | Download reports and CSV files |
""")

col1, col2, col3 = st.columns(3)
col1.info(f"**Ticker:** {st.session_state.get('ticker', 'SPY')}")
col2.info("**Default States:** 3")
col3.info("**Validation:** Walk-Forward")

render_footer()
