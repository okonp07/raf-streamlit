"""Run Analysis page — executes everything in-process."""

import streamlit as st
from core.features import engineer_features
from core.walkforward import run_walkforward

st.header("Run Analysis")

if "raw_df" not in st.session_state:
    st.warning("Fetch data first on the Data Ingestion page.")
    st.stop()

fc = st.session_state.get("feature_config", {})
mc = st.session_state.get("model_config", {})
wf = st.session_state.get("wf_config", {})
ticker = st.session_state.get("ticker", "SPY")

with st.expander("Review Configuration", expanded=True):
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Ticker:** {ticker}")
    col2.markdown(f"**States:** {mc.get('n_states', 3)} | **Cov:** {mc.get('covariance_type', 'full')}")
    col3.markdown(f"**Mode:** {wf.get('mode', 'expanding')} | **Train:** {wf.get('train_window', 504)}d")

st.divider()

if st.button("Run Analysis", type="primary", use_container_width=True):
    progress = st.progress(0, text="Starting...")
    status = st.empty()

    try:
        status.info("Engineering features...")
        featured_df = engineer_features(st.session_state["raw_df"], fc)
        status.info(f"Features ready: {len(featured_df)} rows")

        result = run_walkforward(featured_df, mc, wf, progress_bar=progress)

        st.session_state["result"] = result
        progress.progress(100, text="Complete!")
        status.empty()

        st.success(f"Done! **{result['n_folds']}** folds in **{result['duration_secs']}s**")
        st.balloons()
        st.info("Go to **Results Dashboard** to explore.")

    except Exception as e:
        st.error(f"Analysis failed: {e}")
