"""Model Configuration page."""

import streamlit as st
from components.theme import apply_theme

apply_theme()

st.header("Model Configuration")

if "model_config" not in st.session_state:
    st.session_state["model_config"] = {}
mc = st.session_state["model_config"]

mc["n_states"] = st.slider("Number of Hidden States", 2, 6, mc.get("n_states", 3))

col1, col2 = st.columns(2)
mc["covariance_type"] = col1.selectbox("Covariance Type", ["full", "diag", "tied", "spherical"],
                                        index=["full", "diag", "tied", "spherical"].index(mc.get("covariance_type", "full")))
mc["n_iter"] = col2.number_input("Max Iterations", 10, 1000, mc.get("n_iter", 200))

col1, col2 = st.columns(2)
mc["tol"] = col1.number_input("Tolerance", 1e-8, 1e-1, mc.get("tol", 1e-4), format="%.1e")
mc["random_seed"] = col2.number_input("Random Seed", 0, 99999, mc.get("random_seed", 42))

mc["scaling"] = st.checkbox("Scale features (fit on train only)", value=mc.get("scaling", True))

st.divider()
st.json(mc)
st.session_state["model_config"] = mc
