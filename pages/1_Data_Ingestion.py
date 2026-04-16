"""Data Ingestion page."""

import streamlit as st
from components.theme import apply_theme, render_footer, render_toggle
from core.data import fetch_data

render_toggle()
apply_theme()

st.header("Data Ingestion")
st.markdown("Fetch historical OHLCV data from Yahoo Finance for any listed asset.")

# Popular tickers organised by category
POPULAR_TICKERS = {
    "US Equities / ETFs": ["SPY", "QQQ", "IWM", "DIA", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "GS", "BAC"],
    "International ETFs": ["EFA", "EEM", "VGK", "FXI", "EWJ", "EWZ"],
    "Fixed Income": ["TLT", "IEF", "SHY", "HYG", "LQD", "BND", "AGG"],
    "Commodities": ["GLD", "SLV", "USO", "GDX", "DBA", "DBC"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD", "XRP-USD"],
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"],
    "Volatility": ["^VIX"],
    "Indices": ["^GSPC", "^DJI", "^IXIC", "^RUT", "^FTSE", "^N225"],
}

# Category selector — outside the form so it triggers an immediate rerun
category = st.selectbox("Asset Category", list(POPULAR_TICKERS.keys()))
options = POPULAR_TICKERS[category]

with st.form("fetch"):
    col1, col2 = st.columns(2)
    with col1:
        saved_ticker = st.session_state.get("ticker", "SPY")
        default_idx = options.index(saved_ticker) if saved_ticker in options else 0
        ticker = st.selectbox("Ticker", options, index=default_idx)
        custom = st.text_input("Or type any ticker", value="", placeholder="e.g. NFLX, BTC-USD, ^GSPC")
        if custom.strip():
            ticker = custom.strip().upper()

        start_date = st.text_input("Start Date", value=st.session_state.get("start_date", "2018-01-01"))
    with col2:
        end_date = st.text_input("End Date", value=st.session_state.get("end_date", "2025-01-01"))
        interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])
        auto_adjust = st.checkbox("Auto-adjust prices", value=True)
    submitted = st.form_submit_button("Fetch Data", type="primary")

if submitted:
    with st.spinner("Fetching data..."):
        try:
            df = fetch_data(ticker, start_date, end_date, interval, auto_adjust)
            st.session_state["raw_df"] = df
            st.session_state["ticker"] = ticker
            st.session_state["start_date"] = start_date
            st.session_state["end_date"] = end_date
            st.success(f"Loaded **{len(df)}** rows for **{ticker}**")
        except Exception as e:
            st.error(f"Error: {e}")

if "raw_df" in st.session_state:
    df = st.session_state["raw_df"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(df))
    col2.metric("Start", str(df.index.min().date()))
    col3.metric("End", str(df.index.max().date()))

    tab1, tab2 = st.tabs(["Head", "Tail"])
    with tab1:
        st.dataframe(df.head(10), use_container_width=True)
    with tab2:
        st.dataframe(df.tail(10), use_container_width=True)

render_footer()
