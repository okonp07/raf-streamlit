"""Centralized design system — colors, fonts, spacing, and helpers."""

import streamlit as st

# ─── Regime color palette (premium, muted tones) ──────────────────────────
REGIME_COLORS = {
    "bull":       "#2a9d8f",   # refined teal-green
    "transition": "#e9c46a",   # warm gold
    "stress":     "#e76f51",   # muted crimson-coral
    "extra_1":    "#457b9d",   # steel blue
    "extra_2":    "#9b5de5",   # soft purple
    "extra_3":    "#00b4d8",   # cyan accent
}

# Ordered list for state index mapping (works for 2-6 states)
REGIME_PALETTE = [
    "#2a9d8f",  # bull / low vol     — teal-green
    "#e76f51",  # stress / high vol  — crimson-coral
    "#457b9d",  # moderate / blue    — steel blue
    "#e9c46a",  # transition         — warm gold
    "#9b5de5",  # extra              — soft purple
    "#00b4d8",  # extra              — cyan
]

# Semi-transparent versions for fills
REGIME_PALETTE_ALPHA = [c + "33" for c in REGIME_PALETTE]  # ~20% opacity hex

# ─── Supporting colors ────────────────────────────────────────────────────
TRAIN_COLOR = "#457b9d"
TEST_COLOR  = "#e76f51"
DRAWDOWN_COLOR = "#e76f51"
DRAWDOWN_FILL  = "rgba(231, 111, 81, 0.15)"
PRICE_LINE_DARK  = "#a8b2c1"
PRICE_LINE_LIGHT = "#4a5568"
GRID_DARK  = "rgba(255,255,255,0.07)"
GRID_LIGHT = "rgba(0,0,0,0.07)"
ZERO_LINE_DARK  = "rgba(255,255,255,0.15)"
ZERO_LINE_LIGHT = "rgba(0,0,0,0.12)"

# ─── Typography ───────────────────────────────────────────────────────────
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
TITLE_SIZE = 15
SUBTITLE_SIZE = 12
AXIS_LABEL_SIZE = 11
TICK_SIZE = 10
ANNOTATION_SIZE = 11
LEGEND_SIZE = 11

# ─── Chart dimensions ────────────────────────────────────────────────────
CHART_HEIGHT_MAIN = 480
CHART_HEIGHT_HALF = 380
CHART_HEIGHT_SMALL = 320
CHART_HEIGHT_GAUGE = 240
CHART_HEIGHT_DUAL = 620

# ─── Spacing ──────────────────────────────────────────────────────────────
CHART_MARGIN = dict(l=48, r=24, t=56, b=40)
CHART_MARGIN_COMPACT = dict(l=40, r=16, t=48, b=32)


def is_dark():
    return st.session_state.get("theme") == "dark"


def get_colors():
    """Return a dict of context-aware colors."""
    dark = is_dark()
    return {
        "bg": "rgba(0,0,0,0)",
        "paper": "rgba(0,0,0,0)",
        "text": "#e2e8f0" if dark else "#1a202c",
        "text_secondary": "#94a3b8" if dark else "#64748b",
        "grid": GRID_DARK if dark else GRID_LIGHT,
        "zero_line": ZERO_LINE_DARK if dark else ZERO_LINE_LIGHT,
        "price_line": PRICE_LINE_DARK if dark else PRICE_LINE_LIGHT,
        "border": "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.06)",
    }


