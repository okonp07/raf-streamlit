"""Plotly chart builders — premium dashboard styling with consistent design system."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from components.design import (
    REGIME_PALETTE, FONT_FAMILY,
    TRAIN_COLOR, TEST_COLOR, DRAWDOWN_COLOR, DRAWDOWN_FILL,
    CHART_HEIGHT_MAIN, CHART_HEIGHT_HALF, CHART_HEIGHT_SMALL,
    CHART_HEIGHT_GAUGE, CHART_HEIGHT_DUAL,
    CHART_MARGIN, CHART_MARGIN_COMPACT,
    TITLE_SIZE, SUBTITLE_SIZE, AXIS_LABEL_SIZE, TICK_SIZE,
    ANNOTATION_SIZE, LEGEND_SIZE,
    base_layout, get_colors, regime_color, regime_color_alpha, is_dark,
)


def _label(labels, s):
    """Resolve a regime label from either int or str key."""
    return labels.get(s, labels.get(str(s), f"State {s}"))


# ═══════════════════════════════════════════════════════════════════════════
#  1) PRICE WITH REGIME OVERLAY
# ═══════════════════════════════════════════════════════════════════════════

def price_regime_chart(dates, close, states, labels):
    fig = go.Figure()
    if not close:
        return fig

    c = get_colors()
    y_min, y_max = min(close), max(close)
    y_pad = (y_max - y_min) * 0.03

    # Add colored background bands for regime periods (grouped consecutive)
    unique_states = sorted(set(states))
    legend_shown = {s: False for s in unique_states}

    i = 0
    while i < len(states):
        s = states[i]
        j = i
        while j < len(states) and states[j] == s:
            j += 1
        # Band from dates[i] to dates[j-1]
        label = _label(labels, s)
        color = regime_color(s)
        fig.add_vrect(
            x0=dates[i], x1=dates[j - 1],
            fillcolor=regime_color_alpha(s, 0.12),
            layer="below", line_width=0,
        )
        # Invisible trace for legend entry
        if not legend_shown[s]:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=10, color=color, symbol="square"),
                name=label, legendgroup=str(s),
            ))
            legend_shown[s] = True
        i = j

    # Base price line — clean and prominent
    fig.add_trace(go.Scatter(
        x=dates, y=close, mode="lines", name="Close",
        line=dict(color=c["price_line"], width=2),
        showlegend=False,
        hovertemplate="<b>%{x}</b><br>Price: $%{y:,.2f}<extra></extra>",
    ))

    layout = base_layout(
        title="Price with Regime Overlay",
        subtitle="Close price with colored regime bands",
        height=CHART_HEIGHT_MAIN,
    )
    layout["yaxis"]["title_text"] = "Price ($)"
    layout["yaxis"]["range"] = [y_min - y_pad, y_max + y_pad]
    layout["xaxis"]["title_text"] = ""
    layout["hovermode"] = "x unified"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  2) TRANSITION MATRIX HEATMAP
# ═══════════════════════════════════════════════════════════════════════════

def transition_heatmap(matrix, labels):
    n = len(matrix)
    ticks = [_label(labels, i) for i in range(n)]
    c = get_colors()

    # Custom colorscale — refined blue
    colorscale = [
        [0.0, "rgba(42, 157, 143, 0.05)"],
        [0.3, "rgba(42, 157, 143, 0.25)"],
        [0.6, "rgba(42, 157, 143, 0.55)"],
        [1.0, "rgba(42, 157, 143, 0.95)"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=ticks, y=ticks,
        colorscale=colorscale,
        text=[[f"{v:.2f}" for v in row] for row in matrix],
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=14, family=FONT_FAMILY, color=c["text"]),
        hovertemplate="From: <b>%{y}</b><br>To: <b>%{x}</b><br>Probability: <b>%{z:.3f}</b><extra></extra>",
        showscale=False,
        xgap=3,
        ygap=3,
    ))

    layout = base_layout(
        title="Transition Matrix",
        subtitle="Probability of switching between regimes",
        height=CHART_HEIGHT_HALF,
        margin=CHART_MARGIN_COMPACT,
    )
    layout["xaxis"]["title_text"] = "To"
    layout["yaxis"]["title_text"] = "From"
    layout["yaxis"]["autorange"] = "reversed"
    layout["hovermode"] = "closest"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  3) STATE OCCUPANCY BAR
# ═══════════════════════════════════════════════════════════════════════════

def occupancy_bar(occupancy, labels):
    names = [_label(labels, k) for k in occupancy]
    values = list(occupancy.values())
    colors = [regime_color(i) for i in range(len(occupancy))]
    c = get_colors()

    fig = go.Figure()
    for i, (name, val, color) in enumerate(zip(names, values, colors)):
        fig.add_trace(go.Bar(
            x=[name], y=[val], name=name,
            marker=dict(
                color=color,
                line=dict(width=0),
                opacity=0.85,
            ),
            text=[f"{val:.1%}"],
            textposition="outside",
            textfont=dict(size=ANNOTATION_SIZE, color=c["text"], family=FONT_FAMILY),
            hovertemplate=f"<b>{name}</b><br>Occupancy: {val:.1%}<extra></extra>",
            showlegend=False,
        ))

    layout = base_layout(
        title="State Occupancy",
        subtitle="Fraction of time spent in each regime",
        height=CHART_HEIGHT_HALF,
        margin=CHART_MARGIN_COMPACT,
    )
    layout["yaxis"]["range"] = [0, max(values) * 1.25 if values else 1]
    layout["yaxis"]["title_text"] = "Proportion"
    layout["bargap"] = 0.35
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  4) RETURN DISTRIBUTIONS BY REGIME
# ═══════════════════════════════════════════════════════════════════════════

def return_dist_chart(returns, states, labels):
    fig = go.Figure()
    arr_r, arr_s = np.array(returns), np.array(states)

    for i, s in enumerate(sorted(set(states))):
        label = _label(labels, s)
        color = regime_color(s)
        r = arr_r[arr_s == s]

        fig.add_trace(go.Histogram(
            x=r, name=label,
            marker=dict(color=regime_color_alpha(s, 0.5), line=dict(color=color, width=1)),
            nbinsx=60,
            hovertemplate=f"<b>{label}</b><br>Return: %{{x:.4f}}<br>Count: %{{y}}<extra></extra>",
        ))

    layout = base_layout(
        title="Return Distributions by Regime",
        subtitle="Overlaid histograms showing regime-specific return profiles",
        height=CHART_HEIGHT_HALF,
    )
    layout["barmode"] = "overlay"
    layout["xaxis"]["title_text"] = "Log Return"
    layout["yaxis"]["title_text"] = "Frequency"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  5) FOLD TIMELINE
# ═══════════════════════════════════════════════════════════════════════════

def fold_timeline(folds):
    """Gantt-style fold timeline using horizontal bars for train/test periods."""
    import pandas as pd

    c = get_colors()
    tasks = []
    for f in folds:
        fid = f["fold_id"]
        tasks.append(dict(Fold=f"Fold {fid}", Start=f["train_start"], End=f["train_end"], Phase="Train"))
        tasks.append(dict(Fold=f"Fold {fid}", Start=f["test_start"], End=f["test_end"], Phase="Test"))

    fig = go.Figure()

    # Render train then test so test overlaps visually
    for phase, color, opacity in [("Train", TRAIN_COLOR, 0.75), ("Test", TEST_COLOR, 0.9)]:
        phase_tasks = [t for t in tasks if t["Phase"] == phase]
        for t in phase_tasks:
            fid_num = int(t["Fold"].split()[-1])
            fig.add_trace(go.Scatter(
                x=[t["Start"], t["End"]], y=[fid_num, fid_num],
                mode="lines",
                line=dict(color=color, width=18),
                opacity=opacity,
                name=phase if fid_num == 0 else None,
                showlegend=fid_num == 0,
                legendgroup=phase,
                hovertemplate=(
                    f"<b>{t['Fold']} — {phase}</b><br>"
                    f"{t['Start']} → {t['End']}<extra></extra>"
                ),
            ))

    n = len(folds)
    layout = base_layout(
        title="Walk-Forward Fold Timeline",
        subtitle=f"{n} folds — train (blue) and test (coral) windows",
        height=max(280, n * 40 + 100),
    )
    layout["xaxis"]["title_text"] = ""
    layout["yaxis"]["title_text"] = ""
    layout["yaxis"]["dtick"] = 1
    layout["yaxis"]["tickprefix"] = "Fold "
    layout["hovermode"] = "closest"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  6) CUMULATIVE DRAWDOWN
# ═══════════════════════════════════════════════════════════════════════════

def drawdown_chart(dates, returns):
    r = np.array(returns)
    cum = np.cumsum(r)
    dd = cum - np.maximum.accumulate(cum)
    c = get_colors()

    fig = go.Figure()

    # Fill area
    fig.add_trace(go.Scatter(
        x=dates, y=dd.tolist(),
        fill="tozeroy",
        fillcolor=DRAWDOWN_FILL,
        line=dict(color=DRAWDOWN_COLOR, width=1.5),
        name="Drawdown",
        hovertemplate="<b>%{x}</b><br>Drawdown: %{y:.4f}<extra></extra>",
    ))

    # Zero baseline
    fig.add_hline(y=0, line_dash="dot", line_color=c["zero_line"], line_width=1)

    # Annotate max drawdown
    if len(dd) > 0:
        min_idx = int(np.argmin(dd))
        min_val = dd[min_idx]
        fig.add_annotation(
            x=dates[min_idx], y=min_val,
            text=f"Max: {min_val:.4f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowcolor=DRAWDOWN_COLOR,
            font=dict(size=ANNOTATION_SIZE, color=DRAWDOWN_COLOR, family=FONT_FAMILY),
            bgcolor="rgba(0,0,0,0.5)" if is_dark() else "rgba(255,255,255,0.8)",
            borderpad=4,
        )

    layout = base_layout(
        title="Cumulative Drawdown",
        subtitle="Underwater equity curve from cumulative log returns",
        height=CHART_HEIGHT_HALF,
    )
    layout["yaxis"]["title_text"] = "Drawdown"
    layout["xaxis"]["title_text"] = "Date"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  7) REGIME PROBABILITY TIMELINE (Monitor page)
# ═══════════════════════════════════════════════════════════════════════════

def regime_probability_chart(dates, probabilities, labels, states, alerts=None):
    fig = go.Figure()
    probs = np.array(probabilities)
    n_states = probs.shape[1]

    for s in range(n_states):
        label = _label(labels, s)
        color = regime_color(s)
        fig.add_trace(go.Scatter(
            x=dates, y=probs[:, s], mode="lines", name=label,
            line=dict(color=color, width=1),
            fill="tonexty" if s > 0 else "tozeroy",
            fillcolor=regime_color_alpha(s, 0.3),
            stackgroup="probs",
            hovertemplate=f"<b>{label}</b><br>%{{x}}<br>Prob: %{{y:.1%}}<extra></extra>",
        ))

    if alerts:
        alert_dates = [a["date"] for a in alerts]
        alert_y = [1.02] * len(alerts)
        alert_text = [
            f"<b>{a['severity']}</b>: {a['current_regime']} ({a['confidence']:.0%}) → {a['alternative_regime']} ({a['alt_probability']:.0%})"
            for a in alerts
        ]
        fig.add_trace(go.Scatter(
            x=alert_dates, y=alert_y, mode="markers", name="Alert",
            marker=dict(symbol="triangle-down", size=10, color="#e76f51",
                        line=dict(width=1, color="#c0392b")),
            text=alert_text, hoverinfo="text",
        ))

    layout = base_layout(
        title="Regime Probabilities Over Time",
        subtitle="Model confidence in each regime state across the observation period",
        height=CHART_HEIGHT_MAIN,
    )
    layout["yaxis"]["range"] = [0, 1.05]
    layout["yaxis"]["title_text"] = "Probability"
    layout["xaxis"]["title_text"] = "Date"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  8) CURRENT REGIME GAUGE (Monitor page)
# ═══════════════════════════════════════════════════════════════════════════

def current_regime_gauge(label, confidence, color_idx=0):
    c = get_colors()
    color = regime_color(color_idx)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        title={"text": f"<b>{label}</b>", "font": {"size": 13, "family": FONT_FAMILY, "color": c["text"]}},
        number={"suffix": "%", "font": {"size": 28, "family": FONT_FAMILY, "color": c["text"]}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 9, "color": c["text_secondary"]}},
            "bar": {"color": color, "thickness": 0.75},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": regime_color_alpha(1, 0.1)},
                {"range": [40, 60], "color": regime_color_alpha(3, 0.1)},
                {"range": [60, 100], "color": regime_color_alpha(0, 0.1)},
            ],
            "threshold": {
                "line": {"color": "#e76f51", "width": 2},
                "thickness": 0.8,
                "value": 60,
            },
        },
    ))
    fig.update_layout(
        height=CHART_HEIGHT_GAUGE,
        margin=dict(l=24, r=24, t=40, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  9) FORWARD PROJECTION (Monitor page)
# ═══════════════════════════════════════════════════════════════════════════

def forward_projection_chart(projection_df, labels):
    fig = go.Figure()
    cols = [c for c in projection_df.columns if c != "day"]
    for i, col in enumerate(cols):
        color = regime_color(i)
        fig.add_trace(go.Scatter(
            x=projection_df["day"], y=projection_df[col],
            mode="lines+markers", name=col,
            line=dict(color=color, width=2.5),
            marker=dict(size=4, color=color, line=dict(width=0)),
            hovertemplate=f"<b>{col}</b><br>Day %{{x}}<br>Prob: %{{y:.1%}}<extra></extra>",
        ))

    layout = base_layout(
        title="Forward Regime Probability Projection",
        subtitle="Projected regime evolution using the learned transition matrix",
        height=CHART_HEIGHT_HALF,
    )
    layout["yaxis"]["range"] = [0, 1]
    layout["yaxis"]["title_text"] = "Probability"
    layout["xaxis"]["title_text"] = "Days Ahead"
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 10) PRICE WITH PROBABILITIES (Monitor page — dual panel)
# ═══════════════════════════════════════════════════════════════════════════

def price_with_probabilities(dates, close, probabilities, labels):
    c = get_colors()
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.06,
    )

    # Price line
    fig.add_trace(go.Scatter(
        x=dates, y=close, mode="lines", name="Close",
        line=dict(color=c["price_line"], width=1.5),
        hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # Probability areas
    probs = np.array(probabilities)
    n_states = probs.shape[1]
    for s in range(n_states):
        label = _label(labels, s)
        color = regime_color(s)
        fig.add_trace(go.Scatter(
            x=dates, y=probs[:, s], mode="lines", name=label,
            line=dict(color=color, width=1),
            fill="tonexty" if s > 0 else "tozeroy",
            fillcolor=regime_color_alpha(s, 0.3),
            stackgroup="probs",
            hovertemplate=f"<b>{label}</b>: %{{y:.1%}}<extra></extra>",
        ), row=2, col=1)

    layout = base_layout(
        title="Price & Regime Probabilities",
        subtitle="Close price with underlying regime probability decomposition",
        height=CHART_HEIGHT_DUAL,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Price", row=1, col=1,
                     gridcolor=c["grid"], tickfont=dict(size=TICK_SIZE, color=c["text_secondary"]))
    fig.update_yaxes(title_text="Probability", range=[0, 1], row=2, col=1,
                     gridcolor=c["grid"], tickfont=dict(size=TICK_SIZE, color=c["text_secondary"]))
    fig.update_xaxes(gridcolor=c["grid"], row=1, col=1)
    fig.update_xaxes(gridcolor=c["grid"], row=2, col=1)
    return fig
