"""Export page."""

import json

import pandas as pd
import streamlit as st

from components.design import render_page_hero, render_stat_cards
from components.theme import apply_theme, render_footer, render_toggle

render_toggle()
apply_theme()

result = st.session_state.get("result")
monitor = st.session_state.get("monitor")
if not result:
    render_page_hero(
        "Export & Report",
        "Run an analysis first so the app can generate downloadable fold metrics, state assignments, summary JSON, and the markdown report.",
        eyebrow="Step 7",
        badges=["No active analysis"],
    )
    st.warning("No results to export. Run an analysis first.")
    st.stop()

render_page_hero(
    "Export & Report",
    "Package the walk-forward output into portable files for research, review, or handoff. Every download is generated directly from the current Streamlit session.",
    eyebrow="Step 7",
    badges=[
        "CSV metrics",
        "State assignments",
        "Summary JSON",
        "Markdown report",
    ],
)

render_stat_cards(
    [
        {
            "label": "Folds",
            "value": result["n_folds"],
            "note": "Successful walk-forward folds included in the current export package.",
        },
        {
            "label": "States",
            "value": result["n_states"],
            "note": "Canonical regime count used across the dashboard and exports.",
        },
        {
            "label": "Coverage",
            "value": f"{result.get('coverage_pct', 0):.1f}%",
            "note": "Share of modelled dates with out-of-sample state assignments.",
        },
        {
            "label": "Runtime",
            "value": f"{result['duration_secs']}s",
            "note": "Elapsed time recorded for the active analysis run.",
        },
    ]
)

st.markdown('<div class="section-gap-lg"></div>', unsafe_allow_html=True)

fold_rows = []
for fold in result["folds"]:
    row = {
        "fold_id": fold["fold_id"],
        "train_start": fold["train_start"],
        "train_end": fold["train_end"],
        "test_start": fold["test_start"],
        "test_end": fold["test_end"],
        "train_persistence": fold["train_persistence"],
        "test_persistence": fold["test_persistence"],
        "state_separation": fold["state_separation"],
        "log_likelihood": fold.get("log_likelihood"),
        "aic": fold.get("aic"),
        "bic": fold.get("bic"),
    }
    for key, value in fold["test_occupancy"].items():
        row[f"occ_state_{key}"] = value
    fold_rows.append(row)
fold_metrics_csv = pd.DataFrame(fold_rows).to_csv(index=False)

assignment_rows = []
phase_by_date = {
    dt: phase
    for dt, phase in zip(result.get("timeline_dates", []), result.get("timeline_phases", []))
}
for fold in result["folds"]:
    for dt, state_value in zip(fold["test_dates"], fold["test_states"]):
        assignment_rows.append(
            {
                "date": dt,
                "fold_id": fold["fold_id"],
                "state": state_value,
                "label": fold["regime_labels"].get(
                    state_value,
                    fold["regime_labels"].get(str(state_value), f"State {state_value}"),
                ),
                "phase": phase_by_date.get(dt),
            }
        )
states_csv = pd.DataFrame(assignment_rows).to_csv(index=False)

summary = {
    "n_folds": result["n_folds"],
    "n_states": result["n_states"],
    "duration_secs": result["duration_secs"],
    "regime_labels": result["regime_labels"],
    "phase_descriptions": result.get("phase_descriptions", {}),
    "robustness": result["robustness"],
    "coverage_pct": result.get("coverage_pct", 0),
    "overlay_note": result.get("overlay_note", ""),
    "smoothing_note": result.get("smoothing_note", ""),
    "phase_note": result.get("phase_note", ""),
    "forward_validation": result.get("forward_validation", []),
    "forward_validation_interpretation": result.get("forward_validation_interpretation", ""),
}

