"""Export page — download CSV, JSON, and report."""

import json
import streamlit as st
import pandas as pd

st.header("Export & Report")

result = st.session_state.get("result")
if not result:
    st.warning("No results to export. Run an analysis first.")
    st.stop()

col1, col2, col3 = st.columns(3)

# Fold metrics CSV
with col1:
    st.subheader("Fold Metrics")
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
    st.download_button("Download CSV", csv, "fold_metrics.csv", "text/csv")

# State assignments
with col2:
    st.subheader("State Assignments")
    assign_rows = []
    for f in result["folds"]:
        for dt, st_val in zip(f["test_dates"], f["test_states"]):
            assign_rows.append({"date": dt, "fold_id": f["fold_id"], "state": st_val,
                                "label": f["regime_labels"].get(st_val, f["regime_labels"].get(str(st_val), f"S{st_val}"))})
    states_csv = pd.DataFrame(assign_rows).to_csv(index=False)
    st.download_button("Download States", states_csv, "state_assignments.csv", "text/csv")

# Summary JSON
with col3:
    st.subheader("Summary JSON")
    summary = {"n_folds": result["n_folds"], "n_states": result["n_states"],
               "duration_secs": result["duration_secs"], "regime_labels": result["regime_labels"],
               "robustness": result["robustness"]}
    st.download_button("Download JSON", json.dumps(summary, indent=2, default=str), "summary.json", "application/json")

st.divider()

# Generate report
st.subheader("Report")
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

st.download_button("Download Report", report, "report.md", "text/markdown")
st.markdown(report)
