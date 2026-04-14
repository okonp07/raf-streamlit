"""Results Dashboard page."""

import streamlit as st
import pandas as pd
from components.charts import (
    price_regime_chart, transition_heatmap, occupancy_bar,
    return_dist_chart, fold_timeline, drawdown_chart,
)

st.header("Results Dashboard")

result = st.session_state.get("result")
if not result:
    st.warning("No results yet. Run an analysis first.")
    st.stop()

labels = result["regime_labels"]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("States", result["n_states"])
col2.metric("Folds", result["n_folds"])
col3.metric("Duration", f"{result['duration_secs']}s")
col4.metric("Avg Persistence", f"{result['robustness'].get('avg_test_persistence', 0):.3f}")

# Regime labels
st.subheader("Regime Labels")
label_cols = st.columns(len(labels))
for col, (sid, label) in zip(label_cols, sorted(labels.items(), key=lambda x: int(x[0]))):
    col.info(f"**State {sid}:** {label}")

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

    st.plotly_chart(drawdown_chart(result["all_test_dates"], result["test_returns"]), use_container_width=True)
    st.plotly_chart(fold_timeline(result["folds"]), use_container_width=True)

with tab_folds:
    folds = result["folds"]
    fold_names = [f"Fold {f['fold_id']}" for f in folds]
    selected = st.selectbox("Select Fold", fold_names)
    fold = folds[fold_names.index(selected)]

    col1, col2 = st.columns(2)
    col1.metric("Train", f"{fold['train_start']} to {fold['train_end']}")
    col2.metric("Test", f"{fold['test_start']} to {fold['test_end']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Train Persistence", f"{fold['train_persistence']:.3f}")
    col2.metric("Test Persistence", f"{fold['test_persistence']:.3f}")
    col3.metric("State Separation", f"{fold['state_separation']:.4f}")

    st.subheader("Train Regime Stats")
    train_rows = []
    for s in fold["regime_stats"]:
        lbl = fold["regime_labels"].get(s["state"], fold["regime_labels"].get(str(s["state"]), f"S{s['state']}"))
        if s.get("count", 0) > 0:
            train_rows.append({"Regime": lbl, "Count": s["count"], "Mean Ret": f"{s['mean_return']:.6f}",
                               "Vol": f"{s['std_return']:.6f}", "Sharpe": f"{s['sharpe']:.2f}",
                               "Max DD": f"{s['max_drawdown']:.4f}", "% Pos": f"{s['positive_pct']:.1%}"})
    st.dataframe(pd.DataFrame(train_rows), use_container_width=True, hide_index=True)

    st.subheader("Test Regime Stats")
    test_rows = []
    for s in fold["test_regime_stats"]:
        lbl = fold["regime_labels"].get(s["state"], fold["regime_labels"].get(str(s["state"]), f"S{s['state']}"))
        if s.get("count", 0) > 0:
            test_rows.append({"Regime": lbl, "Count": s["count"], "Mean Ret": f"{s['mean_return']:.6f}",
                              "Vol": f"{s['std_return']:.6f}", "Sharpe": f"{s['sharpe']:.2f}",
                              "Max DD": f"{s['max_drawdown']:.4f}", "% Pos": f"{s['positive_pct']:.1%}"})
    st.dataframe(pd.DataFrame(test_rows), use_container_width=True, hide_index=True)

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

    st.subheader("Consistency Across Folds")
    rows = []
    for sid, stats in robust["regime_consistency"].items():
        lbl = labels.get(int(sid), labels.get(str(sid), f"State {sid}"))
        rows.append({"Regime": lbl, "Mean Return CV": stats["mean_return_cv"],
                     "Vol CV": stats["vol_cv"], "Folds Present": stats["n_folds_present"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
