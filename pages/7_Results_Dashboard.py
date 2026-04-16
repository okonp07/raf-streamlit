"""Results Dashboard page — premium visual analytics."""

import streamlit as st
import pandas as pd
from components.theme import apply_theme, render_footer, render_toggle
from components.design import styled_dataframe, regime_color, REGIME_PALETTE, FONT_FAMILY
from components.charts import (
    price_regime_chart, transition_heatmap, occupancy_bar,
    return_dist_chart, fold_timeline, drawdown_chart,
)

render_toggle()
apply_theme()

st.header("Results Dashboard")

result = st.session_state.get("result")
if not result:
    st.warning("No results yet. Run an analysis first.")
    st.stop()

labels = result["regime_labels"]

# ─── KPI Row ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("States", result["n_states"])
col2.metric("Folds", result["n_folds"])
col3.metric("Duration", f"{result['duration_secs']}s")
col4.metric("Avg Persistence", f"{result['robustness'].get('avg_test_persistence', 0):.3f}")

# ─── Regime Labels ────────────────────────────────────────────────────────
st.markdown("")  # spacer
label_cols = st.columns(len(labels))
for idx, (col, (sid, label)) in enumerate(zip(label_cols, sorted(labels.items(), key=lambda x: int(x[0])))):
    color = regime_color(idx)
    col.markdown(
        f'<div style="background:{color}22;border-left:4px solid {color};'
        f'padding:10px 14px;border-radius:0 8px 8px 0;font-size:0.85rem;">'
        f'<span style="opacity:0.7;">State {sid}</span><br>'
        f'<b>{label}</b></div>',
        unsafe_allow_html=True,
    )

st.markdown("")  # spacer

# ─── Tabs ─────────────────────────────────────────────────────────────────
tab_overview, tab_folds, tab_robustness = st.tabs(["Overview", "Per-Fold", "Robustness"])

with tab_overview:
    st.plotly_chart(price_regime_chart(
        result["all_test_dates"], result["test_close"],
        result["all_test_states"], labels
    ), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        last = result["folds"][-1]
        st.plotly_chart(transition_heatmap(last["transition_matrix"], labels), use_container_width=True)
    with col2:
        st.plotly_chart(occupancy_bar(last["test_occupancy"], labels), use_container_width=True)

    st.plotly_chart(return_dist_chart(
        result["test_returns"], result["all_test_states"], labels
    ), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(drawdown_chart(result["all_test_dates"], result["test_returns"]), use_container_width=True)
    with col2:
        st.plotly_chart(fold_timeline(result["folds"]), use_container_width=True)

with tab_folds:
    folds = result["folds"]
    fold_names = [f"Fold {f['fold_id']}" for f in folds]
    selected = st.selectbox("Select Fold", fold_names)
    fold = folds[fold_names.index(selected)]

    col1, col2 = st.columns(2)
    col1.metric("Train Period", f"{fold['train_start']}  →  {fold['train_end']}")
    col2.metric("Test Period", f"{fold['test_start']}  →  {fold['test_end']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Train Persistence", f"{fold['train_persistence']:.3f}")
    col2.metric("Test Persistence", f"{fold['test_persistence']:.3f}")
    col3.metric("State Separation", f"{fold['state_separation']:.4f}")

    st.markdown("")

    # ─── Train Regime Stats Table ─────────────────────────────────────────
    st.markdown("##### Train Regime Statistics")
    train_rows = []
    for s in fold["regime_stats"]:
        lbl = fold["regime_labels"].get(s["state"], fold["regime_labels"].get(str(s["state"]), f"S{s['state']}"))
        if s.get("count", 0) > 0:
            train_rows.append({
                "Regime": lbl,
                "Count": f"{s['count']:,}",
                "Mean Return": f"{s['mean_return']:.6f}",
                "Volatility": f"{s['std_return']:.6f}",
                "Sharpe": f"{s['sharpe']:.2f}",
                "Max DD": f"{s['max_drawdown']:.4f}",
                "% Positive": f"{s['positive_pct']:.1%}",
            })
    styled_dataframe(pd.DataFrame(train_rows))

    st.markdown("")

    # ─── Test Regime Stats Table ──────────────────────────────────────────
    st.markdown("##### Test Regime Statistics")
    test_rows = []
    for s in fold["test_regime_stats"]:
        lbl = fold["regime_labels"].get(s["state"], fold["regime_labels"].get(str(s["state"]), f"S{s['state']}"))
        if s.get("count", 0) > 0:
            test_rows.append({
                "Regime": lbl,
                "Count": f"{s['count']:,}",
                "Mean Return": f"{s['mean_return']:.6f}",
                "Volatility": f"{s['std_return']:.6f}",
                "Sharpe": f"{s['sharpe']:.2f}",
                "Max DD": f"{s['max_drawdown']:.4f}",
                "% Positive": f"{s['positive_pct']:.1%}",
            })
    styled_dataframe(pd.DataFrame(test_rows))

    st.markdown("")
    st.plotly_chart(transition_heatmap(fold["transition_matrix"], fold["regime_labels"]), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Log-Likelihood", f"{fold.get('log_likelihood', 'N/A')}")
    col2.metric("AIC", f"{fold.get('aic', 'N/A')}")
    col3.metric("BIC", f"{fold.get('bic', 'N/A')}")

with tab_robustness:
    robust = result["robustness"]
    st.markdown(f"**{robust['interpretation']}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Stable Regimes", f"{robust['stable_regimes']} / {robust['n_states']}")
    col2.metric("Avg Test Persistence", f"{robust['avg_test_persistence']:.3f}")
    col3.metric("Total Folds", robust["n_folds"])

    st.markdown("")
    st.markdown("##### Consistency Across Folds")
    rows = []
    for sid, stats in robust["regime_consistency"].items():
        lbl = labels.get(int(sid), labels.get(str(sid), f"State {sid}"))
        rows.append({
            "Regime": lbl,
            "Mean Return CV": f"{stats['mean_return_cv']:.4f}" if isinstance(stats['mean_return_cv'], (int, float)) else str(stats['mean_return_cv']),
            "Volatility CV": f"{stats['vol_cv']:.4f}" if isinstance(stats['vol_cv'], (int, float)) else str(stats['vol_cv']),
            "Folds Present": stats["n_folds_present"],
        })
    styled_dataframe(pd.DataFrame(rows))

render_footer()
