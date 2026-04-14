"""Plotly chart builders."""

import numpy as np
import plotly.graph_objects as go

COLORS = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]


def price_regime_chart(dates, close, states, labels):
    fig = go.Figure()
    if not close:
        return fig
    fig.add_trace(go.Scatter(x=dates, y=close, mode="lines", name="Close", line=dict(color="white", width=1)))
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
                      template="plotly_dark", height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig


def transition_heatmap(matrix, labels):
    n = len(matrix)
    ticks = [labels.get(i, labels.get(str(i), f"State {i}")) for i in range(n)]
    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=ticks, y=ticks, colorscale="Blues",
        text=[[f"{v:.2f}" for v in row] for row in matrix],
        texttemplate="%{text}", textfont=dict(size=14),
    ))
    fig.update_layout(title="Transition Matrix", xaxis_title="To", yaxis_title="From",
                      template="plotly_dark", height=400)
    return fig


def occupancy_bar(occupancy, labels):
    names = [labels.get(k, labels.get(str(k), f"State {k}")) for k in occupancy]
    fig = go.Figure(data=go.Bar(x=names, y=list(occupancy.values()),
                                marker_color=[COLORS[i % len(COLORS)] for i in range(len(occupancy))]))
    fig.update_layout(title="State Occupancy", yaxis=dict(range=[0, 1]), template="plotly_dark", height=350)
    return fig


def return_dist_chart(returns, states, labels):
    fig = go.Figure()
    arr_r, arr_s = np.array(returns), np.array(states)
    for i, s in enumerate(sorted(set(states))):
        label = labels.get(s, labels.get(str(s), f"State {s}"))
        fig.add_trace(go.Histogram(x=arr_r[arr_s == s], name=label, opacity=0.7,
                                   marker_color=COLORS[i % len(COLORS)], nbinsx=50))
    fig.update_layout(title="Return Distributions by Regime", barmode="overlay", template="plotly_dark", height=400)
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
                      template="plotly_dark", height=max(300, len(folds) * 30 + 100))
    return fig


def drawdown_chart(dates, returns):
    r = np.array(returns)
    cum = np.cumsum(r)
    dd = cum - np.maximum.accumulate(cum)
    fig = go.Figure(data=go.Scatter(x=dates, y=dd.tolist(), fill="tozeroy", line=dict(color="#e74c3c", width=1)))
    fig.update_layout(title="Cumulative Drawdown", template="plotly_dark", height=350)
    return fig
