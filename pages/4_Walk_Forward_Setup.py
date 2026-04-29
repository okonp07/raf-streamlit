"""Walk-forward setup page."""

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

if "wf_config" not in st.session_state:
    st.session_state["wf_config"] = {}
wf = st.session_state["wf_config"]

render_page_hero(
    "Walk-Forward Setup",
    "Define how the model is trained and scored through time. These settings determine the chronology, fold density, and realism of the out-of-sample evaluation.",
    eyebrow="Step 4",
    badges=["Expanding or rolling", "Chronological scoring", "No look-ahead leakage"],
)

col1, col2 = st.columns(2)
wf["mode"] = col1.selectbox(
    "Mode",
    ["expanding", "rolling"],
    index=0 if wf.get("mode", "expanding") == "expanding" else 1,
)
wf["train_window"] = col2.number_input(
    "Train Window (days)",
    min_value=100,
    max_value=5000,
    value=wf.get("train_window", 504),
)

col1, col2 = st.columns(2)
wf["test_window"] = col1.number_input(
    "Test Window (days)",
    min_value=10,
    max_value=504,
    value=wf.get("test_window", 63),
)
wf["step_size"] = col2.number_input(
    "Step Size (days)",
    min_value=1,
    max_value=252,
    value=wf.get("step_size", 63),
)

col1, col2 = st.columns(2)
wf["min_observations"] = col1.number_input(
    "Minimum Observations",
    min_value=50,
    max_value=1000,
    value=wf.get("min_observations", 252),
)
wf["refit_every"] = col2.number_input(
    "Refit Every N Steps",
    min_value=1,
    max_value=20,
    value=wf.get("refit_every", 1),
)

estimated_folds = None
if "raw_df" in st.session_state:
    n = len(st.session_state["raw_df"])
    estimated_folds = max(
        0,
        (n - wf["train_window"] - wf["test_window"]) // wf["step_size"] + 1,
    )

render_stat_cards(
    [
        {
            "label": "Mode",
            "value": wf["mode"].title(),
            "note": "Expanding windows grow through time; rolling windows maintain a fixed memory.",
        },
        {
            "label": "Train Window",
            "value": wf["train_window"],
            "note": "Number of observations the model can learn from in each fold.",
        },
        {
            "label": "Test Window",
            "value": wf["test_window"],
            "note": "Length of the unseen interval that receives out-of-sample predictions.",
        },
        {
            "label": "Estimated Folds",
            "value": estimated_folds if estimated_folds is not None else "Fetch data first",
            "note": "Approximate number of folds implied by the current dataset and window choices.",
        },
    ]
)

st.markdown(
    """
    <div class="note-box">
        <strong>Reading the trade-off.</strong> Larger training windows typically stabilise the HMM, while smaller test windows create more folds and a finer-grained view of changing market structure. A step size equal to the test window produces non-overlapping out-of-sample periods.
    </div>
    """,
    unsafe_allow_html=True,
)

st.session_state["wf_config"] = wf

render_footer()
