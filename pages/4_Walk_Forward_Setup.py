"""Walk-Forward Setup page."""

import streamlit as st
from components.theme import apply_theme

apply_theme()

st.header("Walk-Forward Setup")

if "wf_config" not in st.session_state:
    st.session_state["wf_config"] = {}
wf = st.session_state["wf_config"]

col1, col2 = st.columns(2)
wf["mode"] = col1.selectbox("Mode", ["expanding", "rolling"],
                             index=0 if wf.get("mode", "expanding") == "expanding" else 1)
wf["train_window"] = col2.number_input("Train Window (days)", 100, 5000, wf.get("train_window", 504))

col1, col2 = st.columns(2)
wf["test_window"] = col1.number_input("Test Window (days)", 10, 504, wf.get("test_window", 63))
wf["step_size"] = col2.number_input("Step Size (days)", 1, 252, wf.get("step_size", 63))

col1, col2 = st.columns(2)
wf["min_observations"] = col1.number_input("Min Observations", 50, 1000, wf.get("min_observations", 252))
wf["refit_every"] = col2.number_input("Refit Every N Steps", 1, 20, wf.get("refit_every", 1))

if "raw_df" in st.session_state:
    n = len(st.session_state["raw_df"])
    est = max(0, (n - wf["train_window"] - wf["test_window"]) // wf["step_size"] + 1)
    st.info(f"Estimated **{est}** folds with {n} data points")

st.divider()
st.json(wf)
st.session_state["wf_config"] = wf
