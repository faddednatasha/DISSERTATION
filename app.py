"""
╔══════════════════════════════════════════════════════════════════════════╗
║   GEOPOLITICAL SHOCK & VOLATILITY ANALYZER — Indian Stock Market        ║
║   Built with: Streamlit · yfinance · ARCH · Plotly                      ║
║   Inspired by: MBA Dissertation — Aayushi Tewari, UPES 2026             ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import warnings
warnings.filterwarnings("ignore")

from events_data import GEOPOLITICAL_EVENTS, CATEGORIES, REGIONS, CATEGORY_COLORS
from volatility_models import (
    compute_rolling_volatility,
    compute_garch_volatility,
    compute_tarch_volatility,
    compute_event_impact,
)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Geopolitical Shock & Volatility Analyzer",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (Slate & Emerald Theme) ────────────────────────────────────────
st.markdown("""
<style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #f8fafc;
        color: #334155;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.25rem; font-weight: 700; color: #0f172a;
        padding-bottom: 0.5rem; margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    .section-header {
        font-size: 1.25rem; font-weight: 600; color: #0f172a;
        margin-top: 1.75rem; margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }
    
    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #475569 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    /* Badges & Tables */
    .event-badge {
        display: inline-block; padding: 2px 10px; border-radius: 6px;
        font-size: 0.75rem; font-weight: 600; color: white; margin-right: 5px;
    }
    
    /* Sidebar Styling Override */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/NSE_Logo.svg/320px-NSE_Logo.svg.png", width=120)
    st.markdown("## ⚙️ Settings")

    index_choice = st.selectbox(
        "Select Index",
        ["NIFTY 50 (^NSEI)", "BSE SENSEX (^BSESN)", "NIFTY Bank (^NSEBANK)"],
        index=0,
    )
    TICKER_MAP = {
        "NIFTY 50 (^NSEI)":      "^NSEI",
        "BSE SENSEX (^BSESN)":   "^BSESN",
        "NIFTY Bank (^NSEBANK)": "^NSEBANK",
    }
    ticker = TICKER_MAP[index_choice]

    st.markdown("### 📅 Date Range")
    start_date = st.date_input("Start Date", value=date(2015, 1, 1), min_value=date(2000, 1, 1))
    end_date   = st.date_input("End Date",   value=date.today())

    st.markdown("### 🌍 Filter Events")
    sel_categories = st.multiselect("Event Category", CATEGORIES, default=CATEGORIES)
    sel_regions    = st.multiselect("Region", REGIONS, default=REGIONS)
    sel_severity   = st.multiselect("Severity", ["High", "Medium"], default=["High", "Medium"])

    st.markdown("### 📊 Volatility Settings")
    rolling_window = st.slider("Rolling Vol Window (days)", 5, 63, 21)
    event_window   = st.slider("Event Impact Window (days)", 5, 30, 10)

    show_garch = st.checkbox("Show GARCH(1,1)", value=True)
    show_tarch = st.checkbox("Show TARCH(1,1) — Asymmetric", value=True)

    st.markdown("---")
    st.caption("📚 Based on MBA Dissertation:\n*Time-Series Analysis of Market Liquidity & Volatility Clusters* — Aayushi Tewari, UPES 2026")

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data(ticker, start, end):
    df = yf.download(ticker, start=str(start), end=str(end), progress=False, auto_adjust=True)
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    df["Returns"] = df["Close"].pct_change()
    return df

# ── Filter Events ─────────────────────────────────────────────────────────────
def filter_events(events, start, end, categories, regions, severities):
    filtered = []
    for e in events:
        edate = pd.Timestamp(e["date"])
        if (edate >= pd.Timestamp(start) and edate <= pd.Timestamp(end)
                and e["category"] in categories
                and e["region"] in regions
                and e["severity"] in severities):
            filtered.append(e)
    return filtered

# ── Main App ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">Geopolitical Shock & Volatility Analyzer</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #475569; margin-top:-10px;'>Investigate how global geopolitical events drive volatility clusters in the Indian stock market.</p>", unsafe_allow_html=True)

