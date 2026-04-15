"""Plotly chart builders — theme-aware (works in both light and dark mode)."""

import numpy as np
import plotly.graph_objects as go

COLORS = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]

# Use plotly's default template so Streamlit's theme controls the background
def _template():
    import streamlit as st
    return st.session_state.get("plotly_template", "plotly")


def price_regime_chart(dates, close, states, labels):
    fig = go.Figure()
    if not close:
        return fig
    import streamlit as st
    line_color = "#aaaaaa" if st.session_state.get("theme") == "dark" else "#555555"
    fig.add_trace(go.Scatter(x=dates, y=close, mode="lines", name="Close", line=dict(color=line_color, width=1.5)))
    for s in sorted(set(states)):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        color = COLORS[s % len(COLORS)]
        sd, sc = [], []
        shown = False
        for i, st in enumerate(states):
            if st == s and i < len(close):
                sd.append(dates[i])
                sc.append(close[i])
            else:
                if sd:
                    fig.add_trace(go.Scatter(x=sd, y=sc, mode="markers", marker=dict(color=color, size=3),
                                            name=label, showlegend=not shown, legendgroup=str(s)))
                    shown = True
                    sd, sc = [], []
        if sd:
            fig.add_trace(go.Scatter(x=sd, y=sc, mode="markers", marker=dict(color=color, size=3),
                                    name=label, showlegend=not shown, legendgroup=str(s)))
    fig.update_layout(title="Price with Regime Overlay", xaxis_title="Date", yaxis_title="Price",
                      template=_template(), height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02),
                      plot_bgcolor="rgba(0,0,0,0)")
    return fig


def transition_heatmap(matrix, labels):
    n = len(matrix)
    ticks = [labels.get(i, labels.get(str(i), f"State {i}")) for i in range(n)]
    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=ticks, y=ticks, colorscale="Blues",
        text=[[f"{v:.2f}" for v in row] for row in matrix],
        texttemplate="%{text}", textfont=dict(size=14, color="#333"),
    ))
    fig.update_layout(title="Transition Matrix", xaxis_title="To", yaxis_title="From",
                      template=_template(), height=400)
    return fig


def occupancy_bar(occupancy, labels):
    names = [labels.get(k, labels.get(str(k), f"State {k}")) for k in occupancy]
    fig = go.Figure(data=go.Bar(x=names, y=list(occupancy.values()),
                                marker_color=[COLORS[i % len(COLORS)] for i in range(len(occupancy))]))
    fig.update_layout(title="State Occupancy", yaxis=dict(range=[0, 1]), template=_template(), height=350)
    return fig


def return_dist_chart(returns, states, labels):
    fig = go.Figure()
    arr_r, arr_s = np.array(returns), np.array(states)
    for i, s in enumerate(sorted(set(states))):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        fig.add_trace(go.Histogram(x=arr_r[arr_s == s], name=label, opacity=0.7,
                                   marker_color=COLORS[i % len(COLORS)], nbinsx=50))
    fig.update_layout(title="Return Distributions by Regime", barmode="overlay", template=_template(), height=400)
    return fig


def fold_timeline(folds):
    fig = go.Figure()
    for f in folds:
        fid = f["fold_id"]
        fig.add_trace(go.Scatter(x=[f["train_start"], f["train_end"]], y=[fid, fid],
                                 mode="lines", line=dict(color="#3498db", width=8),
                                 name="Train" if fid == 0 else None, showlegend=fid == 0, legendgroup="train"))
        fig.add_trace(go.Scatter(x=[f["test_start"], f["test_end"]], y=[fid, fid],
                                 mode="lines", line=dict(color="#e74c3c", width=8),
                                 name="Test" if fid == 0 else None, showlegend=fid == 0, legendgroup="test"))
    fig.update_layout(title="Fold Timeline", xaxis_title="Date", yaxis_title="Fold",
                      template=_template(), height=max(300, len(folds) * 30 + 100))
    return fig


