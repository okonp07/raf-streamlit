"""Results dashboard page."""

import pandas as pd
import streamlit as st

from components.charts import (
    drawdown_chart,
    fold_timeline,
    occupancy_bar,
    price_phase_chart,
    price_regime_chart,
    return_dist_chart,
    transition_heatmap,
)
from components.design import (
    phase_color,
    render_chart,
    render_page_hero,
    render_stat_cards,
    regime_color,
    styled_dataframe,
)
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

result = st.session_state.get("result")
if not result:
    render_page_hero(
        "Results Dashboard",
        "Run an analysis first to populate the out-of-sample diagnostics, regime overlays, and robustness metrics.",
        eyebrow="Walk-Forward Output",
        badges=["No active analysis", "Awaiting result"],
    )
    st.warning("No results yet. Run an analysis first.")
    st.stop()

labels = result["regime_labels"]
phase_descriptions = result.get("phase_descriptions", {})

render_page_hero(
    "Results Dashboard",
    "Inspect the walk-forward output through two complementary lenses: the HMM's statistical regime assignments and a model-driven market-phase layer that maps those regimes into more intuitive cycle language.",
    eyebrow="Walk-Forward Output",
    badges=[
        f"{result['n_states']} states",
        f"{result['n_folds']} folds",
        f"{result.get('coverage_pct', 0):.1f}% out-of-sample coverage",
    ],
)

render_stat_cards(
    [
        {
            "label": "Duration",
            "value": f"{result['duration_secs']}s",
            "note": "End-to-end run time for feature engineering and walk-forward fitting.",
        },
        {
            "label": "Avg Persistence",
            "value": f"{result['robustness'].get('avg_test_persistence', 0):.3f}",
            "note": "Mean regime persistence across test folds.",
        },
        {
            "label": "Stable Regimes",
            "value": f"{result['robustness']['stable_regimes']} / {result['robustness']['n_states']}",
            "note": "Cross-fold consistency after state canonicalisation.",
        },
        {
            "label": "Overlay Coverage",
            "value": f"{result.get('coverage_pct', 0):.1f}%",
            "note": "Share of modelled dates with out-of-sample state assignments.",
        },
    ]
)

st.markdown(
    f"""
    <div class="note-box">
        <strong>Overlay note.</strong> {result.get('overlay_note', '')}<br>
        <strong>Smoothing note.</strong> {result.get('smoothing_note', '')}<br>
        <strong>Phase note.</strong> {result.get('phase_note', '')}
    </div>
    """,
    unsafe_allow_html=True,
)