monitor_summary = monitor.get("summary") if monitor else None
if monitor_summary:
    summary["monitor"] = {
        "current_regime": monitor_summary.get("current_label"),
        "current_confidence": monitor_summary.get("current_confidence"),
        "current_run_start": monitor_summary.get("current_run_start"),
        "current_run_length": monitor_summary.get("current_run_length"),
        "observed_average_duration": monitor_summary.get("observed_average_duration"),
        "blended_total_duration": monitor_summary.get("blended_total_duration"),
        "estimated_remaining_steps": monitor_summary.get("estimated_remaining_steps"),
        "likely_end_date": monitor_summary.get("likely_end_date"),
        "probability_end_10": monitor_summary.get("probability_end_10"),
        "probability_end_20": monitor_summary.get("probability_end_20"),
        "probability_end_30": monitor_summary.get("probability_end_30"),
    }
phase_monitor_summary = monitor.get("phase_summary") if monitor else None
if phase_monitor_summary:
    summary["monitor_phase"] = {
        "current_phase": phase_monitor_summary.get("current_phase"),
        "current_run_start": phase_monitor_summary.get("current_run_start"),
        "current_run_length": phase_monitor_summary.get("current_run_length"),
        "observed_average_duration": phase_monitor_summary.get("observed_average_duration"),
        "blended_total_duration": phase_monitor_summary.get("blended_total_duration"),
        "estimated_remaining_steps": phase_monitor_summary.get("estimated_remaining_steps"),
        "likely_end_date": phase_monitor_summary.get("likely_end_date"),
        "probability_end_10": phase_monitor_summary.get("probability_end_10"),
        "probability_end_20": phase_monitor_summary.get("probability_end_20"),
        "probability_end_30": phase_monitor_summary.get("probability_end_30"),
    }

labels = result["regime_labels"]
robust = result["robustness"]
report_lines = [
    "# Regime-Aware Forecasting Report",
    "",
    "## Dataset",
    f"- **Ticker:** {st.session_state.get('ticker', 'SPY')}",
    f"- **States:** {result['n_states']}",
    f"- **Folds:** {result['n_folds']}",
    f"- **Duration:** {result['duration_secs']}s",
    f"- **Out-of-sample coverage:** {result.get('coverage_pct', 0):.1f}%",
    "",
    "## Regimes",
]
for state_id, label in sorted(labels.items(), key=lambda x: int(x[0])):
    report_lines.append(f"- State {state_id}: **{label}**")

report_lines.extend(
    [
        "",
        "## Overlay Interpretation",
        f"- {result.get('overlay_note', '')}",
        f"- {result.get('smoothing_note', '')}",
        f"- {result.get('phase_note', '')}",
        "",
        "## Market Phase Layer",
    ]
)
for phase, description in result.get("phase_descriptions", {}).items():
    report_lines.append(f"- **{phase}**: {description}")

report_lines.extend(
    [
        "",
        "## Robustness",
        f"- Stable regimes: {robust['stable_regimes']} / {result['n_states']}",
        f"- Average test persistence: {robust['avg_test_persistence']}",
        f"- {robust['interpretation']}",
    ]
)

if result.get("forward_validation"):
    report_lines.extend(
        [
            "",
            "## Forward Regime Validation",
            f"- {result.get('forward_validation_interpretation', '')}",
        ]
    )
    for row in result["forward_validation"]:
        fwd_7 = f"{row['avg_fwd_return_7']:.2%}" if row.get("avg_fwd_return_7") is not None else "N/A"
        fwd_14 = f"{row['avg_fwd_return_14']:.2%}" if row.get("avg_fwd_return_14") is not None else "N/A"
        fwd_30 = f"{row['avg_fwd_return_30']:.2%}" if row.get("avg_fwd_return_30") is not None else "N/A"
        fwd_vol = (
            f"{row['avg_forward_realized_vol_30d']:.2%}"
            if row.get("avg_forward_realized_vol_30d") is not None
            else "N/A"
        )
        fwd_dd = (
            f"{row['avg_forward_max_drawdown_30d']:.2%}"
            if row.get("avg_forward_max_drawdown_30d") is not None
            else "N/A"
        )
        dd_hit = (
            f"{row['drawdown_hit_rate_30d']:.1%}"
            if row.get("drawdown_hit_rate_30d") is not None
            else "N/A"
        )
        report_lines.append(
            f"- **{row['label']}**: avg duration {row['avg_duration']:.1f} steps, "
            f"fwd 7d {fwd_7}, fwd 14d {fwd_14}, fwd 30d {fwd_30}, "
            f"fwd vol 30d {fwd_vol}, avg forward max drawdown 30d {fwd_dd}, "
            f"10% drawdown hit rate {dd_hit}."
        )

