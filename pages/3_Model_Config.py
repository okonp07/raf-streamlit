"""Model configuration page."""

import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

if "model_config" not in st.session_state:
    st.session_state["model_config"] = {}
mc = st.session_state["model_config"]

render_page_hero(
    "Model Configuration",
    "Control the HMM itself: how many hidden states it can use, how flexible the covariance structure is, and how hard the optimiser should work before giving up.",
    eyebrow="Step 3",
    badges=["Gaussian HMM", "Scalable from 2 to 6 states", "Train-only scaling"],
)

mc["n_states"] = st.slider("Number Of Hidden States", 2, 6, mc.get("n_states", 3))

col1, col2 = st.columns(2)
cov_options = ["full", "diag", "tied", "spherical"]
mc["covariance_type"] = col1.selectbox(
    "Covariance Type",
    cov_options,
    index=cov_options.index(mc.get("covariance_type", "diag")),
)
mc["n_iter"] = col2.number_input(
    "Max Iterations",
    min_value=10,
    max_value=1000,
    value=mc.get("n_iter", 200),
)

col1, col2 = st.columns(2)
mc["tol"] = col1.number_input(
    "Tolerance",
    min_value=1e-8,
    max_value=1e-1,
    value=mc.get("tol", 1e-4),
    format="%.1e",
)
mc["random_seed"] = col2.number_input(
    "Random Seed",
    min_value=0,
    max_value=99999,
    value=mc.get("random_seed", 42),
)

mc["scaling"] = st.checkbox(
    "Scale features using training data only",
    value=mc.get("scaling", True),
)

mc["min_regime_duration"] = st.slider(
    "Minimum Regime Duration (display smoothing)",
    min_value=1,
    max_value=30,
    value=mc.get("min_regime_duration", 5),
    help="Short predicted runs below this length are merged into neighboring regimes before the app presents them.",
)

render_stat_cards(
    [
        {
            "label": "State Count",
            "value": mc["n_states"],
            "note": "Two states often produce a clean bull vs stress split. Three can capture a transition regime.",
        },
        {
            "label": "Covariance",
            "value": mc["covariance_type"],
            "note": "The app defaults to diag because it is usually more stable on financial walk-forward windows.",
        },
        {
            "label": "Optimiser Budget",
            "value": mc["n_iter"],
            "note": "Maximum EM iterations available to the model fit.",
        },
        {
            "label": "Scaling",
            "value": "Enabled" if mc["scaling"] else "Disabled",
            "note": "Feature standardisation is fit only on the training window before scoring test data.",
        },
        {
            "label": "Min Regime Duration",
            "value": f"{mc['min_regime_duration']} steps",
            "note": "A value of 1 disables smoothing. Higher values produce more persistent, cleaner overlays.",
        },
    ]
)

st.markdown(
    """
    <div class="note-box">
        <strong>Practical guidance.</strong> This app now starts on <em>diag</em> covariance because it tends to separate regimes more reliably with limited fold sizes. The default minimum-duration filter also suppresses one-off regime flickers. If you want a more reactive but noisier map, lower the smoothing threshold toward <em>1</em>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.session_state["model_config"] = mc

render_footer()
