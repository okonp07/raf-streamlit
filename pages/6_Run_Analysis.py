"""Run analysis page."""

from datetime import datetime

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle
from core.features import engineer_features
from core.walkforward import run_walkforward

render_toggle()
apply_theme()

if "raw_df" not in st.session_state:
    render_page_hero(
        "Run Analysis",
        "This step executes the feature pipeline and walk-forward regime model. Fetch market data first so the app has a dataset to work with.",
        eyebrow="Step 5",
        badges=["Awaiting dataset"],
    )
    st.warning("Fetch data first on the Data Ingestion page.")
    st.stop()

fc = st.session_state.get("feature_config", {})
mc = st.session_state.get("model_config", {})
wf = st.session_state.get("wf_config", {})
ticker = st.session_state.get("ticker", "SPY")

render_page_hero(
    "Run Analysis",
    "Launch the in-app regime engine. The app will engineer features, fit the HMM fold by fold, canonicalise state colours, and package the results for the dashboard and export pages.",
    eyebrow="Step 5",
    badges=[ticker, f"{mc.get('n_states', 3)} states", wf.get("mode", "expanding").title()],
)

render_stat_cards(
    [
        {
            "label": "Ticker",
            "value": ticker,
            "note": "The market series currently loaded into session state.",
        },
        {
            "label": "Feature Families",
            "value": len([k for k, v in fc.items() if v]),
            "note": "Count of enabled feature toggles and rolling-window groups.",
        },
        {
            "label": "States",
            "value": mc.get("n_states", 3),
            "note": "Hidden-state count currently configured for the HMM.",
        },
        {
            "label": "Walk-Forward Mode",
            "value": wf.get("mode", "expanding").title(),
            "note": "Chronological evaluation mode used to score the model.",
        },
    ]
)

with st.expander("Review Current Configuration", expanded=True):
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"""
        **Data**

        - Ticker: `{ticker}`
        - Date range: `{st.session_state.get('start_date', 'N/A')}` to `{st.session_state.get('end_date', 'N/A')}`
        - Rows loaded: `{len(st.session_state['raw_df']):,}`
        """
    )
    col2.markdown(
        f"""
        **Model**

        - States: `{mc.get('n_states', 3)}`
        - Covariance: `{mc.get('covariance_type', 'diag')}`
        - Iterations: `{mc.get('n_iter', 200)}`
        - Scaling: `{'On' if mc.get('scaling', True) else 'Off'}`
        - Min regime duration: `{mc.get('min_regime_duration', 5)}`
        """
    )
    col3.markdown(
        f"""
        **Walk-Forward**

        - Mode: `{wf.get('mode', 'expanding')}`
        - Train window: `{wf.get('train_window', 504)}`
        - Test window: `{wf.get('test_window', 63)}`
        - Step size: `{wf.get('step_size', 63)}`
        """
    )

st.markdown(
    """
    <div class="note-box">
        <strong>What happens next.</strong> The results dashboard will show a muted full-price context line and only colour the dates that were genuinely scored out of sample. That makes the overlay much more faithful to the walk-forward methodology.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Run Walk-Forward Analysis", type="primary", use_container_width=True):
    progress = st.progress(0, text="Starting analysis...")
    status = st.empty()

    try:
        status.info("Engineering features from OHLCV data...")
        featured_df = engineer_features(st.session_state["raw_df"], fc)
        progress.progress(20, text="Features engineered")

        status.info("Running walk-forward HMM fits and scoring test windows...")
        result = run_walkforward(featured_df, mc, wf, progress_bar=progress)

        st.session_state["result"] = result
        st.session_state["last_run_at"] = datetime.now().isoformat(timespec="seconds")
        progress.progress(100, text="Analysis complete")
        status.empty()

        st.success(
            f"Completed {result['n_folds']} folds in {result['duration_secs']}s. Open the Results Dashboard to inspect the regime structure."
        )
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")

render_footer()