# Data source info
st.markdown("""
<div style="background:#f1f5f9; border-left:4px solid #6366f1; border-radius:6px; padding:12px 16px; margin-bottom:20px; font-size:0.88rem; color:#334155;">
    📡 <b>Live Market Data:</b> Fetched via <b>yfinance</b> (Yahoo Finance API) —
    NIFTY 50 (<code>^NSEI</code>), BSE SENSEX (<code>^BSESN</code>), NIFTY Bank (<code>^NSEBANK</code>).
    Refreshes every <b>1 hour</b>. &nbsp;|&nbsp;
    🌍 <b>Geopolitical Events:</b> Curated from dissertation research (Chapter 5) + public financial news.
    &nbsp;|&nbsp; 📅 <b>History:</b> Jan 2000 → Today.
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("⏳ Fetching market data..."):
    df = load_market_data(ticker, start_date, end_date)

if df is None or df.empty:
    st.error("❌ Could not fetch data. Check your internet connection or try a different date range.")
    st.stop()

returns = df["Returns"].dropna()

# Filter events
active_events = filter_events(
    GEOPOLITICAL_EVENTS, start_date, end_date,
    sel_categories, sel_regions, sel_severity
)

# ── TOP KPI ROW ───────────────────────────────────────────────────────────────
latest_close  = float(df["Close"].iloc[-1])
prev_close    = float(df["Close"].iloc[-2])
day_change    = (latest_close - prev_close) / prev_close * 100
total_return  = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
annualised_vol = returns.std() * np.sqrt(252) * 100
max_drawdown  = ((df["Close"] / df["Close"].cummax()) - 1).min() * 100

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📈 Latest Close",    f"{latest_close:,.2f}", f"{day_change:+.2f}%")
col2.metric("📊 Period Return",   f"{float(total_return):.1f}%")
col3.metric("🌊 Avg Annual Vol",  f"{float(annualised_vol):.1f}%")
col4.metric("📉 Max Drawdown",    f"{float(max_drawdown):.1f}%")
col5.metric("🌍 Events Shown",    len(active_events))

st.markdown("<hr style='border-color:#e2e8f0; margin: 24px 0;'/>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Price & Events", "🌊 Volatility Analysis", "🔍 Event Impact Deep-Dive", "📋 Model Parameters"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Price Chart + Geopolitical Event Markers
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Price History with Geopolitical Event Markers</div>', unsafe_allow_html=True)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.7, 0.3],
        subplot_titles=("Index Price (Log Scale)", "Daily Returns (%)"),
        vertical_spacing=0.08
    )

    # Price line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        name="Close Price", line=dict(color="#0f172a", width=1.5),
        hovertemplate="%{x|%d %b %Y}<br>Close: %{y:,.2f}<extra></extra>"
    ), row=1, col=1)

    # Event markers
    for ev in active_events:
        edate = pd.Timestamp(ev["date"])
        if edate in df.index or (df.index[0] <= edate <= df.index[-1]):
            idx = df.index.searchsorted(edate)
            if idx < len(df):
                price_at_event = float(df["Close"].iloc[idx])
                color = CATEGORY_COLORS.get(ev["category"], "#6366f1")
                fig.add_vline(
                    x=edate, line_width=1.5,
                    line_dash="dot", line_color=color, row=1, col=1
                )
                fig.add_annotation(
                    x=edate, y=price_at_event * 1.02,
                    text=f"▼ {ev['event'][:28]}",
                    showarrow=False, font=dict(size=8, color=color),
                    textangle=-60, row=1, col=1
                )

    # Daily returns bar
    colors_ret = ["#ef4444" if r < 0 else "#10b981" for r in df["Returns"].fillna(0)]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Returns"] * 100,
        name="Daily Return %", marker_color=colors_ret, opacity=0.7,
        hovertemplate="%{x|%d %b %Y}<br>Return: %{y:.2f}%<extra></extra>"
    ), row=2, col=1)

    fig.update_yaxes(type="log", row=1, col=1, title_text="Price (Log)", title_font=dict(color="#334155"))
    fig.update_yaxes(row=2, col=1, title_text="Return %", title_font=dict(color="#334155"))
    fig.update_layout(
        height=600, showlegend=False,
        plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
        margin=dict(l=60, r=20, t=50, b=40),
        hovermode="x unified",
        font=dict(color="#334155")
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    st.plotly_chart(fig, use_container_width=True)

    # Event legend
    st.markdown("**Event Categories:**")
    cols = st.columns(len(CATEGORY_COLORS))
    for i, (cat, color) in enumerate(CATEGORY_COLORS.items()):
        cols[i % len(cols)].markdown(
            f'<span class="event-badge" style="background:{color}">{cat}</span>',
            unsafe_allow_html=True
        )

    # Event table
    if active_events:
        st.markdown('<div class="section-header">📋 Geopolitical Events in Selected Period</div>', unsafe_allow_html=True)
        ev_df = pd.DataFrame(active_events)[["date", "event", "category", "region", "severity", "description"]]
        ev_df.columns = ["Date", "Event", "Category", "Region", "Severity", "Description"]
        ev_df = ev_df.sort_values("Date", ascending=False)
        st.dataframe(ev_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Volatility Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Volatility Comparison: Rolling Std Dev vs GARCH vs TARCH</div>', unsafe_allow_html=True)

    # Compute volatilities
    rolling_vol = compute_rolling_volatility(returns, window=rolling_window)

    garch_vol, garch_summary = None, None
    tarch_vol, tarch_summary = None, None

    with st.spinner("Fitting GARCH(1,1)..."):
        if show_garch:
            garch_vol, garch_summary = compute_garch_volatility(returns)

    with st.spinner("Fitting TARCH(1,1)..."):
        if show_tarch:
            tarch_vol, tarch_summary = compute_tarch_volatility(returns)

    # Plot
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=rolling_vol.index, y=rolling_vol,
        name=f"Rolling Vol ({rolling_window}d)", line=dict(color="#6366f1", width=1.5),
        hovertemplate="%{x|%d %b %Y}<br>Rolling Vol: %{y:.1f}%<extra></extra>"
    ))

    if show_garch and garch_vol is not None:
        fig2.add_trace(go.Scatter(
            x=garch_vol.index, y=garch_vol,
            name="GARCH(1,1)", line=dict(color="#334155", width=1.5, dash="dash"),
            hovertemplate="%{x|%d %b %Y}<br>GARCH Vol: %{y:.1f}%<extra></extra>"
        ))
    elif show_garch and isinstance(garch_summary, str):
        st.warning(f"GARCH fitting issue: {garch_summary}")

    if show_tarch and tarch_vol is not None:
        fig2.add_trace(go.Scatter(
            x=tarch_vol.index, y=tarch_vol,
            name="TARCH(1,1) — Asymmetric", line=dict(color="#ef4444", width=1.5, dash="dot"),
            hovertemplate="%{x|%d %b %Y}<br>TARCH Vol: %{y:.1f}%<extra></extra>"
        ))
    elif show_tarch and isinstance(tarch_summary, str):
        st.warning(f"TARCH fitting issue: {tarch_summary}")

    # Add event markers
    for ev in active_events:
        edate = pd.Timestamp(ev["date"])
        color = CATEGORY_COLORS.get(ev["category"], "#6366f1")
        fig2.add_vline(x=edate, line_width=1, line_dash="dot", line_color=color, opacity=0.4)

    fig2.update_layout(
        height=450, title="Annualised Conditional Volatility (%) — All Models",
        yaxis_title="Volatility (%)", xaxis_title="",
        plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=60, b=40), hovermode="x unified",
        font=dict(color="#334155")
    )
    fig2.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig2.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    st.plotly_chart(fig2, use_container_width=True)

    # Volatility distribution
    st.markdown('<div class="section-header">📊 Return Distribution & Volatility Clustering</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=returns * 100, nbinsx=100,
            marker_color="#6366f1", opacity=0.75, name="Daily Returns"
        ))
        fig_hist.update_layout(
            title="Return Distribution (Fat Tails = Volatility Clustering)",
            xaxis_title="Daily Return (%)", yaxis_title="Frequency",
            height=320, plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
            margin=dict(l=50, r=20, t=50, b=40), showlegend=False,
            font=dict(color="#334155")
        )
        fig_hist.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
        fig_hist.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        sq_returns = (returns ** 2) * 100
        fig_sq = go.Figure()
        fig_sq.add_trace(go.Scatter(
            x=sq_returns.index, y=sq_returns,
            line=dict(color="#ef4444", width=0.8), name="Squared Returns"
        ))
        fig_sq.update_layout(
            title="Squared Returns — Visualising Volatility Clusters",
            xaxis_title="", yaxis_title="Squared Return × 100",
            height=320, plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
            margin=dict(l=50, r=20, t=50, b=40), showlegend=False,
            font=dict(color="#334155")
        )
        for ev in active_events:
            edate = pd.Timestamp(ev["date"])
            fig_sq.add_vline(x=edate, line_width=0.8, line_dash="dot",
                             line_color=CATEGORY_COLORS.get(ev["category"], "#6366f1"), opacity=0.4)
        fig_sq.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
        fig_sq.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
        st.plotly_chart(fig_sq, use_container_width=True)

    # Descriptive stats
    st.markdown('<div class="section-header">📐 Descriptive Statistics</div>', unsafe_allow_html=True)
    stats = {
        "Mean Daily Return (%)":    f"{returns.mean()*100:.4f}",
        "Std Dev Daily Return (%)": f"{returns.std()*100:.4f}",
        "Skewness":                 f"{returns.skew():.4f}",
        "Kurtosis (Excess)":        f"{returns.kurt():.4f}",
        "Min Return (%)":           f"{returns.min()*100:.2f}",
        "Max Return (%)":           f"{returns.max()*100:.2f}",
        "Ann. Volatility (%)":      f"{returns.std()*np.sqrt(252)*100:.2f}",
        "Observations":             f"{len(returns):,}",
    }
    stats_df = pd.DataFrame(stats.items(), columns=["Metric", "Value"])
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Event Impact Deep Dive
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🔍 Event Impact Deep-Dive</div>', unsafe_allow_html=True)
    st.info(f"Comparing market behaviour **{event_window} days before** vs **{event_window} days after** each geopolitical event.")

    if not active_events:
        st.warning("No events match your current filters.")
    else:
        # Compute impact for all events
        impact_rows = []
        for ev in active_events:
            impact = compute_event_impact(df[["Close"]], ev["date"], window=event_window)
            if impact:
                impact_rows.append({
                    "Event": ev["event"],
                    "Date": ev["date"],
                    "Category": ev["category"],
                    "Severity": ev["severity"],
                    "Event Day Ret (%)": impact["event_day_return"],
                    f"Pre-{event_window}d Ret (%)": impact["pre_cum_return"],
                    f"Post-{event_window}d Ret (%)": impact["post_cum_return"],
                    "Pre Vol (Ann%)": impact["pre_volatility"],
                    "Post Vol (Ann%)": impact["post_volatility"],
                    "Vol Change (%)": impact["vol_change_pct"],
                })

        if impact_rows:
            impact_df = pd.DataFrame(impact_rows).sort_values("Date", ascending=False)

            # Summary bar chart
            fig3 = go.Figure()
            colors = ["#ef4444" if v > 0 else "#10b981" for v in impact_df["Vol Change (%)"]]
            fig3.add_trace(go.Bar(
                x=impact_df["Event"],
                y=impact_df["Vol Change (%)"],
                marker_color=colors,
                text=[f"{v:+.1f}%" for v in impact_df["Vol Change (%)"]],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Vol Change: %{y:+.1f}%<extra></extra>"
            ))
            fig3.update_layout(
                title=f"Volatility Change After Each Geopolitical Event (Post vs Pre {event_window} days)",
                xaxis_title="", yaxis_title="Volatility Change (%)",
                height=400, plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
                xaxis_tickangle=-35, margin=dict(l=60, r=20, t=60, b=120),
                showlegend=False, font=dict(color="#334155")
            )
            fig3.add_hline(y=0, line_color="#0f172a", line_width=1)
            fig3.update_xaxes(showgrid=False)
            fig3.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
            st.plotly_chart(fig3, use_container_width=True)

            # Event day return chart
            fig4 = go.Figure()
            colors2 = ["#ef4444" if v < 0 else "#10b981"
                       for v in impact_df["Event Day Ret (%)"].fillna(0)]
            fig4.add_trace(go.Bar(
                x=impact_df["Event"],
                y=impact_df["Event Day Ret (%)"],
                marker_color=colors2,
                text=[f"{v:+.2f}%" if v is not None else "N/A"
                      for v in impact_df["Event Day Ret (%)"]],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Event Day Return: %{y:+.2f}%<extra></extra>"
            ))
            fig4.update_layout(
                title="Index Return on the Day of Each Event",
                xaxis_title="", yaxis_title="Return (%)",
                height=380, plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
                xaxis_tickangle=-35, margin=dict(l=60, r=20, t=60, b=120),
                showlegend=False, font=dict(color="#334155")
            )
            fig4.add_hline(y=0, line_color="#0f172a", line_width=1)
            fig4.update_xaxes(showgrid=False)
            fig4.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
            st.plotly_chart(fig4, use_container_width=True)

            # Table
            st.markdown('<div class="section-header">📋 Full Impact Table</div>', unsafe_allow_html=True)
            display_cols = ["Event", "Date", "Category", "Severity",
                            "Event Day Ret (%)", f"Pre-{event_window}d Ret (%)",
                            f"Post-{event_window}d Ret (%)", "Pre Vol (Ann%)",
                            "Post Vol (Ann%)", "Vol Change (%)"]
            st.dataframe(
                impact_df[display_cols].reset_index(drop=True),
                use_container_width=True, hide_index=True
            )

            # Single event zoom
            st.markdown('<div class="section-header">🔎 Zoom into a Single Event</div>', unsafe_allow_html=True)
            event_names = [e["event"] for e in active_events]
            selected_event_name = st.selectbox("Select an event to zoom in", event_names)
            selected_ev = next((e for e in active_events if e["event"] == selected_event_name), None)

            if selected_ev:
                edate = pd.Timestamp(selected_ev["date"])
                idx = df.index.searchsorted(edate)
                zoom_start = max(0, idx - 30)
                zoom_end   = min(len(df), idx + 31)
                zoom_df    = df.iloc[zoom_start:zoom_end]

                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(
                    x=zoom_df.index, y=zoom_df["Close"],
                    mode="lines+markers", line=dict(color="#0f172a", width=2),
                    marker=dict(size=4), name="Close Price"
                ))
                
                edate_str = edate.strftime("%Y-%m-%d")
                fig5.add_shape(
                    type="line",
                    x0=edate_str, x1=edate_str, y0=0, y1=1,
                    xref="x", yref="paper",
                    line=dict(color="#ef4444", width=2, dash="solid")
                )
                fig5.add_annotation(
                    x=edate_str, y=0.97, xref="x", yref="paper",
                    text=f"◀ {selected_ev['event'][:30]}",
                    showarrow=False, font=dict(color="#ef4444", size=9),
                    xanchor="left", bgcolor="rgba(248, 250, 252, 0.8)"
                )
                # PRE shading
                fig5.add_shape(
                    type="rect",
                    x0=zoom_df.index[0].strftime("%Y-%m-%d"), x1=edate_str,
                    y0=0, y1=1, xref="x", yref="paper",
                    fillcolor="#6366f1", opacity=0.05, line_width=0
                )
                fig5.add_annotation(
                    x=zoom_df.index[0].strftime("%Y-%m-%d"), y=0.05,
                    xref="x", yref="paper",
                    text="PRE", showarrow=False,
                    font=dict(color="#6366f1", size=10, family="Arial Black"),
                    xanchor="left"
                )
                # POST shading
                fig5.add_shape(
                    type="rect",
                    x0=edate_str, x1=zoom_df.index[-1].strftime("%Y-%m-%d"),
                    y0=0, y1=1, xref="x", yref="paper",
                    fillcolor="#ef4444", opacity=0.05, line_width=0
                )
                fig5.add_annotation(
                    x=zoom_df.index[-1].strftime("%Y-%m-%d"), y=0.05,
                    xref="x", yref="paper",
                    text="POST", showarrow=False,
                    font=dict(color="#ef4444", size=10, family="Arial Black"),
                    xanchor="right"
                )
                fig5.update_layout(
                    title=f"±30 Days Around: {selected_ev['event']} ({selected_ev['date']})",
                    height=360, plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
                    margin=dict(l=60, r=20, t=60, b=40), showlegend=False,
                    font=dict(color="#334155")
                )
                fig5.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
                fig5.update_yaxes(showgrid=True, gridcolor="#e2e8f0", title_text="Price")
                st.plotly_chart(fig5, use_container_width=True)

                st.info(f"**📝 Event Context:** {selected_ev['description']}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Model Parameters
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📋 GARCH & TARCH Model Parameters</div>', unsafe_allow_html=True)
    st.markdown("These parameters describe how volatility behaves in the selected index and time period. Based on the methodology from the MBA dissertation.")

    col_g, col_t = st.columns(2)

    with col_g:
        st.markdown("#### GARCH(1,1) — Symmetric Model")
        st.markdown("Assumes positive and negative shocks have *equal* impact on volatility.")
        if show_garch:
            if garch_vol is not None and isinstance(garch_summary, dict):
                st.success("✅ Model fitted successfully")
                params = {
                    "ω (Omega) — Base Variance":        garch_summary["omega"],
                    "α (Alpha) — ARCH Effect":          garch_summary["alpha"],
                    "β (Beta) — GARCH Persistence":     garch_summary["beta"],
                    "α + β (Persistence)":              garch_summary["persistence"],
                    "AIC":                              garch_summary["aic"],
                    "BIC":                              garch_summary["bic"],
                    "Log-Likelihood":                   garch_summary["log_likelihood"],
                }
                for k, v in params.items():
                    st.metric(k, v)
                if garch_summary["persistence"] > 0.95:
                    st.warning("⚠️ High persistence (>0.95) — volatility shocks are long-lasting.")
            else:
                st.error(f"Model error: {garch_summary}")
        else:
            st.info("Enable GARCH(1,1) in sidebar to view parameters.")

    with col_t:
        st.markdown("#### TARCH(1,1) — Asymmetric Model (GJR-GARCH)")
        st.markdown("Captures the **leverage effect** — bad news amplifies volatility more than good news.")
        if show_tarch:
            if tarch_vol is not None and isinstance(tarch_summary, dict):
                st.success("✅ Model fitted successfully")
                params = {
                    "ω (Omega) — Base Variance":        tarch_summary["omega"],
                    "α (Alpha) — ARCH Effect":          tarch_summary["alpha"],
                    "γ (Gamma) — Leverage/Asymmetry":   tarch_summary["gamma"],
                    "β (Beta) — GARCH Persistence":     tarch_summary["beta"],
                    "Persistence (α+β+0.5γ)":           tarch_summary["persistence"],
                    "Leverage Ratio (Bad/Good News)":    tarch_summary["leverage_ratio"],
                    "AIC":                              tarch_summary["aic"],
                    "BIC":                              tarch_summary["bic"],
                }
                for k, v in params.items():
                    st.metric(k, v)
                if tarch_summary["gamma"] > 0:
                    st.warning(f"📌 Leverage Effect Confirmed: γ = {tarch_summary['gamma']} > 0 — negative shocks amplify volatility ~{tarch_summary['leverage_ratio']}× more than positive shocks.")
            else:
                st.error(f"Model error: {tarch_summary}")
        else:
            st.info("Enable TARCH(1,1) in sidebar to view parameters.")

    st.markdown("<hr style='border-color:#e2e8f0; margin: 24px 0;'/>", unsafe_allow_html=True)
    st.markdown("#### 📖 How to Read These Parameters")
    st.markdown("""
| Parameter | What It Means |
|---|---|
| **α (Alpha)** | How much yesterday's shock affects today's volatility |
| **β (Beta)** | How much yesterday's volatility persists today |
| **α + β** | Total persistence — closer to 1 = shocks last longer |
| **γ (Gamma)** | Asymmetry — if γ > 0, bad news hits harder than good news |
| **Leverage Ratio** | How many times more bad news amplifies vol vs good news |
| **AIC / BIC** | Model fit — lower is better; use to compare GARCH vs TARCH |
    """)

    st.markdown("<hr style='border-color:#e2e8f0; margin: 24px 0;'/>", unsafe_allow_html=True)
    st.caption("Dissertation finding: TARCH(1,1) had γ = 0.1284 (p<0.001) on NIFTY 50 (2000–2026), confirming negative shocks amplify volatility ~2.44× more than positive shocks.")