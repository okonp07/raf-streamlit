"""Data ingestion page."""

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle
from core.data import fetch_data

render_toggle()
apply_theme()

render_page_hero(
    "Data Ingestion",
    "Pull historical OHLCV data from Yahoo Finance and establish the dataset that will drive every downstream feature, regime, and monitoring view.",
    eyebrow="Step 1",
    badges=["Yahoo Finance", "OHLCV", "Cached fetches"],
)

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

category = st.selectbox("Asset Category", list(POPULAR_TICKERS.keys()))
options = POPULAR_TICKERS[category]

st.markdown(
    """
    <div class="note-box">
        <strong>Tip.</strong> Choose a category to browse common symbols, or type any Yahoo Finance ticker manually. The data you fetch here becomes the shared dataset for the rest of the app.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("fetch"):
    col1, col2 = st.columns(2)
    with col1:
        saved_ticker = st.session_state.get("ticker", "SPY")
        default_idx = options.index(saved_ticker) if saved_ticker in options else 0
        ticker = st.selectbox("Ticker", options, index=default_idx)
        custom = st.text_input(
            "Or type any ticker",
            value="",
            placeholder="Examples: NFLX, BTC-USD, ^GSPC",
        )
        if custom.strip():
            ticker = custom.strip().upper()
        start_date = st.text_input(
            "Start Date",
            value=st.session_state.get("start_date", "2018-01-01"),
        )
    with col2:
        end_date = st.text_input(
            "End Date",
            value=st.session_state.get("end_date", "2025-01-01"),
        )
        interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])
        auto_adjust = st.checkbox("Auto-adjust prices", value=True)

    submitted = st.form_submit_button("Fetch Market Data", type="primary")

if submitted:
    with st.spinner("Fetching data from Yahoo Finance..."):
        try:
            df = fetch_data(ticker, start_date, end_date, interval, auto_adjust)
            st.session_state["raw_df"] = df
            st.session_state["ticker"] = ticker
            st.session_state["start_date"] = start_date
            st.session_state["end_date"] = end_date
            st.success(f"Loaded {len(df):,} rows for {ticker}.")
        except Exception as exc:
            st.error(f"Error: {exc}")

if "raw_df" in st.session_state:
    df = st.session_state["raw_df"]
    render_stat_cards(
        [
            {
                "label": "Rows",
                "value": f"{len(df):,}",
                "note": "Usable observations after any forward-fill and dropna steps.",
            },
            {
                "label": "Start",
                "value": str(df.index.min().date()),
                "note": "Earliest available observation in the current dataset.",
            },
            {
                "label": "End",
                "value": str(df.index.max().date()),
                "note": "Latest available observation in the current dataset.",
            },
        {
            "label": "Columns",
            "value": "OHLCV",
            "note": f"Columns available: {', '.join(df.columns)}.",
        },
    ]
)

    tab1, tab2 = st.tabs(["First Rows", "Latest Rows"])
    with tab1:
        st.dataframe(df.head(10), use_container_width=True)
    with tab2:
        st.dataframe(df.tail(10), use_container_width=True)

render_footer()