def base_layout(title="", subtitle="", height=CHART_HEIGHT_MAIN, margin=None):
    """Return a base layout dict for consistent chart styling."""
    c = get_colors()
    template = "plotly_dark" if is_dark() else "plotly"

    layout = dict(
        template=template,
        height=height,
        margin=margin or CHART_MARGIN,
        font=dict(family=FONT_FAMILY, size=TICK_SIZE, color=c["text"]),
        title=dict(
            text=f"<b>{title}</b>" + (f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{c['text_secondary']}'>{subtitle}</span>" if subtitle else ""),
            font=dict(size=TITLE_SIZE, color=c["text"]),
            x=0.0, xanchor="left",
        ) if title else None,
        plot_bgcolor=c["bg"],
        paper_bgcolor=c["paper"],
        xaxis=dict(
            gridcolor=c["grid"],
            zerolinecolor=c["zero_line"],
            tickfont=dict(size=TICK_SIZE, color=c["text_secondary"]),
            title_font=dict(size=AXIS_LABEL_SIZE, color=c["text_secondary"]),
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            gridcolor=c["grid"],
            zerolinecolor=c["zero_line"],
            tickfont=dict(size=TICK_SIZE, color=c["text_secondary"]),
            title_font=dict(size=AXIS_LABEL_SIZE, color=c["text_secondary"]),
            showgrid=True,
            gridwidth=1,
        ),
        legend=dict(
            font=dict(size=LEGEND_SIZE, color=c["text"]),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#1e293b" if is_dark() else "#ffffff",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#e2e8f0" if is_dark() else "#1a202c",
            bordercolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    return layout


def regime_color(state_idx):
    """Get regime color by state index."""
    return REGIME_PALETTE[state_idx % len(REGIME_PALETTE)]


def regime_color_alpha(state_idx, alpha=0.2):
    """Get regime color with alpha as rgba string."""
    hex_c = REGIME_PALETTE[state_idx % len(REGIME_PALETTE)]
    r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render_chart(fig, key=None):
    """Render a Plotly figure with clean modebar config."""
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": [
                "select2d", "lasso2d", "autoScale2d",
                "hoverClosestCartesian", "hoverCompareCartesian",
                "toggleSpikelines",
            ],
            "displaylogo": False,
        },
    )


def styled_dataframe(df, hide_index=True):
    """Render a dataframe with premium styling via CSS injection."""
    table_css = """
    <style>
        .premium-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
            border-radius: 8px;
            overflow: hidden;
        }
        .premium-table thead th {
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .premium-table tbody td {
            padding: 9px 14px;
            text-align: right;
        }
        .premium-table tbody td:first-child {
            text-align: left;
            font-weight: 500;
        }
        .premium-table tbody tr:hover {
            opacity: 0.85;
        }
    </style>
    """
    st.markdown(table_css, unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=hide_index)


def card_css():
    """Inject CSS for chart card containers."""
    dark = is_dark()
    card_bg = "rgba(15, 23, 42, 0.6)" if dark else "rgba(255, 255, 255, 0.7)"
    card_border = "rgba(255,255,255,0.06)" if dark else "rgba(0,0,0,0.06)"
    metric_bg = "rgba(15, 23, 42, 0.5)" if dark else "rgba(255, 255, 255, 0.8)"

    st.markdown(f"""
    <style>
        /* Chart containers */
        [data-testid="stPlotlyChart"] {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 8px;
            margin-bottom: 12px;
        }}
        /* Metric cards */
        [data-testid="stMetric"] {{
            background: {metric_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 16px 18px;
        }}
        [data-testid="stMetricValue"] {{
            font-family: {FONT_FAMILY};
            font-weight: 700;
            font-size: 1.4rem !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-family: {FONT_FAMILY};
            font-weight: 500;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.7;
        }}
        /* Dataframe styling */
        .stDataFrame {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            overflow: hidden;
        }}
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: {FONT_FAMILY};
            font-size: 0.85rem;
            font-weight: 500;
            padding: 8px 20px;
            border-radius: 6px 6px 0 0;
        }}
        /* Download buttons */
        [data-testid="stDownloadButton"] > button {{
            border-radius: 8px;
            font-family: {FONT_FAMILY};
            font-weight: 500;
            padding: 10px 24px;
            transition: all 0.2s ease;
        }}
        /* Expander */
        div[data-testid="stExpander"] {{
            border-radius: 10px;
            border: 1px solid {card_border};
        }}
    </style>
    """, unsafe_allow_html=True)
