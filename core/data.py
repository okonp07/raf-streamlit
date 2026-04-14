"""Data ingestion via yfinance."""

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(
    ticker: str, start_date: str, end_date: str,
    interval: str = "1d", auto_adjust: bool = True
) -> pd.DataFrame:
    df = yf.download(
        ticker, start=start_date, end=end_date,
        interval=interval, auto_adjust=auto_adjust, progress=False,
    )
    if df is None or df.empty:
        raise ValueError(f"No data returned for {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.index.name = "Date"
    df = df.sort_index()

    expected = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df[expected]

    if df.isnull().sum().sum() > 0:
        df = df.ffill(limit=5).dropna()

    return df
