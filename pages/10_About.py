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
    I design and deploy end-to-end data systems that turn raw data into production-ready intelligence.

    My core stack includes Python, Streamlit, BigQuery, Supabase, Hugging Face, PySpark, SQL, Machine Learning, LLMs, and Transformers.

    My work spans risk scoring systems, A/B testing, Traditional and AI-powered dashboards, RAG pipelines, predictive analytics, LLM-based solutions and AI research.

    Currently, I work as a Senior Data Scientist in the department of Research and Development at MIVA Open University, where I carry out AI / ML Research and build intelligent systems that drive analytics, decision support and scalable AI innovation.

    *I believe: models are trained, systems are engineered and impact is delivered.*
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
    I am a Data Scientist with a background in Civil Engineering, combining analytical thinking and technical skills to solve real-world problems with data.

    My core focus areas include machine learning, predictive modeling, quantitative analysis, and data-driven decision support. I work primarily with Python across the full analytics lifecycle — from data wrangling and feature engineering to model development and deployment.

    My work spans financial modeling, regime detection, time-series forecasting, risk analytics, and infrastructure data analysis. I bring a structured, engineering-first approach to every problem, ensuring that solutions are not only statistically sound but practically useful.

    Currently, I work as a Data Scientist at PSP Analytics and hold a degree in Financial Engineering from WorldQuant University, where I deepened my expertise in quantitative methods and portfolio theory.

    *I believe: good data tells a story, good models listen, and good decisions follow.*
    """)

st.divider()

render_footer()
