"""Feature Configuration page."""

import streamlit as st
from components.theme import apply_theme

apply_theme()

st.header("Feature Configuration")

if "feature_config" not in st.session_state:
    st.session_state["feature_config"] = {}
fc = st.session_state["feature_config"]

st.subheader("Returns")
col1, col2 = st.columns(2)
fc["log_returns"] = col1.checkbox("Log Returns", value=fc.get("log_returns", True))
fc["simple_returns"] = col2.checkbox("Simple Returns", value=fc.get("simple_returns", True))

st.subheader("Volatility & Rolling Stats")
fc["volatility_windows"] = st.multiselect("Volatility Windows", [5, 10, 20, 30, 60], default=fc.get("volatility_windows", [5, 10, 20]))
fc["rolling_mean_windows"] = st.multiselect("Rolling Mean Windows", [5, 10, 20, 30, 60], default=fc.get("rolling_mean_windows", [5, 20]))

col1, col2, col3 = st.columns(3)
fc["drawdown"] = col1.checkbox("Drawdown", value=fc.get("drawdown", True))
fc["rolling_max_drawdown"] = col2.checkbox("Rolling Max DD", value=fc.get("rolling_max_drawdown", True))
fc["atr_range"] = col3.checkbox("ATR Range", value=fc.get("atr_range", True))

col1, col2, col3 = st.columns(3)
fc["volume_change"] = col1.checkbox("Volume Change", value=fc.get("volume_change", True))
fc["z_scored_return"] = col2.checkbox("Z-Scored Return", value=fc.get("z_scored_return", True))
fc["realized_vol"] = col3.checkbox("Realized Vol", value=fc.get("realized_vol", True))

st.subheader("Momentum & Technicals")
fc["momentum_windows"] = st.multiselect("Momentum Windows", [5, 10, 20, 30, 60], default=fc.get("momentum_windows", [10, 20]))

col1, col2, col3, col4 = st.columns(4)
fc["rsi"] = col1.checkbox("RSI", value=fc.get("rsi", True))
fc["macd"] = col2.checkbox("MACD", value=fc.get("macd", True))
fc["rolling_skew"] = col3.checkbox("Skewness", value=fc.get("rolling_skew", True))
fc["rolling_kurtosis"] = col4.checkbox("Kurtosis", value=fc.get("rolling_kurtosis", True))

st.session_state["feature_config"] = fc
