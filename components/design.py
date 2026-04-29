"""Centralized design system - colors, typography, spacing, and helpers."""

import streamlit as st

# Regime color palette
REGIME_COLORS = {
    "bull": "#14b8a6",
    "transition": "#f6c453",
    "stress": "#f97366",
    "extra_1": "#4f7cff",
    "extra_2": "#0ea5e9",
    "extra_3": "#84cc16",
}

REGIME_PALETTE = [
    "#14b8a6",
    "#f97366",
    "#4f7cff",
    "#f6c453",
    "#0ea5e9",
    "#84cc16",
]

PHASE_COLORS = {
    "Bull Expansion": "#14b8a6",
    "Repair": "#84cc16",
    "Distribution": "#f59e0b",
    "Capitulation": "#4f7cff",
}

TRAIN_COLOR = "#4f7cff"
TEST_COLOR = "#f97366"
DRAWDOWN_COLOR = "#e76f51"
DRAWDOWN_FILL  = "rgba(231, 111, 81, 0.15)"
PRICE_LINE_DARK  = "#a8b2c1"
PRICE_LINE_LIGHT = "#4a5568"
GRID_DARK  = "rgba(255,255,255,0.07)"
GRID_LIGHT = "rgba(0,0,0,0.07)"
ZERO_LINE_DARK  = "rgba(255,255,255,0.15)"
ZERO_LINE_LIGHT = "rgba(0,0,0,0.12)"

# Typography
FONT_FAMILY = "'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
DISPLAY_FONT = "'Sora', 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
TITLE_SIZE = 17
SUBTITLE_SIZE = 12
AXIS_LABEL_SIZE = 11
TICK_SIZE = 10
ANNOTATION_SIZE = 11
LEGEND_SIZE = 11

# Chart dimensions
CHART_HEIGHT_MAIN = 480
CHART_HEIGHT_HALF = 380
CHART_HEIGHT_SMALL = 320
CHART_HEIGHT_GAUGE = 240
CHART_HEIGHT_DUAL = 620

# Spacing
CHART_MARGIN = dict(l=52, r=24, t=88, b=78)
CHART_MARGIN_COMPACT = dict(l=44, r=18, t=76, b=72)


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
            font=dict(size=TITLE_SIZE, family=DISPLAY_FONT, color=c["text"]),
            x=0.0, xanchor="left",
            y=0.97,
            yanchor="top",
            pad=dict(t=4, b=12),
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
            automargin=True,
        ),
        yaxis=dict(
            gridcolor=c["grid"],
            zerolinecolor=c["zero_line"],
            tickfont=dict(size=TICK_SIZE, color=c["text_secondary"]),
            title_font=dict(size=AXIS_LABEL_SIZE, color=c["text_secondary"]),
            showgrid=True,
            gridwidth=1,
            automargin=True,
        ),
        legend=dict(
            font=dict(size=LEGEND_SIZE, color=c["text"]),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="left",
            x=0,
            itemclick="toggleothers",
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


def phase_color(name):
    """Get market phase color by phase name."""
    return PHASE_COLORS.get(name, "#94a3b8")


def phase_color_alpha(name, alpha=0.2):
    """Get market phase color with alpha as rgba string."""
    hex_c = phase_color(name)
    r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render_page_hero(title, description, eyebrow=None, badges=None):
    """Render a product-style page hero."""
    badge_markup = ""
    if badges:
        badge_markup = "".join(
            f'<span class="hero-badge">{badge}</span>'
            for badge in badges
        )

    eyebrow_markup = (
        f'<div class="hero-eyebrow">{eyebrow}</div>'
        if eyebrow else ""
    )

    st.markdown(
        f"""
        <section class="hero-shell">
            {eyebrow_markup}
            <h1>{title}</h1>
            <p>{description}</p>
            <div class="hero-badges">{badge_markup}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(items):
    """Render a row of metric cards with HTML styling."""
    if not items:
        return

    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        value = item.get("value", "-")
        label = item.get("label", "")
        note = item.get("note", "")
        col.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_info_cards(items, columns=3):
    """Render evenly spaced informational cards."""
    if not items:
        return

    cols = st.columns(columns)
    for idx, item in enumerate(items):
        col = cols[idx % columns]
        col.markdown(
            f"""
            <div class="glass-card info-card">
                <div class="info-card-kicker">{item.get("kicker", "")}</div>
                <h3>{item.get("title", "")}</h3>
                <p>{item.get("body", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


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
    """Render a dataframe with lightweight premium styling."""
    table_css = """
    <style>
        .premium-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
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
    card_bg = "rgba(8, 18, 32, 0.66)" if dark else "rgba(255, 255, 255, 0.78)"
    card_border = "rgba(255,255,255,0.08)" if dark else "rgba(15,23,42,0.08)"
    metric_bg = "rgba(8, 18, 32, 0.58)" if dark else "rgba(255, 255, 255, 0.88)"

    st.markdown(f"""
    <style>
        /* Chart containers */
        [data-testid="stPlotlyChart"] {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 10px 10px 6px;
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
            font-family: {DISPLAY_FONT};
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
            padding: 12px 18px;
            min-height: 3.2rem;
            white-space: normal;
            line-height: 1.35;
            text-align: center;
            transition: all 0.2s ease;
        }}
        /* Expander */
        div[data-testid="stExpander"] {{
            border-radius: 10px;
            border: 1px solid {card_border};
        }}
    </style>
    """, unsafe_allow_html=True)