label_cols = st.columns(len(labels))
for idx, (col, (sid, label)) in enumerate(
    zip(label_cols, sorted(labels.items(), key=lambda x: int(x[0])))
):
    color = regime_color(idx)
    col.markdown(
        f"""
        <div class="glass-card info-card" style="padding:1rem 1rem 0.85rem;border-left:4px solid {color};">
            <div class="info-card-kicker">State {sid}</div>
            <h3 style="margin-bottom:0.25rem;">{label}</h3>
            <p>Canonical colour assignment is held consistent across folds for the dashboard views.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if phase_descriptions:
    st.markdown(
        """
        <div class="note-box">
            <strong>Market phase layer.</strong> These labels are derived from the HMM regime plus trailing drawdown and trend context, so they should align more closely with how a human would describe capitulation, repair, distribution, and bull expansion.
        </div>
        """,
        unsafe_allow_html=True,
    )

    phase_cols = st.columns(len(phase_descriptions))
    for col, (phase, description) in zip(phase_cols, phase_descriptions.items()):
        color = phase_color(phase)
        col.markdown(
            f"""
            <div class="glass-card info-card" style="padding:1rem 1rem 0.85rem;border-left:4px solid {color};">
                <div class="info-card-kicker">Market Phase</div>
                <h3 style="margin-bottom:0.25rem;">{phase}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

tab_overview, tab_folds, tab_robustness = st.tabs(
    ["Overview", "Per-Fold Diagnostics", "Robustness"]
)

with tab_overview:
    render_chart(
        price_regime_chart(
            result["timeline_dates"],
            result["timeline_close"],
            result["timeline_states"],
            labels,
        )
    )
    render_chart(
        price_phase_chart(
            result["timeline_dates"],
            result["timeline_close"],
            result.get("timeline_phases", []),
            phase_descriptions,
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        render_chart(
            transition_heatmap(result["folds"][-1]["transition_matrix"], labels)
        )
    with col2:
        render_chart(occupancy_bar(result["folds"][-1]["test_occupancy"], labels))

    col1, col2 = st.columns(2)
    with col1:
        render_chart(return_dist_chart(result["oos_returns"], result["oos_states"], labels))
    with col2:
        render_chart(drawdown_chart(result["oos_dates"], result["oos_returns"]))

    render_chart(fold_timeline(result["folds"]))

with tab_folds:
    folds = result["folds"]
    fold_names = [f"Fold {f['fold_id']}" for f in folds]
    selected = st.selectbox("Select Fold", fold_names)
    fold = folds[fold_names.index(selected)]

    render_stat_cards(
        [
            {
                "label": "Train Window",
                "value": f"{fold['train_start']} to {fold['train_end']}",
                "note": "Chronological in-sample fitting window.",
            },
            {
                "label": "Test Window",
                "value": f"{fold['test_start']} to {fold['test_end']}",
                "note": "Out-of-sample scoring interval for this fold.",
            },
            {
                "label": "State Separation",
                "value": f"{fold['state_separation']:.4f}",
                "note": "Between-state separation relative to within-state variance.",
            },
            {
                "label": "Test Persistence",
                "value": f"{fold['test_persistence']:.3f}",
                "note": "Day-to-day continuity of predicted states on this fold.",
            },
        ]
    )

    if fold.get("warnings"):
        st.markdown(
            f"""
            <div class="note-box">
                <strong>Fold note.</strong> {' '.join(fold['warnings'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    train_rows = []
    for stat in fold["regime_stats"]:
        if stat.get("count", 0) == 0:
            continue
        label = fold["regime_labels"].get(
            stat["state"],
            fold["regime_labels"].get(str(stat["state"]), f"State {stat['state']}"),
        )
        train_rows.append(
            {
                "Regime": label,
                "Count": f"{stat['count']:,}",
                "Mean Return": f"{stat['mean_return']:.6f}",
                "Volatility": f"{stat['std_return']:.6f}",
                "Sharpe": f"{stat['sharpe']:.2f}",
                "Max Drawdown": f"{stat['max_drawdown']:.4f}",
                "% Positive": f"{stat['positive_pct']:.1%}",
            }
        )

    test_rows = []
    for stat in fold["test_regime_stats"]:
        if stat.get("count", 0) == 0:
            continue
        label = fold["regime_labels"].get(
            stat["state"],
            fold["regime_labels"].get(str(stat["state"]), f"State {stat['state']}"),
        )
        test_rows.append(
            {
                "Regime": label,
                "Count": f"{stat['count']:,}",
                "Mean Return": f"{stat['mean_return']:.6f}",
                "Volatility": f"{stat['std_return']:.6f}",
                "Sharpe": f"{stat['sharpe']:.2f}",
                "Max Drawdown": f"{stat['max_drawdown']:.4f}",
                "% Positive": f"{stat['positive_pct']:.1%}",
            }
        )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Train Regime Statistics")
        styled_dataframe(pd.DataFrame(train_rows))
    with col2:
        st.subheader("Test Regime Statistics")
        styled_dataframe(pd.DataFrame(test_rows))

    render_chart(transition_heatmap(fold["transition_matrix"], fold["regime_labels"]))

    render_stat_cards(
        [
            {
                "label": "Log-Likelihood",
                "value": f"{fold.get('log_likelihood', 0):.2f}",
                "note": "Training log-likelihood for the fitted HMM.",
            },
            {
                "label": "AIC",
                "value": f"{fold.get('aic', 0):.2f}",
                "note": "Complexity-penalised in-sample fit.",
            },
            {
                "label": "BIC",
                "value": f"{fold.get('bic', 0):.2f}",
                "note": "Stronger complexity penalty with sample-size scaling.",
            },
            {
                "label": "Test Occupancy",
                "value": f"{max(fold['test_occupancy'].values()):.1%}",
                "note": "Largest regime share within the test window.",
            },
        ]
    )

with tab_robustness:
    robust = result["robustness"]
    forward_validation = result.get("forward_validation", [])

    st.markdown(
        f"""
        <div class="note-box">
            <strong>Interpretation.</strong> {robust['interpretation']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_stat_cards(
        [
            {
                "label": "Stable Regimes",
                "value": f"{robust['stable_regimes']} / {robust['n_states']}",
                "note": "Regimes that remain reasonably consistent across folds.",
            },
            {
                "label": "Average Test Persistence",
                "value": f"{robust['avg_test_persistence']:.3f}",
                "note": "Average day-to-day state continuity across all folds.",
            },
            {
                "label": "Total Folds",
                "value": robust["n_folds"],
                "note": "Successful walk-forward folds included in the report.",
            },
        ]
    )

    rows = []
    for sid, stats in robust["regime_consistency"].items():
        label = labels.get(int(sid), labels.get(str(sid), f"State {sid}"))
        rows.append(
            {
                "Regime": label,
                "Mean Return CV": (
                    f"{stats['mean_return_cv']:.4f}"
                    if isinstance(stats["mean_return_cv"], (int, float))
                    else str(stats["mean_return_cv"])
                ),
                "Volatility CV": (
                    f"{stats['vol_cv']:.4f}"
                    if isinstance(stats["vol_cv"], (int, float))
                    else str(stats["vol_cv"])
                ),
                "Folds Present": stats["n_folds_present"],
            }
        )

    st.subheader("Cross-Fold Consistency")
    styled_dataframe(pd.DataFrame(rows))

    if forward_validation:
        st.markdown(
            f"""
            <div class="note-box">
                <strong>Forward validation.</strong> {result.get('forward_validation_interpretation', '')}
            </div>
            """,
            unsafe_allow_html=True,
        )

        validation_rows = []
        for row in forward_validation:
            validation_rows.append(
                {
                    "Regime": row["label"],
                    "Obs": f"{row['count']:,}",
                    "Avg Duration": f"{row['avg_duration']:.1f}",
                    "Avg Fwd 7d": (
                        f"{row['avg_fwd_return_7']:.2%}"
                        if row.get("avg_fwd_return_7") is not None
                        else "N/A"
                    ),
                    "Avg Fwd 14d": (
                        f"{row['avg_fwd_return_14']:.2%}"
                        if row.get("avg_fwd_return_14") is not None
                        else "N/A"
                    ),
                    "Avg Fwd 30d": (
                        f"{row['avg_fwd_return_30']:.2%}"
                        if row.get("avg_fwd_return_30") is not None
                        else "N/A"
                    ),
                    "Fwd Vol 30d": (
                        f"{row['avg_forward_realized_vol_30d']:.2%}"
                        if row.get("avg_forward_realized_vol_30d") is not None
                        else "N/A"
                    ),
                    "Avg Fwd Max DD 30d": (
                        f"{row['avg_forward_max_drawdown_30d']:.2%}"
                        if row.get("avg_forward_max_drawdown_30d") is not None
                        else "N/A"
                    ),
                    "DD > 10% Hit Rate": (
                        f"{row['drawdown_hit_rate_30d']:.1%}"
                        if row.get("drawdown_hit_rate_30d") is not None
                        else "N/A"
                    ),
                }
            )

        st.subheader("Forward Regime Diagnostics")
        styled_dataframe(pd.DataFrame(validation_rows))

render_footer()
