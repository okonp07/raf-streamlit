"""Regime Monitor — live probabilities, transition alerts, and forward projection."""

import streamlit as st
import pandas as pd
import numpy as np
from components.theme import apply_theme, render_footer, render_toggle
from components.design import styled_dataframe
from components.charts import (
    regime_probability_chart, current_regime_gauge,
    forward_projection_chart, price_with_probabilities,
)
from core.monitor import train_full_model, detect_alerts, project_forward

render_toggle()
apply_theme()

st.header("Regime Monitor")
st.markdown(
    "Real-time regime probability tracking, transition alerts, and forward projections. "
    "This page trains a model on **all available data** and shows where the market stands *right now*."
)

# --- Prerequisites ---
if "raw_df" not in st.session_state:
    st.warning("Fetch data first on the **Data Ingestion** page.")
    st.stop()

fc = st.session_state.get("feature_config", {})
mc = st.session_state.get("model_config", {})
ticker = st.session_state.get("ticker", "SPY")

# --- Controls ---
col1, col2, col3 = st.columns(3)
alert_threshold = col1.slider("Alert Threshold", 0.3, 0.8, 0.6, 0.05,
                               help="Flag when current regime confidence drops below this level")
lookback = col2.number_input("Alert Lookback (days)", 3, 20, 5,
                              help="Number of days to assess probability trend")
projection_days = col3.number_input("Projection Horizon (days)", 5, 90, 30,
                                     help="How far ahead to project regime probabilities")

st.divider()

# --- Train & Monitor ---
if st.button("Run Regime Monitor", type="primary", use_container_width=True):
    with st.spinner("Training model on full dataset..."):
        try:
            monitor = train_full_model(st.session_state["raw_df"], fc, mc)
            st.session_state["monitor"] = monitor
            st.success("Model trained successfully.")
        except Exception as e:
            st.error(f"Training failed: {e}")
            st.stop()

monitor = st.session_state.get("monitor")
if not monitor:
    st.info("Click **Run Regime Monitor** to train the model and generate live insights.")
    render_footer()
    st.stop()

# --- Current State ---
labels = monitor["labels"]
states = monitor["states"]
probs = monitor["probabilities"]
dates = monitor["dates"]
close = monitor["close"]
n_states = monitor["n_states"]

current_state = states[-1]
current_probs = probs[-1]
current_label = labels.get(current_state, labels.get(str(current_state), f"State {current_state}"))
current_confidence = current_probs[current_state]

st.subheader(f"Current Regime: {current_label}")

# Gauge + regime breakdown
gauge_cols = st.columns(n_states)
for i in range(n_states):
    label = labels.get(i, labels.get(str(i), f"State {i}"))
    with gauge_cols[i]:
        st.plotly_chart(current_regime_gauge(label, current_probs[i], i), use_container_width=True)

# Key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ticker", ticker)
col2.metric("Data Points", len(dates))
col3.metric("Last Date", dates[-1])
col4.metric("Confidence", f"{current_confidence:.1%}")

st.divider()

# --- Tabs ---
tab_probs, tab_alerts, tab_projection, tab_price = st.tabs([
    "Probability Timeline", "Transition Alerts", "Forward Projection", "Price & Probabilities"
])

with tab_probs:
    alerts = detect_alerts(probs, states, dates, labels, alert_threshold, lookback)
    st.plotly_chart(
        regime_probability_chart(dates, probs, labels, states, alerts),
        use_container_width=True,
    )

    # Show probability table for last N days
    st.subheader("Recent Regime Probabilities")
    n_recent = st.slider("Show last N days", 5, 60, 20, key="recent_days")
    recent_data = []
    for i in range(-n_recent, 0):
        row = {"Date": dates[i], "Regime": labels.get(states[i], labels.get(str(states[i]), f"State {states[i]}"))}
        for s in range(n_states):
            lbl = labels.get(s, labels.get(str(s), f"State {s}"))
            row[lbl] = f"{probs[i][s]:.1%}"
        recent_data.append(row)
    styled_dataframe(pd.DataFrame(recent_data))

