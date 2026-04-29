"""Configuration & Features Guide page."""

import streamlit as st
from pathlib import Path
from components.design import render_page_hero
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

render_page_hero(
    "Configuration Guide",
    "A reference page for the configurable features, parameters, and modelling choices available throughout the app.",
    eyebrow="Reference",
    badges=["Feature definitions", "Model parameters", "Workflow reference"],
)

guide_path = Path("features.md")
if guide_path.exists():
    st.markdown(guide_path.read_text())
else:
    st.error("Guide file (features.md) not found.")

render_footer()
