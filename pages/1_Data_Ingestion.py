"""Data Ingestion page."""

import streamlit as st
from components.theme import apply_theme, render_footer
from core.data import fetch_data

apply_theme()

st.header("Data Ingestion")
st.markdown("Fetch SPY (or other ticker) OHLCV data from Yahoo Finance.")

with st.form("fetch"):
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker", value=st.session_state.get("ticker", "SPY"))
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
