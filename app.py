
from pathlib import Path
import sys
import html

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.analytics import load_sales, load_inventory, kpis
from src.etl import run_pipeline


# =========================================================
# 1. PAGE CONFIGURATION AND DESIGN SYSTEM
# =========================================================

st.set_page_config(
    page_title="RetailPulse | Retail Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# User-selectable appearance. Streamlit owns this widget's state;
# do not prepopulate the same key through session_state.
appearance = st.sidebar.segmented_control(
    "Appearance",
    options=["Dark", "Light"],
    default="Dark",
    key="rp_appearance",
    label_visibility="collapsed"
)

BG = "#0B1220"
PANEL = "#121D2E"
PANEL_ALT = "#17253A"
TEXT = "#E8EEF7"
MUTED = "#91A2B8"
TEAL = "#27D3B0"
BLUE = "#5B9BFF"
BORDER = "#26364D"

COLORS = [
    TEAL, BLUE, "#F6B85A", "#A78BFA",
    "#F27E9D", "#70C1D3", "#A3D977"
]

st.markdown("""
<style>
:root {
    --rp-bg: #0B1220;
    --rp-sidebar: #0E1929;
    --rp-panel: #121D2E;
    --rp-panel2: #17253A;
    --rp-text: #E8EEF7;
    --rp-muted: #91A2B8;
    --rp-accent: #27D3B0;
    --rp-blue: #5B9BFF;
    --rp-border: #26364D;
}

/* App canvas and content rhythm */
.stApp {
    background: var(--rp-bg);
    color: var(--rp-text);
}
[data-testid="stHeader"] {
    background: rgba(11,18,32,.96);
}
.block-container {
    max-width: 1600px;
    padding: 2.1rem clamp(1rem, 3vw, 3rem) 3rem;
}
h1, h2, h3, h4 {
    color: var(--rp-text) !important;
    letter-spacing: -.035em;
}
h1 {
    font-size: clamp(1.8rem, 3vw, 2.55rem) !important;
    font-weight: 780 !important;
    line-height: 1.12 !important;
}
p, label, .stCaption {
    color: var(--rp-muted);
}
[data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}

/* Sidebar brand and navigation */
[data-testid="stSidebar"] {
    background: var(--rp-sidebar);
    border-right: 1px solid var(--rp-border);
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.35rem 1rem 1.5rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
}
.rp-sidebar-brand {
    padding: 8px 8px 22px;
}
.rp-brand-icon {
    display: inline-flex;
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: #173E42;
    color: var(--rp-accent);
    align-items: center;
    justify-content: center;
    font-size: 23px;
    font-weight: 800;
    margin-right: 11px;
    box-shadow: 0 5px 18px rgba(39,211,176,.10);
}
.rp-sidebar-caption {
    color: #91A2B8;
    font-size: .68rem;
    letter-spacing: .16em;
    font-weight: 800;
    margin: 1.25rem 0 .65rem .45rem;
    text-transform: uppercase;
}
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: .28rem;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: .62rem .7rem;
    margin: 0;
    min-height: 40px;
    transition: background .18s ease, border-color .18s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: #15243A;
    border-color: #26364D;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, rgba(39,211,176,.16), rgba(39,211,176,.045));
    border: 1px solid rgba(39,211,176,.28);
    box-shadow: inset 3px 0 0 var(--rp-accent);
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: #C7D3E2 !important;
    font-size: .9rem;
    font-weight: 560;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #F2F7FC !important;
    font-weight: 700;
}

/* Section labels, cards and metrics */
.rp-eyebrow {
    color: var(--rp-accent);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .17em;
    text-transform: uppercase;
    margin-bottom: .55rem;
}
.rp-sub {
    color: var(--rp-muted);
    font-size: 1rem;
    margin-top: -.45rem;
    margin-bottom: .7rem;
}
.rp-card {
    background: linear-gradient(145deg,#15243A,#101A2A);
    border: 1px solid var(--rp-border);
    border-radius: 16px;
    padding: 18px 20px;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg,#15243A,#111C2C);
    border: 1px solid var(--rp-border);
    border-radius: 15px;
    padding: 17px 18px;
    min-height: 112px;
    box-shadow: 0 8px 24px rgba(0,0,0,.10);
}
[data-testid="stMetricLabel"] {
    color: var(--rp-muted) !important;
    font-size: .82rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--rp-text) !important;
    font-weight: 750 !important;
    font-size: clamp(1.2rem, 2vw, 1.75rem) !important;
}
[data-testid="stMetricDelta"] {
    color: var(--rp-accent) !important;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--rp-border);
    border-radius: 16px;
    background: rgba(18,29,46,.30);
}

/* Charts and tables */
div[data-testid="stPlotlyChart"] {
    background: #101B2B;
    border: 1px solid var(--rp-border);
    border-radius: 14px;
    padding: 8px;
    overflow: hidden;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--rp-border);
    border-radius: 12px;
}
hr {
    border-color: var(--rp-border);
    margin: 1.35rem 0;
}

/* Compact, Amazon-inspired active filter summary */
.rp-filter-summary {
    background: linear-gradient(145deg, #121D2E, #101A2A);
    border: 1px solid var(--rp-border);
    border-radius: 14px;
    padding: 13px 16px;
    margin: .65rem 0 1rem;
}
.rp-filter-summary-title {
    color: var(--rp-text);
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .12em;
    margin-right: 10px;
}
.rp-filter-count {
    color: var(--rp-accent);
    background: rgba(39,211,176,.10);
    border: 1px solid rgba(39,211,176,.20);
    border-radius: 20px;
    padding: 3px 9px;
    font-size: .72rem;
    font-weight: 700;
}
.rp-filter-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 10px;
}
.rp-filter-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    max-width: 100%;
    background: #17283D;
    border: 1px solid #2B4059;
    border-radius: 7px;
    padding: 5px 9px;
    font-size: .76rem;
}
.rp-chip-label {
    color: #91A2B8;
}
.rp-chip-value {
    color: #E8EEF7;
    font-weight: 650;
}
.rp-filter-chip-muted {
    background: rgba(39,211,176,.06);
    border-color: rgba(39,211,176,.15);
}
[data-testid="stExpander"] {
    background: #101B2B;
    border: 1px solid var(--rp-border);
    border-radius: 14px;
    margin-bottom: 1.1rem;
}
[data-testid="stExpander"] summary {
    color: var(--rp-text);
    font-weight: 650;
}

/* Inputs */
[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background: #15243A;
    border-color: var(--rp-border);
    border-radius: 9px;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #193B46;
    border: 1px solid rgba(39,211,176,.12);
}
/* Neutral high-contrast action buttons across the whole application */
.stButton > button, .stDownloadButton > button, [data-testid="stLinkButton"] a {
    background: #F8FAFC !important;
    color: #142338 !important;
    border: 1px solid #C8D3E0 !important;
    border-radius: 10px;
    font-weight: 800 !important;
    min-height: 42px;
    text-shadow: none;
    box-shadow: 0 2px 8px rgba(0,0,0,.10);
    transition: transform .18s ease, background .18s ease, border-color .18s ease;
}
.stButton > button *, .stDownloadButton > button *,
[data-testid="stLinkButton"] a * {
    color: #142338 !important;
    font-weight: 800 !important;
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    background: #E7F4F1 !important;
    border-color: #27D3B0 !important;
    color: #102C2A !important;
    transform: translateY(-1px);
}
.stButton > button:hover *, .stDownloadButton > button:hover *,
[data-testid="stLinkButton"] a:hover * {
    color: #102C2A !important;
}
.stAlert {
    border-radius: 12px;
}


/* Explicit high-contrast buttons, including sidebar actions */
.stApp .stButton > button,
.stApp .stDownloadButton > button,
.stApp [data-testid="stLinkButton"] a,
.stApp [data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF !important;
    color: #142338 !important;
    -webkit-text-fill-color: #142338 !important;
    border: 1px solid #D5DEE8 !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.12) !important;
}
.stApp .stButton > button *,
.stApp .stDownloadButton > button *,
.stApp [data-testid="stLinkButton"] a *,
.stApp [data-testid="stSidebar"] .stButton > button * {
    color: #142338 !important;
    -webkit-text-fill-color: #142338 !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}
.stApp .stButton > button:hover,
.stApp .stDownloadButton > button:hover,
.stApp [data-testid="stLinkButton"] a:hover,
.stApp [data-testid="stSidebar"] .stButton > button:hover {
    background: #E8F4F1 !important;
    border-color: #27D3B0 !important;
}

/* Responsive layout: let metric and chart columns wrap cleanly */
@media (max-width: 900px) {
    .block-container {
        padding: 1.35rem 1rem 2rem;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: .8rem !important;
    }
    [data-testid="column"] {
        min-width: min(100%, 280px) !important;
        flex: 1 1 280px !important;
    }
    [data-testid="stMetric"] {
        min-height: 96px;
    }
}
@media (max-width: 600px) {
    [data-testid="stSidebar"] {
        min-width: 0;
    }
    .block-container {
        padding: 1rem .75rem 1.5rem;
    }
    h1 {
        font-size: 1.75rem !important;
    }
    [data-testid="stPlotlyChart"] {
        padding: 2px;
    }
    [data-testid="stMetric"] {
        padding: 13px;
    }
}
</style>
""", unsafe_allow_html=True)

# Theme overrides are intentionally explicit so text, filters, tables and chart surfaces
# all switch together rather than leaving dark components inside a light page.
if appearance == "Light":
    st.markdown("""
    <style>
    :root {
        --rp-bg: #F3F6FA;
        --rp-sidebar: #FFFFFF;
        --rp-panel: #FFFFFF;
        --rp-panel2: #EDF2F8;
        --rp-text: #172437;
        --rp-muted: #52647A;
        --rp-accent: #087F70;
        --rp-blue: #2869C7;
        --rp-border: #D7E0EA;
    }
    .stApp { background: #F3F6FA !important; color: #172437 !important; }
    [data-testid="stHeader"] { background: rgba(243,246,250,.96) !important; }
    [data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #D7E0EA !important; }
    [data-testid="stSidebar"] * { color: #26384D; }
    h1,h2,h3,h4,strong { color: #172437 !important; }
    p,label,.stCaption,[data-testid="stMarkdownContainer"] p { color: #52647A; }
    .rp-eyebrow { color: #087F70 !important; }
    .rp-sub { color: #52647A !important; }
    .rp-sidebar-caption { color: #687B91 !important; }
    .rp-brand-icon { background: #DDF4EF !important; color: #087F70 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { color: #35485E !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: #F0F5F9 !important; border-color: #D7E0EA !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background: #E5F5F1 !important; border-color: #A9DCD1 !important; box-shadow: inset 3px 0 0 #087F70 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #123B37 !important; }
    [data-testid="stMetric"] { background: linear-gradient(145deg,#FFFFFF,#F7FAFD) !important; border-color: #D7E0EA !important; box-shadow: 0 5px 18px rgba(28,48,72,.06) !important; }
    [data-testid="stMetricLabel"] { color: #52647A !important; }
    [data-testid="stMetricValue"] { color: #172437 !important; }
    [data-testid="stMetricDelta"] { color: #087F70 !important; }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF !important; border-color: #D7E0EA !important; }
    div[data-testid="stPlotlyChart"] { background: #FFFFFF !important; border-color: #D7E0EA !important; }
    [data-testid="stDataFrame"] { border-color: #D7E0EA !important; }
    .rp-filter-summary { background: #FFFFFF !important; border-color: #D7E0EA !important; }
    .rp-filter-summary-title { color: #172437 !important; }
    .rp-filter-count { color: #075F55 !important; background: #E1F4EF !important; border-color: #B8E3D9 !important; }
    .rp-filter-chip { background: #F1F5F9 !important; border-color: #D7E0EA !important; }
    .rp-chip-label { color: #63758A !important; }
    .rp-chip-value { color: #24364B !important; }
    .rp-filter-chip-muted { background: #EAF6F3 !important; border-color: #C7E8DF !important; }
    [data-testid="stExpander"] { background: #FFFFFF !important; border-color: #D7E0EA !important; }
    [data-testid="stExpander"] summary { color: #172437 !important; }
    [data-baseweb="select"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input { background: #FFFFFF !important; border-color: #C9D5E2 !important; color: #172437 !important; }
    [data-testid="stMultiSelect"] [data-baseweb="tag"] { background: #DDF1EC !important; border-color: #B9DED5 !important; }
    [data-testid="stMultiSelect"] [data-baseweb="tag"] * { color: #174A43 !important; }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stMultiSelect"] label,
    [data-testid="stSelectbox"] label { color: #34465C !important; }
    [data-baseweb="select"] *,
    [data-testid="stDateInput"] input { color: #172437 !important; }
    [data-testid="stDataFrame"] { background: #FFFFFF !important; border-color: #D7E0EA !important; }
    [data-testid="stTable"] { background: #FFFFFF !important; color: #26384D !important; }
    [data-testid="stPlotlyChart"] { background: #FFFFFF !important; }
    .stButton > button, .stDownloadButton > button, [data-testid="stLinkButton"] a {
        background: #FFFFFF !important;
        color: #142338 !important;
        border: 1px solid #C8D3E0 !important;
        box-shadow: 0 2px 8px rgba(28,48,72,.08) !important;
    }
    .stButton > button *, .stDownloadButton > button *, [data-testid="stLinkButton"] a * {
        color: #142338 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stLinkButton"] a:hover {
        background: #E7F4F1 !important;
        border-color: #087F70 !important;
        color: #123B37 !important;
    }
    .stButton > button:hover *, .stDownloadButton > button:hover *, [data-testid="stLinkButton"] a:hover * {
        color: #123B37 !important;
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button * {
        background: #FFFFFF !important;
        color: #142338 !important;
        -webkit-text-fill-color: #142338 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #E8F4F1 !important;
        border-color: #087F70 !important;
    }
    hr { border-color: #D7E0EA !important; }
    </style>
    """, unsafe_allow_html=True)

# Force high-contrast text inside teal action buttons in dark mode too.
st.markdown("""
<style>
.stButton > button, .stDownloadButton > button,
[data-testid="stLinkButton"] a,
.stButton > button p, .stDownloadButton > button p,
[data-testid="stLinkButton"] a p {
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. CHART THEME AND HELPER FUNCTIONS
# =========================================================

PLOT = dict(
    template="plotly_dark" if appearance == "Dark" else "plotly_white",
    paper_bgcolor="#101B2B" if appearance == "Dark" else "#FFFFFF",
    plot_bgcolor="#101B2B" if appearance == "Dark" else "#FFFFFF",
    font=dict(
        family="Inter, sans-serif",
        color=TEXT if appearance == "Dark" else "#172437"
    ),
    margin=dict(l=20, r=20, t=45, b=20),
    colorway=COLORS,
    xaxis=dict(
        gridcolor=BORDER if appearance == "Dark" else "#E2E8F0",
        zerolinecolor=BORDER if appearance == "Dark" else "#CBD5E1"
    ),
    yaxis=dict(
        gridcolor=BORDER if appearance == "Dark" else "#E2E8F0",
        zerolinecolor=BORDER if appearance == "Dark" else "#CBD5E1"
    ),
    hoverlabel=dict(
        bgcolor=PANEL_ALT if appearance == "Dark" else "#FFFFFF",
        bordercolor=BORDER if appearance == "Dark" else "#CBD5E1",
        font_color=TEXT if appearance == "Dark" else "#172437"
    )
)


def style(fig, height=360):
    fig.update_layout(
        **PLOT,
        height=height,
        legend_title_text="",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0,
            font=dict(color=TEXT if appearance == "Dark" else "#34465C")
        ),
        hovermode="closest"
    )
    axis_color = TEXT if appearance == "Dark" else "#34465C"
    grid_color = BORDER if appearance == "Dark" else "#DCE4ED"
    fig.update_xaxes(
        tickfont=dict(color=axis_color),
        title_font=dict(color=axis_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color
    )
    fig.update_yaxes(
        tickfont=dict(color=axis_color),
        title_font=dict(color=axis_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color
    )
    fig.update_annotations(font=dict(color=axis_color))
    fig.update_traces(textfont=dict(color=axis_color))
    fig.update_layout(
        coloraxis_colorbar=dict(
            tickfont=dict(color=axis_color),
            title_font=dict(color=axis_color)
        )
    )
    return fig


def money(value):
    """Display amounts without assuming the source currency."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


def panel_heading(title, subtitle=None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def show_chart(fig, height=360):
    st.plotly_chart(
        style(fig, height),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "responsive": True
        }
    )


def empty_message(message):
    st.info(message)


def show_table(data, height=None, **kwargs):
    """Render readable, theme-aware tables with explicit cell-level styling."""
    if appearance == "Dark":
        header_bg = "#1B2B40"
        header_fg = "#F4F7FB"
        row_bg = "#101B2B"
        alt_bg = "#16243A"
        body_fg = "#E3EBF5"
        border = "#2B3D55"
    else:
        # Light mode uses a true light table body, not the dark Streamlit canvas.
        header_bg = "#24364B"
        header_fg = "#FFFFFF"
        row_bg = "#FFFFFF"
        alt_bg = "#F3F6FA"
        body_fg = "#1E2D40"
        border = "#D8E1EB"

    def row_style(row):
        # Alternating row fills improve scanning in long data tables.
        row_number = row.name if isinstance(row.name, int) else 0
        fill = row_bg if row_number % 2 == 0 else alt_bg
        return [
            f"background-color: {fill}; color: {body_fg}; "
            f"border-bottom: 1px solid {border};"
            for _ in row
        ]

    styled = (
        data.style
        .apply(row_style, axis=1)
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", header_bg),
                ("color", header_fg),
                ("font-weight", "700"),
                ("border", f"1px solid {border}"),
                ("padding", "10px 12px"),
                ("text-align", "left")
            ]},
            {"selector": "tbody td", "props": [
                ("border", f"1px solid {border}"),
                ("padding", "9px 12px")
            ]},
            {"selector": "th.row_heading", "props": [
                ("background-color", header_bg),
                ("color", header_fg),
                ("border", f"1px solid {border}")
            ]},
            {"selector": "th.blank", "props": [
                ("background-color", header_bg),
                ("border", f"1px solid {border}")
            ]}
        ])
    )

    render_kwargs = {"use_container_width": True, "hide_index": True}
    render_kwargs.update(kwargs)
    if height is not None:
        render_kwargs["height"] = height

    # Streamlit dataframe renders Styler cell-level background/text colours.
    # Avoid the unsupported `theme` argument for compatibility with Streamlit 1.50.
    st.dataframe(styled, **render_kwargs)