def regime_probability_chart(dates, probabilities, labels, states, alerts=None):
    """Stacked area chart of regime probabilities over time with optional alert markers."""
    fig = go.Figure()
    probs = np.array(probabilities)
    n_states = probs.shape[1]

    for s in range(n_states):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        fig.add_trace(go.Scatter(
            x=dates, y=probs[:, s], mode="lines", name=label,
            line=dict(color=COLORS[s % len(COLORS)], width=1),
            fill="tonexty" if s > 0 else "tozeroy",
            stackgroup="probs",
        ))

    if alerts:
        alert_dates = [a["date"] for a in alerts]
        alert_y = [1.02] * len(alerts)
        alert_text = [f"{a['severity']}: {a['current_regime']} ({a['confidence']:.0%}) → {a['alternative_regime']} ({a['alt_probability']:.0%})" for a in alerts]
        fig.add_trace(go.Scatter(
            x=alert_dates, y=alert_y, mode="markers", name="Transition Alert",
            marker=dict(symbol="triangle-down", size=10, color="#e74c3c"),
            text=alert_text, hoverinfo="text",
        ))

    fig.update_layout(
        title="Regime Probabilities Over Time",
        xaxis_title="Date", yaxis_title="Probability",
        yaxis=dict(range=[0, 1.05]),
        template=_template(), height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def current_regime_gauge(label, confidence, color_idx=0):
    """Gauge chart showing current regime confidence."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        title={"text": f"Current: {label}"},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS[color_idx % len(COLORS)]},
            "steps": [
                {"range": [0, 40], "color": "rgba(231,76,60,0.2)"},
                {"range": [40, 60], "color": "rgba(243,156,18,0.2)"},
                {"range": [60, 100], "color": "rgba(46,204,113,0.2)"},
            ],
            "threshold": {
                "line": {"color": "#e74c3c", "width": 3},
                "thickness": 0.8,
                "value": 60,
            },
        },
    ))
    fig.update_layout(template=_template(), height=280)
    return fig


def forward_projection_chart(projection_df, labels):
    """Line chart of projected regime probabilities over N days."""
    fig = go.Figure()
    cols = [c for c in projection_df.columns if c != "day"]
    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=projection_df["day"], y=projection_df[col],
            mode="lines+markers", name=col,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            marker=dict(size=4),
        ))
    fig.update_layout(
        title="Forward Regime Probability Projection",
        xaxis_title="Days Ahead", yaxis_title="Probability",
        yaxis=dict(range=[0, 1]),
        template=_template(), height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def price_with_probabilities(dates, close, probabilities, labels):
    """Price chart with regime probability shading underneath."""
    from plotly.subplots import make_subplots
    import streamlit as st

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4],
                        vertical_spacing=0.05)
    line_color = "#aaaaaa" if st.session_state.get("theme") == "dark" else "#555555"
    fig.add_trace(go.Scatter(x=dates, y=close, mode="lines", name="Close",
                             line=dict(color=line_color, width=1.5)), row=1, col=1)

    probs = np.array(probabilities)
    n_states = probs.shape[1]
    for s in range(n_states):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        fig.add_trace(go.Scatter(
            x=dates, y=probs[:, s], mode="lines", name=label,
            line=dict(color=COLORS[s % len(COLORS)], width=1),
            fill="tonexty" if s > 0 else "tozeroy",
            stackgroup="probs",
        ), row=2, col=1)

    fig.update_layout(
        title="Price & Regime Probabilities",
        template=_template(), height=650,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Probability", range=[0, 1], row=2, col=1)
    return fig


def drawdown_chart(dates, returns):
    r = np.array(returns)
    cum = np.cumsum(r)
    dd = cum - np.maximum.accumulate(cum)
    fig = go.Figure(data=go.Scatter(x=dates, y=dd.tolist(), fill="tozeroy", line=dict(color="#e74c3c", width=1)))
    fig.update_layout(title="Cumulative Drawdown", template=_template(), height=350)
    return fig