with tab_alerts:
    alerts = detect_alerts(probs, states, dates, labels, alert_threshold, lookback)

    if not alerts:
        st.success(f"No transition alerts detected at the {alert_threshold:.0%} threshold.")
    else:
        st.warning(f"**{len(alerts)}** transition alerts detected.")

        # Summary metrics
        high = sum(1 for a in alerts if a["severity"] == "High")
        medium = sum(1 for a in alerts if a["severity"] == "Medium")
        low = sum(1 for a in alerts if a["severity"] == "Low")
        col1, col2, col3 = st.columns(3)
        col1.metric("High Severity", high)
        col2.metric("Medium Severity", medium)
        col3.metric("Low Severity", low)

        # Recent alerts first
        alert_df = pd.DataFrame(alerts[::-1])
        alert_df = alert_df.rename(columns={
            "date": "Date",
            "current_regime": "Current Regime",
            "confidence": "Confidence",
            "alternative_regime": "Emerging Regime",
            "alt_probability": "Emerging Prob",
            "declining": "Declining Trend",
            "severity": "Severity",
        })
        alert_df["Confidence"] = alert_df["Confidence"].apply(lambda x: f"{x:.1%}")
        alert_df["Emerging Prob"] = alert_df["Emerging Prob"].apply(lambda x: f"{x:.1%}")
        styled_dataframe(alert_df)

    # Explain the alerts
    with st.expander("How alerts work"):
        st.markdown(f"""
        A **transition alert** fires when the model's confidence in the current regime
        drops below **{alert_threshold:.0%}**. This means the model is uncertain about
        whether the market is still in the same regime — a potential early warning
        that a regime change is underway.

        - **High severity**: Confidence < 40% — the model strongly doubts the current regime
        - **Medium severity**: Confidence 40–50% — regime is ambiguous
        - **Low severity**: Confidence 50–{alert_threshold:.0%} — early warning

        The **Emerging Regime** column shows which alternative regime has the highest
        probability, and **Declining Trend** indicates whether confidence has been
        falling over the last {lookback} days.
        """)

with tab_projection:
    st.subheader("Forward Regime Probability Projection")
    st.markdown(
        f"Using the learned transition matrix to project regime probabilities "
        f"**{projection_days} days** ahead from the current state."
    )

    projection = project_forward(monitor["transmat"], current_probs, labels, projection_days)
    st.plotly_chart(forward_projection_chart(projection, labels), use_container_width=True)

    # Show convergence info
    final_probs = projection.iloc[-1]
    st.subheader("Projected Steady-State")
    proj_cols = st.columns(n_states)
    for i, s in enumerate(range(n_states)):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        with proj_cols[i]:
            current_p = current_probs[s]
            final_p = final_probs[label]
            delta = final_p - current_p
            st.metric(label, f"{final_p:.1%}", delta=f"{delta:+.1%}")

    # Transition matrix
    st.subheader("Transition Matrix")
    T = np.array(monitor["transmat"])
    tmat_labels = [labels.get(i, labels.get(str(i), f"State {i}")) for i in range(n_states)]
    tmat_df = pd.DataFrame(T, index=tmat_labels, columns=tmat_labels)
    tmat_df = tmat_df.map(lambda x: f"{x:.3f}")
    styled_dataframe(tmat_df, hide_index=False)

    with st.expander("How forward projection works"):
        st.markdown("""
        The HMM learns a **transition matrix** — the probability of moving from one
        regime to another on any given day. By multiplying the current probability
        distribution by this matrix repeatedly, we project how regime probabilities
        evolve over time.

        - **Short-term** (1–5 days): Probabilities are dominated by the current regime
        - **Medium-term** (5–30 days): Transition dynamics become visible
        - **Long-term** (30+ days): Probabilities converge to the **stationary distribution** — the long-run average time spent in each regime

        This is a **probabilistic forecast**, not a deterministic prediction.
        The actual regime path will depend on incoming market data.
        """)

with tab_price:
    st.plotly_chart(
        price_with_probabilities(dates, close, probs, labels),
        use_container_width=True,
    )

render_footer()