def safe_sum(frame, column):
    if column not in frame.columns:
        return 0.0
    return float(frame[column].sum())


def safe_unique(frame, column):
    if column not in frame.columns:
        return 0
    return int(frame[column].nunique())


def metric_cards(frame):
    values = kpis(frame)

    has_cost = (
        "cost" in frame.columns
        and frame["cost"].notna().any()
    )

    return values, has_cost


# =========================================================
# 3. SIDEBAR NAVIGATION
# =========================================================

PAGES = [
    "Executive Overview",
    "Sales Performance",
    "Product Intelligence",
    "Store & Region",
    "Inventory Intelligence",
    "Chart Explorer",
    "Data Explorer",
    "Project & Methodology"
]

PAGE_ICONS = {
    "Executive Overview": "◈",
    "Sales Performance": "↗",
    "Product Intelligence": "◇",
    "Store & Region": "⌖",
    "Inventory Intelligence": "▦",
    "Chart Explorer": "◫",
    "Data Explorer": "▤",
    "Project & Methodology": "ⓘ"
}

st.sidebar.markdown("""
<div class="rp-sidebar-brand">
    <div style="display:flex;align-items:center">
        <span class="rp-brand-icon">◈</span>
        <div>
            <div style="font-size:22px;font-weight:800;letter-spacing:-1px">
                RetailPulse
            </div>
            <div style="font-size:11px;color:#91A2B8">
                RETAIL INTELLIGENCE
            </div>
        </div>
    </div>
    <div style="font-size:11px;color:#91A2B8;margin-top:12px">
        Your retail analytics workspace
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="rp-sidebar-caption">WORKSPACE</div>',
    unsafe_allow_html=True
)

if "rp_page" not in st.session_state:
    st.session_state["rp_page"] = PAGES[0]

page = st.sidebar.radio(
    "Workspace",
    PAGES,
    key="rp_page",
    format_func=lambda x: f"{PAGE_ICONS[x]}   {x}",
    label_visibility="collapsed"
)

st.sidebar.divider()


# =========================================================
# 4. PIPELINE CONTROL AND DATA LOADING
# =========================================================

st.sidebar.markdown(
    '<div class="rp-sidebar-caption">DATA OPERATIONS</div>',
    unsafe_allow_html=True
)

if st.sidebar.button(
    "↻  Refresh data pipeline",
    use_container_width=True,
    key="rp_run_pipeline"
):
    try:
        with st.spinner("Refreshing and validating retail data..."):
            result = run_pipeline()

        st.cache_data.clear()

        st.sidebar.success(
            f"Loaded {result['sales']['rows_out']:,} sales rows"
        )
        st.rerun()

    except Exception as exc:
        st.sidebar.error(f"Pipeline failed: {exc}")

st.sidebar.caption(
    "Run after replacing source CSV files in data/raw/."
)

# Load data using cached functions from analytics.py.
df = load_sales()
inv = load_inventory()


# =========================================================
# 5. EMPTY DATA HANDLING
# =========================================================

if df.empty:
    st.markdown(
        '<div class="rp-eyebrow">RETAIL PERFORMANCE / BUSINESS INTELLIGENCE</div>',
        unsafe_allow_html=True
    )
    st.title("RetailPulse")
    st.warning(
        "Retail data has not been loaded yet. "
        "This project does not use fabricated business records."
    )
    st.markdown("### Load the source dataset")
    st.write(
        "1. Place the sales and inventory CSV files in `data/raw/`."
    )
    st.write(
        "2. Run `python3 -m src.etl` or use the pipeline button."
    )
    st.link_button(
        "Open original Mendeley dataset",
        "https://data.mendeley.com/datasets/27x8mjm8k4/1"
    )
    st.stop()


# =========================================================
# 6. DATA PREPARATION
# =========================================================

# Ensure expected date columns are datetime.
df["date"] = pd.to_datetime(df["date"], errors="coerce")

if not inv.empty and "date" in inv.columns:
    inv["date"] = pd.to_datetime(inv["date"], errors="coerce")

# Handle missing optional dimensions safely.
for column in ["division", "category", "subcategory", "segment"]:
    if column not in df.columns:
        df[column] = "Unknown"
    df[column] = df[column].fillna("Unknown").astype(str)

for column in ["store_id", "sku_id"]:
    if column in df.columns:
        df[column] = df[column].astype(str)

if "is_return" not in df.columns:
    df["is_return"] = (df["sales"] < 0).astype(int)

if "sales_type" not in df.columns:
    df["sales_type"] = "Unknown"

if "weekday" not in df.columns:
    df["weekday"] = df["date"].dt.day_name()

if "year_month" not in df.columns:
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

# Inventory dimensions.
if not inv.empty:
    for column in ["division", "category", "subcategory", "segment"]:
        if column not in inv.columns:
            inv[column] = "Unknown"
        inv[column] = inv[column].fillna("Unknown").astype(str)

    for column in ["store_id", "sku_id"]:
        if column in inv.columns:
            inv[column] = inv[column].astype(str)


# =========================================================
# 7. GLOBAL FILTERS WITH PERSISTENT SESSION STATE
# =========================================================

min_date = df["date"].min().date()
max_date = df["date"].max().date()

stores = sorted(df["store_id"].dropna().unique().tolist())
divisions = sorted(df["division"].dropna().unique().tolist())
categories = sorted(df["category"].dropna().unique().tolist())
sales_types = sorted(df["sales_type"].dropna().unique().tolist())

filter_defaults = {
    "rp_date_range": (min_date, max_date),
    "rp_stores": stores.copy(),
    "rp_divisions": divisions.copy(),
    "rp_categories": categories.copy(),
    "rp_sales_types": sales_types.copy()
}

# Initialise state only once.
for key, default in filter_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Remove stale selections if source data changes.
for key, options in [
    ("rp_stores", stores),
    ("rp_divisions", divisions),
    ("rp_categories", categories),
    ("rp_sales_types", sales_types)
]:
    st.session_state[key] = [
        value for value in st.session_state[key]
        if value in options
    ]

# Ensure date range is within available data.
saved_range = st.session_state["rp_date_range"]

if not isinstance(saved_range, (tuple, list)) or len(saved_range) != 2:
    saved_range = (min_date, max_date)

start_saved = max(min_date, min(saved_range[0], max_date))
end_saved = max(min_date, min(saved_range[1], max_date))

if start_saved > end_saved:
    start_saved, end_saved = min_date, max_date

st.session_state["rp_date_range"] = (start_saved, end_saved)


# Single page header — keep it above the filter controls.
st.markdown(
    '<div class="rp-eyebrow">RETAIL PERFORMANCE / BUSINESS INTELLIGENCE</div>',
    unsafe_allow_html=True
)
st.title(page)
st.markdown(
    '<p class="rp-sub">A decision-support workspace across sales, '
    'products, stores and inventory.</p>',
    unsafe_allow_html=True
)

# Amazon-inspired filter experience:
# compact summary chips remain visible; detailed controls open on demand.
current_stores = st.session_state["rp_stores"]
current_divisions = st.session_state["rp_divisions"]
current_categories = st.session_state["rp_categories"]
current_sales_types = st.session_state["rp_sales_types"]
current_range = st.session_state["rp_date_range"]

active_filter_count = sum([
    len(current_stores) != len(stores),
    len(current_divisions) != len(divisions),
    len(current_categories) != len(categories),
    len(current_sales_types) != len(sales_types),
    tuple(current_range) != (min_date, max_date)
])

def filter_chip(label, value):
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    return (
        '<span class="rp-filter-chip">'
        f'<span class="rp-chip-label">{safe_label}</span>'
        f'<span class="rp-chip-value">{safe_value}</span>'
        '</span>'
    )

chip_html = []
if tuple(current_range) != (min_date, max_date):
    chip_html.append(filter_chip("Date", f"{current_range[0]} – {current_range[1]}"))
if len(current_stores) != len(stores):
    chip_html.append(filter_chip("Stores", f"{len(current_stores)} selected"))
if len(current_divisions) != len(divisions):
    chip_html.append(filter_chip("Divisions", f"{len(current_divisions)} selected"))
if len(current_categories) != len(categories):
    chip_html.append(filter_chip("Categories", f"{len(current_categories)} selected"))
if len(current_sales_types) != len(sales_types):
    chip_html.append(filter_chip("Sales type", f"{len(current_sales_types)} selected"))

if chip_html:
    chips_markup = '<div class="rp-filter-chips">' + "".join(chip_html) + '</div>'
else:
    chips_markup = (
        '<div class="rp-filter-chips">'
        '<span class="rp-filter-chip rp-filter-chip-muted">'
        '<span class="rp-chip-value">All data · No filters applied</span>'
        '</span></div>'
    )

st.markdown(
    '<div class="rp-filter-summary">'
    '<div><span class="rp-filter-summary-title">FILTERS</span>'
    f'<span class="rp-filter-count">{active_filter_count} active</span></div>'
    + chips_markup +
    '</div>',
    unsafe_allow_html=True
)

with st.expander("⚙  Refine dashboard data", expanded=False):
    st.caption("Selections apply consistently across every dashboard page.")
    filter_row_1 = st.columns([1.2, 1, 1])
    with filter_row_1[0]:
        date_range = st.date_input(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            key="rp_date_range"
        )
    with filter_row_1[1]:
        selected_stores = st.multiselect(
            "Stores", options=stores, key="rp_stores",
            placeholder="All stores"
        )
    with filter_row_1[2]:
        selected_divisions = st.multiselect(
            "Divisions", options=divisions, key="rp_divisions",
            placeholder="All divisions"
        )

    filter_row_2 = st.columns([1, 1, 1])
    with filter_row_2[0]:
        selected_categories = st.multiselect(
            "Categories", options=categories, key="rp_categories",
            placeholder="All categories"
        )
    with filter_row_2[1]:
        selected_sales_types = st.multiselect(
            "Sales type", options=sales_types, key="rp_sales_types",
            placeholder="All sales types"
        )
    with filter_row_2[2]:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        if st.button("Reset all filters", use_container_width=True, key="rp_reset_filters"):
            for key, value in filter_defaults.items():
                st.session_state[key] = value
            st.rerun()

# Read the current selections after widgets render.
date_range = st.session_state["rp_date_range"]
selected_stores = st.session_state["rp_stores"]
selected_divisions = st.session_state["rp_divisions"]
selected_categories = st.session_state["rp_categories"]
selected_sales_types = st.session_state["rp_sales_types"]


# =========================================================
# 8. APPLY GLOBAL FILTERS
# =========================================================

f = df

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    f = f[
        f["date"].dt.date.between(start_date, end_date)
    ]

f = f[
    f["store_id"].isin(selected_stores)
    & f["division"].isin(selected_divisions)
    & f["category"].isin(selected_categories)
    & f["sales_type"].isin(selected_sales_types)
]

# Inventory shares date/store/division/category filters.
inv_filtered = inv

if not inv.empty:
    if "date" in inv_filtered.columns:
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            inv_filtered = inv_filtered[
                inv_filtered["date"].dt.date.between(
                    date_range[0], date_range[1]
                )
            ]

    if "store_id" in inv_filtered.columns:
        inv_filtered = inv_filtered[
            inv_filtered["store_id"].isin(selected_stores)
        ]

    if "division" in inv_filtered.columns:
        inv_filtered = inv_filtered[
            inv_filtered["division"].isin(selected_divisions)
        ]

    if "category" in inv_filtered.columns:
        inv_filtered = inv_filtered[
            inv_filtered["category"].isin(selected_categories)
        ]


# =========================================================
# 9. PAGE HEADER AND FILTER STATUS
# =========================================================

if f.empty:
    st.info(
        "No sales records match the selected filters. "
        "Adjust the filters or use Reset all filters."
    )
    st.stop()

st.caption(
    f"Showing {len(f):,} sales records  ·  "
    f"{f['date'].min():%d %b %Y} – {f['date'].max():%d %b %Y}  ·  "
    f"{f['store_id'].nunique()} stores"
)


# =========================================================
# 10. SHARED METRICS AND AGGREGATIONS
# =========================================================

m, has_cost = metric_cards(f)

total_sales = safe_sum(f, "sales")
total_profit = safe_sum(f, "gross_profit")
total_units = safe_sum(f, "quantity")
return_rows = f[f["is_return"].astype(str).isin(["1", "True", "true"])]
return_count = len(return_rows)
return_rate = return_count / len(f) * 100 if len(f) else 0

monthly_data = (
    f.groupby("year_month", as_index=False)
    .agg(
        sales=("sales", "sum"),
        profit=("gross_profit", "sum"),
        units=("quantity", "sum"),
        records=("sales", "size")
    )
    .sort_values("year_month")
)


def metric_row():
    a, b, c, d, e = st.columns(5)

    a.metric("Net sales", money(total_sales))
    b.metric(
        "Gross profit",
        money(total_profit) if has_cost else "N/A"
    )
    c.metric(
        "Gross margin",
        f"{m['margin']:.1f}%" if has_cost else "N/A"
    )
    d.metric("Net units", f"{total_units:,.0f}")
    e.metric("Stores", f"{m['stores']:,}")


# =========================================================
# 11. EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":

    metric_row()
    st.divider()

    left, right = st.columns([1.65, 1])

    with left:
        with st.container(border=True):
            panel_heading(
                "Sales & profit trajectory",
                "Monthly performance across the selected period"
            )

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=monthly_data["year_month"],
                y=monthly_data["sales"],
                mode="lines+markers",
                name="Net sales",
                line=dict(color=TEAL, width=3),
                fill="tozeroy",
                fillcolor="rgba(39,211,176,.08)"
            ))

            if has_cost:
                fig.add_trace(go.Scatter(
                    x=monthly_data["year_month"],
                    y=monthly_data["profit"],
                    mode="lines+markers",
                    name="Gross profit",
                    line=dict(color=BLUE, width=2)
                ))

            show_chart(fig, 390)

    with right:
        with st.container(border=True):
            panel_heading(
                "Sales mix by category",
                "Contribution to net sales"
            )

            cat = (
                f.groupby("category", as_index=False)["sales"]
                .sum()
                .sort_values("sales", ascending=False)
            )

            show_chart(
                px.pie(
                    cat,
                    names="category",
                    values="sales",
                    hole=.62,
                    color_discrete_sequence=COLORS
                ),
                390
            )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading(
                "Top categories",
                "Ranked by net sales"
            )

            x = (
                f.groupby("category", as_index=False)["sales"]
                .sum()
                .nlargest(10, "sales")
                .sort_values("sales")
            )

            show_chart(
                px.bar(
                    x,
                    x="sales",
                    y="category",
                    orientation="h",
                    color="sales",
                    color_continuous_scale=["#17384A", TEAL]
                ),
                340
            )

    with c2:
        with st.container(border=True):
            panel_heading(
                "Sales by weekday",
                "Understand day-of-week patterns"
            )

            weekday_order = [
                "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"
            ]

            x = (
                f.groupby("weekday", as_index=False)["sales"]
                .sum()
            )

            x["weekday"] = pd.Categorical(
                x["weekday"],
                categories=weekday_order,
                ordered=True
            )

            x = x.sort_values("weekday")

            show_chart(
                px.bar(
                    x,
                    x="weekday",
                    y="sales",
                    color="sales",
                    color_continuous_scale=["#17384A", BLUE]
                ),
                340
            )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("Return records", f"{return_count:,}")
    c2.metric("Return rate", f"{return_rate:.2f}%")
    c3.metric("Unique SKUs", f"{safe_unique(f, 'sku_id'):,}")


# =========================================================
# 12. SALES PERFORMANCE
# =========================================================

elif page == "Sales Performance":

    metric_row()
    st.divider()

    with st.container(border=True):
        panel_heading(
            "Monthly sales analysis",
            "Track revenue and units over time"
        )

        measure = st.selectbox(
            "Select trend metric",
            ["sales", "profit", "units", "records"],
            format_func=lambda x: {
                "sales": "Net sales",
                "profit": "Gross profit",
                "units": "Net units",
                "records": "Sales records"
            }[x],
            key="sales_trend_measure"
        )

        show_chart(
            px.area(
                monthly_data,
                x="year_month",
                y=measure,
                markers=True,
                color_discrete_sequence=[TEAL]
            ),
            380
        )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading(
                "Sales distribution by category",
                "Distribution and spread of transaction values"
            )

            show_chart(
                px.box(
                    f,
                    x="category",
                    y="sales",
                    color="category",
                    points=False
                ),
                380
            )

    with c2:
        with st.container(border=True):
            panel_heading(
                "Quantity versus sales",
                "Explore the relationship between units and sales"
            )

            scatter = (
                f.groupby(["sku_id", "category"], as_index=False)
                .agg(
                    units=("quantity", "sum"),
                    sales=("sales", "sum")
                )
            )

            show_chart(
                px.scatter(
                    scatter,
                    x="units",
                    y="sales",
                    color="category",
                    hover_name="sku_id"
                ),
                380
            )

    with st.container(border=True):
        panel_heading(
            "Sales type performance",
            "Compare full-price, promotional and markdown sales"
        )

        x = (
            f.groupby("sales_type", as_index=False)
            .agg(
                sales=("sales", "sum"),
                units=("quantity", "sum"),
                records=("sales", "size")
            )
            .sort_values("sales", ascending=False)
        )

        show_chart(
            px.bar(
                x,
                x="sales_type",
                y="sales",
                color="sales_type",
                color_discrete_sequence=COLORS
            ),
            350
        )

    st.subheader("Sales records")

    show_table(
        f.head(1000),
        use_container_width=True,
        hide_index=True,
        height=350
    )

    st.download_button(
        "Download filtered sales CSV",
        f.to_csv(index=False).encode("utf-8"),
        "retailpulse_filtered_sales.csv",
        "text/csv"
    )


# =========================================================
# 13. PRODUCT INTELLIGENCE
# =========================================================

elif page == "Product Intelligence":

    metric_row()
    st.divider()

    product_data = (
        f.groupby(
            ["sku_id", "category", "subcategory"],
            as_index=False
        )
        .agg(
            sales=("sales", "sum"),
            profit=("gross_profit", "sum"),
            units=("quantity", "sum"),
            records=("sales", "size")
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading(
                "Top 20 products",
                "Ranked by net sales"
            )

            top = (
                product_data.nlargest(20, "sales")
                .sort_values("sales")
            )

            show_chart(
                px.bar(
                    top,
                    x="sales",
                    y="sku_id",
                    orientation="h",
                    color="sales",
                    color_continuous_scale=["#17384A", TEAL]
                ),
                450
            )

    with c2:
        with st.container(border=True):
            panel_heading(
                "Category contribution",
                "Product hierarchy sales contribution"
            )

            category_data = (
                f.groupby("category", as_index=False)["sales"]
                .sum()
            )

            show_chart(
                px.treemap(
                    category_data,
                    path=["category"],
                    values="sales",
                    color="sales",
                    color_continuous_scale=["#17384A", TEAL]
                ),
                450
            )

    with st.container(border=True):
        panel_heading(
            "Product profitability",
            "Sales and profit by SKU"
        )

        if has_cost:
            show_chart(
                px.scatter(
                    product_data,
                    x="sales",
                    y="profit",
                    size="units",
                    color="category",
                    hover_name="sku_id"
                ),
                420
            )
        else:
            empty_message(
                "Product profitability is unavailable because cost data is missing."
            )

    st.subheader("Product performance table")

    show_table(
        product_data.sort_values("sales", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=350
    )


# =========================================================
# 14. STORE AND REGION
# =========================================================

elif page == "Store & Region":

    metric_row()
    st.divider()

    store_data = (
        f.groupby("store_id", as_index=False)
        .agg(
            sales=("sales", "sum"),
            profit=("gross_profit", "sum"),
            units=("quantity", "sum"),
            records=("sales", "size"),
            skus=("sku_id", "nunique")
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading(
                "Top 20 stores",
                "Store ranking by net sales"
            )

            top = (
                store_data.nlargest(20, "sales")
                .sort_values("sales")
            )

            show_chart(
                px.bar(
                    top,
                    x="sales",
                    y="store_id",
                    orientation="h",
                    color="sales",
                    color_continuous_scale=["#17384A", TEAL]
                ),
                450
            )

    with c2:
        with st.container(border=True):
            panel_heading(
                "Store sales and profit",
                "Compare store-level financial performance"
            )

            if has_cost:
                show_chart(
                    px.scatter(
                        store_data,
                        x="sales",
                        y="profit",
                        size="units",
                        hover_name="store_id",
                        color="sales"
                    ),
                    450
                )
            else:
                empty_message("Cost information is not available.")

    with st.container(border=True):
        panel_heading(
            "Store performance heatmap",
            "Category-level sales across stores"
        )

        pivot = f.pivot_table(
            index="store_id",
            columns="category",
            values="sales",
            aggfunc="sum",
            fill_value=0
        )

        show_chart(
            px.imshow(
                pivot,
                aspect="auto",
                color_continuous_scale=["#142238", TEAL] if appearance == "Dark" else ["#F1F5F9", "#9BD8CA", "#087F70"]
            ),
            480
        )

    st.subheader("Store summary")

    show_table(
        store_data.sort_values("sales", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 15. INVENTORY INTELLIGENCE
# =========================================================

elif page == "Inventory Intelligence":

    if inv_filtered.empty:
        empty_message(
            "No inventory records match the current global filters."
        )
        st.stop()

    inventory_units = safe_sum(inv_filtered, "on_hand")
    negative_stock = int(
        (inv_filtered["on_hand"] < 0).sum()
    )

    stock_value = safe_sum(
        inv_filtered,
        "stocks_selling_amount"
    )

    stock_cost = safe_sum(
        inv_filtered,
        "cost_of_stocks"
    )

    a, b, c, d = st.columns(4)

    a.metric("Stock units", f"{inventory_units:,.0f}")
    b.metric("Stock value", money(stock_value))
    c.metric("Stock cost", money(stock_cost))
    d.metric("Negative stock rows", f"{negative_stock:,}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading(
                "Inventory by category",
                "Units on hand by product category"
            )

            x = (
                inv_filtered.groupby("category", as_index=False)
                ["on_hand"].sum()
                .sort_values("on_hand", ascending=False)
            )

            show_chart(
                px.bar(
                    x,
                    x="category",
                    y="on_hand",
                    color="category",
                    color_discrete_sequence=COLORS
                ),
                370
            )

    with c2:
        with st.container(border=True):
            panel_heading(
                "Inventory stock status",
                "Inventory records by price/stock status"
            )

            if "stock_status" in inv_filtered.columns:
                x = (
                    inv_filtered["stock_status"]
                    .value_counts()
                    .reset_index()
                )
                x.columns = ["stock_status", "records"]

                show_chart(
                    px.pie(
                        x,
                        names="stock_status",
                        values="records",
                        hole=.55,
                        color_discrete_sequence=COLORS
                    ),
                    370
                )
            else:
                empty_message("Stock status is unavailable.")

    with st.container(border=True):
        panel_heading(
            "Inventory by store and category",
            "Explore stock distribution across stores"
        )

        pivot = inv_filtered.pivot_table(
            index="store_id",
            columns="category",
            values="on_hand",
            aggfunc="sum",
            fill_value=0
        )

        show_chart(
            px.imshow(
                pivot,
                aspect="auto",
                color_continuous_scale=["#142238", TEAL] if appearance == "Dark" else ["#F1F5F9", "#9BD8CA", "#087F70"]
            ),
            470
        )

    st.subheader("Inventory records")

    show_table(
        inv_filtered.head(2000),
        use_container_width=True,
        hide_index=True,
        height=350
    )

    st.download_button(
        "Download filtered inventory CSV",
        inv_filtered.to_csv(index=False).encode("utf-8"),
        "retailpulse_filtered_inventory.csv",
        "text/csv"
    )

    st.caption(
        "Inventory records are filtered by their Start Date. "
        "Negative stock rows are retained and flagged, not silently removed."
    )


# =========================================================
# 16. CHART EXPLORER
# =========================================================

elif page == "Chart Explorer":

    st.markdown(
        "Build a custom visualisation from the filtered sales dataset. "
        "Long category labels are shown horizontally where possible."
    )

    dimensions = [
        c for c in [
            "category", "subcategory", "division",
            "segment", "store_id", "sales_type",
            "weekday", "year_month", "sku_id"
        ]
        if c in f.columns
    ]

    measures = [
        c for c in [
            "sales", "quantity", "gross_profit", "cost"
        ]
        if c in f.columns
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        dimension = st.selectbox(
            "Dimension",
            dimensions,
            key="explorer_dimension"
        )

    with c2:
        measure = st.selectbox(
            "Measure",
            measures,
            key="explorer_measure"
        )

    with c3:
        aggregation = st.selectbox(
            "Aggregation",
            ["Sum", "Mean", "Median", "Count"],
            key="explorer_aggregation"
        )

    chart_type = st.selectbox(
        "Visualisation type",
        [
            "Bar",
            "Stacked bar",
            "Line",
            "Area",
            "Donut",
            "Treemap",
            "Scatter",
            "Histogram",
            "Box plot",
            "Violin"
        ],
        key="explorer_chart_type"
    )

    agg_map = {
        "Sum": "sum",
        "Mean": "mean",
        "Median": "median",
        "Count": "count"
    }

    grouped = (
        f.groupby(dimension, as_index=False)[measure]
        .agg(agg_map[aggregation])
    )

    grouped = grouped.rename(
        columns={measure: "value"}
    )

    grouped = grouped.sort_values(
        "value",
        ascending=False
    )

    if chart_type == "Bar":
        # Horizontal bars are easier to read for long product/category labels.
        bar_data = grouped.head(25).sort_values("value", ascending=True)
        fig = px.bar(
            bar_data,
            x="value",
            y=dimension,
            orientation="h",
            color=dimension,
            color_discrete_sequence=COLORS,
            hover_data={dimension: True, "value": ":,.2f"}
        )
        fig.update_yaxes(automargin=True, title_text="")
        fig.update_xaxes(title_text=measure.replace("_", " ").title(), automargin=True)

    elif chart_type == "Stacked bar":
        second = "sales_type" if dimension != "sales_type" else "category"

        stacked = (
            f.groupby([dimension, second], as_index=False)[measure]
            .sum()
        )

        stacked = stacked.groupby([dimension, second], as_index=False)[measure].sum()
        top_dims = (
            stacked.groupby(dimension)[measure].sum()
            .nlargest(20).index
        )
        stacked = stacked[stacked[dimension].isin(top_dims)]
        fig = px.bar(
            stacked,
            x=dimension,
            y=measure,
            color=second,
            barmode="stack",
            color_discrete_sequence=COLORS
        )
        fig.update_xaxes(tickangle=-35, automargin=True)

    elif chart_type == "Line":
        fig = px.line(
            grouped,
            x=dimension,
            y="value",
            markers=True
        )

    elif chart_type == "Area":
        fig = px.area(
            grouped,
            x=dimension,
            y="value"
        )

    elif chart_type == "Donut":
        fig = px.pie(
            grouped,
            names=dimension,
            values="value",
            hole=.55
        )

    elif chart_type == "Treemap":
        fig = px.treemap(
            grouped,
            path=[dimension],
            values="value"
        )

    elif chart_type == "Scatter":
        if dimension == "sku_id":
            scatter_data = grouped.head(500)
        else:
            scatter_data = grouped

        fig = px.scatter(
            scatter_data,
            x=dimension,
            y="value",
            color=dimension
        )

    elif chart_type == "Histogram":
        fig = px.histogram(
            f,
            x=measure,
            nbins=35,
            color_discrete_sequence=[TEAL]
        )

    elif chart_type == "Box plot":
        fig = px.box(
            f,
            x=dimension,
            y=measure,
            color=dimension,
            points=False
        )

    else:
        fig = px.violin(
            f,
            x=dimension,
            y=measure,
            color=dimension,
            box=True,
            points=False
        )

    with st.container(border=True):
        show_chart(fig, 480)

    st.download_button(
        "Download chart data",
        grouped.to_csv(index=False).encode("utf-8"),
        "retailpulse_chart_data.csv",
        "text/csv"
    )


# =========================================================
# 17. DATA EXPLORER
# =========================================================

elif page == "Data Explorer":

    st.subheader("Filtered sales dataset")

    a, b, c = st.columns(3)

    a.metric("Rows", f"{len(f):,}")
    b.metric("Columns", f"{len(f.columns):,}")
    c.metric("Missing values", f"{int(f.isna().sum().sum()):,}")

    show_table(
        f.head(5000),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    st.download_button(
        "Download filtered sales data",
        f.to_csv(index=False).encode("utf-8"),
        "retailpulse_sales_data.csv",
        "text/csv"
    )

    st.divider()

    st.subheader("Data quality indicators")

    quality_data = pd.DataFrame({
        "Metric": [
            "Sales rows",
            "Missing dates",
            "Missing store IDs",
            "Missing SKU IDs",
            "Negative sales rows",
            "Negative quantity rows",
            "Duplicate rows"
        ],
        "Value": [
            len(f),
            int(f["date"].isna().sum()),
            int(f["store_id"].isna().sum()),
            int(f["sku_id"].isna().sum()),
            int((f["sales"] < 0).sum()),
            int((f["quantity"] < 0).sum()),
            int(f.duplicated().sum())
        ]
    })

    show_table(
        quality_data,
        use_container_width=True,
        hide_index=True
    )

    if not inv_filtered.empty:
        st.subheader("Inventory data quality")

        inv_quality = pd.DataFrame({
            "Metric": [
                "Inventory rows",
                "Negative stock rows",
                "Missing inventory dates",
                "Duplicate inventory rows"
            ],
            "Value": [
                len(inv_filtered),
                int((inv_filtered["on_hand"] < 0).sum()),
                int(inv_filtered["date"].isna().sum()),
                int(inv_filtered.duplicated().sum())
            ]
        })

        show_table(
            inv_quality,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# 18. PROJECT AND METHODOLOGY
# =========================================================

elif page == "Project & Methodology":

    st.markdown("## RetailPulse")
    st.markdown(
        "Retail sales and inventory intelligence using Python, "
        "Pandas, SQLite, Streamlit and Plotly."
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            panel_heading("Project architecture")

            st.markdown("""
            **Source data**

            - Retail sales CSV
            - Retail inventory CSV

            **ETL pipeline**

            - Source column canonicalisation
            - Date and numeric conversion
            - Data-quality profiling
            - Derived business metrics

            **Warehouse**

            - SQLite
            - `fact_sales`
            - `fact_inventory`
            - `data_quality_runs`

            **Analytics**

            - Pandas
            - SQL
            - Plotly
            - Streamlit
            """)

    with c2:
        with st.container(border=True):
            panel_heading("Business metrics")

            st.markdown("""
            | Metric | Definition |
            |---|---|
            | Net sales | Sum of signed sales amounts |
            | Gross profit | Sales minus COGS |
            | Gross margin | Profit divided by sales |
            | Return rate | Return records / sales records |
            | Net units | Sum of signed quantities |
            | Stock units | Sum of inventory on-hand units |
            | Stock value | Sum of inventory selling value |
            """)

    st.divider()

    st.subheader("Dataset information")

    st.write(
        "Source: Retail Transactions and Stocks Data, "
        "Jimmy Smith, Mendeley Data."
    )

    st.link_button(
        "Open dataset source",
        "https://data.mendeley.com/datasets/27x8mjm8k4/1"
    )

    st.caption(
        "The sales data currently covers 1 June 2025 to 24 April 2026. "
        "Dataset publication date does not imply complete FY 2026–27 coverage."
    )

    st.warning(
        "The source currency has not been verified. Monetary values "
        "are displayed without a currency symbol. Return and inventory "
        "date semantics should be considered when interpreting KPIs."
    )

    st.divider()

    st.markdown("### Technology stack")

    st.markdown(
        "`Python` · `Pandas` · `NumPy` · `SQLite` · "
        "`Streamlit` · `Plotly` · `Pytest`"
    )

    st.caption("RetailPulse · Retail analytics portfolio project")
