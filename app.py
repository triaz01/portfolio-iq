import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf
from datetime import datetime
from logic.extractor import parse_pasted_text, parse_csv_dataframe
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary, generate_trading_signals
from logic.ips_engine import calculate_ips, assess_alignment
from logic.monte_carlo import run_monte_carlo
from logic.pdf_generator import generate_pdf_report

st.set_page_config(page_title='Portfolio Analyzer', layout='wide', initial_sidebar_state='collapsed')

def smart_format_ticker(ticker):
    """
    Smart ticker auto-correction for Canadian stocks.
    
    Logic:
    1. Strip whitespace and convert to uppercase
    2. If ticker contains a dot, return as-is (e.g., XIU.TO, BTC-USD)
    3. Check if ticker exists on US exchanges
    4. If US ticker is invalid, try appending .TO for TSX
    5. Return the valid ticker or original if neither works
    """
    # Step 1: Clean and uppercase
    ticker = ticker.strip().upper()
    
    # Step 2: If already has a dot, return as-is
    if '.' in ticker:
        return ticker
    
    # Step 3: Check US exchanges first
    try:
        hist = yf.Ticker(ticker).history(period='1d')
        if not hist.empty:
            return ticker  # US ticker is valid
    except:
        pass  # Continue to TSX check
    
    # Step 4: Try .TO suffix for TSX
    try:
        tsx_ticker = ticker + '.TO'
        hist_tsx = yf.Ticker(tsx_ticker).history(period='1d')
        if not hist_tsx.empty:
            return tsx_ticker  # TSX ticker is valid
    except:
        pass  # Fall through to return original
    
    # Step 5: Return original ticker and let downstream error handling catch it
    return ticker

def build_growth_chart(chart_data):
    """Build a styled Plotly line chart for portfolio growth trajectory."""
    colors = ['#1e3a8a', '#82ca9d', '#f59e0b']
    fig = px.line(
        chart_data,
        labels={"value": "Growth Multiplier", "index": "Date", "variable": "Series"},
        color_discrete_sequence=colors
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Growth Multiplier (Starting at 1.0)",
        xaxis_title="",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#4a5568')),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
        font=dict(color='#4a5568')
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
    fig.update_yaxes(showgrid=False, tickformat=".1f", tickfont=dict(color='#4a5568'))
    return fig

# Initialize tutorial session state
if 'tutorial_seen' not in st.session_state:
    st.session_state.tutorial_seen = False

# ── TOP NAV ──────────────────────────────────────────
nav_col1, nav_col2 = st.columns([1, 1])
with nav_col1:
    st.markdown(
        '<div style="'
        'display:flex;align-items:center;gap:12px;'
        'padding:8px 0;'
        '">'
        '<img src="app/static/logo.png" '
        'style="height:36px;width:auto;" '
        'alt="PortfolioIQ" '
        'onerror="this.style.display=\'none\';'
        'this.nextElementSibling.style.display=\'flex\';">'
        '<div style="'
        'display:none;'  
        'align-items:center;gap:10px;'
        '">'
        '<div style="'
        'width:32px;height:32px;border-radius:8px;'
        'background:#1a3d6e;'
        'display:flex;align-items:center;'
        'justify-content:center;'
        'font-size:16px;'
        '">📊</div>'
        '<span style="'
        'font-family:DM Serif Display,Georgia,serif;'
        'font-size:20px;color:#0d1117;letter-spacing:-0.3px;'
        '">Portfolio<span style="color:#2556a0;">IQ</span>'
        '</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
with nav_col2:
    st.session_state['base_currency'] = st.selectbox(
        'Currency',
        ['CAD', 'USD'],
        index=0,
        label_visibility='collapsed'
    )
st.markdown(
        '<hr style="border:none;border-top:1px solid #e4e4dc;'
        'margin:4px 0 16px 0;">',
        unsafe_allow_html=True
    )
# ── END TOP NAV ───────────────────────────────────────

# Design System CSS
st.markdown("""
<style>
    /* Global background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Card containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 15px;
        border: none;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Dark blue buttons */
    .stButton>button {
        border-radius: 20px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        background: #1e3a8a;
        color: #ffffff;
        border: 1px solid #1e3a8a;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #2563eb;
        border-color: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Tutorial styles */
    .tutorial-step {
        text-align: center;
        padding: 1rem;
    }
    .tutorial-step-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .tutorial-step-title {
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .tutorial-step-desc {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Investor summary */
    .investor-summary {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.7;
        padding: 0.5rem 0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'app_step' not in st.session_state:
    st.session_state.app_step = 'onboarding'
if 'ips_profile' not in st.session_state:
    st.session_state.ips_profile = None
if 'ips_targets' not in st.session_state:
    st.session_state.ips_targets = None
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'current_metrics' not in st.session_state:
    st.session_state.current_metrics = None
if 'current_portfolio' not in st.session_state:
    st.session_state.current_portfolio = None
if 'current_chart' not in st.session_state:
    st.session_state.current_chart = None

# Page routing logic
if st.session_state.app_step == 'onboarding':
    from pages.page_ips import render_ips_page
    render_ips_page()
elif st.session_state.app_step == 'analysis':
    from pages.page_analyzer import render_analyzer_page
    render_analyzer_page()