if monitor_summary:
    report_lines.extend(
        [
            "",
            "## Current Regime Monitor",
            f"- Current regime: **{monitor_summary.get('current_label', 'N/A')}**",
            f"- Current confidence: {monitor_summary.get('current_confidence', 0):.1%}",
            f"- In regime since: {monitor_summary.get('current_run_start', 'N/A')}",
            f"- Time spent in regime: {monitor_summary.get('current_run_length', 0)} modeled steps",
            f"- Typical regime length: {monitor_summary.get('blended_total_duration', 0):.1f} modeled steps",
            f"- Estimated remaining: {monitor_summary.get('estimated_remaining_steps', 0):.1f} modeled steps",
            f"- Likely regime end date: {monitor_summary.get('likely_end_date', 'N/A')}",
            f"- Change risk within 10 steps: {monitor_summary.get('probability_end_10', 0):.1%}",
            f"- Change risk within 20 steps: {monitor_summary.get('probability_end_20', 0):.1%}",
            f"- Change risk within 30 steps: {monitor_summary.get('probability_end_30', 0):.1%}",
        ]
    )

if phase_monitor_summary:
    report_lines.extend(
        [
            "",
            "## Current Market Phase Monitor",
            f"- Current market phase: **{phase_monitor_summary.get('current_phase', 'N/A')}**",
            f"- In phase since: {phase_monitor_summary.get('current_run_start', 'N/A')}",
            f"- Time spent in phase: {phase_monitor_summary.get('current_run_length', 0)} modeled steps",
            f"- Typical phase length: {phase_monitor_summary.get('blended_total_duration', 0):.1f} modeled steps",
            f"- Estimated remaining: {phase_monitor_summary.get('estimated_remaining_steps', 0):.1f} modeled steps",
            f"- Likely phase end date: {phase_monitor_summary.get('likely_end_date', 'N/A')}",
            f"- Phase change risk within 10 steps: {phase_monitor_summary.get('probability_end_10', 0):.1%}",
            f"- Phase change risk within 20 steps: {phase_monitor_summary.get('probability_end_20', 0):.1%}",
            f"- Phase change risk within 30 steps: {phase_monitor_summary.get('probability_end_30', 0):.1%}",
        ]
    )

report_lines.extend(
    [
        "",
        "## Caveats",
        "- Regime detection is unsupervised and the labels are statistical interpretations rather than ground truth.",
        "- The walk-forward overlay only colours dates that were genuinely scored out of sample.",
        "- HMM results remain sensitive to the number of states, feature set, and windowing choices.",
    ]
)
report = "\n".join(report_lines)

top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)
with top_left:
    st.download_button(
        "Fold Metrics CSV",
        fold_metrics_csv,
        "fold_metrics.csv",
        "text/csv",
        use_container_width=True,
        help="One row per successful walk-forward fold.",
    )
with top_right:
    st.download_button(
        "State Assignments CSV",
        states_csv,
        "state_assignments.csv",
        "text/csv",
        use_container_width=True,
        help="Out-of-sample date-by-date state assignments.",
    )
with bottom_left:
    st.download_button(
        "Summary JSON",
        json.dumps(summary, indent=2, default=str),
        "summary.json",
        "application/json",
        use_container_width=True,
        help="Dashboard summary plus monitor state if available.",
    )
with bottom_right:
    st.download_button(
        "Markdown Report",
        report,
        "report.md",
        "text/markdown",
        use_container_width=True,
        help="Portable narrative report for review or sharing.",
    )

st.markdown('<div class="section-gap-md"></div>', unsafe_allow_html=True)

with st.expander("Preview Markdown Report", expanded=False):
    st.markdown(report)

render_footer()
