"""Feature configuration page."""

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

if "feature_config" not in st.session_state:
    st.session_state["feature_config"] = {}
fc = st.session_state["feature_config"]

render_page_hero(
    "Feature Configuration",
    "Shape the feature space the HMM will observe. These inputs determine whether the model leans more on volatility, trend, drawdown, or technical context.",
    eyebrow="Step 2",
    badges=["No look-ahead leakage", "Configurable rolling windows", "Technical + statistical signals"],
)

st.markdown(
    """
    <div class="note-box">
        <strong>How to think about this page.</strong> Fewer, cleaner features can make the state structure more stable. Broader feature sets can capture richer behaviour, but they also increase the chance of noisier regimes.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Returns")
col1, col2 = st.columns(2)
fc["log_returns"] = col1.checkbox("Log Returns", value=fc.get("log_returns", True))
fc["simple_returns"] = col2.checkbox("Simple Returns", value=fc.get("simple_returns", True))

st.subheader("Volatility And Rolling Statistics")
fc["volatility_windows"] = st.multiselect(
    "Volatility Windows",
    [5, 10, 20, 30, 60],
    default=fc.get("volatility_windows", [5, 10, 20]),
)
fc["rolling_mean_windows"] = st.multiselect(
    "Rolling Mean Windows",
    [5, 10, 20, 30, 60],
    default=fc.get("rolling_mean_windows", [5, 20]),
)

col1, col2, col3 = st.columns(3)
fc["drawdown"] = col1.checkbox("Drawdown", value=fc.get("drawdown", True))
fc["rolling_max_drawdown"] = col2.checkbox(
    "Rolling Max Drawdown",
    value=fc.get("rolling_max_drawdown", True),
)
fc["atr_range"] = col3.checkbox("ATR Range", value=fc.get("atr_range", True))

col1, col2, col3 = st.columns(3)
fc["volume_change"] = col1.checkbox("Volume Change", value=fc.get("volume_change", True))
fc["z_scored_return"] = col2.checkbox(
    "Z-Scored Return",
    value=fc.get("z_scored_return", True),
)
fc["realized_vol"] = col3.checkbox("Realised Volatility", value=fc.get("realized_vol", True))

st.subheader("Momentum And Technical Indicators")
fc["momentum_windows"] = st.multiselect(
    "Momentum Windows",
    [5, 10, 20, 30, 60],
    default=fc.get("momentum_windows", [10, 20]),
)

col1, col2, col3, col4 = st.columns(4)
fc["rsi"] = col1.checkbox("RSI", value=fc.get("rsi", True))
fc["macd"] = col2.checkbox("MACD Histogram", value=fc.get("macd", True))
fc["rolling_skew"] = col3.checkbox("Rolling Skewness", value=fc.get("rolling_skew", True))
fc["rolling_kurtosis"] = col4.checkbox(
    "Rolling Kurtosis",
    value=fc.get("rolling_kurtosis", True),
)

st.session_state["feature_config"] = fc

active_groups = sum(
    [
        fc.get("log_returns", True) or fc.get("simple_returns", True),
        bool(fc.get("volatility_windows", [])),
        bool(fc.get("rolling_mean_windows", [])),
        fc.get("drawdown", True),
        fc.get("rolling_max_drawdown", True),
        fc.get("atr_range", True),
        fc.get("volume_change", True),
        fc.get("z_scored_return", True),
        bool(fc.get("momentum_windows", [])),
        fc.get("realized_vol", True),
        fc.get("rsi", True),
        fc.get("macd", True),
        fc.get("rolling_skew", True),
        fc.get("rolling_kurtosis", True),
    ]
)

render_stat_cards(
    [
        {
            "label": "Active Feature Groups",
            "value": active_groups,
            "note": "High-level count of enabled feature families.",
        },
        {
            "label": "Volatility Windows",
            "value": ", ".join(map(str, fc.get("volatility_windows", []))) or "None",
            "note": "Trailing windows used to compute rolling volatility.",
        },
        {
            "label": "Momentum Windows",
            "value": ", ".join(map(str, fc.get("momentum_windows", []))) or "None",
            "note": "Lookback windows used for price momentum features.",
        },
    ]
)

render_footer()
