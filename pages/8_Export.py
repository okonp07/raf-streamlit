"""Export page — download CSV, JSON, and report with premium layout."""

import json
import streamlit as st
import pandas as pd
from components.theme import apply_theme, render_footer, render_toggle
from components.design import is_dark, FONT_FAMILY

render_toggle()
apply_theme()

st.header("Export & Report")

result = st.session_state.get("result")
if not result:
    st.warning("No results to export. Run an analysis first.")
    st.stop()

# ─── Export cards ─────────────────────────────────────────────────────────
dark = is_dark()
card_bg = "rgba(15, 23, 42, 0.5)" if dark else "rgba(255, 255, 255, 0.75)"
card_border = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.06)"
text_color = "#e2e8f0" if dark else "#1a202c"
sub_color = "#94a3b8" if dark else "#64748b"

st.markdown(f"""
<style>
    .export-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 8px;
    }}
    .export-card h4 {{
        font-family: {FONT_FAMILY};
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 6px;
        color: {text_color};
    }}
    .export-card p {{
        font-family: {FONT_FAMILY};
        font-size: 0.82rem;
        color: {sub_color};
        margin-bottom: 16px;
    }}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Fold metrics CSV
with col1:
    st.markdown('<div class="export-card"><h4>Fold Metrics</h4><p>Persistence, separation, AIC/BIC per fold</p></div>', unsafe_allow_html=True)
    rows = []
    for f in result["folds"]:
        row = {"fold_id": f["fold_id"], "train_start": f["train_start"], "train_end": f["train_end"],
               "test_start": f["test_start"], "test_end": f["test_end"],
               "train_persistence": f["train_persistence"], "test_persistence": f["test_persistence"],
               "state_separation": f["state_separation"], "log_likelihood": f.get("log_likelihood"),
               "aic": f.get("aic"), "bic": f.get("bic")}
        for k, v in f["test_occupancy"].items():
            row[f"occ_state_{k}"] = v
        rows.append(row)
    csv = pd.DataFrame(rows).to_csv(index=False)
    st.download_button("Download CSV", csv, "fold_metrics.csv", "text/csv", use_container_width=True)

# State assignments
with col2:
    st.markdown('<div class="export-card"><h4>State Assignments</h4><p>Date-level regime labels across all folds</p></div>', unsafe_allow_html=True)
    assign_rows = []
    for f in result["folds"]:
        for dt, st_val in zip(f["test_dates"], f["test_states"]):
            assign_rows.append({"date": dt, "fold_id": f["fold_id"], "state": st_val,
                                "label": f["regime_labels"].get(st_val, f["regime_labels"].get(str(st_val), f"S{st_val}"))})
    states_csv = pd.DataFrame(assign_rows).to_csv(index=False)
    st.download_button("Download States", states_csv, "state_assignments.csv", "text/csv", use_container_width=True)

# Summary JSON
with col3:
    st.markdown('<div class="export-card"><h4>Summary JSON</h4><p>Robustness metrics and regime labels</p></div>', unsafe_allow_html=True)
    summary = {"n_folds": result["n_folds"], "n_states": result["n_states"],
               "duration_secs": result["duration_secs"], "regime_labels": result["regime_labels"],
               "robustness": result["robustness"]}
    st.download_button("Download JSON", json.dumps(summary, indent=2, default=str), "summary.json", "application/json", use_container_width=True)

st.markdown("")
st.divider()
st.markdown("")

# ─── Generated Report ────────────────────────────────────────────────────
st.markdown("##### Analysis Report")
labels = result["regime_labels"]
robust = result["robustness"]
lines = [
    f"# Regime-Aware Forecasting Report\n",
    f"## Dataset\n- **Ticker:** {st.session_state.get('ticker', 'SPY')}",
    f"- **States:** {result['n_states']}\n- **Folds:** {result['n_folds']}",
    f"- **Duration:** {result['duration_secs']}s\n",
    f"## Regimes",
]
for s, label in sorted(labels.items(), key=lambda x: int(x[0])):
    lines.append(f"- State {s}: **{label}**")
lines.extend([
    f"\n## Robustness",
    f"- Stable: {robust['stable_regimes']} / {result['n_states']}",
    f"- Avg persistence: {robust['avg_test_persistence']}",
    f"- {robust['interpretation']}",
    f"\n## Caveats",
    f"- Regime detection is unsupervised — labels inferred from statistics.",
    f"- HMM assumes Gaussian emissions; real markets have fat tails.",
    f"- Walk-forward reduces but does not eliminate overfitting.",
])
report = "\n".join(lines)

col1, col2 = st.columns([3, 1])
with col2:
    st.download_button("Download Report", report, "report.md", "text/markdown", use_container_width=True)

with st.expander("Preview Report", expanded=False):
    st.markdown(report)

render_footer()
