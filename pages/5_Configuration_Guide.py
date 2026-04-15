"""Configuration & Features Guide page."""

import streamlit as st
from pathlib import Path
from components.theme import apply_theme, render_footer

apply_theme()

st.header("Configuration & Features Guide")
st.caption("A detailed reference for every configurable parameter in the app.")

guide_path = Path("features.md")
if guide_path.exists():
    st.markdown(guide_path.read_text())
else:
    st.error("Guide file (features.md) not found.")

render_footer()
