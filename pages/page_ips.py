import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from textwrap import dedent
from logic.extractor import parse_pasted_text, parse_csv_dataframe
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary, generate_trading_signals
from logic.ips_engine import calculate_ips, assess_alignment
from logic.monte_carlo import run_monte_carlo
from logic.pdf_generator import generate_pdf_report
from ui.styles import inject_styles
from ui.components import hero_section


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


def render_ips_page():
    """Render Page 1: IPS Builder Form"""
    inject_styles()
    
    # Get base currency from session state or default to CAD
    base_currency = st.session_state.get('base_currency', 'CAD')
    
    # Render hero section
    st.markdown(hero_section(), unsafe_allow_html=True)
    
    st.markdown("""
<style>
.piq-usp * { box-sizing: border-box; }
.piq-usp {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 0 0 40px 0;
}
.piq-usp-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 28px 24px;
}
.piq-usp-card-1 { border-top: 4px solid #1a3d6e; }
.piq-usp-card-2 { border-top: 4px solid #c9943a; }
.piq-usp-card-3 { border-top: 4px solid #1a6e4a; }
.piq-usp-icon {
    width: 42px; height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    font-size: 22px;
    line-height: 1;
}
.piq-usp-icon-1 { background: #dbeafe; }
.piq-usp-icon-2 { background: #fef3c7; }
.piq-usp-icon-3 { background: #dcfce7; }
.piq-usp-title {
    font-size: 16px;
    font-weight: 700;
    color: #0d1117;
    margin-bottom: 10px;
    font-family: Georgia, serif;
    letter-spacing: -0.2px;
    line-height: 1.3;
}
.piq-usp-body {
    font-size: 14px;
    color: #64748b;
    line-height: 1.7;
    font-family: Arial, sans-serif;
}
</style>

<div class="piq-usp">
  <div class="piq-usp-card piq-usp-card-1">
    <div class="piq-usp-icon piq-usp-icon-1">&#128737;</div>
    <div class="piq-usp-title">IPS-Driven Analysis</div>
    <div class="piq-usp-body">Every metric, target, and alert is calibrated
    to your client&rsquo;s Investment Policy Statement &mdash; 
    not generic benchmarks.</div>
  </div>
  <div class="piq-usp-card piq-usp-card-2">
    <div class="piq-usp-icon piq-usp-icon-2">&#128200;</div>
    <div class="piq-usp-title">Institutional-Grade Risk Tools</div>
    <div class="piq-usp-body">Volatility, beta, correlation matrix, drawdown,
    Monte Carlo simulations &mdash; the same toolkit used by 
    professional portfolio managers.</div>
  </div>
  <div class="piq-usp-card piq-usp-card-3">
    <div class="piq-usp-icon piq-usp-icon-3">&#9889;</div>
    <div class="piq-usp-title">Portfolio Analysis in Minutes</div>
    <div class="piq-usp-body">Answer 5 questions, get your IPS, input or 
    upload portfolio, get analysis, download PDF tear sheet.</div>
  </div>
</div>
""", unsafe_allow_html=True)
    
    # Onboarding UI
    if st.session_state.app_step == 'onboarding':
        # Use native Streamlit container with custom styling
        with st.container(border=True):
            # Apply custom card styling via CSS targeting the Streamlit container
            st.markdown("""
<style>
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 44px !important;
    box-shadow: 0 2px 16px rgba(13,17,23,0.06) !important;
}
.piq-eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: #2556a0;
    margin-bottom: 8px;
    font-family: Arial, sans-serif;
}
.piq-form-title {
    font-size: 30px;
    font-weight: 700;
    color: #0d1117;
    letter-spacing: -0.5px;
    margin: 0 0 10px 0;
    font-family: Georgia, serif;
    line-height: 1.15;
}
.piq-form-desc {
    font-size: 15px;
    color: #64748b;
    line-height: 1.65;
    margin: 0 0 32px 0;
    font-family: Arial, sans-serif;
}
.piq-section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 20px 0;
}
.piq-section-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: #dbeafe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.piq-section-title {
    font-size: 16px;
    font-weight: 700;
    color: #0d1117;
    font-family: Arial, sans-serif;
    line-height: 1.3;
}
.piq-section-sub {
    font-size: 13px;
    color: #94a3b8;
    font-family: Arial, sans-serif;
}
.piq-divider {
    height: 1px;
    background: #f1f5f9;
    margin: 32px 0;
}
</style>

<div class="piq-eyebrow">Step 1 of 3</div>
<div class="piq-form-title">Define Your Investment Policy</div>
<div class="piq-form-desc">Answer a few questions to create your 
personalized Investment Policy Statement. This guides every 
metric and alignment check in the analysis.</div>

<div class="piq-section-header">
  <div class="piq-section-icon">&#9201;</div>
  <div>
    <div class="piq-section-title">Time Horizon &amp; Liquidity</div>
    <div class="piq-section-sub">When will you need to access this capital?</div>
  </div>
</div>
""", unsafe_allow_html=True)
            
            time_horizon = st.slider(
                'How long until you need to withdraw a significant portion of this money?',
                min_value=1,
                max_value=30,
                value=10,
                format='%d Years',
                help='Longer time horizons generally allow you to take on more risk because you have time to recover from market dips.'
            )
            
            liquidity = st.select_slider(
                'What portion of your portfolio might you need in cash within the next 12 months?',
                options=['None (0%)', 'Low (< 10%)', 'Moderate (10-25%)', 'High (> 25%)'],
                value='Low (< 10%)',
                help='Money you need in cash soon should not be exposed to the stock market. High liquidity needs require a more conservative approach.'
            )
            
            st.markdown("""
<div class="piq-divider"></div>
<div class="piq-section-header">
  <div class="piq-section-icon" style="background:#fef3c7;">&#127919;</div>
  <div>
    <div class="piq-section-title">Investment Objectives</div>
    <div class="piq-section-sub">What is the primary goal for this portfolio?</div>
  </div>
</div>
""", unsafe_allow_html=True)
            
            objective = st.radio(
                'What is your primary goal?',
                ['Capital Preservation', 'Steady Income', 'Balanced Growth', 'Maximum Capital Appreciation'],
                horizontal=True,
                help='Capital preservation protects what you have. Income generates cash flow. Growth aims to increase the total value of your assets over time.'
            )
            
            st.markdown("""
<div class="piq-divider"></div>
<div class="piq-section-header">
  <div class="piq-section-icon" style="background:#fce7f3;">&#128200;</div>
  <div>
    <div class="piq-section-title">Risk Tolerance</div>
    <div class="piq-section-sub">How do you respond to market volatility?</div>
  </div>
</div>
""", unsafe_allow_html=True)
            
            crash_reaction = st.radio(
                'If your portfolio dropped 20% in one month, what would you do?',
                ['Sell to avoid further losses', 'Do nothing and wait', 'Buy more at a discount'],
                horizontal=True,
                help='This measures your emotional tolerance for risk. Panic selling locks in losses, while buying the dip requires strong risk tolerance.'
            )
            
            knowledge = st.select_slider(
                'How would you rate your investment experience?',
                options=['Novice', 'Intermediate', 'Advanced', 'Expert'],
                value='Intermediate'
            )
            
            st.markdown('<div class="piq-divider"></div>', unsafe_allow_html=True)
            
            if st.button('Generate My IPS', use_container_width=True):
                profile, targets = calculate_ips(time_horizon, liquidity, objective, crash_reaction, knowledge)
                st.session_state.ips_profile = profile
                st.session_state.ips_targets = targets
                st.session_state.app_step = 'analysis'
                st.rerun()
    
    # Compact IPS banner
    if st.session_state.ips_profile and st.session_state.ips_targets:
        st.markdown(f"""
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            background:#d6e4f7;
            border:1px solid #2556a0;
            border-radius:10px;
            padding:12px 20px;
            margin-bottom:20px;
            font-family:'DM Sans',sans-serif;
        ">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="color:#4ade80;font-size:10px;">●</span>
                <span style="font-size:13px;font-weight:600;color:#1a3d6e;">
                    Active IPS: {st.session_state.ips_profile}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("↺ Reset IPS", use_container_width=True):
                st.session_state.app_step = 'onboarding'
                st.session_state.ips_profile = None
                st.session_state.ips_targets = None
                st.session_state.pdf_data = None
                st.rerun()
