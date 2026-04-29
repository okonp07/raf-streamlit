"""Regime-Aware Forecasting Streamlit home page."""

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle

st.set_page_config(
    page_title="Regime-Aware Forecasting",
    page_icon=None,
    layout="wide",
)

render_toggle()
apply_theme()

current_ticker = st.session_state.get("ticker", "SPY")
default_states = st.session_state.get("model_config", {}).get("n_states", 3)
validation_mode = st.session_state.get("wf_config", {}).get("mode", "expanding").title()
render_page_hero(
    "Regime-Aware Forecasting",
    "A single Streamlit application for detecting hidden market regimes, validating them with walk-forward testing, and presenting the results through a professional-grade analytical interface.",
    eyebrow="Single-App Quant Workflow",
    badges=[
        "Gaussian HMM engine",
        "Walk-forward validation",
        "Out-of-sample regime overlay",
        "Live regime monitor",
        "Dark and light modes",
    ],
)

render_stat_cards(
    [
        {
            "label": "Active Ticker",
            "value": current_ticker,
            "note": "The currently selected asset for data ingestion and analysis.",
        },
        {
            "label": "Default States",
            "value": default_states,
            "note": "Current hidden-state count selected in model configuration.",
        },
        {
            "label": "Validation Mode",
            "value": validation_mode,
            "note": "Chronological evaluation style for the walk-forward engine.",
        },
        {
            "label": "Architecture",
            "value": "One Streamlit App",
            "note": "No separate backend required for the interactive experience.",
        },
    ]
)

st.markdown(
    """
    <section class="glass-card info-card" style="padding:1.45rem 1.5rem 1.35rem;margin-top:0.85rem;">
        <div class="info-card-kicker">Overview</div>
        <h3 style="margin-bottom:0.6rem;">A single workflow for understanding market structure from first data pull to live monitoring</h3>
        <p>
            Regime-Aware Forecasting is built to help you read market structure rather than isolated price moves.
            Instead of treating every return the same way, the app uses a Gaussian Hidden Markov Model to infer
            latent states such as bull expansion, transition, stress, and recovery so the same price series can be
            interpreted in a richer regime-aware context.
        </p>
        <p>
            The workflow is intentionally chronological. You begin with <strong>Data Ingestion</strong> to load OHLCV
            history from Yahoo Finance, then move into <strong>Feature Configuration</strong> to choose the volatility,
            momentum, drawdown, and technical signals you want the model to learn from. In
            <strong> Model + Walk-Forward</strong>, you set the number of hidden states and the rolling or expanding
            evaluation windows, then run the engine so the HMM is fit on past data and scored on unseen future windows
            rather than on a random split.
        </p>
        <p>
            From there, the <strong>Results Dashboard</strong> brings the analysis together through the out-of-sample
            overlay, fold diagnostics, transition structure, robustness statistics, and the market-phase layer that
            translates the raw regime model into more intuitive cycle language. It also checks whether those regimes
            separate meaningfully on forward returns, realized volatility, drawdown risk, and average duration rather
            than asking you to trust the colors on sight. <strong>Export</strong> packages the
            session into CSV, JSON, and markdown outputs for research or reporting. Finally, <strong>Regime Monitor</strong>
            trains on the full available history to show what regime and market phase the model believes we are in now,
            how long we have likely been there, and how far through that run we may already be.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

render_footer()
