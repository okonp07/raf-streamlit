"""About page — author profiles."""

import base64
import streamlit as st
from pathlib import Path
from components.theme import apply_theme, render_footer

apply_theme()

st.header("About")
st.markdown("Meet the team behind Regime-Aware Forecasting.")

st.divider()


def circular_image_html(image_path: str, size: int = 160) -> str:
    """Return HTML for a circular image from a local file."""
    path = Path(image_path)
    if path.exists():
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f"""
        <div style="display:flex;justify-content:center;margin-bottom:16px;">
            <img src="data:image/png;base64,{b64}"
                 style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;
                        border:3px solid #1a73e8;" />
        </div>
        """
    return ""


def initial_placeholder_html(initials: str, size: int = 160) -> str:
    """Return HTML for a circular placeholder with initials."""
    return f"""
    <div style="display:flex;justify-content:center;margin-bottom:16px;">
        <div style="width:{size}px;height:{size}px;border-radius:50%;
                    background:linear-gradient(135deg,#1a73e8,#56b4e9);
                    display:flex;align-items:center;justify-content:center;
                    border:3px solid #1a73e8;color:#fff;font-size:48px;font-weight:bold;">
            {initials}
        </div>
    </div>
    """


col1, col2 = st.columns(2)

with col1:
    okon_img = circular_image_html("assets/prince-okon.png")
    if okon_img:
        st.markdown(okon_img, unsafe_allow_html=True)
    else:
        st.markdown(initial_placeholder_html("OP"), unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;">
        <h3>Okon Prince</h3>
        <p style="font-size:0.9rem;opacity:0.8;margin-top:-8px;">AI Engineer & Data Scientist | Senior Data Scientist at MIVA Open University</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Okon Prince is a Data Scientist and Machine Learning Engineer with expertise
    in quantitative finance, statistical modelling, and production ML systems.
    He specialises in building end-to-end pipelines that translate complex
    analytical methods into practical, deployable tools. His work spans regime
    detection, time-series forecasting, and risk analytics. He is passionate
    about making advanced quantitative techniques accessible to a wider audience.
    """)

with col2:
    hart_img = circular_image_html("assets/hart_cropped.jpeg")
    if hart_img:
        st.markdown(hart_img, unsafe_allow_html=True)
    else:
        st.markdown(initial_placeholder_html("HO"), unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;">
        <h3>Hart Ofigwe</h3>
        <p style="font-size:0.9rem;opacity:0.8;margin-top:-8px;">Data Scientist | Machine Learning Engineer | Quant | Civil Engineer<br>PSP Analytics · WorldQuant University</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Hart Ofigwe is a finance professional and quantitative analyst with deep
    domain knowledge in market microstructure, portfolio management, and
    financial risk. He designed the analytical framework behind this application,
    defining the feature set, validation methodology, and interpretation logic
    that drive the regime detection engine. His focus is on bridging the gap
    between academic research and real-world investment decision-making.
    """)

st.divider()

render_footer()
