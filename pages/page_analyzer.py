import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from logic.extractor import parse_pasted_text, parse_csv_dataframe
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary, generate_trading_signals
from logic.ips_engine import assess_alignment
from logic.monte_carlo import run_monte_carlo
from logic.pdf_generator import generate_pdf_report
from ui.styles import inject_styles
from ui.components import stat_card, signal_badge, ips_status_badge, alert_box, section_card_open, section_card_close


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


def render_analyzer_page():
    """Render Page 2: Portfolio Analyzer and Results Dashboard"""
    inject_styles()
    
    # Get base currency from session state or default to CAD
    base_currency = st.session_state.get('base_currency', 'CAD')
    
    # Compact IPS banner
    if st.session_state.ips_profile and st.session_state.ips_targets:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.info(f"🎯 **Active IPS**: {st.session_state.ips_profile}")
        with col2:
            if st.button("🔄 Reset IPS", use_container_width=True):
                st.session_state.app_step = 'onboarding'
                st.session_state.ips_profile = None
                st.session_state.ips_targets = None
                st.session_state.pdf_data = None
                st.rerun()
    
    # Data Ingestion Card
    with st.container(border=True):
        st.subheader('📥 Portfolio Data')
        input_method = st.radio(
            "Input Method",
            options=["Paste Text", "Upload CSV"],
            horizontal=True,
            label_visibility='collapsed'
        )
        
        if input_method == "Paste Text":
            pasted_text = st.text_area(
                "Enter your portfolio data (e.g., 'AAPL 100, MSFT 50, GOOGL 25')",
                height=150,
                placeholder="AAPL 100\nMSFT 50\nGOOGL 25",
                help='Paste your holdings directly from your brokerage account (Format: Ticker followed by Shares, e.g., AAPL 100).'
            )
            
            if st.button("Analyze Portfolio"):
                try:
                    portfolio = parse_pasted_text(pasted_text)
                    
                    if not portfolio:
                        st.error("No valid tickers found. Please check your input format.")
                    else:
                        with st.spinner("Fetching market data..."):
                            metrics = calculate_portfolio_metrics(portfolio, base_currency)
                        
                        if metrics is None:
                            st.error("Unable to fetch data for the provided tickers. Please verify ticker symbols.")
                        else:
                            st.session_state.current_metrics = metrics
                            st.session_state.current_portfolio = portfolio
                            st.session_state.current_chart = build_growth_chart(metrics['chart_data'])
                            st.success("✅ Analysis complete! Results are displayed below.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        
        elif input_method == "Upload CSV":
            # Create sample CSV template
            sample_csv = pd.DataFrame({
                'Ticker': ['AAPL', 'RY.TO', 'ZUH'],
                'Shares': [100, 50, 25]
            }).to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Sample CSV Template",
                data=sample_csv,
                file_name="portfolio_template.csv",
                mime="text/csv"
            )
            
            uploaded_file = st.file_uploader("Upload CSV (Ticker, Shares)", type=['csv'],
                                       help='Two-column CSV: Column 1 = Ticker Symbol, Column 2 = Number of Shares.')
            
            if uploaded_file is not None:
                try:
                    # Read the CSV file
                    df = pd.read_csv(uploaded_file)
                    st.success(f"CSV file loaded successfully! Found {len(df)} rows.")
                    
                    # Show preview of uploaded data
                    with st.expander("📊 Preview uploaded data"):
                        st.dataframe(df.head(10))
                    
                    if st.button("Analyze Portfolio"):
                        try:
                            # Parse CSV using our extractor
                            portfolio = parse_csv_dataframe(df)
                            
                            if not portfolio:
                                st.error("No valid tickers found in CSV. Please check your file format.")
                            else:
                                with st.spinner("Fetching market data..."):
                                    metrics = calculate_portfolio_metrics(portfolio, base_currency)
                                
                                if metrics is None:
                                    st.error("Unable to fetch data for the provided tickers. Please verify ticker symbols.")
                                else:
                                    st.session_state.current_metrics = metrics
                                    st.session_state.current_portfolio = portfolio
                                    st.session_state.current_chart = build_growth_chart(metrics['chart_data'])
                                    st.success("✅ Analysis complete! Results are displayed below.")
                        
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
        
        # Analysis Display Section - Shows cards based on session state
        if st.session_state.get('current_metrics'):
            metrics = st.session_state.current_metrics
            
            # Display ignored tickers warning if any
            if metrics.get('ignored_tickers') and len(metrics['ignored_tickers']) > 0:
                st.warning(f"⚠️ The following tickers were ignored due to insufficient data: {', '.join(metrics['ignored_tickers'])}")
            
            # Performance Metrics Card
            with st.container(border=True):
                st.subheader('📊 Portfolio Performance Metrics')
                
                # Create columns for metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Annual Return", f"{metrics['annualized_return'] * 100:.2f}%",
                            help='The average yearly return your portfolio has generated over the last 3 years.')
                
                with col2:
                    st.metric("Volatility", f"{metrics['annual_volatility'] * 100:.2f}%",
                            help='A measure of your portfolio\'s risk level. Higher volatility means larger price swings, which can be both good and bad.')
                
                with col3:
                    st.metric("Max Drawdown", f"{metrics['max_drawdown'] * 100:.2f}%",
                            help='The largest peak-to-trough decline your portfolio experienced. Lower is better.')
                
                with col4:
                    st.metric("Dividend Yield", f"{metrics['weighted_dividend_yield']:.2f}%",
                            help='The percentage of your portfolio\'s total value that is paid out to you in cash dividends over the course of a year.')
                
                with col5:
                    st.metric("Beta", f"{metrics['portfolio_beta']:.2f}",
                            help='How volatile your portfolio is relative to the market. Beta < 1 = less volatile, Beta > 1 = more volatile.')
                
                # Investor summary paragraph
                summary = generate_investor_summary(metrics)
                st.markdown(f'<p class="investor-summary">{summary}</p>', unsafe_allow_html=True)
            
            # Visualization Card
            with st.container(border=True):
                st.subheader('📊 3-Year Growth Trajectory')
                
                # Build chart if not yet in session state
                if not st.session_state.get('current_chart') or not hasattr(st.session_state.current_chart, 'data'):
                    st.session_state.current_chart = build_growth_chart(metrics['chart_data'])
                
                st.plotly_chart(st.session_state.current_chart, use_container_width=True)
            
            # Individual Stock Projections Card
            if 'projection_df' in metrics and not metrics['projection_df'].empty:
                with st.container(border=True):
                    st.subheader('🎯 Analyst Target Projections')
                    st.caption('Individual stock projections based on current analyst price targets.')
                    
                    # Format the projection dataframe for display
                    projection_display = metrics['projection_df'].copy()
                    projection_display['Current Price'] = projection_display['Current Price'].round(2)
                    projection_display['Target Price'] = projection_display['Target Price'].round(2)
                    projection_display['Current Value'] = projection_display['Current Value'].round(2)
                    projection_display['Projected Value'] = projection_display['Projected Value'].round(2)
                    
                    # Calculate upside percentage
                    projection_display['Upside %'] = ((projection_display['Target Price'] / projection_display['Current Price']) - 1) * 100
                    projection_display['Upside %'] = projection_display['Upside %'].round(2)
                    
                    # Calculate total portfolio values
                    current_total = projection_display['Current Value'].sum()
                    projected_total = projection_display['Projected Value'].sum()
                    total_upside = ((projected_total / current_total) - 1) * 100
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Portfolio Value", f"${current_total:,.0f}")
                    with col2:
                        st.metric("Projected Portfolio Value", f"${projected_total:,.0f}")
                    with col3:
                        st.metric("Total Upside Potential", f"{total_upside:.1f}%")
                    
                    st.markdown("---")
                    
                    # Reorder columns for better display (use original column names)
                    projection_display = projection_display[['Ticker', 'Shares', 'Current Price', 'Target Price', 'Upside %', 'Current Value', 'Projected Value']]
                    
                    # Rename columns for better readability
                    projection_display.columns = ['Ticker', 'Shares', 'Current Price ($)', 'Target Price ($)', 'Upside %', 'Current Value ($)', 'Projected Value ($)']
                    
                    # Add color coding based on upside/downside - apply to entire row
                    def color_projection_rows(row):
                        upside = row['Upside %']
                        if pd.isna(upside) or upside == 0:
                            return ['background-color: white'] * len(row)
                        elif upside > 0:
                            return ['background-color: #dcfce7; color: #166534'] * len(row)  # Light green
                        elif upside < 0:
                            return ['background-color: #fef2f2; color: #991b1b'] * len(row)  # Light red
                        else:
                            return ['background-color: white'] * len(row)
                    
                    # Apply styling to the dataframe - color entire row based on upside
                    styled_df = projection_display.style.apply(color_projection_rows, axis=1)
                    
                    # Format numeric columns to 2 decimal places
                    styled_df = styled_df.format({
                        'Current Price ($)': '{:.2f}',
                        'Target Price ($)': '{:.2f}',
                        'Upside %': '{:.2f}',
                        'Current Value ($)': '{:.2f}',
                        'Projected Value ($)': '{:.2f}'
                    })
                    
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Risk Analysis Card - Correlation Heatmap
            if metrics.get('correlation_matrix') is not None and not metrics['correlation_matrix'].empty:
                with st.container(border=True):
                    st.subheader('🔗 Asset Correlation Analysis')
                    
                    # Calculate correlation safely
                    corr_matrix = metrics['correlation_matrix']
                    
                    # Build the visual heatmap
                    fig_corr = px.imshow(
                        corr_matrix,
                        text_auto='.2f',
                        color_continuous_scale='Blues',
                        aspect='auto',
                    )
                    
                    # Update layout to match our UI
                    fig_corr.update_layout(
                        margin=dict(l=20, r=20, t=30, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Render the chart in Streamlit
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # Add interpretation caption
                    st.caption("📊 Correlation values range from -1 to 1. Values closer to 1 indicate assets that move together, while values closer to -1 indicate assets that move in opposite directions. Lower correlations generally provide better diversification.")
            
            # Trading Signals Card
            with st.container(border=True):
                st.subheader('🎯 Automated Trading Signals')
                st.caption('Analyzes medium-term momentum, 200-day trend, and 6-month relative strength against SPY to generate a durable, rules-based rating.')
                
                # Get list of tickers from portfolio
                tickers = list(st.session_state.current_portfolio.keys())
                
                # Generate trading signals automatically (cached for 1 hour)
                signals_df = generate_trading_signals(tickers)
                
                # Apply professional styling to entire row based on Recommendation
                def style_row(row):
                    recommendation = row['Recommendation']
                    if recommendation == 'Buy':
                        return ['background-color: #d4edda; color: #155724;'] * len(row)
                    elif recommendation == 'Hold':
                        return ['background-color: #fff3cd; color: #856404;'] * len(row)
                    elif recommendation == 'Sell / Avoid':
                        return ['background-color: #f8d7da; color: #721c24;'] * len(row)
                    else:
                        return ['background-color: #e2e8f0; color: #475569;'] * len(row)
                
                # Apply styling and formatting
                styled_signals = signals_df.style.apply(style_row, axis=1).format({
                    'Momentum (%)': lambda x: x if isinstance(x, str) else f'{x:.2f}',
                    'Trend vs 200DMA (%)': lambda x: x if isinstance(x, str) else f'{x:.2f}',
                    'Rel Strength vs SPY (%)': lambda x: x if isinstance(x, str) else f'{x:.2f}'
                }, na_rep='N/A')
                
                # Display the styled DataFrame
                st.dataframe(styled_signals, use_container_width=True, hide_index=True)
                
                st.caption("💡 Signals are based on quantitative rules and cached for 1 hour. Buy = Strong positive momentum + trend. Hold = Mixed signals. Sell/Avoid = Negative momentum or trend.")
            
            # IPS Alignment Card
            if st.session_state.ips_targets:
                with st.container(border=True):
                    st.subheader('⚖️ IPS Alignment Check')
                    
                    # Create alignment table
                    targets = st.session_state.ips_targets
                    beta_min, beta_max = targets['beta_range']
                    vol_min, vol_max = targets['volatility_range']
                    yield_min = targets.get('yield_min', 0)
                    
                    alignment_results = assess_alignment(
                        metrics, targets, st.session_state.ips_profile
                    )
                    
                    # Calculate status for each metric
                    beta_status = 'OK' if beta_min <= metrics['portfolio_beta'] <= beta_max else 'Adjust'
                    vol_status = 'OK' if vol_min <= metrics['annual_volatility'] <= vol_max else 'Adjust'
                    yield_status = 'OK' if yield_min <= metrics['weighted_dividend_yield'] else 'Adjust'
                    
                    # Alignment table
                    alignment_data = {
                        'Metric': ['Portfolio Beta', 'Volatility', 'Dividend Yield'],
                        'Your Portfolio': [
                            f"{metrics['portfolio_beta']:.2f}",
                            f"{metrics['annual_volatility']*100:.1f}%",
                            f"{metrics['weighted_dividend_yield']:.1f}%"
                        ],
                        'IPS Target': [
                            f"{beta_min:.1f} - {beta_max:.1f}",
                            f"{vol_min*100:.0f}% - {vol_max*100:.0f}%",
                            f"≥{yield_min*100:.0f}%"
                        ],
                        'Status': [
                            beta_status,
                            vol_status,
                            yield_status
                        ]
                    }
                    
                    alignment_df = pd.DataFrame(alignment_data)
                    st.dataframe(alignment_df, use_container_width=True, hide_index=True)
                    
                    # Alignment summary
                    st.markdown("##### 📋 Alignment Summary")
                    alignment_results = assess_alignment(metrics, targets, st.session_state.ips_profile)
                    alignment_text = '\n'.join(alignment_results['bullets'])
                    st.markdown(alignment_text, unsafe_allow_html=True)
            
            # Monte Carlo Simulation Card
            with st.container(border=True):
                st.subheader('🔮 Monte Carlo Retirement Simulation')
                st.caption('Simulates 500 retirement scenarios with fixed annual withdrawals to test sequence of returns risk.')
                
                # Monte Carlo inputs
                mc_col1, mc_col2 = st.columns(2)
                with mc_col1:
                    sim_years = st.slider(
                        'Projection Horizon',
                        min_value=5,
                        max_value=30,
                        value=20,
                        help='Number of years to simulate portfolio withdrawals.'
                    )
                with mc_col2:
                    annual_withdrawal = st.number_input(
                        'Annual Withdrawal ($)',
                        min_value=0,
                        max_value=500000,
                        value=40000,
                        step=5000,
                        help='Fixed amount to withdraw each year from the portfolio.'
                    )
                
                # Run Monte Carlo simulation
                mc_results = run_monte_carlo(
                    initial_value=metrics['total_value'],
                    cagr=metrics['annualized_return'],
                    volatility=metrics['annual_volatility'],
                    years=sim_years,
                    simulations=500,
                    annual_withdrawal=annual_withdrawal
                )
                
                # Create projection table from Monte Carlo results
                st.markdown("##### 📈 Projection Summary")
                projection_data = {
                    'Scenario': ['Conservative (10th Percentile)', 'Expected (50th Percentile)', 'Optimistic (90th Percentile)'],
                    'Final Portfolio Value': [
                        f"${mc_results['10th Percentile (Bear Market)'].iloc[-1]:,.0f}",
                        f"${mc_results['50th Percentile (Expected)'].iloc[-1]:,.0f}",
                        f"${mc_results['90th Percentile (Bull Market)'].iloc[-1]:,.0f}"
                    ]
                }
                
                projection_df = pd.DataFrame(projection_data)
                st.dataframe(projection_df, use_container_width=True, hide_index=True)
                
                # Create Monte Carlo chart
                mc_fig = px.line(
                    mc_results,
                    labels={
                        "value": "Portfolio Value ($)",
                        "index": "Years",
                        "variable": "Percentile"
                    },
                    color_discrete_map={
                        '10th': '#dc2626',
                        '50th': '#2563eb',
                        '90th': '#16a34a'
                    }
                )
                
                mc_fig.update_traces(line=dict(width=2))
                mc_fig.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Portfolio Value ($)",
                    xaxis_title="Years",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(color='#4a5568')
                    ),
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=40, b=0),
                    font=dict(color='#4a5568')
                )
                mc_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
                mc_fig.update_yaxes(showgrid=False, tickformat="$,.0f", tickfont=dict(color='#4a5568'), rangemode='tozero')
                
                # Store Monte Carlo figure in session state for PDF generation
                st.session_state.current_monte_carlo_fig = mc_fig
                
                st.plotly_chart(mc_fig, use_container_width=True)
                
                st.caption("📊 This simulation runs 500 randomized market scenarios based on your portfolio's historical risk/return profile. The three lines represent the range of probable outcomes: bear market (10th percentile), expected case (median), and bull market (90th percentile).")
            
            # PDF Generation
            if st.button("📄 Generate PDF Report", type="primary", use_container_width=True, key="pdf_generate"):
                # Create progress container
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Use session state data
                    if 'current_metrics' in st.session_state:
                        # Step 1: Prepare data
                        status_text.text("⏳ Preparing data... (20%)")
                        progress_bar.progress(20)
                        
                        # Step 2: Prepare IPS alignment text
                        status_text.text("⏳ Preparing IPS alignment... (40%)")
                        progress_bar.progress(40)
                        
                        # Get alignment text
                        alignment_results = assess_alignment(
                            st.session_state.current_metrics, 
                            st.session_state.ips_targets
                        )
                        clean_bullets = []
                        for bullet in alignment_results['alignment_text'].split('\n'):
                            if bullet.strip().startswith('•'):
                                clean_bullet = bullet.strip()[2:].strip()
                                # Remove any remaining non-ASCII characters
                                clean_bullet = ''.join(char for char in clean_bullet if ord(char) < 128)
                                clean_bullets.append(clean_bullet.strip())
                        
                        # Step 3: Prepare chart
                        status_text.text("⏳ Preparing chart... (60%)")
                        progress_bar.progress(60)
                        
                        # Generate PDF
                        chart_fig = st.session_state.get('current_chart')
                        if not chart_fig or not hasattr(chart_fig, 'data'):
                            chart_fig = build_growth_chart(st.session_state.current_metrics['chart_data'])
                        
                        # Step 4: Generate PDF
                        status_text.text("⏳ Generating PDF document... (80%)")
                        progress_bar.progress(80)
                        
                        pdf_bytes = generate_pdf_report(
                            metrics=st.session_state.current_metrics,
                            ips_profile=st.session_state.ips_profile,
                            ips_alignment_text=clean_bullets,
                            growth_chart_fig=chart_fig,
                            projection_df=st.session_state.current_metrics['projection_df'],
                            ips_targets=st.session_state.ips_targets,
                            monte_carlo_fig=st.session_state.get('current_monte_carlo_fig')
                        )
                        
                        # Step 5: Complete
                        status_text.text("✅ Finalizing... (100%)")
                        progress_bar.progress(100)
                        
                        # Store in session state
                        st.session_state.pdf_data = pdf_bytes
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Trigger automatic download
                        st.success("✅ PDF Report generated successfully! Download starting...")
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"Portfolio_Tear_Sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        progress_bar.empty()
                        status_text.empty()
                        st.error("Please analyze a portfolio first before generating PDF.")
                
                except Exception as pdf_error:
                    progress_bar.empty()
                    status_text.empty()
                    import traceback
                    error_details = traceback.format_exc()
                    st.error(f"PDF generation failed: {str(pdf_error)}")
                    with st.expander("🔍 Error Details (for debugging)"):
                        st.code(error_details)
