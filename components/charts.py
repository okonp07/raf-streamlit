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

    # Base price line — subtle and elegant
    fig.add_trace(go.Scatter(
        x=dates, y=close, mode="lines", name="Close",
        line=dict(color=c["price_line"], width=1.5),
        hovertemplate="<b>%{x}</b><br>Price: $%{y:,.2f}<extra></extra>",
    ))

    # Regime colored segments as background bands (vertical spans)
    # Group consecutive same-state periods for cleaner rendering
    for s in sorted(set(states)):
        label = _label(labels, s)
        color = regime_color(s)
        sd, sc = [], []
        shown = False
        for i, state_val in enumerate(states):
            if state_val == s and i < len(close):
                sd.append(dates[i])
                sc.append(close[i])
            else:
                if sd:
                    fig.add_trace(go.Scatter(
                        x=sd, y=sc, mode="markers",
                        marker=dict(color=color, size=5, opacity=0.8,
                                    line=dict(width=0)),
                        name=label, showlegend=not shown,
                        legendgroup=str(s),
                        hovertemplate=f"<b>{label}</b><br>%{{x}}<br>${{y:,.2f}}<extra></extra>",
                    ))
                    shown = True
                    sd, sc = [], []
        if sd:
            fig.add_trace(go.Scatter(
                x=sd, y=sc, mode="markers",
                marker=dict(color=color, size=5, opacity=0.8,
                            line=dict(width=0)),
                name=label, showlegend=not shown,
                legendgroup=str(s),
                hovertemplate=f"<b>{label}</b><br>%{{x}}<br>${{y:,.2f}}<extra></extra>",
            ))

    layout = base_layout(
        title="Price with Regime Overlay",
        subtitle="Close price colored by detected market regime",
        height=CHART_HEIGHT_MAIN,
    )
    layout["yaxis"]["title_text"] = "Price"
    layout["xaxis"]["title_text"] = "Date"
    layout["hovermode"] = "closest"
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
    fig = go.Figure()
    c = get_colors()

    for f in folds:
        fid = f["fold_id"]
        # Train bar
        fig.add_trace(go.Scatter(
            x=[f["train_start"], f["train_end"]], y=[fid, fid],
            mode="lines",
            line=dict(color=TRAIN_COLOR, width=14),
            name="Train" if fid == 0 else None,
            showlegend=fid == 0,
            legendgroup="train",
            hovertemplate=f"<b>Fold {fid} — Train</b><br>{f['train_start']} → {f['train_end']}<extra></extra>",
        ))
        # Test bar
        fig.add_trace(go.Scatter(
            x=[f["test_start"], f["test_end"]], y=[fid, fid],
            mode="lines",
            line=dict(color=TEST_COLOR, width=14),
            name="Test" if fid == 0 else None,
            showlegend=fid == 0,
            legendgroup="test",
            hovertemplate=f"<b>Fold {fid} — Test</b><br>{f['test_start']} → {f['test_end']}<extra></extra>",
        ))

    layout = base_layout(
        title="Fold Timeline",
        subtitle="Walk-forward train/test windows across time",
        height=max(CHART_HEIGHT_SMALL, len(folds) * 36 + 100),
    )
    layout["xaxis"]["title_text"] = "Date"
    layout["yaxis"]["title_text"] = "Fold"
    layout["yaxis"]["dtick"] = 1
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
