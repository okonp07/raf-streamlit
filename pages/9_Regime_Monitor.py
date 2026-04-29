"""Regime Monitor — live probabilities, transition alerts, and forward projection."""

import streamlit as st
import pandas as pd
import numpy as np
from components.theme import apply_theme, render_footer, render_toggle
from components.design import render_chart, render_page_hero, render_stat_cards, styled_dataframe
from components.charts import (
    regime_probability_chart, current_regime_gauge,
    forward_projection_chart, price_phase_chart, price_with_probabilities,
)
from core.monitor import train_full_model, detect_alerts, project_forward

render_toggle()
apply_theme()

render_page_hero(
    "Regime Monitor",
    "Train one model on the full available history to inspect the current market state, monitor confidence drift, and project forward regime probabilities using the learned transition matrix.",
    eyebrow="Live Monitoring",
    badges=["Full-history fit", "Probability alerts", "Forward projection"],
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
summary = monitor.get("summary", {})
phases = monitor.get("phases", [])
phase_descriptions = monitor.get("phase_descriptions", {})
phase_summary = monitor.get("phase_summary", {})

current_state = states[-1]
current_probs = probs[-1]
current_label = summary.get(
    "current_label",
    labels.get(current_state, labels.get(str(current_state), f"State {current_state}")),
)
current_confidence = summary.get("current_confidence", current_probs[current_state])
progress_ratio = float(summary.get("progress_ratio", 0.0))
progress_pct = max(0.0, min(progress_ratio * 100, 100.0))
progress_fill = 0.0 if progress_pct == 0 else max(progress_pct, 8.0)
current_phase = phase_summary.get("current_phase", phases[-1] if phases else "N/A")
phase_progress_ratio = float(phase_summary.get("progress_ratio", 0.0))
phase_progress_pct = max(0.0, min(phase_progress_ratio * 100, 100.0))
phase_progress_fill = 0.0 if phase_progress_pct == 0 else max(phase_progress_pct, 8.0)

render_stat_cards(
    [
        {
            "label": "Current Regime",
            "value": current_label,
            "note": "Highest-probability regime on the latest observation.",
        },
        {
            "label": "Confidence",
            "value": f"{current_confidence:.1%}",
            "note": "Posterior probability assigned to the current regime.",
        },
        {
            "label": "Current Market Phase",
            "value": current_phase,
            "note": phase_summary.get(
                "current_phase_description",
                "Model-derived cycle language layered on top of the statistical regime.",
            ),
        },
        {
            "label": "In Phase Since",
            "value": phase_summary.get("current_run_start", dates[-1]),
            "note": "First date of the current uninterrupted market-phase run.",
        },
    ]
)

lifecycle_col1, lifecycle_col2 = st.columns(2)

with lifecycle_col1:
    st.markdown(
        f"""
        <div class="glass-card runway-card">
            <div class="info-card-kicker">Regime Lifecycle Estimate</div>
            <h3>{current_label} is approximately {progress_pct:.0f}% through its current regime run.</h3>
            <p>
                Using the HMM transition matrix and observed historical run lengths, the model estimates
                roughly <strong>{summary.get("estimated_remaining_steps", 0):.1f}</strong> more modeled steps in
                this regime, with a tentative regime-end window around <strong>{summary.get("likely_end_date", dates[-1])}</strong>.
            </p>
            <div class="runway-track">
                <div class="runway-fill" style="width:{progress_fill:.1f}%"></div>
            </div>
            <div class="runway-meta">
                <span><strong>Entered</strong> {summary.get("current_run_start", dates[-1])}</span>
                <span><strong>Expected length</strong> {summary.get("blended_total_duration", summary.get("current_run_length", 1))} steps</span>
                <span><strong>Likely end</strong> {summary.get("likely_end_date", dates[-1])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with lifecycle_col2:
    st.markdown(
        f"""
        <div class="glass-card runway-card">
            <div class="info-card-kicker">Market Phase Lifecycle Estimate</div>
            <h3>{current_phase} is approximately {phase_progress_pct:.0f}% through its current phase run.</h3>
            <p>
                This phase is derived from the HMM regime plus trailing drawdown and trend context. Based on prior
                runs of the same phase, the model estimates roughly <strong>{phase_summary.get("estimated_remaining_steps", 0):.1f}</strong>
                more modeled steps before the phase is likely to turn, with a tentative phase-end window around
                <strong>{phase_summary.get("likely_end_date", dates[-1])}</strong>.
            </p>
            <div class="runway-track">
                <div class="runway-fill" style="width:{phase_progress_fill:.1f}%"></div>
            </div>
            <div class="runway-meta">
                <span><strong>Entered</strong> {phase_summary.get("current_run_start", dates[-1])}</span>
                <span><strong>Expected length</strong> {phase_summary.get("blended_total_duration", phase_summary.get("current_run_length", 1))} steps</span>
                <span><strong>Likely end</strong> {phase_summary.get("likely_end_date", dates[-1])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_stat_cards(
    [
        {
            "label": "Time In Regime",
            "value": f"{summary.get('current_run_length', 1)} steps",
            "note": "How long the current statistical regime has lasted so far.",
        },
        {
            "label": "Regime Remaining",
            "value": f"{summary.get('estimated_remaining_steps', 0):.1f} steps",
            "note": "Model-implied time left before the current regime is more likely to end.",
        },
        {
            "label": "Time In Phase",
            "value": f"{phase_summary.get('current_run_length', 1)} steps",
            "note": "How long the current market phase has lasted so far.",
        },
        {
            "label": "Phase Remaining",
            "value": f"{phase_summary.get('estimated_remaining_steps', 0):.1f} steps",
            "note": "Historically conditioned estimate of remaining time in the current market phase.",
        },
    ]
)

render_stat_cards(
    [
        {
            "label": "Regime Change Risk 20",
            "value": f"{summary.get('probability_end_20', 0):.1%}",
            "note": "Probability the current HMM regime ends within the next 20 modeled steps.",
        },
        {
            "label": "Phase Change Risk 20",
            "value": f"{phase_summary.get('probability_end_20', 0):.1%}",
            "note": "Historical probability the current market phase ends within the next 20 modeled steps.",
        },
        {
            "label": "Ticker",
            "value": ticker,
            "note": "Asset currently loaded into the monitoring workflow.",
        },
        {
            "label": "Data Points",
            "value": len(dates),
            "note": "Feature-ready observations used for the full-history fit.",
        },
    ]
)

# Gauge + regime breakdown
st.subheader("Probability Split Today")
gauge_cols = st.columns(n_states)
for i in range(n_states):
    label = labels.get(i, labels.get(str(i), f"State {i}"))
    with gauge_cols[i]:
        render_chart(current_regime_gauge(label, current_probs[i], i))

st.markdown(
    f"""
    <div class="note-box">
        <strong>Current read.</strong> The model was trained on all available data through <strong>{dates[-1]}</strong>. The regime estimate is the raw HMM view with a minimum-duration display filter, and the market-phase estimate is a second layer derived from that regime plus trailing price structure. Together they should tell you both what statistical state the model sees and where that state sits in the broader market cycle.<br>
        <strong>Smoothing note.</strong> {monitor.get('smoothing_note', '')}
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# --- Tabs ---
tab_probs, tab_alerts, tab_projection, tab_price = st.tabs([
    "Probability Timeline", "Transition Alerts", "Forward Projection", "Price & Probabilities"
])

with tab_probs:
    alerts = detect_alerts(probs, states, dates, labels, alert_threshold, lookback)
    render_chart(regime_probability_chart(dates, probs, labels, states, alerts))

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
    render_chart(forward_projection_chart(projection, labels))

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
    render_chart(price_with_probabilities(dates, close, probs, labels))
    render_chart(price_phase_chart(dates, close, phases, phase_descriptions))
    st.markdown(
        f"""
        <div class="note-box">
            <strong>Phase logic.</strong> {monitor.get('phase_note', '')}
        </div>
        """,
        unsafe_allow_html=True,
    )

render_footer()
